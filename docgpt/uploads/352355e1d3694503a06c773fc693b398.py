from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import doctr

# conf for text detection

# predictor = detection_predictor('linknet_resnet18_rotation', pretrained=True,
#                                 assume_straight_pages=False, preserve_aspect_ratio=True)

# use TenserRT for increase performance speed
"""
Architectures

db_resnet50 + crnn_vgg16_bn =  (value='6064', confidence=1.0) (value='364929143031201', confidence=0.85),
db_resnet50 + crnn_mobilenet_v3_large =  (value='6064', confidence=1.0) (value='364929143031201', confidence=0.73),
db_resnet50 + master = (value='6064', confidence=1.0) (value='364929143031201', confidence=0.85)

db_mobilenet_v3_large + crnn_vgg16_bn =
            Word(value='6064', confidence=1.0),
            Word(value='3649', confidence=1.0),
            Word(value='2914', confidence=1.0),
            Word(value='3031', confidence=1.0),
            Word(value='201', confidence=1.0)
 db_mobilenet_v3_large + crnn_mobilenet_v3_small / db_mobilenet_v3_large = [
            Word(value='6064', confidence=1.0),
            Word(value='3649', confidence=1.0),
            Word(value='2914', confidence=1.0),
            Word(value='3031', confidence=1.0),
            Word(value='201', confidence=0.99),
            Word(value='PIN-code:', confidence=0.96),
          ]


best result so far = db_mobilenet_v3_large + crnn_vgg16_bn
"""

model = ocr_predictor('db_mobilenet_v3_large', 'crnn_vgg16_bn', pretrained=True,
                      assume_straight_pages=True, preserve_aspect_ratio=True)

image = DocumentFile.from_images("rotate.png")

output = model(image)
print("#######################################")
print(doctr.__version__)
print(output)
