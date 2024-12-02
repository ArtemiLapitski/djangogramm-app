from django.forms import Form, ModelForm, CharField, formset_factory, Textarea, TextInput
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
import pathlib
from slugify import slugify
from feed.models import Image
from djangogramm.settings import MAX_IMAGE_FILE_SIZE


class PostForm(Form):
    body = CharField(max_length=250, widget=Textarea(attrs={'class': 'form-control'}), required=False)
    tags = CharField(max_length=25, widget=TextInput(attrs={'class': 'form-control'}), required=False)

    def clean_tags(self) -> list:
        tags = self.cleaned_data.get('tags')

        if tags:
            tags_stripped = tags.strip()
            if '  ' in tags_stripped:
                raise ValidationError('Tags should be separated by single space character')

            tags_list = tags_stripped.split(' ')

            if len(set(tags_list)) != len(tags_list):
                raise ValidationError('Tags cannot repeat for a single post')

            for tag in tags_list:
                if tag[0] != '#':
                    raise ValidationError('Hash mark should be the first symbol of each tag')
                elif not tag.split('#')[1].isalpha():
                    raise ValidationError('Only letters are allowed after a hash mark')

            return tags_list


class ImageForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Image
        fields = ['image']

    def clean_image(self) -> InMemoryUploadedFile:
        image = self.cleaned_data['image']
        if image.size > MAX_IMAGE_FILE_SIZE:
            raise ValidationError("Image file too large ( > 10mb )")
        file_name = pathlib.Path(image.name).stem
        extension = pathlib.Path(image.name).suffix
        image.name = slugify(file_name) + extension
        return image


ImageFormSet = formset_factory(ImageForm, extra=5, max_num=5, min_num=1)
