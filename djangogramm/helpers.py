import os
import sys
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def getenv_bool(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f'Variable `{name}` not set!')
    elif value not in ['True', 'False']:
        raise ValueError(f"Invalid value `{value}` for variable `{name}`. Only 'True' or 'False' values are allowed")
    else:
        return value == 'True'


def get_inmemory_image(path_to_folder: str, file_name: str) -> InMemoryUploadedFile:
    path_to_file = os.path.join(path_to_folder, file_name)
    image_io = BytesIO()
    image_pil = Image.open(path_to_file)
    image_pil.save(image_io, format="JPEG")
    return InMemoryUploadedFile(image_io, 'ImageField', file_name, 'JPEG', sys.getsizeof(image_io),
                                None)
