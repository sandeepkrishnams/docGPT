import os
import uuid
import hashlib
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from tika import parser, detector
import pytesseract
import pysolr
from django.conf import settings


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


def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))


def extract_text_from_document(document_path):
    parsed_data = parser.from_file(document_path)
    status = parsed_data['status']  # type: ignore
    if 'content' in parsed_data and status == 200:
        return parsed_data['content'], parsed_data['metadata']  # type: ignore
    else:
        return None, None


def get_content(document_path):
    # TODO: Replace the absalute path with relative path. Now we are passing Absalute path to the detector function
    dirname = os.path.dirname(__file__)
    newDirNameArr = dirname.split('/')
    newDirNameArr.pop()
    newDir = '/'.join(newDirNameArr)
    filename = newDir + document_path
    detected_mime_type = detector.from_file(filename)
    print(detected_mime_type)
    text_content = None

    if detected_mime_type.lower().startswith("image"):
        text_content = extract_text_from_image(filename)
    else:
        text_content, metadata = extract_text_from_document(filename)
        if text_content is None:
            return
    return text_content


def add_content_to_solr(data):
    solr_url = settings.SOLR_HOST_URL
    solr = pysolr.Solr(solr_url, always_commit=True)
    solr.add([data])
