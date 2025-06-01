import base64
import uuid
from io import BytesIO
from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from rest_framework import serializers


class CustomBase64ImageField(serializers.ImageField):
    ALLOWED_FORMATS = {'jpeg', 'jpg', 'png', 'gif', 'bmp'}

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                image_file = self._decode_base64_image(data)
            except ValueError as e:
                raise serializers.ValidationError(str(e))
            return super().to_internal_value(image_file)

        return super().to_internal_value(data)

    def _decode_base64_image(self, data: str) -> InMemoryUploadedFile:
        try:
            header, base64_data = data.split(";base64,")
            image_format = header.split("/")[-1].lower()
        except ValueError:
            raise ValueError("Неверный формат строки base64 изображения")

        try:
            decoded_image = base64.b64decode(base64_data)
        except (TypeError, ValueError):
            raise ValueError("Ошибка декодирования base64")

        if image_format not in self.ALLOWED_FORMATS:
            raise ValueError(f"Недопустимый формат изображения. Разрешены: {', '.join(self.ALLOWED_FORMATS)}")

        try:
            image = Image.open(BytesIO(decoded_image))
            image.verify()
            image = Image.open(BytesIO(decoded_image))
        except Exception:
            raise ValueError("Поврежденный файл изображения")

        file_name = f"{uuid.uuid4()}.{image_format}"
        
        image_io = BytesIO()
        image.save(image_io, format=image_format.upper())
        image_io.seek(0)

        return InMemoryUploadedFile(
            file=image_io,
            field_name=None,
            name=file_name,
            content_type=f'image/{image_format}',
            size=len(decoded_image),
            charset=None
        )

    def _get_image_format(self, image_data: bytes) -> Optional[str]:
        try:
            image = Image.open(BytesIO(image_data))
            return image.format.lower()
        except Exception:
            return None
