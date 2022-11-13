from configparser import ConfigParser
from PIL import Image
import requests
import base64
import tweepy
from io import BytesIO
import time


def start_api():
    '''Start the tweepy api with the credentials.

    The function reads the credentials from the file "credentials.ini".

    Returns
    ----------
    api: tweepy.API
        The tweepy instance to connect and interact with Twitter.
    '''

    config = ConfigParser()
    config.read('credentials.ini')

    api_key = config['credentials']['api_key']
    api_key_secret = config['credentials']['api_key_secret']
    access_token = config['credentials']['access_token']
    access_token_secret = config['credentials']['access_token_secret']

    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_key_secret,
        access_token,
        access_token_secret)

    api = tweepy.API(auth)

    return api


def get_since_id(api):
    '''Get the last interaction.

    This function reads the user timeline and get the id
    for the last tweet sent.

    Parameters
    ----------
    api: tweepy.API
        The tweepy instance to connect and interact with Twitter.
    
    Returns
    ----------
    since_id: int
        The status_id for the last interaction.
    '''

    timeline = api.home_timeline(count=1)

    since_id = timeline[0].in_reply_to_status_id

    return since_id


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

    url = 'http://localhost:3674/predict'
    response = requests.post(url, files=file)

    # decode image
    data = base64.b64decode(response.json()['data'])
    size = response.json()['size']
    boxes = response.json()['boxes']
    image = Image.frombytes('RGB', size, data)

    # get boxes
    boxes = response.json()['boxes']

    return image, boxes


def get_label_text(label, count):
    '''Create the text for one label.

    Calculates the number of repetitions and makes a
    text for describing this label. Adds "s" or "es"
    when there is more than one.

    Parameters
    ----------
    label: str
        The label.
    count: int
        The number of repetitions
    
    Returns
    ----------
    label_text: str
        The text for the label.
    '''

    # correct plural names
    plural = count > 1
    ends_with_s = label.endswith('s')
    if label in ['skis', 'scissors']:
        label = label
    elif plural and ends_with_s:
        label += 'es'
    elif plural:
        label += 's'

    label_text = '\n{} {}'.format(count, label)

    return label_text


def generate_text(boxes, screen_name):
    '''Generate the text for the tweet.

    The text will contain a mention to the user and a list
    enumerating all objects detected. If there are no objects
    then a special text is returned.

    Parameters
    ----------
    boxes: list
        The list with the labels, probability and bounding boxes.
    screen_name: str
        The twitter username for the response.
    
    Returns
    ----------
    text: str
        The complete text response.
    '''

    if len(boxes) == 0:
        return 'Sorry @{}, I have found nothing. Try with other image.'.format(screen_name)

    labels = [box[0] for box in boxes]
    labels_set = set(labels)

    text = ' This image contains:'
    for label in labels_set:

        count = labels.count(label)
        label_text = get_label_text(label, count)

        text += label_text

    # concatenate mention and text
    text = '@' + screen_name + text

    return text


def send_tweet(api, status_id, image, text):
    '''Sends one tweet with the answer

    Parameters
    ----------
    api: tweepy.API
        The tweepy instance to connect and interact with Twitter.
    status_id: int
        The tweet id we are responding.
    image: PIL.Image
        The annotated image.
    text: str
        The text in the tweet.
    '''
    # Encode the image
    file = BytesIO()
    image.save(file, 'jpeg')
    file.seek(0)

    api.update_status_with_media(
        text,
        'dummy_name.jpeg',
        in_reply_to_status_id=status_id,
        file=file)


def proc_mention(api, mention):
    '''Process one mention.

    Parameters
    ----------
    api: tweepy.API
        The tweepy instance to connect and interact with Twitter.
    mention: tweepy.models.status
        The tweepy status for the mention.
    '''

    screen_name = mention.author.screen_name
    media_url = mention.entities['media'][0]['media_url']
    status_id = mention.id

    image, boxes = get_prediction(media_url)

    text = generate_text(boxes, screen_name)

    send_tweet(api, status_id, image, text)


def proc_all_mentions(api):
    '''Process all mentions.

    Reads the last interaction and get all mentions
    since then.

    Parameters
    ----------
    api: tweepy.API
        The tweepy instance to connect and interact with Twitter.
    '''

    # get last interaction
    since_id = get_since_id(api)

    # get only new mentions
    mentions = api.mentions_timeline(since_id=since_id)

    # reverse to respond in order
    mentions = mentions[::-1]

    for mention in mentions:

        proc_mention(api, mention)


if __name__ == '__main__':
    
    api = start_api()

    while True:

        proc_all_mentions(api)

        time.sleep(30)
