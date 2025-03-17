from django.contrib.auth.models import AbstractUser , BaseUserManager
from django.db import models
import uuid

# Create your models here.

class UserManager(BaseUserManager):
     def create_user(self, email, password = None , **extra_fields ):
        if not email:
            raise ValueError("Email not given")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


     def create_superuser(self,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True )
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Role(models.TextChoices):
    ADMIN = "admin" , "Admin"
    HR =   "hr" , "HR"
    CANDIDATE = "CANDIDATE" , "Candidate"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4 , editable= False)
    email = models.EmailField(unique = True)
    role = models.CharField(max_length=20, choices= Role.choices , default= Role.CANDIDATE)
    company = models.CharField(max_length=255, null=True , blank= True)



    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    objects = UserManager()



    def __str__(self):
        
        return f"{self.email} - {self.role}"
