from PIL import Image
from tika import parser, language, detector
import pytesseract


def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))


def extract_text_from_document(document_path):
    parsed_data = parser.from_file(document_path)
    status = parsed_data['status']
    if 'content' in parsed_data and status == 200:
        return parsed_data['content'], parsed_data['metadata']
    else:
        return None, None


def main():
    document_path = '/home/bridge/projects/workshops/python-projects/movie-projects/download.jpeg'

    try:
        detected_mime_type = detector.from_file(document_path)
        detected_language = language.from_file(document_path)
        metadata = None
        text_content = None

        if detected_mime_type.lower().startswith("image"):
            text_content = extract_text_from_image(document_path)
        else:
            text_content, metadata = extract_text_from_document(document_path)
            if text_content is None:
                print("No content found in the document.")
                return

        print("Detected Language:", detected_language)
        print("Detected MIME Type:", detected_mime_type)
        print("Metadata:", metadata)
        print("Content:", text_content)

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
