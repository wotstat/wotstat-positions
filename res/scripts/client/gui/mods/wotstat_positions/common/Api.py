import json
import BigWorld
from gui import SystemMessages
from helpers import getClientLanguage
from .Logger import Logger
from .Notifier import Notifier
from .i18n import t

JSON_HEADERS = {'Content-Type': 'application/json'}
LANGUAGE = getClientLanguage()

logger = Logger.instance()

class PreferredServerVariant:
  DEFAULT = 0
  ALTERNATIVE = 1
  AUTO = 2

notifier = Notifier.instance()
class Api:

  def __init__(self, serverUrl, alternativeServerUrl, preferredServer=PreferredServerVariant.DEFAULT):
    self.preferredServer = preferredServer
    self.serverUrl = serverUrl
    self.alternativeServerUrl = alternativeServerUrl

    self.errorsCount = 0
    self.tryAlternativeServer = False
    self.preventTryAlternativeServer = False
    self.useAlternativeServer = False

  def setPreferredServer(self, variant):
    # type: (int) -> None
    self.preferredServer = variant

  def getServerUrl(self):
    # type: () -> str

    if self.preferredServer == PreferredServerVariant.DEFAULT: return self.serverUrl
    elif self.preferredServer == PreferredServerVariant.ALTERNATIVE: return self.alternativeServerUrl
    if self.useAlternativeServer or self.tryAlternativeServer: return self.alternativeServerUrl
    
    return self.serverUrl
  
  def request(self, url, callback, method='GET', headers=None, postData=None, timeout=30):
    # type: (str, callable, str, dict, str, int) -> None
    
    def onComplete(result):
      # type: (str) -> None

      if self.preferredServer != PreferredServerVariant.AUTO:
        self.errorsCount = 0
        callback(result)
        return
      
      if self.preventTryAlternativeServer or self.useAlternativeServer:
        callback(result)
        return
      
      if result.responseCode == 200 and self.tryAlternativeServer:
        logger.info('Try alternative server success')
        self.useAlternativeServer = True
        self.tryAlternativeServer = False
        self.errorsCount = 0
        notifier.showNotification(t('request.switchToAlternativeServer'), SystemMessages.SM_TYPE.InformationHeader, messageData={'header': t('settings:modDisplayName')})
        callback(result)
        return
      

      if result.responseCode != 200:

        if self.tryAlternativeServer:
          logger.info('Try alternative server error: %s' % result.responseCode)
          self.useAlternativeServer = False
          self.tryAlternativeServer = False
          self.preventTryAlternativeServer = True
          self.errorsCount = 0
          callback(result)
          return

        if (self.errorsCount < 2):
          self.errorsCount += 1
          logger.error('Request error: %s, retry %s to main server' % (result.responseCode, self.errorsCount))
          BigWorld.fetchURL(self.getServerUrl() + url, onComplete, method=method, headers=headers, postData=postData, timeout=timeout)
          return
        else:
          logger.error('Request error: %s, try alternative server' % result.responseCode)
          self.tryAlternativeServer = True
          self.errorsCount = 0
          BigWorld.fetchURL(self.getServerUrl() + url, onComplete, method=method, headers=headers, postData=postData, timeout=timeout)
          return
        
      callback(result)

    
    BigWorld.fetchURL(self.getServerUrl() + url, onComplete, method=method, headers=headers, postData=postData, timeout=timeout)
  
  def report(self, data, callback):
    # type: (dict, callable) -> None
    self.request('/api/v1/report', callback, headers=JSON_HEADERS, method='POST', postData=json.dumps(data), timeout=5)

  def requestPositions(self, data, callback):
    # type: (dict, callable) -> None
    self.request('/api/v2/positions', callback, headers=JSON_HEADERS, method='POST', postData=json.dumps(data), timeout=5)

  def checkLicense(self, license, callback):
    # type: (str, callable) -> None
    self.request('/api/v1/activation/check?key=%s&language=%s' % (license, LANGUAGE), callback, timeout=5)

  def afterReset(self, params, callback):
    # type: (dict, callable) -> None

    postfix = '&'.join(['%s=%s' % (k, v) for k, v in params.items() if v is not None])
    self.request(
      '/api/v1/afterReset?' + postfix,
      callback, 
      method='GET',
      timeout=5
    )

  def greeting(self, params, callback):
    # type: (dict, callable) -> None
    
    postfix = '&'.join(['%s=%s' % (k, v) for k, v in params.items() if v is not None])
    self.request(
      '/api/v1/greeting?' + postfix,
      callback, 
      method='GET',
      timeout=5
    )

  def getActivatorPageUrl(self, requestId):
    # type: (str) -> str
    if LANGUAGE != 'ru': return self.getServerUrl() + '/en/request-licence-key/?requestId=' + requestId
    else: return self.getServerUrl() + '/request-licence-key/?requestId=' + requestId

  def getWebSocketActivationUrl(self, requestId):
    # type: (str) -> str
    wsUrl = self.getServerUrl().replace('http://', 'ws://').replace('https://', 'wss://') + '/api/v1/activation/wot'
    return '%s/%s?language=%s' % (wsUrl, requestId, LANGUAGE)
  