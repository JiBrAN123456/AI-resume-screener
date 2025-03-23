from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Create your models here.


class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4 , editable= False)
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="resumes")
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True , null= True)
    name = models.CharField(max_length=255, blank=True , null =True)
    email = models.EmailField(blank=True , null = True)
    phone = models.CharField(max_length=200 ,blank=True , null = True)
    skills = models.TextField(null= True , blank= True)
    education = models.TextField(null= True , blank= True)
    experience = models.TextField(null= True , blank= True)
    score = models.FloatField(default=0.0)
    uploaded_at =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.name or "Resume"}"