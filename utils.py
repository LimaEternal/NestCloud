from werkzeug.utils import secure_filename
import math
import os
from datetime import datetime
from nestcloud import app
import uuid
from typing import Optional, Tuple
from PIL import Image, ImageOps


def get_human_readable_size(size_bytes: int) -> str:
    """Конвертация байтов в человекочитаемый формат"""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def is_image_file(filename: str) -> bool:
    """Проверка, является ли файл изображением по расширению."""
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
    _, ext = os.path.splitext(filename.lower())
    return ext in image_extensions


def generate_image_preview(
    source_path: str,
    output_dir: Optional[str] = None,
    max_size: Tuple[int, int] = (128, 128),
    quality: int = 85,
) -> Optional[str]:
    """
    Создаёт уменьшенную копию изображения для превью.

    :param source_path: полный путь к исходному файлу
    :param output_dir: каталог для сохранения превью (по умолчанию /previews рядом с файлом)
    :param max_size: максимальные размеры превью (ширина, высота)
    :param quality: качество JPEG/WebP при сохранении
    :return: путь к превью или None, если генерация невозможна
    """

    if Image is None or ImageOps is None:
        raise RuntimeError(
            "Pillow не установлен. Установите пакет 'Pillow' в виртуальное окружение."
        )

    if not os.path.exists(source_path):
        print(f"   ⚠️ Исходный файл не найден: {source_path}")
        return None

    if output_dir is None:
        parent_dir = os.path.dirname(source_path)
        output_dir = os.path.join(parent_dir, "previews")

    os.makedirs(output_dir, exist_ok=True)
    print(f"   → Папка для превью: {output_dir}")

    base_name = os.path.basename(source_path)
    preview_name = f"preview_{base_name}.jpg"
    preview_path = os.path.join(output_dir, preview_name)
    print(f"   → Путь к превью: {preview_path}")

    try:
        with Image.open(source_path) as img:
            print(f"   → Изображение открыто: {img.size}, формат: {img.format}")
            img = ImageOps.exif_transpose(img)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"   → Размер после уменьшения: {img.size}")
            img.convert("RGB").save(preview_path, format="JPEG", quality=quality)
            print(f"   → Превью сохранено: {preview_path}")
    except Exception as e:
        print(f"   ❌ Ошибка при обработке изображения: {e}")
        import traceback

        traceback.print_exc()
        return None

    return preview_path


def get_file_icon(filename: str) -> str:
    """
    Возвращает путь к иконке файла в зависимости от его расширения.

    :param filename: имя файла
    :return: относительный путь к иконке в папке static/file_icons
    """
    # Получаем расширение файла в нижнем регистре
    ext = os.path.splitext(filename)[1].lower()

    # Сопоставление расширений с иконками
    icon_map = {
        # Архивы
        ".zip": "archive.png",
        ".rar": "archive.png",
        ".7z": "archive.png",
        ".tar": "archive.png",
        ".gz": "archive.png",
        ".bz2": "archive.png",
        # Аудио
        ".mp3": "audio.png",
        ".wav": "audio.png",
        ".ogg": "audio.png",
        ".flac": "audio.png",
        ".aac": "audio.png",
        ".m4a": "audio.png",
        # Видео
        ".mp4": "video.png",
        ".avi": "video.png",
        ".mov": "video.png",
        ".mkv": "video.png",
        ".wmv": "video.png",
        ".flv": "video.png",
        # Документы
        ".pdf": "document.png",
        ".doc": "document.png",
        ".docx": "document.png",
        ".txt": "document.png",
        ".rtf": "document.png",
        ".xls": "document.png",
        ".xlsx": "document.png",
        ".ppt": "document.png",
        ".pptx": "document.png",
    }

    # Возвращаем соответствующую иконку или иконку "другие файлы" по умолчанию
    icon_filename = icon_map.get(ext, "other.png")
    return f"file_icons/{icon_filename}"


def save_file(file, user_id: int) -> dict:
    """Сохраняет файл в папку пользователя и возвращает данные для БД/превью"""
    print(f"   → Сохранение файла для пользователя {user_id}")

    # 1. Путь к папке пользователя
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], f"{user_id}")
    print(f"   → Папка пользователя: {user_folder}")

    # 2. Проверяем существование папки
    if not os.path.exists(user_folder):
        print(f"   ⚠️ Папка не существует! Пытаемся создать...")
        os.makedirs(user_folder, exist_ok=True)

    # 3. Генерируем уникальное имя
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(user_folder, unique_filename)
    print(f"   → Итоговый путь: {filepath}")

    # 4. Сохраняем файл на диск
    try:
        file.save(filepath)
        print(f"   ✅ Файл сохранён на диск")
    except Exception as e:
        print(f"   ❌ Ошибка сохранения на диск: {str(e)}")
        raise

    # 5. Готовим данные для БД
    file_size = os.path.getsize(filepath)
    human_size = get_human_readable_size(file_size)
    upload_time = datetime.now()

    # 6. Генерируем превью для изображений или используем иконку для других файлов
    preview_relpath = None
    original_filename = file.filename  # Оригинальное имя до secure_filename
    print(
        f"   → Проверка на изображение: оригинальное имя = {original_filename}, обработанное = {filename}"
    )

    if is_image_file(original_filename):
        print(f"   → Файл определён как изображение, генерирую превью...")
        try:
            preview_absolute = generate_image_preview(
                filepath,
                output_dir=os.path.join(user_folder, "previews"),
            )
            if preview_absolute:
                preview_relpath = os.path.relpath(preview_absolute, user_folder)
                print(f"   ✅ Превью создано: {preview_relpath}")
                print(f"   → Абсолютный путь: {preview_absolute}")
            else:
                print(f"   ⚠️ generate_image_preview вернул None")
        except Exception as e:
            print(f"   ❌ Не удалось создать превью: {e}")
            import traceback

            traceback.print_exc()
    else:
        # Для не-изображений используем иконку
        preview_relpath = get_file_icon(original_filename)
        print(
            f"   → Файл не является изображением, используется иконка: {preview_relpath}"
        )

    print(f"   → Размер: {file_size} байт → {human_size}")
    return {
        "stored_filename": unique_filename,
        "original_filename": original_filename,
        "human_size": human_size,
        "upload_time": upload_time,
        "preview_relpath": preview_relpath,
        "absolute_path": filepath,
    }
