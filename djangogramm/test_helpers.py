from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image
from feed.services import PostService, ImageService
from djangogramm.settings import MAX_AVATAR_FILE_SIZE, MAX_IMAGE_FILE_SIZE

first_user_credentials = {
            'username': 'jsmith@mail.com',
            'password': '8uhb5thm'
}

second_user_credentials = {
            'username': 'mthatcher@mail.com',
            'password': '8uhb5thm'
}

third_user_credentials = {
            'username': 'mcurie@mail.com',
            'password': '8uhb5thm'
}

registration_credentials = {
            'email': 'some_email@mail.com',
            'password1': '8uhb5thm',
            'password2': '8uhb5thm'
        }


allowed_avatar_file_size: int = int(MAX_AVATAR_FILE_SIZE / 10)
not_allowed_avatar_file_size: int = MAX_AVATAR_FILE_SIZE + 1

allowed_image_file_size: int = int(MAX_IMAGE_FILE_SIZE / 10)
not_allowed_image_file_size: int = MAX_IMAGE_FILE_SIZE + 1


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


# remove name
def create_test_user(email: str, password: str, avatar_name: str = "avatar.jpg"):
    avatar = create_mock_image(target_file_size=int(MAX_AVATAR_FILE_SIZE / 10), image_size=(100, 100), name=avatar_name)
    user = get_user_model().objects.create(email=email, is_active=True,
                                           activation_link='dce9d1e9-91ef-4557-b880-9adc0d6c74ab', first_name='Test',
                                           last_name='User', bio="some bio", avatar=avatar)
    user.set_password(password)
    user.save()
    return user


def create_test_post(user_id, body, target_file_size, image_name: str = 'foo.jpg'):
    image_allowed = create_mock_image(target_file_size=target_file_size, image_size=(300, 300), name=image_name)
    post_data = {
        'user_id': user_id,
        'body': body,
        'tags': ['#tag']
    }
    post = PostService.create_post(**post_data)
    ImageService.add(image=image_allowed, post=post)

    return post
