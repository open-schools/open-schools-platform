import io
import logging
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple

import pdfplumber
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from django.http import HttpResponse, Http404
from pypdf import PdfWriter, PdfReader

from open_schools_platform.receipt_management.receipts.models import Receipt, ReceiptService
from open_schools_platform.receipt_management.receipts.selectors import get_receipts_for_family
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.student_management.students.selectors import get_student_profile # Added
from open_schools_platform.receipt_management.receipts.serializers import GetReceiptDetailedSerializer # Added

logger = logging.getLogger(__name__)

PATTERNS = {
            'internal_receipt_number': r'(?:Лицевой счет)[\s:]*(\d+)',
            'payer_full_name': r'(?:Плательщик)[\s:]*([А-Яа-я\s]+?)(?:\s+Группа)',
            'recipient_full_name': r'(?:За кого)[\s:]*([А-Яа-я\s]+)(?=\s*Счет от)',
            'institution_name': r'(Департамент[^)]*[)])',
            'service_category': r'(?:Группа)[\\s:]*([А-ЯА-я\\s\\d]+?)(?=\\s*Наименование платежа)',
            'payment_due_date': r'(?:Оплатить до)[\\s:]*(\\d{1,2}\\.\\d{1,2}\\.\\d{4})',
            'payment_purpose': r'(?:Наименование платежа)[\\s:]*([^З]+?)(?=\\s*За кого)',
            'receipt_date': r'(?:Счет от)[\\s:]*(\\d{1,2}\\.\\d{1,2}\\.\\d{4})',
        }

MONTHS_RU = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
             'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']


def clean_row(row):
    cleaned = []
    for cell in row:
        if cell is None:
            cleaned.append(cell)
        else:
            cell_str = str(cell).replace('\n', '').strip()
            if re.match(r'^\d+[ ]*\d*,\d{2}$', cell_str):
                cell_str = cell_str.replace(' ', '').replace(',', '.')
            cleaned.append(cell_str)
    return cleaned


def create_formatted_headers(text: str) -> List[str]:
    receipt_date_match = re.search(PATTERNS['receipt_date'], text)
    if not receipt_date_match:
        return []

    receipt_date = datetime.strptime(receipt_date_match.group(1), '%d.%m.%Y').date()
    first_day_current = receipt_date.replace(day=1)
    first_day_next = (receipt_date + relativedelta(months=1)).replace(day=1)

    month_name = MONTHS_RU[receipt_date.month - 1]
    year = receipt_date.year

    return [
        'Учреждение',
        'Вид услуги',
        f'Задолженность на {first_day_current.strftime("%d.%m.%Y")}',
        f'Начислено за {month_name} {year}',
        'Перерасчет за предыдущие периоды',
        f'Оплачено {month_name} {year}',
        f'Задолженность на {first_day_next.strftime("%d.%m.%Y")}',
        'Предоплата',
        'Итого к оплате в рублях'
    ]


def extract_text_and_tables_from_pdf(pdf_file) -> Tuple[str, List]:
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_x_tolerance": 4,
    }

    pdf_file.seek(0)
    text = ''
    clean_table = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:

            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

            tables = page.extract_tables(table_settings=table_settings)
            if tables and not clean_table:
                for row in tables[0]:
                    if (sum(1 for cell in row if cell is not None) >= 3 and
                            not any('Учреждение' in str(cell or '') for cell in row)):
                        clean_table.append(clean_row(row))

    if clean_table:
        headers = create_formatted_headers(text)
        if headers:
            clean_table.insert(0, headers)

    return text, clean_table


def parse_amount(amount_str: str) -> Decimal:
    if not amount_str or amount_str == '0.00':
        return Decimal('0.00')

    try:
        return Decimal(str(amount_str))
    except (ValueError, InvalidOperation):
        return Decimal('0.00')


class PDFReceiptParser:

    def __init__(self):
        self.patterns = {
            'internal_receipt_number': r'(?:Лицевой счет)[\s:]*(\d+)',
            'payer_full_name': r'(?:Плательщик)[\s:]*([А-Яа-я\s]+?)(?:\s+Группа)',
            'recipient_full_name': r'(?:За кого)[\s:]*([А-Яа-я\s]+)(?=\s*Счет от)',
            'institution_name': r'(Департамент[^)]*[)])',
            'service_category': r'(?:Группа)[\\s:]*([А-ЯА-я\\s\\d]+?)(?=\\s*Наименование платежа)',
            'payment_due_date': r'(?:Оплатить до)[\\s:]*(\\d{1,2}\\.\\d{1,2}\\.\\d{4})',
            'payment_purpose': r'(?:Наименование платежа)[\\s:]*([^З]+?)(?=\\s*За кого)',
            'receipt_date': r'(?:Счет от)[\\s:]*(\\d{1,2}\\.\\d{1,2}\\.\\d{4})',
        }

    def extract_financial_data_from_table(self, tables: List) -> Dict:
        """Extract and sum financial data from table rows"""
        financial_data = {
            'debt_at_month_start': Decimal('0.00'),
            'charged_this_month': Decimal('0.00'),
            'recalculation_amount': Decimal('0.00'),
            'paid_amount': Decimal('0.00'),
            'debt_at_next_month_start': Decimal('0.00'),
            'prepayment': Decimal('0.00'),
            'service_amount': Decimal('0.00'),
            'services': []
        }
        if not tables or len(tables) < 2:
            return financial_data

        for row in tables[1:]:
            if not row or len(row) < 9:
                continue

            service_info = {
                'institution': row[0],
                'service_name': row[1],
                'debt_at_month_start': parse_amount(row[2]),
                'charged_this_month': parse_amount(row[3]),
                'recalculation_amount': parse_amount(row[4]),
                'paid_amount': parse_amount(row[5]),
                'debt_at_next_month_start': parse_amount(row[6]),
                'prepayment': parse_amount(row[7]),
                'service_amount': parse_amount(row[8])
            }

            financial_data['services'].append(service_info)

            financial_data['debt_at_month_start'] += service_info['debt_at_month_start']
            financial_data['charged_this_month'] += service_info['charged_this_month']
            financial_data['recalculation_amount'] += service_info['recalculation_amount']
            financial_data['paid_amount'] += service_info['paid_amount']
            financial_data['debt_at_next_month_start'] += service_info['debt_at_next_month_start']
            financial_data['prepayment'] += service_info['prepayment']
            financial_data['service_amount'] += service_info['service_amount']

        return financial_data

    def extract_receipt_data(self, text, tables):
        extracted_data = {}

        for field, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    value = match.group(1).strip()

                    if field in ['receipt_date', 'payment_due_date']:
                        value = datetime.strptime(value, '%d.%m.%Y')
                        value = value.strftime('%Y-%m-%d')

                    extracted_data[field] = value

                except IndexError:
                    value = match.group(0).strip()
                    extracted_data[field] = value

        financial_data = self.extract_financial_data_from_table(tables)
        extracted_data.update(financial_data)

        extracted_data['service_amount'] = financial_data['service_amount']
        extracted_data['total_amount'] = financial_data['service_amount']

        service_names = [s['service_name'] for s in financial_data['services'] if s['service_name']]
        extracted_data['service_name'] = ', '.join(service_names) if service_names else "Образовательные услуги"

        return extracted_data

    def parse_pdf_receipt(self, pdf_file, student_profile: StudentProfile = None) -> Dict: # Made student_profile optional
        """
        Main method to parse PDF receipt and return structured data
        """
        try:
            pdf_text, tables = extract_text_and_tables_from_pdf(pdf_file)

            logger.info(f"Extracted text length: {len(pdf_text)}")
            logger.info(f"Found {len(tables)} tables")

            receipt_data = self.extract_receipt_data(pdf_text, tables)

            logger.info(f"Extracted receipt data: {receipt_data}")

            if student_profile:
                receipt_data.setdefault('student_profile', student_profile)
                receipt_data.setdefault('recipient_full_name', student_profile.name)


            receipt_data.setdefault('internal_receipt_number', f"REC-{datetime.now().strftime('%Y%m%d%H%M%S%f')}") # Added %f for more uniqueness
            receipt_data.setdefault('institution_name', "МБОУ гимназия №5") # This might need to be dynamic
            receipt_data.setdefault('service_name', "Образовательные услуги")
            receipt_data.setdefault('service_amount', Decimal('0.00'))
            receipt_data.setdefault('total_amount', Decimal('0.00'))
            receipt_data.setdefault('receipt_date', date.today())
            receipt_data.setdefault('payment_due_date', date.today())
            receipt_data.setdefault('payment_purpose', "Оплата образовательных услуг")
            receipt_data.setdefault('service_category', "ПЛАТНЫЕ УСЛУГИ")

            return receipt_data

        except Exception as e:
            logger.error(f"Error parsing PDF receipt: {str(e)}")
            raise ValueError(f"Failed to parse PDF receipt: {str(e)}")


def process_pdf_receipt(pdf_file, student_profile: StudentProfile) -> Receipt:
    """
    Process uploaded PDF file and create receipt
    """
    parser = PDFReceiptParser()

    receipt_data = parser.parse_pdf_receipt(pdf_file, student_profile)

    pdf_file.seek(0)
    pdf_content = ContentFile(pdf_file.read())
    receipt_data['pdf_file'] = pdf_content

    receipt = create_receipt(**receipt_data)

    receipt.pdf_file.save(
        f"receipt_{receipt.id}.pdf",
        pdf_content,
        save=True
    )

    logger.info(f"Processed PDF receipt {receipt.id} for student {student_profile.name}")
    return receipt


# def extract_individual_receipts_from_pdf(pdf_file) -> List[Dict]:
#     """
#     Extracts individual receipt data from a multi-page PDF, where each page is one receipt.
#     Returns a list of dictionaries, each containing parsed data and 'pdf_page_content' (BytesIO).
#     """
#     logger.info("Starting extraction of individual receipts from multi-page PDF.")
#     parser = PDFReceiptParser()
#     receipts_data_list = []
#
#     pdf_file.seek(0)
#     pdf_content_bytes = pdf_file.read()  # Read the entire PDF content once
#     pdf_file_main_stream = io.BytesIO(pdf_content_bytes) # Use this stream for PdfReader
#
#     try:
#         # Use a separate BytesIO stream for pdfplumber if needed for initial page count or other ops
#         # Or, if pdfplumber is only used for text/table extraction within parse_pdf_receipt,
#         # it will receive single-page streams.
#
#         # Get page count using PdfReader first
#         temp_reader_for_page_count = PdfReader(io.BytesIO(pdf_content_bytes))
#         num_pages = len(temp_reader_for_page_count.pages)
#
#         if num_pages == 0:
#             logger.warning("Uploaded PDF has no pages.")
#             return []
#
#         logger.info(f"PDF has {num_pages} pages. Iterating through each page.")
#
#         for i in range(num_pages):
#             page_num_for_logging = i + 1
#             logger.info(f"Processing page {page_num_for_logging} of {num_pages}")
#
#             single_page_pdf_stream = io.BytesIO()
#             writer = PdfWriter()
#
#             # Use the main BytesIO stream for PdfReader, re-create reader or seek for each page
#             # Creating a new reader instance for each page from the same main stream is safer
#             current_page_reader = PdfReader(io.BytesIO(pdf_content_bytes))
#
#             if i < len(current_page_reader.pages):
#                 writer.add_page(current_page_reader.pages[i])
#                 writer.write(single_page_pdf_stream)
#                 single_page_pdf_stream.seek(0) # Reset stream for parsing
#
#                 # Pass the single-page stream to the parser
#                 parsed_data = parser.parse_pdf_receipt(single_page_pdf_stream, student_profile=None)
#                 print(parsed_data)
#
#                 if parsed_data.get('recipient_full_name'):
#                     parsed_data['source_page_number'] = page_num_for_logging
#                     single_page_pdf_stream.seek(0)
#                     # Store the stream itself, it will be read later in process_bulk_pdf_receipt
#                     parsed_data['pdf_page_content'] = single_page_pdf_stream
#                     receipts_data_list.append(parsed_data)
#                     logger.info(f"Successfully parsed receipt from page {page_num_for_logging}. Recipient: {parsed_data.get('recipient_full_name')}")
#                 else:
#                     logger.warning(f"Could not extract recipient_full_name from page {page_num_for_logging}. Skipping this page.")
#                     single_page_pdf_stream.close() # Close stream if not used
#             else:
#                 # This case should ideally not be reached if num_pages is accurate
#                 logger.warning(f"Page index {i} out of bounds for PdfReader with {len(current_page_reader.pages)} pages.")
#                 single_page_pdf_stream.close() # Close stream if error
#
#     except Exception as e:
#         logger.error(f"Error processing multi-page PDF for individual receipts: {str(e)}", exc_info=True)
#         # Clean up any streams in receipts_data_list if an error occurs mid-processing
#         for data_item in receipts_data_list:
#             if 'pdf_page_content' in data_item and hasattr(data_item['pdf_page_content'], 'close'):
#                 data_item['pdf_page_content'].close()
#         return []
#     finally:
#         pdf_file_main_stream.close() # Close the main BytesIO stream
#
#     logger.info(f"Extracted {len(receipts_data_list)} potential receipts from the PDF.")
#     return receipts_data_list
#
#
# def process_bulk_pdf_receipt(pdf_file) -> Dict[str, any]:
#     """
#     Process uploaded PDF file that contains multiple receipts (one per page).
#     Tries to identify students by recipient_full_name and create receipts.
#     """
#     individual_receipt_data_list = extract_individual_receipts_from_pdf(pdf_file)
#
#     created_receipts_api_data = []
#     failed_receipts_info = []
#
#     for receipt_data_item in individual_receipt_data_list:
#         student_name = receipt_data_item.get('recipient_full_name')
#         pdf_page_content_stream = receipt_data_item.pop('pdf_page_content', None)
#         source_page_number = receipt_data_item.get('source_page_number', 'unknown')
#
#         if not student_name:
#             logger.warning(f"Skipping receipt item from page {source_page_number} due to missing recipient_full_name.")
#             failed_receipts_info.append({'reason': 'Missing recipient_full_name', 'source_page': source_page_number, 'data': receipt_data_item})
#             if pdf_page_content_stream:
#                 pdf_page_content_stream.close()
#             continue
#
#         if not pdf_page_content_stream:
#             logger.warning(f"Skipping receipt for {student_name} from page {source_page_number} due to missing PDF page content.")
#             failed_receipts_info.append({'student_name': student_name, 'source_page': source_page_number, 'reason': 'Missing PDF page content', 'data': receipt_data_item})
#             continue
#
#         try:
#             student_profile = get_student_profile(filters={'name__icontains': student_name}, empty_exception=False)
#             if not student_profile:
#                 name_parts = student_name.split()
#                 if len(name_parts) >= 2:
#                     student_profile = get_student_profile(
#                         filters={'user__last_name__icontains': name_parts[0], 'user__first_name__icontains': name_parts[1]},
#                         empty_exception=False
#                     )
#                 if not student_profile and len(name_parts) >= 3:
#                      student_profile = get_student_profile(
#                         filters={'user__last_name__icontains': name_parts[0], 'user__first_name__icontains': name_parts[1], 'user__patronymic__icontains': name_parts[2]},
#                         empty_exception=False
#                     )
#
#             if student_profile:
#                 current_receipt_data = receipt_data_item.copy()
#                 current_receipt_data['student_profile'] = student_profile
#
#                 current_receipt_data.pop('source_page_number', None)
#
#                 pdf_page_content_stream.seek(0) # Ensure stream is at the beginning before reading
#                 file_content = pdf_page_content_stream.read()
#                 # Create a new ContentFile for each receipt
#                 pdf_for_receipt_model = ContentFile(file_content, name=f"receipt_p{source_page_number}_for_{student_name.replace(' ', '_')}.pdf")
#                 current_receipt_data['pdf_file'] = pdf_for_receipt_model
#
#                 new_receipt = create_receipt(**current_receipt_data)
#
#                 # The FileField in `create_receipt` should handle saving.
#                 # For explicit filename control with receipt ID, we can re-save.
#                 pdf_for_receipt_model.seek(0) # Rewind ContentFile's internal pointer
#                 new_receipt.pdf_file.save(
#                     f"receipt_{new_receipt.id}_p{source_page_number}.pdf",
#                     pdf_for_receipt_model, # Pass the ContentFile
#                     save=True
#                 )
#                 created_receipts_api_data.append(GetReceiptDetailedSerializer(new_receipt).data)
#                 logger.info(f"Created receipt {new_receipt.id} for student: {student_name} from page {source_page_number}")
#             else:
#                 logger.warning(f"Student profile not found for: {student_name} (page {source_page_number}). Skipping receipt creation.")
#                 failed_receipts_info.append({'student_name': student_name, 'source_page': source_page_number, 'reason': 'Student not found'})
#         except Exception as e:
#             logger.error(f"Failed to create receipt for {student_name} (page {source_page_number}): {str(e)}", exc_info=True)
#             failed_receipts_info.append({'student_name': student_name, 'source_page': source_page_number,'reason': str(e)})
#         finally:
#             if pdf_page_content_stream:
#                 pdf_page_content_stream.close()
#
#     return {"created_count": len(created_receipts_api_data), "failed_count": len(failed_receipts_info), "created_receipts": created_receipts_api_data, "failed_details": failed_receipts_info}


def create_receipt(student_profile: StudentProfile, **receipt_data) -> Receipt:
    """
    Create a new receipt and associated services
    """
    services_data = receipt_data.pop('services', [])

    if 'total_amount' not in receipt_data and 'service_amount' in receipt_data:
        receipt_data['total_amount'] = receipt_data['service_amount']

    receipt = Receipt.objects.create_receipt(
        student_profile=student_profile,
        **receipt_data
    )

    for service_data in services_data:
        ReceiptService.objects.create(
            receipt=receipt,
            **service_data
        )

    logger.info(f"Created receipt {receipt.id} with {len(services_data)} services for student {student_profile.name}")
    return receipt


class PDFDownloadService:
    """
    Service for handling PDF download operations for receipts
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def download_single_receipt_pdf(self, receipt: Receipt) -> HttpResponse:
        """
        Download PDF for a single receipt
        
        Args:
            receipt: Receipt instance
            
        Returns:
            HttpResponse with PDF content
            
        Raises:
            Http404: If PDF file not found
        """
        if not receipt.pdf_file:
            raise Http404("PDF file not found for this receipt.")

        try:
            response = HttpResponse(receipt.pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.internal_receipt_number}.pdf"'
            self.logger.info(f"Downloaded PDF for receipt {receipt.id}")
            return response
        except FileNotFoundError:
            self.logger.error(f"PDF file not found on storage for receipt {receipt.id}")
            raise Http404("PDF file not found on storage.")

    # def download_consolidated_family_pdf(self, family, filters=None) -> HttpResponse:
    #     """
    #     Download consolidated PDF for all receipts in a family
    #
    #     Args:
    #         family: Family instance
    #         filters: Optional filters for receipts
    #
    #     Returns:
    #         HttpResponse with consolidated PDF content
    #
    #     Raises:
    #         Http404: If no receipts or valid PDFs found
    #     """
    #     receipts = get_receipts_for_family(family=family, filters=filters or {})
    #
    #     if not receipts.exists():
    #         raise Http404("No receipts found for this family.")
    #
    #     merger = PdfWriter()
    #     processed_count = 0
    #
    #     for receipt in receipts:
    #         if receipt.pdf_file:
    #             try:
    #                 pdf_file_buffer = io.BytesIO(receipt.pdf_file.read())
    #                 reader = PdfReader(pdf_file_buffer)
    #                 for page in reader.pages:
    #                     merger.add_page(page)
    #                 receipt.pdf_file.seek(0)
    #                 processed_count += 1
    #                 self.logger.debug(f"Added PDF for receipt {receipt.id} to consolidated file")
    #             except FileNotFoundError:
    #                 self.logger.warning(f"PDF for receipt {receipt.id} not found on storage. Skipping.")
    #                 continue
    #             except Exception as e:
    #                 self.logger.warning(f"Error processing PDF for receipt {receipt.id}: {e}. Skipping.")
    #                 continue
    #
    #     if not merger.pages:
    #         raise Http404("No valid PDF files found to merge for this family's receipts.")
    #
    #     output_buffer = io.BytesIO()
    #     merger.write(output_buffer)
    #     output_buffer.seek(0)
    #
    #     response = HttpResponse(output_buffer.read(), content_type='application/pdf')
    #     response['Content-Disposition'] = f'attachment; filename="family_{family.id}_receipts.pdf"'
    #
    #     self.logger.info(f"Generated consolidated PDF for family {family.id} with {processed_count} receipts")
    #     return response


class ReceiptUpdateService:
    """
    Service for updating receipt records
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_receipt(self, receipt: Receipt, **receipt_data) -> Receipt:
        """
        Update an existing receipt
        
        Args:
            receipt: Receipt instance to update
            **receipt_data: Fields to update
            
        Returns:
            Updated Receipt instance
        """
        from open_schools_platform.common.services import model_update

        fields = [
            'internal_receipt_number', 'payer_full_name', 'recipient_full_name',
            'institution_name', 'service_name', 'service_category',
            'debt_at_month_start', 'recalculation_amount', 'paid_amount',
            'debt_at_next_month_start', 'prepayment', 'service_amount',
            'total_amount', 'receipt_date', 'payment_due_date', 'payment_purpose',
            'qr_code_data', 'pdf_file'
        ]

        updated_receipt = model_update(
            instance=receipt,
            fields=fields,
            data=receipt_data
        )        
        self.logger.info(f"Updated receipt {receipt.id}")
        return updated_receipt


class ReceiptNotificationService:
    """
    Service for handling receipt notifications
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_receipt_notification(self, receipt: Receipt, notification_type: str = 'initial',
                                  custom_message: str = '') -> bool:
        """
        Send notification to parents about receipt
        
        Args:
            receipt: Receipt instance
            notification_type: Type of notification ('initial', 'reminder', 'overdue')
            custom_message: Optional custom message to append
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            from open_schools_platform.receipt_management.receipts.models import ReceiptNotification
            from open_schools_platform.user_management.users.services import notify_user
            from django.utils import timezone

            families = receipt.student_profile.families.all()
            parent_profiles = []

            for family in families:
                parent_profiles.extend(family.parent_profiles.all())

            if not parent_profiles:
                self.logger.warning(f"No parent profiles found for receipt {receipt.id}")
                return False

            notification = ReceiptNotification.objects.create_notification(
                receipt=receipt,
                notification_type=notification_type
            )

            title = self._get_notification_title(notification_type)
            body = self._get_notification_body(receipt, notification_type, custom_message)

            successful_sends = 0
            for parent_profile in parent_profiles:
                if hasattr(parent_profile.user, 'firebase_token'):
                    success = notify_user(
                        user=parent_profile.user,
                        title=title,
                        body=body,
                        data={'receipt_id': str(receipt.id)}
                    )
                    if success:
                        successful_sends += 1

            if successful_sends > 0:
                notification.is_sent = True
                notification.sent_at = timezone.now()
                notification.save()

            self.logger.info(f"Sent receipt notification {notification.id} to {successful_sends} parents")
            return successful_sends > 0

        except Exception as e:
            self.logger.error(f"Error sending receipt notification: {str(e)}")
            return False

    def bulk_send_receipt_notifications(self, receipt_ids: List[str], notification_type: str = 'initial',
                                        custom_message: str = '') -> Dict[str, int]:
        """
        Send notifications for multiple receipts
        
        Args:
            receipt_ids: List of receipt IDs
            notification_type: Type of notification
            custom_message: Optional custom message
            
        Returns:
            Dictionary with success and failed counts
        """
        results = {'success': 0, 'failed': 0}

        for receipt_id in receipt_ids:
            try:
                receipt = Receipt.objects.get(id=receipt_id)
                success = self.send_receipt_notification(receipt, notification_type, custom_message)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1

            except Receipt.DoesNotExist:
                self.logger.error(f"Receipt {receipt_id} not found")
                results['failed'] += 1
            except Exception as e:
                self.logger.error(f"Error sending notification for receipt {receipt_id}: {str(e)}")
                results['failed'] += 1

        self.logger.info(f"Bulk notification results: {results['success']} successful, {results['failed']} failed")
        return results

    def _get_notification_title(self, notification_type: str) -> str:
        """
        Get notification title based on type
        """
        titles = {
            'initial': 'Новая квитанция',
            'reminder': 'Напоминание об оплате',
            'overdue': 'Просрочен платёж'
        }
        return titles.get(notification_type, 'Уведомление о платеже')

    def _get_notification_body(self, receipt: Receipt, notification_type: str, custom_message: str = '') -> str:
        """
        Get notification body text
        """
        base_messages = {
            'initial': f'Получена новая квитанция на сумму {receipt.total_amount} руб. для {receipt.recipient_full_name}',
            'reminder': f'Напоминаем об оплате квитанции на сумму {receipt.total_amount} руб. до {receipt.payment_due_date}',
            'overdue': f'Просрочен платёж по квитанции на сумму {receipt.total_amount} руб. для {receipt.recipient_full_name}'
        }

        body = base_messages.get(notification_type, f'Квитанция на сумму {receipt.total_amount} руб.')

        if custom_message:
            body += f"\n\n{custom_message}"

        return body


def update_receipt(receipt: Receipt, **receipt_data) -> Receipt:
    """Convenience function for updating receipts"""
    service = ReceiptUpdateService()
    return service.update_receipt(receipt, **receipt_data)


def send_receipt_notification(receipt: Receipt, notification_type: str = 'initial',
                              custom_message: str = '') -> bool:
    """Convenience function for sending receipt notifications"""
    service = ReceiptNotificationService()
    return service.send_receipt_notification(receipt, notification_type, custom_message)


def bulk_send_receipt_notifications(receipt_ids: List[str], notification_type: str = 'initial',
                                    custom_message: str = '') -> Dict[str, int]:
    """Convenience function for bulk sending receipt notifications"""
    service = ReceiptNotificationService()
    return service.bulk_send_receipt_notifications(receipt_ids, notification_type, custom_message)
