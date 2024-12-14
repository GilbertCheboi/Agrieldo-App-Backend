from django.db import models

class EducationalMaterial(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    file = models.FileField(upload_to='educational_materials/', null=True, blank=True)

    def __str__(self):
        return self.title
