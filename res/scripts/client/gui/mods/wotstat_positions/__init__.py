import BigWorld

from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.ModUpdater import ModUpdater
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



DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat.positions/config.cfg'
LICENSE_FILE_PATH = './mods/wotstat.positions.license'


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

    updator = ModUpdater(modName="wotstat.positions",
                         currentVersion=version,
                         ghUrl=self.config.get('ghURL'))
    updator.updateToGitHubReleases(lambda status: logger.info("Update status: %s" % status))


    lastModeVersion = PlayerPrefs.get(PlayerPrefsKeys.LAST_VERSION)
    PlayerPrefs.set(PlayerPrefsKeys.LAST_VERSION, version)
    if lastModeVersion and lastModeVersion != version:
      updator.showReleaseNotes(lastModeVersion)

    self.api = Api(serverUrl=self.config.get('baseURL'), alternativeServerUrl=self.config.get('alternativeBaseURL'))

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
    
    greeting = GreetingNotifier(self.api, self.licenseManager)
    greeting.onGameOpen += self.__onGameOpen

    HotKeys.instance().onCommand += self.__onCommand

  def __getPreferredServer(self, settingsVariant):
    # type: (int) -> int
    if settingsVariant == PreferredServerVariants.MAIN:
      return PreferredServerVariant.DEFAULT
    elif settingsVariant == PreferredServerVariants.ALTERNATIVE:
      return PreferredServerVariant.ALTERNATIVE
    elif settingsVariant == PreferredServerVariants.AUTO:
      return PreferredServerVariant.AUTO
    else:
      return PreferredServerVariant.DEFAULT

  def __onSettingsChanged(self, settings):
    # type: (dict) -> None
    hotkeys.updateCommandHotkey("sendReport", settings.get(SettingsKeys.REPORT_HOTKEY))

    server = settings.get(SettingsKeys.PREFERRED_SERVER)
    self.api.setPreferredServer(self.__getPreferredServer(server))

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