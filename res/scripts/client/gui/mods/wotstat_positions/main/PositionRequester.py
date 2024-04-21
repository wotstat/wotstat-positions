import json
import uuid

import BigWorld # type: ignore
from Vehicle import Vehicle
from constants import ARENA_BONUS_TYPE, ARENA_GAMEPLAY_NAMES, AUTH_REALM, ARENA_PERIOD
from gui.Scaleform.genConsts.BATTLE_MESSAGES_CONSTS import BATTLE_MESSAGES_CONSTS
from helpers import getClientLanguage
from gui import InputHandler
import Keys

from ..common.Logger import Logger
from ..common.Settings import Settings, SettingsKeys, ShowVariants
from ..common.ExeptionHandling import withExceptionHandling
from ..common.BattleMessages import showPlayerMessage
from .utils import shortTankType, getTankType, getTankRole
from .WotHookEvents import wotHookEvents
from .ArenaInfoProvider import ArenaInfoProvider
from . import IPositionDrawer, IPositionRequester, PositionPoint, PositionArea  # noqa: F401

logger = Logger.instance()
settings = Settings.instance()
ARENA_TAGS = dict([(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])
LANGUAGE = getClientLanguage()

JSON_HEADERS = {'Content-Type': 'application/json'}

def getPlayerVehicle(player=BigWorld.player()):

  if hasattr(player, 'vehicle') and player.vehicle is not None:
    return player.vehicle

  if hasattr(player, 'playerVehicleID') and player.playerVehicleID is not None:
    entity = BigWorld.entity(player.playerVehicleID)
    if entity is not None and isinstance(entity, Vehicle) and entity.isPlayerVehicle:
      return entity

  return None

class PositionRequester(IPositionRequester):


  def __init__(self, serverUrl, drawer):
    # type: (str, IPositionDrawer) -> None

    self.__drawer = drawer
    self.__serverUrl = serverUrl
    self.__lastRequestTime = 0

    self.__arenaInfoProvider = ArenaInfoProvider()

    self.__callbackID = None
    self.__isEnable = False
    self.__lastResponse = None # type: PositionsResponse
    self.__altPressed = False

    self.__battleUUID = None
    self.__currentToken = ''

    wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.__onArenaPeriodChange
    settings.onSettingsChanged += self.__onSettingsChanged
    InputHandler.g_instance.onKeyDown += self.__onKey
    InputHandler.g_instance.onKeyUp += self.__onKey
      
  def start(self):
    self.__isEnable = True
    self.__lastRequestTime = 0
    self.__lastResponse = None
    self.__battleUUID = str(uuid.uuid4())

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
    if not self.__isEnable:
      logger.debug('Request loop is not enabled')
      return
    
    self.__callbackID = BigWorld.callback(1, self.__requestLoop)

    player = BigWorld.player()

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
    
    battleTime = self.__battleTime()
    if battleTime <= -10000:
      logger.debug('Battle is still loading')
      return
    
    time = BigWorld.time()
    interval = settings.get(SettingsKeys.UPDATE_INTERVAL)
    interval = 5 if interval < 5 else interval
    if time - self.__lastRequestTime < interval:
      return
    self.__lastRequestTime = time

    arena = self.__arenaInfoProvider

    vehicles = BigWorld.player().arena.vehicles

    allyVehicles = [v['vehicleType'].type for v in [vehicles.get(v.vid, None) for v in arena.getAllyVehicles()] if v]
    enemyVehicles =[v['vehicleType'].type for v in [vehicles.get(v.vid, None) for v in arena.getEnemyVehicles()] if v]

    params = {
      'id': self.__battleUUID,
      'token': self.__currentToken,
      'language': LANGUAGE,
      'region': AUTH_REALM,
      'mode': ARENA_TAGS[player.arena.bonusType],
      'gameplay': ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
      'arena': player.arena.arenaType.geometry,
      'team': player.team,
      'tank': BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
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

    BigWorld.fetchURL(self.__serverUrl + '/positions', self.__onResponse, headers=JSON_HEADERS, method='POST', postData=json.dumps(params))

  @withExceptionHandling()
  def __onResponse(self, data):
    
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

    if 'token' in parsed:
      self.__currentToken = parsed['token']
    
    if data.responseCode != 200:
      logger.error('Response status is not 200: %s' % data.responseCode)
      return

    self.__lastResponse = PositionsResponse(parsed)
    self.__redraw()
  
  def __redraw(self):
    self.__drawer.clear()

    if not self.__lastResponse: return
    if not settings.get(SettingsKeys.ENABLED): return
    if not self.__isEnable: return

    response = self.__lastResponse
    
    if self.__shouldDraw(SettingsKeys.SHOW_AREA):
      self.__drawer.drawPolygons(response.getPolygons())

    if self.__shouldDraw(SettingsKeys.SHOW_MINI_MARKERS):
      self.__drawer.drawPoints(response.getPoints())

    if self.__shouldDraw(SettingsKeys.SHOW_IDEAL_MARKER):
      self.__drawer.drawIdealPoints(response.getIdealPoints())

  def __shouldDraw(self, key):
    variant = settings.get(key)
    return variant == ShowVariants.ALWAYS or \
      (variant == ShowVariants.ON_ALT and self.__altPressed)

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
    self.__data = data

  def getPoints(self):
    if 'positions' not in self.__data:
      return []
    
    positions = self.__data['positions']

    if 'points' not in positions:
      return []
    
    points = positions['points']
    return PositionsResponse.__parsePointsList(points)
  
  def getIdealPoints(self):
    if 'positions' not in self.__data:
      return []
    
    positions = self.__data['positions']

    if 'idealPoints' not in positions:
      return []
    
    points = positions['idealPoints']
    return PositionsResponse.__parsePointsList(points)
  
  def getPolygons(self):
    if 'positions' not in self.__data:
      return []
    
    positions = self.__data['positions']

    if 'polygons' not in positions:
      return []
    
    polygons = positions['polygons']
    if not isinstance(polygons, list):
      return []
    
    parsed = []

    for polygon in polygons:
      if 'efficiency' not in polygon or 'area' not in polygon:
        continue

      area = polygon['area']
      if not isinstance(area, list):
        continue

      parsedArea = []
      for point in area:
        if not isinstance(point, list) or len(point) != 2:
          continue

        x = float(point[0])
        y = float(point[1])
        parsedArea.append((x, y))

      parsed.append(PositionArea(polygon['efficiency'], parsedArea))
      
    return parsed

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