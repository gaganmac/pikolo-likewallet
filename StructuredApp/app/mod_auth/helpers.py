import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from oauth2client.client import GoogleCredentials
credentials = GoogleCredentials.get_application_default()


def analyze(content):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language.LanguageServiceClient()

    document = types.Document(
        content=content,
        type=enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document)

    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    # Print the results
    return score, magnitude


def truncate(num):
	if num > 1000000:
		num = round(num, -6)
		num = str(num)
		num = num[:-6]
		num = num + 'm'
		return num
	elif num > 1000:
		num = round(num, -3)
		num = str(num)
		num = num[:-3]
		num = num + 'k'
		return num
	else:
		return str('{:,}'.format(num))