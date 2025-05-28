import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from simple_history.models import HistoricalRecords

from open_schools_platform.common.models import BaseModel, BaseManager
from open_schools_platform.student_management.students.models import StudentProfile


class ReceiptManager(BaseManager):
    def create_receipt(self, student_profile: StudentProfile, **kwargs):
        receipt = self.model(
            student_profile=student_profile,
            **kwargs
        )
        receipt.full_clean()
        receipt.save(using=self.db)
        return receipt


class Receipt(BaseModel):
    """
    Main receipt model based on the field analysis.
    Contains all essential receipt information for the MVP.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="receipts"
    )

    internal_receipt_number = models.CharField(
        max_length=100,
        help_text="Уникальный идентификатор платёжной записи внутри учётной системы"
    )

    payer_full_name = models.CharField(
        max_length=300,
        help_text="ФИО физического лица, производящего оплату"
    )
    recipient_full_name = models.CharField(
        max_length=300,
        help_text="ФИО обучающегося / лица, за которого осуществляется платёж"
    )

    institution_name = models.CharField(
        max_length=500,
        help_text="Учебное учреждение, оказывающее услугу"
    )

    service_name = models.CharField(
        max_length=300,
        help_text="Наименование конкретной оплачиваемой услуги"
    )
    service_category = models.CharField(
        max_length=200,
        blank=True,
        help_text="Группировка или категория услуги"
    )

    debt_at_month_start = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Остаток долга на первое число текущего месяца"
    )
    charged_this_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Сумма, начисленная за текущий месяц"
    )
    recalculation_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Изменение начислений"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Сколько уже заплатили за услугу"
    )
    debt_at_next_month_start = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Остаток долга на начало следующего месяца"
    )
    prepayment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Деньги, внесенные вперед"
    )
    service_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Фактическая стоимость конкретной услуги за расчетный период"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Конечный итог суммы к оплате"
    )

    receipt_date = models.DateField(
        help_text="Дата создания квитанции"
    )
    payment_due_date = models.DateField(
        help_text="Крайний срок оплаты"
    )

    payment_purpose = models.TextField(
        help_text="Показывает основание для оплаты"
    )    
    qr_code_data = models.TextField(
        blank=True,
        help_text="QR-код данные для быстрой оплаты через банковские приложения"
    )

    pdf_file = models.FileField(
        upload_to='receipts/pdfs/',
        null=True,
        blank=True,
        help_text="PDF файл квитанции"
    )

    history = HistoricalRecords()
    objects = ReceiptManager()

    class Meta:
        ordering = ['-created_at']        
        indexes = [
            models.Index(fields=['student_profile', '-created_at']),
            models.Index(fields=['payment_due_date']),
        ]

    def __str__(self):
        return f"Receipt {self.internal_receipt_number} for {self.recipient_full_name}"

    @property
    def is_overdue(self):
        """Check if receipt payment is overdue"""
        from django.utils import timezone
        return timezone.now().date() > self.payment_due_date and self.total_amount > 0


class ReceiptNotificationManager(BaseManager):
    def create_notification(self, receipt: Receipt, notification_type: str):
        notification = self.model(
            receipt=receipt,
            notification_type=notification_type
        )
        notification.full_clean()
        notification.save(using=self.db)
        return notification


class ReceiptNotification(BaseModel):
    """
    Track notifications sent for receipts
    """
    NOTIFICATION_TYPES = [
        ('initial', 'Initial Receipt Notification'),
        ('reminder', 'Payment Reminder'),
        ('overdue', 'Overdue Payment Notice'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)

    objects = ReceiptNotificationManager()
    history = HistoricalRecords()

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.notification_type} notification for {self.receipt}"


class ReceiptService(BaseModel):
    """
    Individual service within a receipt - for detailed breakdown
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name="services"
    )

    institution = models.CharField(
        max_length=200,
        help_text="Учебное учреждение"
    )
    service_name = models.CharField(
        max_length=300,
        help_text="Название кружка"
    )

    debt_at_month_start = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Долг на начало месяца для этого кружка"
    )
    charged_this_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Сумма, взимаемая в этом месяце за кружок"
    )
    recalculation_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Перерасчет в этом месяце за кружок"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Сколько оплачено за кружок"
    )
    debt_at_next_month_start = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Долг на начало следующего месяца за кружок"
    )
    prepayment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Предоплата за кружок"
    )
    service_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Общая сумма долга за кружок"
    )

    class Meta:
        ordering = ['service_name']

    def __str__(self):
        return f"{self.service_name} - {self.service_amount}"
