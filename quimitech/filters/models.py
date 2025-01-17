from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import os

# Create your models here.
class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}: {self.file.name}"
    
class Filter(models.Model):
    unique_code = models.CharField(max_length=100, unique=True)
    mass_initial_images = models.ManyToManyField(Image, related_name="mass_initial_images")
    mass_final_images = models.ManyToManyField(Image, related_name="mass_final_images")
    sync_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Filter {self.unique_code}"
    
    def get_absolute_url(self):
        return reverse("filter_detail", args=[str(self.id)])
    
    def delete(self, *args, **kwargs):
        for image in self.mass_initial_images.all():
            if os.path.isfile(image.file.path):
                os.remove(image.file.path)
            image.delete()
                
        for image in self.mass_final_images.all():
            if os.path.isfile(image.file.path):
                os.remove(image.file.path)
            image.delete()
            
        super().delete(*args, **kwargs)
    
