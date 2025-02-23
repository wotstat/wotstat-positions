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

from ..common.Logger import Logger
from . import Spots, Heatmap

logger = Logger.instance()

minimapOverlayInstance = None # type: MinimapOverlay

class MinimapOverlay(View):
  
  @staticmethod
  def instance():
    return minimapOverlayInstance
  
  def _populate(self):
    super(MinimapOverlay, self)._populate()
    
    global minimapOverlayInstance
    minimapOverlayInstance = self
    logger.info("MinimapOverlay populate")
    
  def _destroy(self):
    global minimapOverlayInstance
    minimapOverlayInstance = None
    return super(MinimapOverlay, self)._destroy()
  
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
  
  def setupHeatmap(self, heatmap):
    # type: (Heatmap) -> None
    x, y, weight, multiplier = self.prepareHeatmap(heatmap)
    self.as_setupHeatmap(x, y, weight, multiplier)
  
  def setupPopularHeatmap(self, heatmap):
    # type: (Heatmap) -> None
    x, y, weight, multiplier = self.prepareHeatmap(heatmap)
    self.as_setupPopularHeatmap(x, y, weight, multiplier)
  
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

  def py_log(self, message):
    logger.info(message)

  def as_setupSpotPoints(self, points):
    self.flashObject.as_setupSpotPoints(points)
    
  def as_setupHeatmap(self, x, y, weight, multiplier):
    self.flashObject.as_setupHeatmap(x, y, weight, multiplier)
    
  def as_setupPopularHeatmap(self, x, y, weight, multiplier):
    self.flashObject.as_setupPopularHeatmap(x, y, weight, multiplier)
  
  def as_clear(self):
    self.flashObject.as_clear()

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
