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
  PROXY_RU = 3
  PROXY_RU_NO_SSL = 4

PreferredServerVariantNames = {
  PreferredServerVariant.DEFAULT: 'default',
  PreferredServerVariant.ALTERNATIVE: 'alternative',
  PreferredServerVariant.AUTO: 'auto',
  PreferredServerVariant.PROXY_RU: 'proxy_ru',
  PreferredServerVariant.PROXY_RU_NO_SSL: 'proxy_ru_no_ssl'
}

serverToLocalizedNames = {
  PreferredServerVariant.AUTO: t('settings:auto'),
  PreferredServerVariant.DEFAULT: t('settings:main'),
  PreferredServerVariant.ALTERNATIVE: t('settings:alternative'),
  PreferredServerVariant.PROXY_RU: t('settings:proxyRu'),
  PreferredServerVariant.PROXY_RU_NO_SSL: t('settings:proxyRuNoSsl')
}

class ServersStateMachine:
  def __init__(self, defaultServer, alternativeServers):
    # type: (str, list) -> None
    self.servers = [defaultServer] + alternativeServers
    self.currentServerIndex = 0
    self.currentServerErrorCount = 0
    self.currentServerTotalErrorCount = 0
    self.currentServerRequestCount = 0


  def getServerUrl(self):
    # type: () -> str
    return self.servers[self.currentServerIndex]
  
  def nextServer(self):
    if self.currentServerIndex < len(self.servers) - 1:
      self.currentServerIndex += 1
      self.currentServerErrorCount = 0
      self.currentServerTotalErrorCount = 0
      self.currentServerRequestCount = 0
    else:
      logger.warn('No more alternative servers, stay on current server: %s' % self.getServerUrl())
  
  def currentServerErrorShouldRetry(self):
    self.currentServerRequestCount += 1

    isLastAlternative = self.currentServerIndex == len(self.servers) - 1
    if self.currentServerTotalErrorCount > 30 and self.currentServerTotalErrorCount / self.currentServerRequestCount > 0.4 and not isLastAlternative:
      self.nextServer()
      logger.error('Error ratio (%s/%s) = %s > 0.4, switch to next server: %s' %  (
        self.currentServerTotalErrorCount, 
        self.currentServerRequestCount, 
        self.currentServerTotalErrorCount / self.currentServerRequestCount,
        self.getServerUrl()))
      return True

    if self.currentServerErrorCount < 3:
      self.currentServerErrorCount += 1
      logger.error('Request error, retry %s to server: %s' % (self.currentServerErrorCount, self.getServerUrl()))
      return True
    
    self.currentServerErrorCount = 0

    if not isLastAlternative:
      self.nextServer()
      logger.error('Request error 3 times, switch to next server: %s' % self.getServerUrl())
      return True
    
    logger.error('Request error 3 times, no more alternative servers, stop retrying')
    
    return False

  def currentServerSuccess(self):
    self.currentServerErrorCount = 0
    self.currentServerRequestCount += 1

  def reset(self):
    self.currentServerErrorCount = 0
    self.currentServerIndex = 0
    self.currentServerTotalErrorCount = 0
    self.currentServerRequestCount = 0
  

notifier = Notifier.instance()
class Api:

  def __init__(self, defaultServer, alternativeServers, serverUrls, preferredServer=PreferredServerVariant.DEFAULT):
    self.preferredServer = preferredServer
    self.servers = ServersStateMachine(defaultServer, alternativeServers)
    self.serverUrls = serverUrls
    self.defaultServerUrl = defaultServer

  def setPreferredServer(self, variant, notification=False):
    # type: (int, bool) -> None
    
    if self.preferredServer == variant: return
    self.preferredServer = variant
    self.servers.reset()
    if notification:
      notifier.showNotification(
        t('api.serverChanged') % serverToLocalizedNames[self.preferredServer], 
        SystemMessages.SM_TYPE.InformationHeader, 
        None,
        {'header': t('api.serverChangedHeader')})

  def getServerUrl(self):
    # type: () -> str

    if self.preferredServer == PreferredServerVariant.AUTO: return self.servers.getServerUrl()

    if self.preferredServer in self.serverUrls:
      return self.serverUrls[self.preferredServer]
    
    logger.warning('Unknown preferred server variant: %s, use default server' % PreferredServerVariantNames.get(self.preferredServer, self.preferredServer))
    return self.defaultServerUrl
  
  def request(self, url, callback, method='GET', headers=None, postData=None, timeout=30):
    # type: (str, callable, str, dict, str, int) -> None
    
    def onComplete(result):
      # type: (str) -> None

      if self.preferredServer != PreferredServerVariant.AUTO:
        self.servers.reset()
        callback(result)
        return
      
      if result.responseCode == 200:
        self.servers.currentServerSuccess()
        callback(result)
        return
      
      if result.responseCode != 200:
        if self.servers.currentServerErrorShouldRetry():
          targetUrl = str(self.servers.getServerUrl() + url)
          logger.error('Request error code: %s, retry: %s' % (result.responseCode, targetUrl))
          BigWorld.fetchURL(targetUrl, onComplete, method=method, headers=headers, postData=postData, timeout=timeout)
          return

      callback(result)

    
    targetUrl = str(self.getServerUrl() + url)
    logger.debug('Request [%s] to %s with headers: %s and postData: %s' % (method, targetUrl, str(headers), str(postData)))
    BigWorld.fetchURL(targetUrl, onComplete, method=method, headers=headers, postData=postData, timeout=timeout)
  
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
  