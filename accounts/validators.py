import os
from django.core.exceptions import ValidationError


def images_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Only png, jpg, jpeg files are allowed.')
