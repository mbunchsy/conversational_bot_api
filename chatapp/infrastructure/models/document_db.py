from django.db import models
from pgvector.django import VectorField

class DocumentDB(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'documents'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"