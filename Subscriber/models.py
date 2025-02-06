from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()  # Plain text content
    html_content = models.TextField()  # HTML content for rich emails
    send_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)  # Mark if the newsletter was sent

    def __str__(self):
        return self.subject
