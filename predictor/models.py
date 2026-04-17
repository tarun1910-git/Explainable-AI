from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='predictions/')
    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.predicted_class} ({self.confidence:.1f}%)"

    class Meta:
        ordering = ['-created_at']


