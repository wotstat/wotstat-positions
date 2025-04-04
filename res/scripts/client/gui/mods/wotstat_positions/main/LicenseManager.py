import websocket
import uuid
import json

import BigWorld
from helpers import getClientLanguage
from gui import SystemMessages

from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.PlayerPrefs import PlayerPrefs
from ..common.ExceptionHandling import withExceptionHandling
from ..common.Api import Api
from ..constants import PlayerPrefsKeys
from .EnterLicenseWindow import show as showEnterLicenseWindow
from ..common.i18n import t

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

  def __init__(self, api, licenseFilePath):
    # type: (Api, str) -> None

    self.__api = api
    
    try:
      with open(licenseFilePath, "r") as f:
        self.__fileLicense = f.read()
        logger.info('Found license in file: %s' % LicenseManager.obfuscate(self.__fileLicense))
    except Exception as e:
      pass

  @withExceptionHandling()
  def requestInGameUI(self):
    showEnterLicenseWindow(self)
  
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

    BigWorld.wg_openWebBrowser(self.__api.getActivatorPageUrl(self.__uuid))
    if self.__client.status != websocket.ConnectionStatus.Opened and self.__client.status != websocket.ConnectionStatus.Opening:
      self.__client.open(self.__api.getWebSocketActivationUrl(self.__uuid))

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

  def processEnterLicense(self, license):
    
    def onResponse(data):
      # type: (BigWorld.PyURLResponse) -> None
      if data.responseCode == 200:
        
        body = data.body
        if not body:
          logger.error('Response body is empty')
          return
        
        parsed = None # type: dict
        try:
          parsed = json.loads(body)
        except ValueError:
          logger.error('Response body is not a valid JSON: %s' % body)
          return
        
        status = parsed.get('status', None)
        logger.info('License activation status: %s' % str(status))
        if status == "FIRST_ACTIVATION" or status == "ALREADY_ACTIVATED" or status == "PATREON_ACTIVATED":
          logger.info('License activated: %s' % LicenseManager.obfuscate(license))
          self.setLicense(license)
        
        if parsed.get('blocked', False):
          logger.info('License is blocked')
          self.blockLicense()

        message = parsed.get('message', None)
        if message and message.get('text', None):
          notifier.showNotificationFromData(message)
          
      else:
        logger.error('Failed to activate license, code: %s' % str(data.responseCode))
        notifier.showNotification(t('enterLicense.serverError') % str(data.responseCode), SystemMessages.SM_TYPE.Error)
    
    if not license: return
    
    self.__api.checkLicense(license, onResponse)
    logger.info('License entered: %s' % LicenseManager.obfuscate(license))

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