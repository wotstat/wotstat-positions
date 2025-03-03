from math import sqrt
from typing import Tuple
import BigWorld
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from frameworks.wulf import WindowLayer
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.application import AppEntry
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from Avatar import PlayerAvatar

from ..common.Settings import Settings, SettingsKeys, HeatmapLimitVariants
from ..common.Logger import Logger
from .utils import getPlayerVehicle
from ..common.ExceptionHandling import withExceptionHandling
from . import Spots, Heatmap

logger = Logger.instance()

minimapOverlayInstance = None # type: MinimapOverlay

class OverlayVisibilityMode:
  ALWAYS = 'ALWAYS'
  MOUSE_OVER = 'MOUSE_OVER'
  NEVER = 'NEVER'

HEATMAP_LIMIT_VALUES = {
  HeatmapLimitVariants.SMALL: 1000,
  HeatmapLimitVariants.MEDIUM: 5000,
  HeatmapLimitVariants.LARGE: 10000,
  HeatmapLimitVariants.UNLIMITED: -1
}

settings = Settings.instance()

class MinimapOverlay(View):
  
  @staticmethod
  def instance():
    return minimapOverlayInstance
  
  def _populate(self):
    super(MinimapOverlay, self)._populate()
    
    global minimapOverlayInstance
    minimapOverlayInstance = self
    
    self.lastPlayerPosition = None
    self.updatePlayerPositionLoopTimer = None
    
    heatmapLimit = settings.get(SettingsKeys.HEATMAP_LIMIT)
    self.as_setHeatmapLimit(HEATMAP_LIMIT_VALUES.get(heatmapLimit, -1))
    
    self.updatePlayerPositionLoop()
    
  def _destroy(self):
    global minimapOverlayInstance
    minimapOverlayInstance = None
    
    if self.updatePlayerPositionLoopTimer:
      BigWorld.cancelCallback(self.updatePlayerPositionLoopTimer)
      self.updatePlayerPositionLoopTimer = None
      
    return super(MinimapOverlay, self)._destroy()
  
  @withExceptionHandling()
  def setupSpotPoints(self, spots):
    # type: (Spots) -> None
    minBounds, maxBounds = BigWorld.player().arena.getArenaBB()
    width = maxBounds[0] - minBounds[0]
    height = maxBounds[2] - minBounds[2]
    
    points = []
    for spot in spots.points:
      x = (spot.position[0] - minBounds[0]) / width
      y = (spot.position[1] - minBounds[2]) / height
      hits = []
      for hit in spot.hits:
        hitX = (hit[0] - minBounds[0]) / width
        hitY = (hit[1] - minBounds[2]) / height
        hits.append((hitX, hitY, hit[2]))
      
      points.append({ 'position': (x, y, spot.position[2]), 'hits': hits })
      
    self.as_setupSpotPoints(points)
  
  @withExceptionHandling()
  def setupHeatmap(self, heatmap):
    # type: (Heatmap) -> None
    x, y, weight, multiplier = self.prepareHeatmap(heatmap)
    self.as_setupHeatmap(x, y, weight, multiplier)
  
  @withExceptionHandling()
  def setupPopularHeatmap(self, heatmap):
    # type: (Heatmap) -> None
    x, y, weight, multiplier = self.prepareHeatmap(heatmap)
    self.as_setupPopularHeatmap(x, y, weight, multiplier)
  
  @withExceptionHandling()
  def clear(self):
    self.as_clear()
  
  @withExceptionHandling()
  def prepareHeatmap(self, heatmap):
    # type: (Heatmap) -> Tuple[list, list, list]
    minBounds, maxBounds = BigWorld.player().arena.getArenaBB()
    
    x = []
    y = []
    weight = []
    
    width = maxBounds[0] - minBounds[0]
    height = maxBounds[2] - minBounds[2]
    for x_, y_, w in heatmap.points:
      x.append((x_ - minBounds[0]) / width)
      y.append((y_ - minBounds[2]) / height)
      weight.append(w)
    
    multiplier = heatmap.step / max(width, height)
    return x, y, weight, multiplier

  @withExceptionHandling()
  def updatePlayerPositionLoop(self):
    self.updatePlayerPositionLoopTimer = BigWorld.callback(0.1, self.updatePlayerPositionLoop)
    
    player = BigWorld.player() # type: PlayerAvatar
    if not player: return
    if not hasattr(player, 'arena'): return
    if not player.arena: return
    if not hasattr(player, 'getOwnVehiclePosition'): return
    
    
    minBounds, maxBounds = player.arena.getArenaBB()
    
    if not getPlayerVehicle(player): return
    if not player.isOnArena: return
    
    (x, _, z) = player.getOwnVehiclePosition()
    
    if self.lastPlayerPosition:
      lastX, lastZ = self.lastPlayerPosition
      distance = sqrt((x - lastX) ** 2 + (z - lastZ) ** 2)
      if distance < 0.5: return
      
    self.lastPlayerPosition = (x, z)
    
    width = maxBounds[0] - minBounds[0]
    height = maxBounds[2] - minBounds[2]
    
    x = (x - minBounds[0]) / width
    y = (z - minBounds[2]) / height
    
    self.as_setRelativeVehiclePosition(x, y)
  
  def setHeatmapVisible(self, visible):
    self.as_setHeatmapVisible(visible)
    
  def setPopularHeatmapVisible(self, visible):
    self.as_setPopularHeatmapVisible(visible)
    
  def setSpotPointsVisible(self, mode):
    self.as_setSpotPointsVisible(mode)
    
  def setMiniSpotPointsVisible(self, mode):
    self.as_setMiniSpotPointsVisible(mode)
    
  def setVehicleShouldDropSpotRays(self, enabled):
    self.as_setVehicleShouldDropSpotRays(enabled)
    
  def setMouseShouldDropSpotRays(self, enabled):
    self.as_setMouseShouldDropSpotRays(enabled)

  def py_log(self, message):
    logger.info(message)

  def as_setupSpotPoints(self, points):
    self.flashObject.as_setupSpotPoints(points)
    
  def as_setupHeatmap(self, x, y, weight, multiplier):
    self.flashObject.as_setupHeatmap(x, y, weight, multiplier)
    
  def as_setupPopularHeatmap(self, x, y, weight, multiplier):
    self.flashObject.as_setupPopularHeatmap(x, y, weight, multiplier)
    
  def as_setRelativeVehiclePosition(self, x, y):
    self.flashObject.as_setRelativeVehiclePosition(x, y)
  
  def as_clear(self):
    self.flashObject.as_clear()
    
  def as_setHeatmapVisible(self, visible):
    self.flashObject.as_setHeatmapVisible(visible)
    
  def as_setPopularHeatmapVisible(self, visible):
    self.flashObject.as_setPopularHeatmapVisible(visible)
    
  def as_setSpotPointsVisible(self, mode):
    self.flashObject.as_setSpotPointsVisible(mode)
    
  def as_setMiniSpotPointsVisible(self, mode):
    self.flashObject.as_setMiniSpotPointsVisible(mode)
    
  def as_setVehicleShouldDropSpotRays(self, enabled):
    self.flashObject.as_setVehicleShouldDropSpotRays(enabled)
    
  def as_setMouseShouldDropSpotRays(self, enabled):
    self.flashObject.as_setMouseShouldDropSpotRays(enabled)
    
  def as_setHeatmapLimit(self, limit):
    self.flashObject.as_setHeatmapLimit(limit)
    
    

OVERLAY_VIEW = "WOTSTAT_POSITIONS_MINIMAP_OVERLAY_VIEW"
def setup():
  mainViewSettings = ViewSettings(
    OVERLAY_VIEW,
    MinimapOverlay,
    "wotstat.positions.swf",
    WindowLayer.SERVICE_LAYOUT,
    None,
    ScopeTemplates.GLOBAL_SCOPE,
  )
  g_entitiesFactories.addSettings(mainViewSettings)


  def onAppInitialized(event):
    logger.info("App initialized: %s" % event.ns)

    if event.ns == APP_NAME_SPACE.SF_BATTLE:
      app = ServicesLocator.appLoader.getApp(event.ns) # type: AppEntry
      if not app:
        logger.error("App not found")
        return
      
      logger.info("Load overlay view")
      app.loadView(SFViewLoadParams(OVERLAY_VIEW))

  g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
