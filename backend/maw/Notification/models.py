from django.db import models

class Notification(models.Model):
    TYPE_CHOICES = (
        ('Error', 'Error'),
        ('Warning', 'Warning'),
        ('Success', 'Success'),
        ('Restriction', 'Restriction'),
    )

    type = models.CharField(max_length=12, choices=TYPE_CHOICES)
    info = models.JSONField()
    well_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def mark_as_read(self):
        self.well_read = True
        self.save()
