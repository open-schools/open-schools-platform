from django.db import models
import uuid

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    circle = models.ForeignKey(
        'circles.Circle',
        on_delete=models.CASCADE,
        related_name='documents'
    )

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='documents'
    )

    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pdf = models.BinaryField()   # храним pdf в бинарном виде
    parent_signed = models.BooleanField(default=False)
    director_signed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.id}"
