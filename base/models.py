from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone
from django.core.validators import FileExtensionValidator

# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates, saves, and returns a User with the given email and password.
        """
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates, saves, and returns a superuser with the given email and password.
        """
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save(using=self._db)
        return user

AUTH_PROVIDERS = {'email': 'email', 'google': 'google'}

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='images/profile_images/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(Group, blank=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS['email'])


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"



GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Others', 'Others'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, null=True, blank=True)  
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True)
    profile_picture = models.ImageField(upload_to='images/profile_images/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    country = models.CharField(max_length=50, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"User Profile for {self.user.email}"

    class Meta:
        ordering = ['-date_created']


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - passcode"
    


