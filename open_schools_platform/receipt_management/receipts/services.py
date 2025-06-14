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

from open_schools_platform.receipt_management.receipts.selectors import get_receipts_for_family
from open_schools_platform.receipt_management.receipts.models import Receipt, ReceiptService
from open_schools_platform.student_management.students.models import StudentProfile

logger = logging.getLogger(__name__)

PATTERNS = {
    'internal_receipt_number': r'(?:Лицевой счет)[\s:]*(\d+)',
    'payer_full_name': r'(?:Плательщик)[\s:]*([А-Яа-яЁё\s]+?)(?:\s+Группа)',
    'recipient_full_name': r'(?:За кого)[\s:]*([А-Яа-яЁё\s]+)(?=\s*Счет от)',
    'institution_name': r'(Департамент[^)]*[)])',
    'service_category': r'(?:Группа)[\s:]*([А-ЯА-я\s\d]+?)(?=\s*Наименование платежа)',
    'payment_due_date': r'(?:Оплатить до)[\s:]*(\d{1,2}\.\d{1,2}\.\d{4})',
    'payment_purpose': r'(?:Наименование платежа)[\s:]*([^З]+?)(?=\s*За кого)',
    'receipt_date': r'(?:Счет от)[\s:]*(\d{1,2}\.\d{1,2}\.\d{4})',
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


def extract_logical_receipts_from_pdf(pdf_file) -> List[Dict]:
    """
    Extract logical receipts from PDF, handling both single and multi-receipt pages.
    Returns a list of dictionaries, each representing a logical receipt.
    """
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_x_tolerance": 4,
    }

    pdf_file.seek(0)
    logical_receipts = []

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):

            tables = page.extract_tables(table_settings=table_settings)
            logger.debug(f"Page {page_num + 1}: Found {len(tables)} tables")

            needs_horizontal_split = len(tables) >= 4
            if needs_horizontal_split:
                page_width = page.width
                page_height = page.height
                mid_y = page_height / 2

                regions_definitions = [
                    {"name": "Upper Half", "bbox": (0, 0, page_width, mid_y)},
                    {"name": "Lower Half", "bbox": (0, mid_y, page_width, page_height)}
                ]

                for region_def in regions_definitions:
                    cropped_page = page.crop(region_def["bbox"])
                    region_text = cropped_page.extract_text() or ""
                    region_raw_tables = cropped_page.extract_tables(table_settings)

                    processed_region_table = []
                    if region_raw_tables and region_raw_tables[0]:
                        first_raw_table = region_raw_tables[0]
                        temp_clean_table = []
                        for row in first_raw_table:
                            if (sum(1 for cell in row if cell is not None) >= 3 and
                                    not any('Учреждение' in str(cell or '') for cell in row)):
                                temp_clean_table.append(clean_row(row))

                        if temp_clean_table:
                            table_headers = create_formatted_headers(region_text)
                            if table_headers:
                                processed_region_table.append(table_headers)
                            processed_region_table.extend(temp_clean_table)

                    logical_receipts.append({
                        'text': region_text,
                        'processed_table': processed_region_table,
                        'source_page_number': page_num + 1,
                        'source_region_name': region_def["name"]
                    })

            else:
                page_text = page.extract_text() or ""
                clean_table = []

                if tables:
                    first_table = tables[0]
                    temp_clean_table = []
                    for row in first_table:
                        if (sum(1 for cell in row if cell is not None) >= 3 and
                                not any('Учреждение' in str(cell or '') for cell in row)):
                            temp_clean_table.append(clean_row(row))

                    if temp_clean_table:
                        headers = create_formatted_headers(page_text)
                        if headers:
                            clean_table.append(headers)
                        clean_table.extend(temp_clean_table)

                logical_receipts.append({
                    'text': page_text,
                    'processed_table': clean_table,
                    'source_page_number': page_num + 1,
                    'source_region_name': "Full Page"
                })

    logger.info(f"Total logical receipts found: {len(logical_receipts)}")
    return logical_receipts

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
            'payer_full_name': r'(?:Плательщик)[\s:]*([А-Яа-яЁё\s]+?)(?:\s+Группа)',
            'recipient_full_name': r'(?:За кого)[\s:]*([А-Яа-яЁё\s]+)(?=\s*Счет от)',
            'institution_name': r'(Департамент[^)]*[)])',
            'service_category': r'(?:Группа)[\s:]*([А-ЯА-я\s\d]+?)(?=\s*Наименование платежа)',
            'payment_due_date': r'(?:Оплатить до)[\s:]*(\d{1,2}\.\d{1,2}\.\d{4})',
            'payment_purpose': r'(?:Наименование платежа)[\s:]*([^З]+?)(?=\s*За кого)',
            'receipt_date': r'(?:Счет от)[\s:]*(\d{1,2}\.\d{1,2}\.\d{4})',
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

    def parse_pdf_receipt(self, pdf_file, student_profile: StudentProfile = None) -> List[Dict]:
        """
        Main method to parse PDF receipt and return structured data for all logical receipts.
        Returns a list of receipt data dictionaries.
        """
        try:
            logical_receipts = extract_logical_receipts_from_pdf(pdf_file)

            logger.info(f"Found {len(logical_receipts)} logical receipts")

            parsed_receipts = []

            for logical_receipt in logical_receipts:
                receipt_data = self.extract_receipt_data(
                    logical_receipt['text'],
                    logical_receipt['processed_table']
                )
                receipt_data['source_page_number'] = logical_receipt['source_page_number']
                receipt_data['source_region_name'] = logical_receipt['source_region_name']

                logger.info(
                    f"Extracted receipt data for {logical_receipt['source_region_name']} on page {logical_receipt['source_page_number']}: {receipt_data}")

                if student_profile and isinstance(student_profile, StudentProfile):
                    receipt_data.setdefault('student_profile', student_profile)
                    receipt_data.setdefault('recipient_full_name', student_profile.name)

                receipt_data.setdefault('internal_receipt_number', f"REC-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
                receipt_data.setdefault('institution_name', "N/A")
                receipt_data.setdefault('service_name', "N/A")
                receipt_data.setdefault('service_amount', Decimal('0.00'))
                receipt_data.setdefault('total_amount', Decimal('0.00'))
                receipt_data.setdefault('receipt_date', date.today())
                receipt_data.setdefault('payment_due_date', date.today())
                receipt_data.setdefault('payment_purpose', "N/A")
                receipt_data.setdefault('service_category', "N/A")

                parsed_receipts.append(receipt_data)

            return parsed_receipts

        except Exception as e:
            logger.error(f"Error parsing PDF receipt: {str(e)}")
            raise ValueError(f"Failed to parse PDF receipt: {str(e)}")


def process_pdf_receipt(pdf_file, student_profile: StudentProfile) -> Receipt:
    """
    Process uploaded PDF file and create receipt, processes only first recipe.
    Used for legacy compatibility - expects StudentProfile instance
    """
    result = process_pdf_receipts_bulk(pdf_file, student_profile.id if student_profile else None)
    return result["created_receipts"][0] if result["created_receipts"] else None


def process_pdf_receipts_bulk(pdf_file, student_profile_id=None) -> Dict:
    """
    Process uploaded PDF file and create receipts for all logical receipts found
    Args:
        pdf_file: The PDF file to process
        student_profile_id: StudentProfile ID (UUID string) or None
    Returns:
        Dict with:
        - created_receipts: List[Receipt] - Successfully created receipts
        - failed_details: List[Dict] - Details about failed receipt creations
        - created_count: int - Number of successfully created receipts  
        - failed_count: int - Number of failed receipt creations
    """
    parser = PDFReceiptParser()

    actual_student_profile = None
    if student_profile_id is not None:
        try:
            actual_student_profile = StudentProfile.objects.get(id=student_profile_id)
            logger.info(f"Found StudentProfile {actual_student_profile.id}")
        except StudentProfile.DoesNotExist:
            logger.warning(f"No StudentProfile found for ID {student_profile_id}")
            actual_student_profile = None
        except Exception as e:
            logger.error(f"Error getting StudentProfile for ID {student_profile_id}: {str(e)}")
            actual_student_profile = None

    receipt_data_list = parser.parse_pdf_receipt(pdf_file, actual_student_profile)

    created_receipts = []
    failed_details = []

    for i, receipt_data in enumerate(receipt_data_list):
        source_page_number = receipt_data.get('source_page_number', 1)
        source_region_name = receipt_data.get('source_region_name', 'Unknown')
        
        try:
            pdf_file.seek(0)
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            page_index = source_page_number - 1
            if page_index < len(pdf_reader.pages):
                pdf_writer.add_page(pdf_reader.pages[page_index])

                page_pdf_buffer = io.BytesIO()
                pdf_writer.write(page_pdf_buffer)
                page_pdf_buffer.seek(0)

                pdf_content = ContentFile(
                    page_pdf_buffer.read(),
                    name=f"receipt_p{source_page_number}_{source_region_name.replace(' ', '_').lower()}.pdf"
                )
                receipt_data['pdf_file'] = pdf_content
                
            else:
                logger.warning(f"Page {source_page_number} not found in PDF, using entire PDF as fallback")
                pdf_file.seek(0)
                pdf_content = ContentFile(pdf_file.read())
                receipt_data['pdf_file'] = pdf_content
                
        except Exception as pdf_error:
            logger.warning(f"Error extracting page {source_page_number}: {str(pdf_error)}, using entire PDF as fallback")
            pdf_file.seek(0)
            pdf_content = ContentFile(pdf_file.read())
            receipt_data['pdf_file'] = pdf_content

        receipt_data.pop('source_page_number', None)
        receipt_data.pop('source_region_name', None)

        if actual_student_profile:
            receipt_data['student_profile'] = actual_student_profile
        elif 'student_profile' in receipt_data:
            receipt_data.pop('student_profile', None)

        try:
            receipt = create_receipt(**receipt_data)
            created_receipts.append(receipt)
            logger.info(
                f"Processed PDF receipt {receipt.id} for student {receipt_data.get('recipient_full_name', 'Unknown')} from page {source_page_number} ({source_region_name})")

        except Exception as e:
            error_detail = {
                "index": i,
                "page": source_page_number,
                "region": source_region_name,
                "recipient_name": receipt_data.get('recipient_full_name', 'Unknown'),
                "error": str(e)
            }
            failed_details.append(error_detail)
            logger.error(f"Failed to create receipt from page {source_page_number} ({source_region_name}): {str(e)}")
            continue

    return {
        "created_receipts": created_receipts,
        "failed_details": failed_details,
        "created_count": len(created_receipts),
        "failed_count": len(failed_details)
    }


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
            logger.info(f"Downloaded PDF for receipt {receipt.id}")
            return response
        except FileNotFoundError:
            logger.error(f"PDF file not found on storage for receipt {receipt.id}")
            raise Http404("PDF file not found on storage.")

    def download_consolidated_family_pdf(self, family, filters=None) -> HttpResponse:
        """
        Download consolidated PDF for all receipts in a family
            Args:
            family: Family instance
            filters: Optional filters for receipts
            Returns:
            HttpResponse with consolidated PDF content
            Raises:
            Http404: If no receipts or valid PDFs found
        """
        receipts = get_receipts_for_family(family=family, filters=filters or {})
        if not receipts.exists():
            raise Http404("No receipts found for this family.")
        merger = PdfWriter()
        processed_count = 0
        for receipt in receipts:
            if receipt.pdf_file:
                try:
                    pdf_file_buffer = io.BytesIO(receipt.pdf_file.read())
                    reader = PdfReader(pdf_file_buffer)
                    for page in reader.pages:
                        merger.add_page(page)
                    receipt.pdf_file.seek(0)
                    processed_count += 1
                    logger.debug(f"Added PDF for receipt {receipt.id} to consolidated file")
                except FileNotFoundError:
                    logger.warning(f"PDF for receipt {receipt.id} not found on storage. Skipping.")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing PDF for receipt {receipt.id}: {e}. Skipping.")
                    continue
        if not merger.pages:
            raise Http404("No valid PDF files found to merge for this family's receipts.")
        output_buffer = io.BytesIO()
        merger.write(output_buffer)
        output_buffer.seek(0)
        response = HttpResponse(output_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="family_{family.id}_receipts.pdf"'
        logger.info(f"Generated consolidated PDF for family {family.id} with {processed_count} receipts")
        return response


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
    service = ReceiptUpdateService()
    return service.update_receipt(receipt, **receipt_data)


def send_receipt_notification(receipt: Receipt, notification_type: str = 'initial',
                              custom_message: str = '') -> bool:
    """Sends receipt notifications"""
    service = ReceiptNotificationService()
    return service.send_receipt_notification(receipt, notification_type, custom_message)


def bulk_send_receipt_notifications(receipt_ids: List[str], notification_type: str = 'initial',
                                    custom_message: str = '') -> Dict[str, int]:
    """Bulk sending receipt notifications"""
    service = ReceiptNotificationService()
    return service.bulk_send_receipt_notifications(receipt_ids, notification_type, custom_message)
