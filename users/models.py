from django.db.models import EmailField, CharField, TextField, ImageField, BooleanField, DateTimeField
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None):
        if not email:
            raise ValueError("Admin requires an Email")
        user = self.model(
            email=self.normalize_email(email),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            activation_link='superuser',
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    username = None
    email = EmailField(max_length=50, unique=True)
    activation_link = CharField(max_length=36, unique=True)
    bio = TextField(max_length=250, blank=True)
    avatar = ImageField(upload_to="avatars/", blank=True)
    is_active = BooleanField(default=False)
    password_reset_link = CharField(max_length=36, null=True, unique=True)
    date_password_reset_link = DateTimeField(null=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return " ".join([self.first_name, self.last_name])
