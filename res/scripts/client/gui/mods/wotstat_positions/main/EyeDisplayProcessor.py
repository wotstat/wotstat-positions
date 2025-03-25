import BigWorld # noqa: F401
from math import sqrt
from Avatar import PlayerAvatar

from . import IPositionDrawer, Spots # noqa: F401
from .utils import getPlayerVehicle
from ..common.Logger import Logger
from ..common.ExceptionHandling import withExceptionHandling


logger  = Logger.instance()

class EyeDisplayProcessor(object):
  
  def __init__(self, drawer):
    # type: (IPositionDrawer) -> None
    self.drawer = drawer
    self.currentSpot = None
    self.visible = False
    self.spots = None
    self.updatePlayerPositionLoopTimer = None
    self.updatePlayerPositionLoop()
  
  @withExceptionHandling()
  def setupSpotPoints(self, points):
    # type: (Spots) -> None
    self.spots = points
  
  @withExceptionHandling()
  def updatePlayerPositionLoop(self):
    self.updatePlayerPositionLoopTimer = BigWorld.callback(0.1, self.updatePlayerPositionLoop)
    
    if not self.spots: return
    
    player = BigWorld.player() # type: PlayerAvatar
    if not player: return
    if not hasattr(player, 'arena'): return
    if not player.arena: return
    if not hasattr(player, 'getOwnVehiclePosition'): return
    
    if not getPlayerVehicle(player): return
    if not player.isOnArena: return
    
    (x, _, z) = player.getOwnVehiclePosition()
    
    nearestSpot = None
    nearestDist = 1e9
    
    for spot in self.spots.points:
      dist = sqrt((spot.position[0] - x) ** 2 + (spot.position[1] - z) ** 2)
      if nearestSpot is None or dist < nearestDist:
        nearestSpot = spot
        nearestDist = dist
    
    target = nearestSpot if nearestDist < 30 else None
    self.updateCurrentSpot(target)
    
  @withExceptionHandling()
  def updateCurrentSpot(self, spot):
    # type: (Spots.Point) -> None
    if spot == self.currentSpot: return
    
    self.currentSpot = spot
    self.redraw()
    
  @withExceptionHandling()
  def setVisibility(self, visible):
    if self.visible == visible: return
    
    self.visible = visible
    self.redraw()
    
  @withExceptionHandling()  
  def redraw(self):
    self.drawer.drawEyeMarkers([self.currentSpot] if self.visible and self.currentSpot else [])
    
    
    
  