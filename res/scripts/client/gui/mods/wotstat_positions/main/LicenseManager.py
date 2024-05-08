import websocket
import uuid
import json

import BigWorld
from helpers import getClientLanguage
from gui import SystemMessages

from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.PlayerPrefs import PlayerPrefs


LICENSE_PLAYER_PREFS_KEY = 'license'

LANGUAGE = getClientLanguage()

logger = Logger.instance()
notifier = Notifier.instance()

class LicenseType:
  FILE = 'FILE'
  PREDEFINED = 'PREDEFINED'
  NORMAL = 'NORMAL'
  NONE = 'NONE'

class LicenseManager(object):

  __uuid = str(uuid.uuid4())
  __client = None
  __fileLicense = None

  def __init__(self, url, licenseFilePath):
    self.__wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://') + '/api/v1/activation/wot'
    self.__activatorPage = '%s/request-licence-key?requestId=' % url

    try:
      with open(licenseFilePath, "r") as f:
        self.__fileLicense = f.read()
        logger.info('Found license in file: %s' % LicenseManager.obfuscate(self.__fileLicense))
    except Exception as e:
      pass

  def request(self):
    logger.info("Requesting license with: %s" % self.__uuid)

    if not self.__client:
      self.__client = websocket.Client()
      listener = self.__client.listener # type: websocket.Listener
      listener.onOpened += self.__onWebsocketOpened
      listener.onClosed += self.__onWebsocketClosed
      listener.onMessage += self.__onWebsocketMessage

    BigWorld.wg_openWebBrowser(self.__activatorPage + self.__uuid)
    targetUrl = '%s/%s?language=%s' % (self.__wsUrl, self.__uuid, LANGUAGE)
    if self.__client.status != websocket.ConnectionStatus.Opened and self.__client.status != websocket.ConnectionStatus.Opening:
      self.__client.open(targetUrl, reconnect=True)

  def getLicense(self):
    if self.__fileLicense: return self.__fileLicense

    license = PlayerPrefs.get(LICENSE_PLAYER_PREFS_KEY, None)
    if license: return license

    predefined = self.__getPredefinedLicense()
    if predefined: return predefined

    return None
  
  def getLicenseType(self):
    # type: () -> LicenseType

    if self.__fileLicense: return LicenseType.FILE
    if PlayerPrefs.get(LICENSE_PLAYER_PREFS_KEY, None): return LicenseType.NORMAL
    if self.__getPredefinedLicense(): return LicenseType.PREDEFINED
    
    return LicenseType.NONE

  def setLicense(self, license):
    PlayerPrefs.set(LICENSE_PLAYER_PREFS_KEY, license)

  def resetLicense(self):
    PlayerPrefs.delete(LICENSE_PLAYER_PREFS_KEY)

  def __onWebsocketOpened(self, server):
    logger.info('onWebsocketOpened')
    
  def __onWebsocketClosed(self, server, code, reason):
    logger.info('onWebsocketClosed %s %s %s' % (str(server), str(code), str(reason)))

  def __onWebsocketMessage(self, code, payload):
    if code == websocket.OpCode.Text:
      try:
        data = json.loads(payload)
        key = data.get('key', None)

        obfuscatedPayload = str(payload).replace(key, LicenseManager.obfuscate(key)) if key else str(payload)
        logger.info('onWebsocketMessage %s %s' % (str(code), obfuscatedPayload))

        if key:
          logger.info('Set key: %s' % LicenseManager.obfuscate(key))
          self.setLicense(key)

          self.__client.sendText('ACTIVATED')
          self.__client.close()
          self.__uuid = str(uuid.uuid4())

        message = data.get('message', None)
        if message and message.get('text', None):
          notifier.showNotification(message.get('text'), 
                        SystemMessages.SM_TYPE.of(message.get('type', 'Information')),
                        message.get('priority', None),
                        message.get('messageData', None),
                        message.get('savedData', None))

      except:
        logger.error('Failed to parse JSON from payload %s' % payload)
    else:
      logger.info('onWebsocketMessage %s %s' % (str(code), str(payload)))

  def __getPredefinedLicense(self):
    return 'TEST'
  
  @staticmethod
  def obfuscate(license):
    # type: (str) -> str
    return  '*' * (len(license) - 4) + license[-4:]