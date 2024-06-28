from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from djangogramm.settings import MAX_AVATAR_FILE_SIZE
from .validators import name_validator


class RegistrationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2']


class ActivationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'bio', 'avatar']
        required = (
            'first_name',
            'last_name'
        )

    def clean_avatar(self) -> InMemoryUploadedFile:
        avatar = self.cleaned_data['avatar']
        if avatar and avatar.size > MAX_AVATAR_FILE_SIZE:
            raise ValidationError("Image file too large ( > 10mb )")
        return avatar

    def clean_first_name(self) -> str:
        return name_validator(self.cleaned_data['first_name'])

    def clean_last_name(self) -> str:
        return name_validator(self.cleaned_data['last_name'])
