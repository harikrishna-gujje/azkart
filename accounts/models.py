from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self, first_name=None, last_name=None, username=None, phone_number=None, email=None, password=None):
        if not username:
            raise ValueError('Account must have username')

        if not email:
            raise ValueError('Account must have email')

        user = self.model(      #filling the required fields
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email)
        )
        user.phone_number = phone_number
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name=None, last_name=None, username=None, phone_number=None, email=None, password=None):
        user = self.create_user(first_name, last_name, username, phone_number, email, password)

        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True

        user.save(using=self._db)
        return user



class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255, null=True) #this field is not asking due to not a required field, so added nullable True(can be empty)

    #required
    date_joined = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email' #this and password are required by default
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = AccountManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser and self.is_active

    def has_module_perms(self, package_name):
        return self.is_superuser and self.is_active
