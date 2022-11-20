from io import BytesIO
import base64

import requests
from PIL import Image

from src import config


def get_prediction(media_url):
    '''Get the prediction for the image.

    Reads the photo sent and uses the yolo-microservice
    for getting the annotated photo and the labels.

    Parameters
    ----------
    media_url: str
        The url for the image.

    Returns
    ----------
    image: PIL.Image
        The annotated image.
    boxes: list
        The list with the labels, probability and bounding boxes.
    '''

    file = {'image': BytesIO(requests.get(media_url).content)}

    url_pred = config.CONFIG['url_pred']
    response = requests.get(url_pred, files=file)

    # decode image
    data = base64.b64decode(response.json()['data'])
    size = response.json()['size']
    boxes = response.json()['boxes']
    image = Image.frombytes('RGB', size, data)

    # get boxes
    boxes = response.json()['boxes']

    return image, boxes