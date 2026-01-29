from urllib.parse import urlparse

from rest_framework.serializers import ValidationError


def validate_youtube_only(value: str) -> str:
    """
    Разрешаем ссылки только на youtube.com (включая *.youtube.com).
    """
    if not value:
        return value

    parsed = urlparse(value)

    if parsed.scheme not in ("http", "https"):
        raise ValidationError("Ссылка должна начинаться с http:// или https://")

    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]

    if not (host == "youtube.com" or host.endswith(".youtube.com")):
        raise ValidationError("Разрешены только ссылки на youtube.com")

    return value
