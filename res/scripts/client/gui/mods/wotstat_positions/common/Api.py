import json
import BigWorld
import threading
import functools
from gui import SystemMessages
from helpers import getClientLanguage
from .Logger import Logger
from .Notifier import Notifier
from .i18n import t

try: import openwg_network
except ImportError: openwg_network = None

JSON_HEADERS = {'Content-Type': 'application/json'}
LANGUAGE = getClientLanguage()

logger = Logger.instance()

class PreferredServerVariant:
  DEFAULT = 0
  ALTERNATIVE = 1
  AUTO = 2
  PROXY_RU = 3
  PROXY_RU_NO_SSL = 4
  TELEPORT_MSK_1 = 5
  TELEPORT_NBG_1 = 6
  TELEPORT_SPB_1 = 7
  OPENWG_NETWORK = 8

PreferredServerVariantNames = {
  PreferredServerVariant.DEFAULT: 'default',
  PreferredServerVariant.ALTERNATIVE: 'alternative',
  PreferredServerVariant.AUTO: 'auto',
  PreferredServerVariant.PROXY_RU: 'proxy_ru',
  PreferredServerVariant.PROXY_RU_NO_SSL: 'proxy_ru_no_ssl',
  PreferredServerVariant.TELEPORT_MSK_1: 'teleport_msk_1',
  PreferredServerVariant.TELEPORT_NBG_1: 'teleport_nbg_1',
  PreferredServerVariant.TELEPORT_SPB_1: 'teleport_spb_1',
  PreferredServerVariant.OPENWG_NETWORK: 'openwg.network'
}

serverToLocalizedNames = {
  PreferredServerVariant.AUTO: t('settings:auto'),
  PreferredServerVariant.DEFAULT: t('settings:main'),
  PreferredServerVariant.ALTERNATIVE: t('settings:alternative'),
  PreferredServerVariant.PROXY_RU: t('settings:proxyRu'),
  PreferredServerVariant.PROXY_RU_NO_SSL: t('settings:proxyRuNoSsl'),
  PreferredServerVariant.TELEPORT_MSK_1: t('settings:teleportMsk1'),
  PreferredServerVariant.TELEPORT_NBG_1: t('settings:teleportNbg1'),
  PreferredServerVariant.TELEPORT_SPB_1: t('settings:teleportSpb1'),
  PreferredServerVariant.OPENWG_NETWORK: t('settings:openwg.network')
}

def openWGRequest(url, method='GET', headers=None, timeout=30.0, body=None, callback=None):
  def worker():
    resp = openwg_network.request(url, method, headers, timeout, body)
    if callback: BigWorld.callback(0.0, functools.partial(callback, resp))

  t = threading.Thread(target=worker)
  t.daemon = True
  t.start()

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
    self.openWGNetworkRetryCount = 0

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
    
    logger.warn('Unknown preferred server variant: %s, use default server' % PreferredServerVariantNames.get(self.preferredServer, self.preferredServer))
    return self.defaultServerUrl
  
  def request(self, url, callback, method='GET', headers=None, postData=None, timeout=30):
    # type: (str, callable, str, dict, str, int) -> None

    shouldUseOpenWG = openwg_network and (
      (self.preferredServer == PreferredServerVariant.OPENWG_NETWORK) or \
      (self.preferredServer == PreferredServerVariant.AUTO and self.openWGNetworkRetryCount < 3)
    )

    if shouldUseOpenWG:
      targetUrl = str(self.defaultServerUrl + url)
      logger.debug('Request via openwg.network: %s' % targetUrl)

      def onComplete(response):
        status, headers, body = response

        logger.debug('openwg.network response status: %s, headers: %s, body: %s' % (str(status), str(headers), str(body)))

        result = type('Result', (object,), {})()
        result.responseCode = status
        result.headers = headers
        result.body = body

        if result.responseCode == 200:
          self.openWGNetworkRetryCount = 0
          callback(result)
          return
        
        if result.responseCode != 200:
          if self.openWGNetworkRetryCount < 3:
            self.openWGNetworkRetryCount += 1
            logger.error('openwg.network request error code: %s, retry: %s' % (result.responseCode, targetUrl))
            openwg_network.request_callback(targetUrl, method=method, headers=headers, body=postData, callback=onComplete)
            return

        callback(result)

      openWGRequest(targetUrl, method=method, headers=headers, body=postData, callback=onComplete, timeout=timeout)
      return
    
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

    serverUrl = self.getServerUrl()
    if 'openwg.net' in serverUrl: serverUrl = self.defaultServerUrl

    if LANGUAGE != 'ru': return serverUrl + '/en/request-licence-key/?requestId=' + requestId
    else: return serverUrl + '/request-licence-key/?requestId=' + requestId

  def getWebSocketActivationUrl(self, requestId):
    # type: (str) -> str
    wsUrl = self.getServerUrl().replace('http://', 'ws://').replace('https://', 'wss://') + '/api/v1/activation/wot'
    return '%s/%s?language=%s' % (wsUrl, requestId, LANGUAGE)
  