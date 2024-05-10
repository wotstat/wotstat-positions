import websocket
import uuid
import json

import BigWorld
from helpers import getClientLanguage

from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.PlayerPrefs import PlayerPrefs
from ..common.ExceptionHandling import withExceptionHandling
from ..constants import PlayerPrefsKeys

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
  __blocked = False
  __heartbeatTimer = None

  def __init__(self, url, licenseFilePath):
    self.__wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://') + '/api/v1/activation/wot'
    if LANGUAGE != 'ru':
      self.__activatorPage = '%s/en/request-licence-key?requestId=' % url
    else:
      self.__activatorPage = '%s/request-licence-key?requestId=' % url

    try:
      with open(licenseFilePath, "r") as f:
        self.__fileLicense = f.read()
        logger.info('Found license in file: %s' % LicenseManager.obfuscate(self.__fileLicense))
    except Exception as e:
      pass

  def __targetWSUrl(self):
    return '%s/%s?language=%s' % (self.__wsUrl, self.__uuid, LANGUAGE)
  
  @withExceptionHandling()
  def request(self):
    logger.info("Requesting license with: %s" % self.__uuid)

    if not self.__client:
      self.__client = websocket.Client()
      listener = self.__client.listener # type: websocket.Listener
      listener.onOpened += self.__onWebsocketOpened
      listener.onClosed += self.__onWebsocketClosed
      listener.onFailed += self.__onWebsocketFailed
      listener.onMessage += self.__onWebsocketMessage

    BigWorld.wg_openWebBrowser(self.__activatorPage + self.__uuid)
    if self.__client.status != websocket.ConnectionStatus.Opened and self.__client.status != websocket.ConnectionStatus.Opening:
      self.__client.open(self.__targetWSUrl())

  def getLicense(self):
    if self.__fileLicense: return self.__fileLicense

    license = PlayerPrefs.get(PlayerPrefsKeys.LICENSE, None)
    if license: return license

    predefined = self.__getPredefinedLicense()
    if predefined: return predefined

    return None
  
  def hasLicense(self):
    return bool(self.getLicense())
  
  def isBlocked(self):
    return self.__blocked

  def getLicenseType(self):
    # type: () -> LicenseType

    if self.__fileLicense: return LicenseType.FILE
    if PlayerPrefs.get(PlayerPrefsKeys.LICENSE, None): return LicenseType.NORMAL
    if self.__getPredefinedLicense(): return LicenseType.PREDEFINED
    
    return LicenseType.NONE

  def setLicense(self, license):
    PlayerPrefs.set(PlayerPrefsKeys.LICENSE, license)
    self.__blocked = False

  def resetLicense(self):
    PlayerPrefs.delete(PlayerPrefsKeys.LICENSE)
    PlayerPrefs.delete(PlayerPrefsKeys.TOKEN)
    self.__blocked = False

  def blockLicense(self):
    self.__blocked = True

  def getToken(self):
    return PlayerPrefs.get(PlayerPrefsKeys.TOKEN, '')
  
  def setToken(self, token):
    PlayerPrefs.set(PlayerPrefsKeys.TOKEN, token)

  @withExceptionHandling()
  def __onWebsocketOpened(self, server):
    logger.info('onWebsocketOpened')
    if self.__heartbeatTimer is not None:
      BigWorld.cancelCallback(self.__heartbeatTimer)
      self.__heartbeatTimer = None
    self.__heartbeatLoop()
    
  @withExceptionHandling()
  def __onWebsocketFailed(self, server, code, reason):
    logger.info('onWebsocketFailed %s %s %s' % (str(server), str(code), str(reason)))

  @withExceptionHandling()
  def __onWebsocketClosed(self, server, code, reason):
    logger.info('onWebsocketClosed %s %s %s' % (str(server), str(code), str(reason)))

  @withExceptionHandling()
  def __onWebsocketMessage(self, code, payload):
    if payload == 'PONG': return

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

        if data.get('blocked', False):
          logger.info('License is blocked')
          self.blockLicense()

        message = data.get('message', None)
        if message and message.get('text', None):
          notifier.showNotificationFromData(message)

      except:
        logger.error('Failed to parse JSON from payload %s' % payload)
    else:
      logger.info('onWebsocketMessage %s %s' % (str(code), str(payload)))

  @withExceptionHandling()
  def __heartbeatLoop(self):
    self.__heartbeatTimer = BigWorld.callback(5, self.__heartbeatLoop)

    if self.__client and self.__client.status == websocket.ConnectionStatus.Opened:
      self.__client.sendText('PING')

  def __getPredefinedLicense(self):
    return None
  
  @staticmethod
  def obfuscate(license):
    # type: (str) -> str
    return  '*' * (len(license) - 4) + license[-4:]