from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.forms import Form, EmailField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
import pathlib
from slugify import slugify
from users.validators import name_validator
from users.services import UserService
from djangogramm.settings import MAX_AVATAR_FILE_SIZE


class RegistrationForm(Form):
    email = EmailField(max_length=50, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'

    def clean_email(self) -> str:
        email = self.cleaned_data['email']
        validate_email(email)

        if UserService.check_email(email):
            raise ValidationError("User under this email already exists")
        else:
            return email


class ActivationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].widget.attrs['class'] = 'form-control'
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'bio', 'avatar', 'password1', 'password2']
        required = (
            'first_name',
            'last_name',
            'password1',
            'password2'
        )

    def clean_avatar(self) -> InMemoryUploadedFile:
        avatar = self.cleaned_data['avatar']
        if avatar:
            if avatar.size > MAX_AVATAR_FILE_SIZE:
                raise ValidationError("Image file too large ( > 10mb )")
            file_name = pathlib.Path(avatar.name).stem
            extension = pathlib.Path(avatar.name).suffix
            avatar.name = slugify(file_name) + extension
            return avatar

    def clean_first_name(self) -> str:
        return name_validator(self.cleaned_data['first_name'])

    def clean_last_name(self) -> str:
        return name_validator(self.cleaned_data['last_name'])


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class PasswordResetRequestForm(Form):
    email = EmailField(max_length=50, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'

    def clean_email(self) -> str:
        email = self.cleaned_data['email']

        if UserService.check_email(email):
            return email
        else:
            raise ValidationError("Email is not registered")


class PasswordResetForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = "New password:"
        self.fields['password2'].label = "Confirm new password:"
