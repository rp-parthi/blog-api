from django.db import models

LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ta", "Tamil"),
    ]

class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created_at"]