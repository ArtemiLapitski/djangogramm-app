from io import BytesIO
import os
import boto3
from PIL import Image
import requests

IMAGE_THUMBNAIL_SIZE = (600, 800)
AVATAR_THUMBNAIL_SIZE = (100, 100)
IMAGE_BACKGROUND_COLOR = (0, 0, 0)
HOSTNAME = 'your_host_here'
AWS_WEBHOOK_TOKEN = 'your_token_here'


def send_webhook(original: str, thumbnail: str):
    url = HOSTNAME + '/webhook/'
    data = {
        'token': AWS_WEBHOOK_TOKEN,
        'make_thumbnail': {
            'original': original,
            'thumbnail': thumbnail
        }
    }
    return requests.post(url, json=data)


def image_handler(img: Image) -> Image:
    width_actual, height_actual = img.size
    width_target, height_target = IMAGE_THUMBNAIL_SIZE

    if width_actual > width_target or height_actual > height_target:
        img.thumbnail(IMAGE_THUMBNAIL_SIZE)
    width_actual, height_actual = img.size
    result = Image.new(img.mode, IMAGE_THUMBNAIL_SIZE, IMAGE_BACKGROUND_COLOR)
    if width_actual == width_target and height_actual < height_target:
        result.paste(img, (0, (height_target - height_actual) // 2))
        return result
    elif width_actual < width_target and height_actual == height_target:
        result.paste(img, ((width_target - width_actual) // 2, 0))
        return result
    elif width_actual < width_target and height_actual < height_target:
        result.paste(img, ((width_target - width_actual) // 2, (height_target - height_actual) // 2))
        return result
    else:
        return img


def avatar_handler(img: Image) -> Image:
    width_actual, height_actual = img.size
    width_target, height_target = AVATAR_THUMBNAIL_SIZE

    if width_actual > width_target or height_actual > height_target:
        img.thumbnail(AVATAR_THUMBNAIL_SIZE)
        return img
    else:
        return img


def image_to_bytes(image: Image) -> BytesIO:
    output_buffer = BytesIO()
    if image.mode == "RGBA":
        image.save(output_buffer, format='png')
    else:
        image.save(output_buffer, format='JPEG')
    output_buffer.seek(0)
    return output_buffer


def get_avatar_thumbnail_key(source_key: str) -> str:
    file_name = os.path.basename(source_key)
    return 'thumbnails/avatars/' + file_name


def get_image_thumbnail_key(source_key: str) -> str:
    file_name = os.path.basename(source_key)
    return 'thumbnails/images/' + file_name


s3Client = boto3.client('s3')


def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']

    image_obj = s3Client.get_object(Bucket=source_bucket, Key=source_key)
    original_image = Image.open(BytesIO(image_obj['Body'].read()))

    if "avatars/" in source_key:
        resized_image = avatar_handler(original_image)
        new_key = get_avatar_thumbnail_key(source_key)
    else:
        resized_image = image_handler(original_image)
        new_key = get_image_thumbnail_key(source_key)

    output_buffer = image_to_bytes(resized_image)
    s3Client.put_object(Body=output_buffer, Bucket=source_bucket, Key=new_key)
    send_webhook(original=source_key, thumbnail=new_key)
