import BigWorld
from Vehicle import Vehicle
from constants import ARENA_BONUS_TYPE, ARENA_GAMEPLAY_NAMES, AUTH_REALM, ARENA_PERIOD
from urllib import urlencode

from ..common.Logger import Logger
from ..common.ExeptionHandling import withExceptionHandling
from .utils import short_tank_type, get_tank_type, get_tank_role
from .WotHookEvents import wotHookEvents
from . import IPositionDrawer, IPositionRequester

logger = Logger.instance()
ARENA_TAGS = dict([(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])

def getPlayerVehicle():
  player = BigWorld.player()

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

    self.drawer = drawer
    self.serverUrl = serverUrl
    self.__callbackID = None
    self.__isEnable = False

    wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.__onArenaPeriodChange
      
  def start(self):
    self.__isEnable = True

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
    if self.__callbackID is not None:
      BigWorld.cancelCallback(self.__callbackID)

  @withExceptionHandling()
  def __requestLoop(self):
    if not self.__isEnable:
      logger.debug('Request loop is not enabled')
      return
    
    self.__callbackID = BigWorld.callback(5, self.__requestLoop)

    player = BigWorld.player()

    if player is None or not hasattr(player, 'arena'):
      logger.debug('Player is not on arena')
      return
    
    vehicle = getPlayerVehicle()
    if vehicle is None:
      logger.debug('Player vehicle is None')
      return

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
      'position': '(%s;%s)' % (player.position[0], player.position[2]),
      'time': int(self.__battle_time() / 1000),
      'allyfrags': 0,
      'enemyfrags': 0,
    }

    logger.debug('Requesting positions: \n%s' % params)

    targetUrl = self.serverUrl + '/positions?' + '&'.join(['%s=%s' % (k, v) for k, v in params.items()])

    BigWorld.fetchURL(targetUrl, self.__onResponse)

  @withExceptionHandling()
  def __onResponse(self, data):
    logger.debug('Response: %s' % data.body)

    self.drawer.clear()

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
