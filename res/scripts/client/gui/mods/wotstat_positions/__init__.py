import BigWorld

from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.ModUpdater import ModUpdater, UpdateStatus
from .common.Settings import Settings, SettingsKeys, PreferredServerVariants
from .common.HotKeys import HotKeys
from .common.PlayerPrefs import PlayerPrefs
from .common.ExceptionHandling import withExceptionHandling
from .common.Api import Api, PreferredServerVariant
from .main.LifecycleStarter import LifecycleStarter
from .main.PositionRequester import PositionRequester, Commands
from .main.MarkerDrawer import MarkerDrawer
from .main.GreetingNotifier import GreetingNotifier
from .main.LicenseManager import LicenseManager
from .main.MinimapOverlay import setup as minimapOverlaySetup
from .main.EnterLicenseWindow import setup as enterLicenseWindowSetup
from .constants import PlayerPrefsKeys
from .common.CrossGameUtils import gamePublisher, PUBLISHER



DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat.positions/config.cfg'
LICENSE_FILE_PATH = './mods/wotstat.positions.license'

publisher = gamePublisher()


logger = Logger.instance()
hotkeys = HotKeys.instance()
settings = Settings.instance()

class WotstatPositions(object):

  @withExceptionHandling()
  def __init__(self):
    logger.info("Starting WotStatPositions")

    self.config = Config(CONFIG_PATH)

    version = self.config.get("version")
    logger.info("Config loaded. Version: %s" % version)

    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_POS]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
      ServerLoggerBackend(url=self.config.get('lokiURL'),
                          prefix="[MOD_WOTSTAT_POS]",
                          source="mod_positions",
                          modVersion=version,
                          minLevel="INFO")
    ])

    updater = ModUpdater(modName="wotstat.positions",
                         currentVersion=version,
                         ghUrl=self.config.get('ghURL'))
    
    def onRuServerComplete(status):
      logger.info("Ru server update status: %s" % status)
      if status in (UpdateStatus.BAD_INFO, UpdateStatus.NOT_OK_RESPONSE):
        updater.updateToGitHubReleases(lambda status: logger.info("Update status: %s" % status))

    def onMainServerComplete(status):
      logger.info("Main server update status: %s" % status)
      if status in (UpdateStatus.BAD_INFO, UpdateStatus.NOT_OK_RESPONSE):
        updater.updateToLatestVersion('https://ru.install.wotstat.info/api/mod/wotstat.positions/latest', onRuServerComplete)

    updater.updateToLatestVersion('https://install.wotstat.info/api/mod/wotstat.positions/latest', onMainServerComplete)


    lastModeVersion = PlayerPrefs.get(PlayerPrefsKeys.LAST_VERSION)
    PlayerPrefs.set(PlayerPrefsKeys.LAST_VERSION, version)
    if lastModeVersion and lastModeVersion != version:
      updater.showReleaseNotes(lastModeVersion)


    defaultServer = self.config.get('defaultServer')
    alternativeServer = self.config.get('alternativeServer')
    ruProxyServer = self.config.get('ruProxyServer')
    ruProxyNoSslServer = self.config.get('ruProxyNoSslServer')
    servers = {
      PreferredServerVariant.DEFAULT: defaultServer,
      PreferredServerVariant.ALTERNATIVE: alternativeServer,
      PreferredServerVariant.PROXY_RU: ruProxyServer,
      PreferredServerVariant.PROXY_RU_NO_SSL: ruProxyNoSslServer,
      PreferredServerVariant.AUTO: defaultServer,  # AUTO uses the default server
    }
    
    if publisher == PUBLISHER.LESTA:
      self.api = Api(defaultServer, [alternativeServer, ruProxyServer, ruProxyNoSslServer], servers)
    else:
      self.api = Api(defaultServer, [alternativeServer], servers)

    self.firstSettingChanged = True
    settings = Settings.instance()
    settings.onSettingsChanged += self.__onSettingsChanged
    settings.setup("wotstat_positions")
    
    self.licenseManager = LicenseManager(self.api, LICENSE_FILE_PATH)

    minimapOverlaySetup()
    enterLicenseWindowSetup()

    drawer = MarkerDrawer()
    self.requester = PositionRequester(api=self.api, drawer=drawer, licenseManager=self.licenseManager)
    self.requester.onCommand += self.__onServerCommand

    self.lifecycle = LifecycleStarter(self.requester, self.licenseManager)
    
    self.greeting = GreetingNotifier(self.api, self.licenseManager)
    self.greeting.onGameOpen += self.__onGameOpen

    HotKeys.instance().onCommand += self.__onCommand

  def __getPreferredServer(self, settingsVariant):
    # type: (int) -> int

    mapping = {
      PreferredServerVariants.AUTO: PreferredServerVariant.AUTO,
      PreferredServerVariants.MAIN: PreferredServerVariant.DEFAULT,
      PreferredServerVariants.ALTERNATIVE: PreferredServerVariant.ALTERNATIVE,
      PreferredServerVariants.PROXY_RU: PreferredServerVariant.PROXY_RU,
      PreferredServerVariants.PROXY_RU_NO_SSL: PreferredServerVariant.PROXY_RU_NO_SSL,
    }
    
    if settingsVariant not in mapping:
      logger.error("Unknown preferred server variant: %s, use AUTO" % settingsVariant)
      return PreferredServerVariant.AUTO
    
    return mapping[settingsVariant]
  

  def __onSettingsChanged(self, settings):
    # type: (dict) -> None
    hotkeys.updateCommandHotkey("sendReport", settings.get(SettingsKeys.REPORT_HOTKEY))

    server = self.__getPreferredServer(settings.get(SettingsKeys.PREFERRED_SERVER))

    if not self.firstSettingChanged:
      if self.api.preferredServer != server:
        BigWorld.callback(0.5, lambda: self.api.setPreferredServer(server, True))
        BigWorld.callback(1, lambda: self.greeting.requestGreeting())
    else:
      self.firstSettingChanged = False
      self.api.setPreferredServer(server)
      
    logger.debug("Hotkeys commands updated")

  def __onCommand(self, command):
    if not settings.get(SettingsKeys.ENABLED): return
    if not getattr(BigWorld.player(), 'inWorld', False): return

    if command == 'sendReport':
      self.requester.sendReport()

  def __onServerCommand(self, command):
    logger.info("Server command: %s" % command)
    if command == Commands.DISABLE_FOR_SESSION:
      self.lifecycle.disable()
    elif command == Commands.ENABLE_FOR_SESSION:
      self.lifecycle.enable()
    elif command == Commands.RESET_LICENSE:
      self.licenseManager.resetLicense()
    elif command == Commands.BLOCK_LICENSE:
      self.licenseManager.blockLicense()

  def __onGameOpen(self):
    self.lifecycle.enable()