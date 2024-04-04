import json

import BigWorld # type: ignore
from Vehicle import Vehicle
from constants import ARENA_BONUS_TYPE, ARENA_GAMEPLAY_NAMES, AUTH_REALM, ARENA_PERIOD

from ..common.Logger import Logger
from ..common.ExeptionHandling import withExceptionHandling
from .utils import short_tank_type, get_tank_type, get_tank_role
from .WotHookEvents import wotHookEvents
from . import IPositionDrawer, IPositionRequester, PositionPoint, PositionArea  # noqa: F401

logger = Logger.instance()
ARENA_TAGS = dict([(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])

def getPlayerVehicle(player=BigWorld.player()):

  if hasattr(player, 'vehicle') and player.vehicle is not None:
    return player.vehicle

  if hasattr(player, 'playerVehicleID') and player.playerVehicleID is not None:
    entity = BigWorld.entity(player.playerVehicleID)
    if entity is not None and isinstance(entity, Vehicle) and entity.isPlayerVehicle:
      return entity

  return None

class PositionRequester(IPositionRequester):

  def __init__(self, serverUrl, requestPeriod, drawer):
    # type: (str, int, IPositionDrawer) -> None

    self.__drawer = drawer
    self.__serverUrl = serverUrl
    self.__requestPeriod = requestPeriod
    self.__lastRequestTime = 0

    self.__callbackID = None
    self.__isEnable = False

    wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.__onArenaPeriodChange
      
  def start(self):
    self.__isEnable = True
    self.__lastRequestTime = 0

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
  def __requestLoop(self):
    if not self.__isEnable:
      logger.debug('Request loop is not enabled')
      return
    
    self.__callbackID = BigWorld.callback(1, self.__requestLoop)

    player = BigWorld.player()

    if player is None or not hasattr(player, 'arena'):
      logger.debug('Player is not on arena')
      return
    
    vehicle = getPlayerVehicle(player)
    if vehicle is None:
      logger.debug('Player vehicle is None')
      return
    
    time = BigWorld.time()
    if time - self.__lastRequestTime < self.__requestPeriod:
      return
    self.__lastRequestTime = time

    params = {
      'region': AUTH_REALM,
      'mode': ARENA_TAGS[player.arena.bonusType],
      'gameplay': ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
      'arena': player.arena.arenaType.geometry,
      'team': player.team,
      'tank': BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
      'level': player.vehicleTypeDescriptor.level,
      'type': short_tank_type(get_tank_type(player.vehicleTypeDescriptor.type.tags)),
      'role': get_tank_role(player.vehicleTypeDescriptor.role),
      'health': float(vehicle.health) / vehicle.maxHealth,
      'position': '(%s;%s)' % (int(player.position[0]), int(player.position[2])),
      'time': int(self.__battle_time()),
      'allyfrags': 0,
      'enemyfrags': 0,
    }

    targetUrl = self.__serverUrl + '/positions?' + '&'.join(['%s=%s' % (k, v) for k, v in params.items()])

    BigWorld.fetchURL(targetUrl, self.__onResponse)

  @withExceptionHandling()
  def __onResponse(self, data):
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
    
    response = PositionsResponse(parsed)
    
    self.__drawer.clear()
    self.__drawer.drawPolygons(response.getPolygons())
    self.__drawer.drawPoints(response.getPoints())
    self.__drawer.drawIdealPoints(response.getIdealPoints())
    
  def __onArenaPeriodChange(self, obj, period, periodEndTime, periodLength, *a, **k):
    if period is ARENA_PERIOD.BATTLE:
      self.__startBattleTime = periodEndTime - periodLength

  def __battle_time(self):
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