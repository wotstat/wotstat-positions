from typing import Any # noqa: F401

import BigWorld
from Vehicle import Vehicle # noqa: F401
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

from ..common.Logger import Logger
from ..common.ExceptionHandling import withExceptionHandling
from .WotHookEvents import wotHookEvents


logger = Logger.instance()

class VehicleInfo():
  def __init__(self, vid, health, maxHealth, team):
    self.vid = vid
    self.health = health
    self.maxHealth = maxHealth
    self.team = team

  def updateHealth(self, health):
    target = max(0, health)
    if self.health == target: return False
    self.health = target
    return True

  def isAlive(self):
    return self.health > 0

class ArenaInfoProvider():
  vehicles = {}  # type: dict[int, VehicleInfo]
  playerTeam = -1

  __arena = None

  allyTeamHealth = [0, 0]
  enemyTeamHealth = [0, 0]
  allyTeamFragsCount = 0
  enemyTeamFragsCount = 0

  __sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider

  def __init__(self):
    wotHookEvents.Avatar_onBecomePlayer += self.__start
    wotHookEvents.Avatar_onBecomeNonPlayer += self.__stop
    wotHookEvents.Vehicle_onEnterWorld += self.__onVehicleEnter
    wotHookEvents.Vehicle_onHealthChanged += self.__onHealthChanged
    self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
    self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop

  def __start(self, *a, **k):

    def waitVehicles():
      vehicles = BigWorld.player().arena.vehicles.items()
      if len(vehicles) == 0:
        BigWorld.callback(0.1, waitVehicles)
        return

      for vid, v in vehicles:
        if vid not in self.vehicles:
          self.__tryUpdateVehicle(vid, v['maxHealth'], v['maxHealth'])

    waitVehicles()

  def __stop(self, *a, **k):
    self.vehicles = {}
    self.playerTeam = -1
    self.allyTeamFragsCount = 0
    self.enemyTeamFragsCount = 0
    self.allyTeamHealth = [0, 0]
    self.enemyTeamHealth = [0, 0]

  @withExceptionHandling()
  def __onBattleSessionStart(self):
    arena = BigWorld.player().arena
    arena.onVehicleAdded += self.__onVehicleAdded
    arena.onVehicleUpdated += self.__vehicleUpdated
    arena.onVehicleKilled += self.__onVehicleKilled
    self.__arena = arena

  @withExceptionHandling()
  def __onBattleSessionStop(self):
    arena = self.__arena
    if arena is None: return
    arena.onVehicleAdded -= self.__onVehicleAdded
    arena.onVehicleUpdated -= self.__vehicleUpdated
    arena.onVehicleKilled -= self.__onVehicleKilled
    self.__arena = None

  def __onVehicleEnter(self, obj, *a, **k):
    # type: (Vehicle, Any, Any) -> None
    self.__tryUpdateVehicle(obj.id, obj.health, obj.maxHealth)

  def __onHealthChanged(self, obj, newHealth, *a, **k):
    # type: (Vehicle, float, Any, Any) -> None
    self.__tryUpdateVehicle(obj.id, newHealth, obj.maxHealth)

  def __tryUpdateVehicle(self, vid, health, maxHealth=None):
    if vid not in self.vehicles:
      player = BigWorld.player()
      info = player.arena.vehicles[vid] if vid in player.arena.vehicles else None
      if info is not None:
        self.vehicles[vid] = VehicleInfo(vid, health, maxHealth if maxHealth else info['maxHealth'], info['team'])
      else:
        logger.warn("ArenaInfoProvider: TryUpdateVehicle unknown vehicle")

      self.__calculateTeamHealth()
    else:
      if self.vehicles[vid].updateHealth(health):
        self.__calculateTeamHealth()

  @withExceptionHandling()
  def __onVehicleAdded(self, vehicleID):
    vehicle = BigWorld.entity(vehicleID)
    if vehicle is None: return
    self.__tryUpdateVehicle(vehicleID, vehicle.health)

  @withExceptionHandling()
  def __vehicleUpdated(self, vehicleID):
    vehicle = BigWorld.entity(vehicleID)
    if vehicle is None: return
    self.__tryUpdateVehicle(vehicleID, vehicle.health)

  @withExceptionHandling()
  def __onVehicleKilled(self, targetID, *a, **k):
    self.__tryUpdateVehicle(targetID, 0)
    if targetID in self.vehicles:
      team = self.vehicles[targetID].team
      if team == self.playerTeam:
        self.enemyTeamFragsCount += 1
      else:
        self.allyTeamFragsCount +=1

  def __calculateTeamHealth(self):
    self.allyTeamHealth = [0, 0]
    self.enemyTeamHealth = [0, 0]

    if self.playerTeam == -1:
      self.playerTeam = BigWorld.player().team

    for v in self.vehicles.values():
      if v.team == self.playerTeam:
        self.allyTeamHealth[0] += max(0, v.health)
        self.allyTeamHealth[1] += max(0, v.maxHealth)
      else:
        self.enemyTeamHealth[0] += max(0, v.health)
        self.enemyTeamHealth[1] += max(0, v.maxHealth)

  def getAllyVehicles(self):
    return [v for v in self.vehicles.values() if v.team == self.playerTeam]
  
  def getEnemyVehicles(self):
    return [v for v in self.vehicles.values() if v.team != self.playerTeam]