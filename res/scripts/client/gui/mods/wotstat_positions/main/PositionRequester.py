import json
import uuid

import BigWorld
from constants import ARENA_BONUS_TYPE, ARENA_GAMEPLAY_NAMES, AUTH_REALM, ARENA_PERIOD
from gui.Scaleform.genConsts.BATTLE_MESSAGES_CONSTS import BATTLE_MESSAGES_CONSTS
from Avatar import PlayerAvatar
from helpers import getClientLanguage
from gui import InputHandler
import Keys

from ..common.Logger import Logger
from ..common.Settings import Settings, SettingsKeys, ShowVariants, OverlayShowVariants
from ..common.ExceptionHandling import SendExceptionEvent, withExceptionHandling
from ..common.BattleMessages import showPlayerMessage
from ..common.Notifier import Notifier
from ..common.i18n import t
from .utils import shortTankType, getTankType, getTankRole, getPlayerVehicle
from .WotHookEvents import wotHookEvents
from .ArenaInfoProvider import ArenaInfoProvider
from .MinimapOverlay import MinimapOverlay, OverlayVisibilityMode
from ..constants import ServerCommands as Commands
from ..common.Api import Api
from . import IPositionDrawer, IPositionRequester, PositionPoint, LicenseManager, Heatmap, Spots  # noqa: F401
from EyeDisplayProcessor import EyeDisplayProcessor


logger = Logger.instance()
settings = Settings.instance()
ARENA_TAGS = dict([(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])
LANGUAGE = getClientLanguage()

class PositionRequester(IPositionRequester):

  onCommand = SendExceptionEvent()

  def __init__(self, api, drawer, licenseManager):
    # type: (Api, IPositionDrawer, LicenseManager.LicenseManager) -> None

    self.__drawer = drawer
    self.__eyeDisplayProcessor = EyeDisplayProcessor(self.__drawer)
    self.__api = api
    self.__lastRequestTime = 0
    self.__getDrawerReadyRetryCount = 0

    self.__arenaInfoProvider = ArenaInfoProvider()

    self.__callbackID = None
    self.__isEnable = False
    self.__isPaused = False
    self.__isLoading = False
    self.__lastResponse = None # type: PositionsResponse
    self.__altPressed = False

    self.__battleUUID = None
    self.__licenseManager = licenseManager

    self.__lastReportTime = 0
    self.__lastPlayerVehicle = None

    wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.__onArenaPeriodChange
    settings.onSettingsChanged += self.__onSettingsChanged
    InputHandler.g_instance.onKeyDown += self.__onKey
    InputHandler.g_instance.onKeyUp += self.__onKey
      
  def start(self):
    self.__isEnable = True
    self.__isPaused = False
    self.__isLoading = False
    self.__lastRequestTime = 0
    self.__lastReportTime = 0
    self.__getDrawerReadyRetryCount = 0
    self.__lastResponse = None
    self.__lastPlayerVehicle = None
    self.__battleUUID = str(uuid.uuid4())
    self.__licenseCache = self.__licenseManager.getLicense()

    if not self.__licenseCache:
      logger.debug('License is not found')
      return

    player = BigWorld.player()
    if hasattr(player, 'arena'):
      self.__startBattleTime = player.arena.periodEndTime \
        if player.arena.period is ARENA_PERIOD.PREBATTLE \
        else player.arena.periodEndTime - player.arena.periodLength
    else:
      self.__startBattleTime = -10003
    
    logger.debug('Start requesting loop')
    self.__requestLoop()

  def stop(self):
    self.__isEnable = False
    self.__drawer.reset()
    if self.__callbackID is not None:
      BigWorld.cancelCallback(self.__callbackID)
      self.__callbackID = None

  @withExceptionHandling()
  def sendReport(self):
    if not self.__isEnable:
      logger.debug('Request loop is not enabled')
      return
    
    if not self.__lastResponse:
      return
        
    player = BigWorld.player()

    if player is None or not hasattr(player, 'arena'):
      logger.debug('Player is not on arena')
      return
    
    vehicle = getPlayerVehicle(player)
    if vehicle is None:
      logger.debug('Player vehicle is None')
      return
    
    battleTime = self.__battleTime()
    if battleTime <= -10000:
      logger.debug('Battle is still loading')
      return
    
    if BigWorld.time() - self.__lastReportTime < 10:
      showPlayerMessage(t('battleMessage:reportSendTimeLimit'), BATTLE_MESSAGES_CONSTS.COLOR_GOLD)
      return
    self.__lastReportTime = BigWorld.time()


    response = self.__lastResponse

    report = {
      'player': BigWorld.player().name,
      'arena': player.arena.arenaType.geometry,
      'mode': ARENA_TAGS[player.arena.bonusType],
      'gameplay': ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
      'team': player.team,
      'vehicle': BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
      'responseId': response.data.get('id', ''),
      'response': response.data
    }

    def onResponse(data):
      if data.responseCode != 200:
        logger.error('Report response status is not 200: %s' % data.responseCode)
        return

    self.__api.report(report, onResponse)

    showPlayerMessage(t('battleMessage:reportSended'), BATTLE_MESSAGES_CONSTS.COLOR_GOLD)


  @withExceptionHandling()
  def __onSettingsChanged(self, settings):
    self.__redraw()

  @withExceptionHandling()
  def __onKey(self, event):
    # type: (BigWorld.KeyEvent) -> None
    if event.key in (Keys.KEY_LALT, Keys.KEY_RALT):
      if self.__altPressed != event.isKeyDown():
        self.__altPressed = event.isKeyDown()
        self.__redraw()

  @withExceptionHandling()
  def __requestLoop(self):
    self.__callbackID = None

    if not self.__isEnable:
      logger.debug('Request loop is not enabled')
      return
    
    self.__callbackID = BigWorld.callback(1, self.__requestLoop)

    if self.__isPaused:
      logger.debug('Request loop is paused')
      return
    
    if self.__isLoading:
      logger.debug('Request is still loading')
      return

    player = BigWorld.player() # type: PlayerAvatar

    if player is None or not hasattr(player, 'arena'):
      logger.debug('Player is not on arena')
      return
    
    if not self.__battleUUID:
      logger.debug('UUID is none')
      return

    vehicle = getPlayerVehicle(player)
    if vehicle is None:
      logger.debug('Player vehicle is None')
      return
    
    playerVehicleName = vehicle.typeDescriptor.name
    if self.__lastPlayerVehicle and self.__lastPlayerVehicle != playerVehicleName:
      logger.info('Clear old markers due vehicle changed')
      self.__drawer.clear()
      
      overlay = MinimapOverlay.instance()
      if overlay: overlay.clear()
      
      self.__lastPlayerVehicle = None
    
    battleTime = self.__battleTime()
    if battleTime <= -10002:
      logger.debug('Battle is still loading')
      return
    
    time = BigWorld.time()
    interval = max(10, settings.get(SettingsKeys.UPDATE_INTERVAL))
    delta = time - self.__lastRequestTime
    if delta < interval and playerVehicleName == self.__lastPlayerVehicle or delta < 10:
      return
    
    if not self.__drawer.isReady():
      self.__getDrawerReadyRetryCount += 1
      if self.__getDrawerReadyRetryCount < 20:
        return
    
    self.__lastRequestTime = time
    self.__lastPlayerVehicle = playerVehicleName

    arena = self.__arenaInfoProvider

    vehicles = BigWorld.player().arena.vehicles

    allyVehicles = [v['vehicleType'].type for v in [vehicles.get(v.vid, None) for v in arena.getAllyVehicles()] if (v and v['vehicleType'])]
    enemyVehicles =[v['vehicleType'].type for v in [vehicles.get(v.vid, None) for v in arena.getEnemyVehicles()] if (v and v['vehicleType'])]

    params = {
      'id': self.__battleUUID,
      'token': self.__licenseManager.getToken(),
      'license': self.__licenseCache,
      'player': player.name,
      'language': LANGUAGE,
      'region': AUTH_REALM,
      'mode': ARENA_TAGS[player.arena.bonusType],
      'gameplay': ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
      'arena': player.arena.arenaType.geometry,
      'team': player.team,
      'tank': playerVehicleName,
      'level': player.vehicleTypeDescriptor.level,
      'type': shortTankType(getTankType(player.vehicleTypeDescriptor.type.tags)),
      'role': getTankRole(player.vehicleTypeDescriptor.role),
      'health': max(0, float(vehicle.health) / vehicle.maxHealth),
      'position': {'x': int(player.position[0]), 'z': int(player.position[2])},
      'time': int(battleTime),
      'allyFrags': arena.allyTeamFragsCount,
      'enemyFrags': arena.enemyTeamFragsCount,
      'allyHealth': arena.allyTeamHealth[0],
      'enemyHealth': arena.enemyTeamHealth[0],
      'allyMaxHealth': arena.allyTeamHealth[1],
      'enemyMaxHealth': arena.enemyTeamHealth[1],
      'allyRoles': [getTankRole(v.role) for v in allyVehicles if v],
      'allyTypes': [shortTankType(getTankType(v.tags)) for v in allyVehicles if v],
      'allyLevels': [v.level for v in allyVehicles if v],
      'enemyRoles': [getTankRole(v.role) for v in enemyVehicles if v],
      'enemyTypes': [shortTankType(getTankType(v.tags)) for v in enemyVehicles if v],
      'enemyLevels': [v.level for v in enemyVehicles if v],
    }

    logger.info('Requesting positions: %s; for tank: %s, arena: %s, mode: %s' % (params['id'], params['tank'], params['arena'], params['mode']))
    self.__isLoading = True
    self.__api.requestPositions(params, self.__onResponse)

  @withExceptionHandling()
  def __onResponse(self, data):
    self.__isLoading = False
    
    if data.responseCode != 200:
      logger.error('Response status is not 200: %s' % data.responseCode)
      return

    body = data.body
    if not body:
      logger.error('Response body is empty')
      return
    
    parsed = None
    try:
      parsed = json.loads(body)
    except ValueError:
      logger.error('Response body is not a valid JSON: %s' % body)
      return
    
    token = parsed.get('token', None)
    if token is not None: 
      self.__licenseManager.setToken(token)
    
    message = parsed.get('message', None)
    if message is not None:
      mType = message.get('type', None)
      mValue = message.get('value', None)
      color = {
        'error': BATTLE_MESSAGES_CONSTS.COLOR_PURPLE,
        'info': BATTLE_MESSAGES_CONSTS.COLOR_GOLD,
        'warning': BATTLE_MESSAGES_CONSTS.COLOR_YELLOW
      }[mType] if mType in ('error', 'info', 'warning') else BATTLE_MESSAGES_CONSTS.COLOR_PURPLE

      logger.info('Server message: [%s] %s' % (mType, mValue))
      if mType != 'info' or settings.get(SettingsKeys.SHOW_INFO_MESSAGES):
        showPlayerMessage(mValue, color)

    notification = parsed.get('notification', None)
    if notification is not None:
      Notifier.instance().showNotificationFromData(notification)


    skipRedraw = False
    commands = parsed.get('commands', None)
    if commands is not None:
      if isinstance(commands, list):
        for c in commands:
          if c == Commands.PAUSE_REQUESTER:
            self.__isPaused = True
          elif c == Commands.RESUME_REQUESTER:
            self.__isPaused = False
          elif c == Commands.SKIP_REDRAW:
            skipRedraw = True
          elif c == Commands.RESET_DRAWER:
            self.__drawer.reset()

          self.onCommand(c)


    if not skipRedraw:
      self.__lastResponse = PositionsResponse(parsed)
      
      overlay = MinimapOverlay.instance()
      if overlay:
        overlay.setupHeatmap(self.__lastResponse.getHeatmap())
        overlay.setupPopularHeatmap(self.__lastResponse.getPopularHeatmap())
        overlay.setupSpotPoints(self.__lastResponse.getSpotPoints())
        
      self.__eyeDisplayProcessor.setupSpotPoints(self.__lastResponse.getSpotPoints())
        
      self.__redraw()
 
  def __redraw(self):
    if not self.__drawer.isReady():
      return
    
    self.__drawer.clear()

    if not self.__lastResponse: return
    if not settings.get(SettingsKeys.ENABLED): return
    if not self.__isEnable: return

    response = self.__lastResponse
    
    overlay = MinimapOverlay.instance()

    if self.__shouldDraw(SettingsKeys.SHOW_MINIMAP_MARKERS):
      self.__drawer.drawPoints(response.getPoints())
      self.__drawer.drawIdealPoints(response.getIdealPoints())

    if self.__shouldDraw(SettingsKeys.SHOW_IDEAL_MARKER):
      self.__drawer.drawMarkers3D(response.getIdealPoints())

    if self.__shouldDraw(SettingsKeys.SHOW_ALL_MARKERS_3D):
      self.__drawer.drawMarkers3D(response.getPoints())

      if not self.__shouldDraw(SettingsKeys.SHOW_IDEAL_MARKER):
        self.__drawer.drawMarkers3D(response.getIdealPoints())
    
    self.__eyeDisplayProcessor.setVisibility(self.__shouldDraw(SettingsKeys.SHOW_EYE_MARKERS))
    self.__eyeDisplayProcessor.redraw()
    
    if overlay:
      overlay.setHeatmapVisible(self.__shouldDraw(SettingsKeys.SHOW_HEATMAP))
      overlay.setPopularHeatmapVisible(self.__shouldDraw(SettingsKeys.SHOW_POPULAR_HEATMAP))
      overlay.setVehicleShouldDropSpotRays(settings.get(SettingsKeys.VEHICLE_SPOT_RAYS))
      overlay.setMouseShouldDropSpotRays(settings.get(SettingsKeys.MOUSE_SPOT_RAYS))
      overlay.setSpotPointsVisible(self.__overlayMode(SettingsKeys.SHOW_SPOT_POINTS))
      overlay.setMiniSpotPointsVisible(self.__overlayMode(SettingsKeys.SHOW_MINI_SPOT_POINTS))
      

  def __shouldDraw(self, key):
    variant = settings.get(key)
    return variant == ShowVariants.ALWAYS or \
      (variant == ShowVariants.ON_ALT and self.__altPressed)
      
  def __overlayMode(self, key):
    variant = settings.get(key)
    
    if variant == OverlayShowVariants.ALWAYS:
      return OverlayVisibilityMode.ALWAYS
    
    if variant == OverlayShowVariants.ON_ALT and self.__altPressed:
      return OverlayVisibilityMode.ALWAYS
    
    if variant == OverlayShowVariants.MOUSE_OVER:
      return OverlayVisibilityMode.MOUSE_OVER
    
    return OverlayVisibilityMode.NEVER

  def __onArenaPeriodChange(self, obj, period, periodEndTime, periodLength, *a, **k):
    if period is ARENA_PERIOD.BATTLE:
      self.__startBattleTime = periodEndTime - periodLength

  def __battleTime(self):
    player = BigWorld.player()

    if not hasattr(player, 'arena'):
      return -10003

    return {
      ARENA_PERIOD.IDLE: -10001,
      ARENA_PERIOD.WAITING: -10000,
      ARENA_PERIOD.PREBATTLE: BigWorld.serverTime() - player.arena.periodEndTime,
      ARENA_PERIOD.BATTLE: BigWorld.serverTime() - self.__startBattleTime,
      ARENA_PERIOD.AFTERBATTLE: BigWorld.serverTime() - self.__startBattleTime
    }.get(player.arena.period, -10002)

class PositionsResponse(object):
  def __init__(self, data):
    self.data = data
    self.positions = data.get('positions', None)

  def getPoints(self):
    if not self.positions: return []

    if 'points' not in self.positions:
      return []
    
    points = self.positions['points']
    return PositionsResponse.__parsePointsList(points)
  
  def getIdealPoints(self):
    if not self.positions: return []

    if 'idealPoints' not in self.positions:
      return []
    
    points = self.positions['idealPoints']
    return PositionsResponse.__parsePointsList(points)

  def getHeatmap(self):
    return self.__parseHeatmap('heatmap')
  
  def getPopularHeatmap(self):
    return self.__parseHeatmap('popularHeatmap')
  
  def getSpotPoints(self):
    if not self.positions: return Spots([])
    
    points = self.positions.get('spotPoints', None)
    if not points: return Spots([])
    
    if not isinstance(points, list): return Spots([])
    
    parsed = []
    
    for point in points:
      p = point.get('point', None)
      if not p: continue
      
      hits = point.get('hits', None)
      if not hits: continue
      
      if not isinstance(p, list) or len(p) != 3: continue
      if not isinstance(hits, list): continue
      
      parsedHits = []
      for hit in hits:
        if not isinstance(hit, list) or len(hit) != 3: continue
        parsedHits.append((float(hit[0]), float(hit[1]), float(hit[2])))
        
      parsed.append(Spots.Point((float(p[0]), float(p[1]), float(p[2])), parsedHits))
      
    return Spots(parsed)
  
  def __parseHeatmap(self, name):
    if not self.positions: return Heatmap([], 0)
    
    heatmap = self.positions.get(name, None)
    if not heatmap: return Heatmap([], 0)
    
    points = heatmap.get('data', None)
    if not isinstance(points, list): return Heatmap([], 0)
    
    parsed = []
    
    for point in points:
      if not isinstance(point, list) or len(point) != 3: continue
      parsed.append([float(point[0]), float(point[1]), float(point[2])])
      
    return Heatmap(parsed, heatmap.get('step', 0))

  @staticmethod
  def __parsePointsList(points):
    if not isinstance(points, list):
      return []
    
    parsed = []

    for point in points:
      parsedPoint = PositionsResponse.__pasrePoint(point)
      if parsedPoint is not None:
        parsed.append(parsedPoint)

    return parsed
  
  @staticmethod
  def __pasrePoint(point):
    if 'efficiency' not in point or 'position' not in point:
      return None
    
    pos = point['position']
    x = float(pos[0])
    y = float(pos[1])

    return PositionPoint(point['efficiency'], (x, y))