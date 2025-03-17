from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Create your models here.
class Role(models.TextChoices):
    ADMIN = "admin" , "Admin"
    HR = "HR" , "hr"
    CANDIDATE = "CANDIDATE" , "Candidate"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4 , editable= False)
    email = models.EmailField(unique = True)
    role = models.CharField(max_length=20, choices= Role.choices , default= Role.CANDIDATE)
    company = models.CharField(max_length=255, null=True , blank= True)



    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []



    def __str__(self):
        
        return f"{self.email} - {self.role}"
