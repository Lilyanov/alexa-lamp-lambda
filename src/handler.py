import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".dependencies"))
import configparser
import json
import logging
import requests

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
LOG = logging.getLogger('AlexaLampLambda')

config = configparser.RawConfigParser()
config.read('credentials.properties')


class LampController:

    def __init__(self):
        self.username = config.get('Cred', 'username')
        self.password = config.get('Cred', 'password')
        self.url = config.get('Cred', 'url')

    def get_token(self):
        token_response = requests.post(self.url + '/auth/get-token',
                                       json={'username': self.username, 'password': self.password}, verify=False)
        LOG.info("Token response: {}", token_response)
        if token_response.status_code == 200:
            return token_response.json()['token']
        else:
            LOG.error(f"Request failed status code: {token_response.status_code}, reason: {token_response.reason}")

    def switch_lamp(self, request) -> str:
        if 'intent' not in request:
            return "I couldn't understand you. Please repeat!"

        if 'room' not in request['intent']['slots']:
            return "I couldn't understand the room. Please repeat!"

        if 'status' not in request['intent']['slots']:
            return "I couldn't understand the lamp status. Please repeat!"

        room = request['intent']['slots']['room']['value']
        status = request['intent']['slots']['status']['value']

        device_id = 'bedroomLamp'
        if room == 'bedroom':
            device_id = 'bedroomLamp'

        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }
        body = {
            'deviceId': device_id,
            'lampStatus': 1 if status == 'on' else 0
        }
        try:
            LOG.info(f"Sending request with body: {str(body)}")
            response = requests.post('{}/devices/{}/switch'.format(self.url, device_id), json=body, headers=headers, verify=False)
            if response.status_code == 200:
                LOG.info('Request was sent successfully')
                return 'Lamp in the {} was switched {}'.format(room, status)
            else:
                LOG.error(f"Lamp switch returned non successful code: {response.status_code}, reason: {response.reason}")
        except Exception as e:
            LOG.error(f"Lamp switch failed. Reason: {str(e)}")

        return "Sorry, there was a problem. The lamp couldn't be switched"


def lambda_handler(event, context):
    print(json.dumps(event['request']))

    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": LampController().switch_lamp(event['request'])
            }
        }
    }

# s = LampController().switch_lamp({
#     'intent': {
#         'slots': {
#             'room': {
#                 'value': 'bedroom'
#             },
#             'status': {
#                 'value': 'on'
#             }
#         }
#     }
# })