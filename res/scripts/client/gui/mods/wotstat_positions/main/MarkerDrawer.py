from typing import List

import BigWorld
from gui.shared.personality import ServicesLocator
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.battle.shared.minimap import settings, plugins
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from frameworks.wulf import WindowLayer
from Math import Vector3
from gui.battle_control import minimap_utils

from ..common.Logger import Logger
from . import IPositionDrawer, PositionPoint  # noqa: F401

logger = Logger.instance()

class MarkerDrawer(IPositionDrawer):
  __minimap = None
  __markers = {
    settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER: []
  }
  __freeMarkers = {
    settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER: []
  }

  def __init__(self):
    pass

  def drawPoints(self, points):
    # type: (List[PositionPoint]) -> None
    
    for point in points:
      position = point.position
      efficiency = point.efficiency
      marker = self.__createMarker((position[0], 0, position[1]), settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER, settings.CONTAINER_NAME.ICONS)
      if marker:
        marker.setScale(efficiency)

  def drawPolygons(self, polygons):
    pass

  def drawIdealPoints(self, points):
    pass

  def clear(self):
    for key, value in self.__markers.items():
      for marker in value:
        marker.setActive(False)

      self.__freeMarkers[key] = list(value)

  def reset(self):
    for key in self.__markers.keys():
      self.__markers[key] = []
      self.__freeMarkers[key] = []

    self.__minimap = None

  def __createMarker(self, position, markerType, contaier, scale=1.0):

    markers = self.__freeMarkers[markerType]
    if len(markers) > 0:
      marker = markers.pop()
      marker.setPosition(position)
      marker.setScale(scale)
      marker.setActive(True)
      return marker

    if not self.__minimap or not self.__minimap.isCreated():
      battle = ServicesLocator.appLoader.getDefBattleApp()
      if not battle:
        self.__minimap = None
        return
    
      view = battle.containerManager.getContainer(WindowLayer.VIEW).getView()
      if not view:
        self.__minimap = None
        return
      
      self.__minimap = view.components[BATTLE_VIEW_ALIASES.MINIMAP]

    if not self.__minimap:
      return

    markerScales = [0.8, 1.1]
    minimapSizeIndex = settings.clampMinimapSizeIndex(AccountSettings.getSettings('minimapSize'))

    p = float(minimapSizeIndex - plugins._MINIMAP_MIN_SCALE_INDEX) / float(plugins._MINIMAP_MAX_SCALE_INDEX - plugins._MINIMAP_MIN_SCALE_INDEX)
    baseScale = p * markerScales[0] + (1 - p) * markerScales[1]

    logger.info('Create new marker: %s' % str(position))
    marker = Marker(position, markerType, contaier, scale, self.__minimap, baseScale)
    self.__markers[markerType].append(marker)

    return marker

class Marker():
  def __init__(self, position, markerType, container, scale, minimap, baseScale):
    # type: ((float, float, float), str, str, float, plugins.MinimapPlugin, float) -> None
    self.__position = position
    self.__markerType = markerType
    self.__container = container
    self.__minimap = minimap
    self.__baseScale = baseScale
    self.__scale = scale

    self.handle = self.__minimap.addEntry(self.__markerType, self.__container, self.__createMatrix(),
                                          active=True, transformProps=settings.TRANSFORM_FLAG.FULL)

  def setPosition(self, position):
    # type: ((float, float, float)) -> None
    self.__position = position
    self.__minimap.setMatrix(self.handle, self.__createMatrix())
    
  def setScale(self, scale):
    # type: (float) -> None
    self.__scale = scale
    self.__minimap.setMatrix(self.handle, self.__createMatrix())

  def setActive(self, active):
    # type: (bool) -> None
    self.__minimap.setActive(self.handle, active)

  def remove(self):
    self.__minimap.delEntry(self.handle)

  def __createMatrix(self):
    size = self.__baseScale * self.__scale
    return minimap_utils.makePositionAndScaleMatrix(Vector3(self.__position), (size, 1.0, size))
