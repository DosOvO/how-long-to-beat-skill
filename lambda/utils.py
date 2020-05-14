import logging
import os
import boto3
from botocore.exceptions import ClientError
from howlongtobeatpy import HowLongToBeat
from num2words import num2words

ERROR_TEXT = 'Kein Spiel mit dem Titel {} gefunden'

dict = {
  'eins' : '1',
  'zwei' : '2',
  'drei' : '3',
  'vier' : '4',
  'fünf' : '5',
  'sechs' : '6',
  'sieben' : '7',
  'acht' : '8',
  'neun' : '9',
  'zehn' : '10',
  'elf' : '11',
  'zwölf' : '12',
  'dreizehn' : '13',
  'vierzehn' : '14',
  'fünfzehn' : '15',
  'sechzehn' : '16',
  'siebzehn' : '17',
  'achtzehn' : '18',
  'neunzehn' : '19'
  }

def swapWordsWithDigits(text):
    result = text
    words = text.split()
    for word in words:
        if word in dict:
            result = result.replace(word, dict[word])
    return result

def search(gametitle):
    best_element = None
    results_list = HowLongToBeat().search(gametitle)
    if results_list is not None and len(results_list) > 0:
        best_element = max(results_list, key=lambda element: element.similarity)
    return best_element

def getPlaytimeTextMain(gametitle):
    outputText = ERROR_TEXT.format(gametitle)
    game = search(gametitle)
    if game is not None:
        playtime = game.gameplay_main.replace('½', '.5')
        outputText = num2words(playtime, lang='de').replace(' Komma fünf', 'einhalb')
    return outputText

def getPlaytimeTextMainAndExtra(gametitle):
    outputText = ERROR_TEXT.format(gametitle)
    game = search(gametitle)
    if game is not None:
        playtime = game.gameplay_main_extra.replace('\\u+00BD', '.5')
        logging.info(playtime)
        outputText = num2words(playtime, lang='de').replace(' Komma fünf', 'einhalb')
    return outputText

def getPlaytimeTextCompletionist(gametitle):
    outputText = ERROR_TEXT.format(gametitle)
    game = search(gametitle)
    if game is not None:
        playtime = game.gameplay_completionist .replace('\\u+00BD', '.5')
        outputText = num2words(playtime, lang='de').replace(' Komma fünf', 'einhalb')
    return outputText

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response