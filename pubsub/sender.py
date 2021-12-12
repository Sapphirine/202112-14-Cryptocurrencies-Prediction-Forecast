import base64
import json
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def emailSender(event, context):
     """Triggered from a message on a Cloud Pub/Sub topic.
     Args:
          event (dict): Event payload.
          context (google.cloud.functions.Context): Metadata for the event.
     """
     # decrypt the messgage
     # pubsub_message = base64.b64decode(event['data']).decode('utf-8')
     
     message = Mail(
     from_email="sk4920@columbia.edu",
     to_emails="sk4920@columbia.edu",
     subject='Sending with Twilio SendGrid is Fun',
     html_content='<strong>and easy to do anywhere, even with Python</strong>')
     try:
          sg = SendGridAPIClient("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")
          sg.send(message)
     except Exception as e:
          print(str(e))
     # print(pubsub_message)


if __name__ == '__main__':
     emailSender(None, None)