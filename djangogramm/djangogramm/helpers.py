from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image


def image_handler(path: str, size: tuple) -> None:
    image = Image.open(path)
    if image.width > size[0] or image.height > size[1]:
        image.thumbnail(size)
        image.save(path)


def create_mock_image(target_file_size: int, image_size: tuple, name: str = 'foo.jpg') -> InMemoryUploadedFile:
    mock_image = BytesIO()
    color = (255, 0, 0, 0)
    image = Image.new("RGB", image_size, color)
    image.save(mock_image, format='JPEG')
    mock_image.seek(0)

    real_file_size = len(mock_image.read())

    if real_file_size < target_file_size:
        mock_image.write(b'\0' * (target_file_size - real_file_size))
    mock_image.seek(0)

    in_memory_image = InMemoryUploadedFile(mock_image, None, name, 'jpeg', target_file_size,None)

    return in_memory_image


def create_test_user(email: str, password: str):
    user = get_user_model().objects.create(email=email, is_active=True,
                                           activation_link='dce9d1e9-91ef-4557-b880-9adc0d6c74ab', first_name='Test',
                                           last_name='User')
    user.set_password(password)
    user.save()
    return user
