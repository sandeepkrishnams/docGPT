import os
import uuid
import hashlib
from django.core.files.uploadedfile import InMemoryUploadedFile
from tika import parser, language, detector


def create_renamed(document):
    """Compute a ulternative name for filename."""
    unique_id = uuid.uuid4().hex
    file_name, ext = os.path.splitext(document.name)
    new_filename = f"{unique_id}{ext}"
    content_type = document.content_type
    file_size = document.size
    charset = document.charset

    new_document = InMemoryUploadedFile(
        document.file, None, new_filename, content_type, file_size, None, charset
    )
    return new_document


def get_file_hash(file):
    """Compute the hash of a file's content."""
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()
