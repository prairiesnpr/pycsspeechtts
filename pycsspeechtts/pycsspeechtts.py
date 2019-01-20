"""
Python wrapper for Microsoft Cognitive Services Text-to-speech translator
"""

import urllib.parse
from xml.etree import ElementTree
import logging
import sys
import requests

_LOGGER = logging.getLogger(__name__)

AUTH_HOST = "https://eastus.api.cognitive.microsoft.com"
AUTH_PATH = "/sts/v1.0/issueToken"
SPEECH_HOST = 'https://eastus.tts.speech.microsoft.com'
SPEECH_PATH = '/cognitiveservices/v1'
RESOURCE_NAME = 'homeassistant'


class TTSTranslator(object):
    """
    Interface class for the Microsoft Cognitive Services Text-to-speech translator
    """
    def __init__(self, apiKey):
        self._apiKey = apiKey
        headers = {"Ocp-Apim-Subscription-Key":self._apiKey}
        auth_url = urllib.parse.urljoin(AUTH_HOST, AUTH_PATH)
        response = requests.post(auth_url, headers=headers)
        
        if response.status_code == 200:
            _LOGGER.debug("Connection Initialized OK")
            data = response.content
            self._accesstoken = data.decode("UTF-8")
        else:
            _LOGGER.error("Connection Intialization failed, statuscode "+str(response.status_code))
            sys.exit(1)

    def speak(self, language="en-us", gender="Female", voiceType="ZiraRUS", output="riff-16khz-16bit-mono-pcm", rate="+0.00%", volume="+0.00%", pitch="default", contour="(0%,+0%) (100%,+0%)", text=None):
        body = ElementTree.Element('speak',version='1.0')
        body.set('{http://www.w3.org/XML/1998/namespace}lang',language)
        
        voice = ElementTree.SubElement(body,'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang',language)
        voice.set('{http://www.w3.org/XML/1998/namespace}gender',gender)
        voice.set('name','Microsoft Server Speech Text to Speech Voice ('+language+', '+voiceType+')')
        #voice.text = text

        prosody = ElementTree.SubElement(voice,'prosody')
        prosody.set('rate',rate)
        prosody.set('volume',volume)
        prosody.set('pitch', pitch)
        prosody.set('contour',contour)
        prosody.text = text

        headers = {"Content-Type": "application/ssml+xml",
                    "X-Microsoft-OutputFormat": output,
                    "Authorization": "Bearer " + self._accesstoken,
                    "User-Agent": RESOURCE_NAME
        }
        speech_url = urllib.parse.urljoin(SPEECH_HOST, SPEECH_PATH)
        response = requests.post(speech_url, headers=headers, data=ElementTree.tostring(body))
        if response.status_code == requests.codes.ok:
            _LOGGER.debug("Text synthesis OK")
            data = response.content
            return data
        else:
            _LOGGER.error("Text synthesis failed, statuscode "+str(response.status_code))
            return None