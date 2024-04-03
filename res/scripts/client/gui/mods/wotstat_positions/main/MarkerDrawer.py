from typing import List, Tuple, Dict

import BigWorld
from gui.shared.personality import ServicesLocator
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager # noqa: F401
from gui.Scaleform.daapi.view.battle.shared.minimap import settings, plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import CommonMarkerType, MARKER_SYMBOL_NAME
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from frameworks.wulf import WindowLayer
from Math import Vector2, Vector3, Vector4, createTranslationMatrix
from gui.battle_control import minimap_utils

from ..common.Logger import Logger
from . import IPositionDrawer, PositionPoint, PositionArea # noqa: F401

logger = Logger.instance()

CULL_DISTANCE = 1800
MIN_SCALE = 50.0
BOUNDS = Vector4(30, 30, 90, -15)
INNER_BOUNDS = Vector4(15, 15, 70, -35)
BOUNDS_MIN_SCALE = Vector2(1.0, 0.8)
MIN_Y_OFFSET = 1.2
MAX_Y_OFFSET = 2.2
DISTANCE_FOR_MIN_Y_OFFSET = 400
MAX_Y_BOOST = 1.4
BOOST_START = 120

AREA_STEP = 20

class MarkerDrawer(IPositionDrawer):
  __minimap = None
  __markerManager = None # type: MarkersManager

  __markers = {
    settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER: [],
    settings.ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER: [],
    settings.ENTRY_SYMBOL_NAME.VEHICLE: []
  } # type: Dict[str, List[Marker]]
  __freeMarkers = {
    settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER: [],
    settings.ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER: [],
    settings.ENTRY_SYMBOL_NAME.VEHICLE: []
  } # type: Dict[str, List[Marker]]

  __worldMarkers = {
    MARKER_SYMBOL_NAME.NAVIGATION_MARKER: []
  } # type: Dict[str, List[WorldMarker]]
  __freeWorldMarkers = {
    MARKER_SYMBOL_NAME.NAVIGATION_MARKER: []
  } # type: Dict[str, List[WorldMarker]]
  

  def __init__(self):
    self.__minimap = None
    self.__markerManager = None

  def drawPoints(self, points):
    # type: (List[PositionPoint]) -> None
    
    for point in points:
      position = point.position
      efficiency = point.efficiency
      marker = self.__createMarker((position[0], 0, position[1]), settings.ENTRY_SYMBOL_NAME.LOCATION_MARKER, settings.CONTAINER_NAME.ICONS)
      if marker:
        marker.setScale(efficiency)

  def drawPolygons(self, polygons):
    # type: (List[PositionArea]) -> None

    boundingBox = BigWorld.player().arena.arenaType.boundingBox
    x_min, y_min = boundingBox[0]
    x_max, y_max = boundingBox[1]

    xRange = range(int(x_min / AREA_STEP) * AREA_STEP, int(x_max / AREA_STEP) * AREA_STEP, AREA_STEP)
    yRange = range(int(y_min / AREA_STEP) * AREA_STEP, int(y_max / AREA_STEP) * AREA_STEP, AREA_STEP)

    line = 0
    for x in xRange:
      line += 1
      offset = AREA_STEP * 0.5 * (line % 2)
      for y in yRange:
        for polygon in polygons:
          if polygon.isPointInPolygon((x, y)):
            self.__createPointMarker((x, y + offset), green=True, scale=polygon.efficiency)
            break


  def drawIdealPoints(self, points):
    # type: (List[PositionPoint]) -> None

    for point in points:
      position = point.position
      marker = self.__createWorldMarker(position, MARKER_SYMBOL_NAME.NAVIGATION_MARKER)
      if marker:
        marker.setRenderInfo(MIN_SCALE, BOUNDS, INNER_BOUNDS, CULL_DISTANCE, BOUNDS_MIN_SCALE)
        marker.setLocationOffset(MIN_Y_OFFSET, MAX_Y_OFFSET, DISTANCE_FOR_MIN_Y_OFFSET, MAX_Y_BOOST, BOOST_START)

        markerMinimap = self.__createMarker(position, settings.ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER, settings.CONTAINER_NAME.ICONS)
        if markerMinimap:
          markerMinimap.setScale(1)

  def clear(self):
    for key, value in self.__markers.items():
      for marker in value:
        marker.setActive(False)

      self.__freeMarkers[key] = list(value)

    for key, value in self.__worldMarkers.items():
      for marker in value:
        marker.setActive(False)
      
      self.__freeWorldMarkers[key] = list(value)

  def reset(self):
    for key in self.__markers.keys():
      self.__markers[key] = []
      self.__freeMarkers[key] = []

    for key in self.__worldMarkers.keys():
      self.__worldMarkers[key] = []
      self.__freeWorldMarkers[key] = []

    self.__minimap = None
    self.__markerManager = None

  def __createMarker(self, position, markerType, container, scale=1.0):
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
    marker = Marker(position, markerType, container, scale, self.__minimap, baseScale)
    self.__markers[markerType].append(marker)

    return marker
  
  def __createPointMarker(self, position, green=True, scale=1.0):
    # type: (Tuple[float, float], bool, float) -> Marker
    marker = self.__createMarker(position, settings.ENTRY_SYMBOL_NAME.VEHICLE, settings.CONTAINER_NAME.ALIVE_VEHICLES, scale)
    if marker:
      marker.invoke('setVehicleInfo', 777, 'mediumTank', '', 'ally' if green else 'enemy', '')

  def __createWorldMarker(self, position, markerType):
    # type: (Tuple[float, float], str) -> WorldMarker

    markers = self.__freeWorldMarkers[markerType]
    if len(markers) > 0:
      marker = markers.pop()
      marker.setPosition(position)
      marker.setActive(True)
      return marker

    if not self.__markerManager or not self.__markerManager.isCreated():
      battle = ServicesLocator.appLoader.getDefBattleApp()
      if not battle:
        self.__markerManager = None
        return
      
      view = battle.containerManager.getContainer(WindowLayer.VIEW).getView()
      if not view:
        return

      self.__markerManager = view._external[1]

    if not self.__markerManager:
      return
    
    logger.info('Create new world marker: %s' % str(position))
    marker = WorldMarker(position, markerType, self.__markerManager)
    self.__worldMarkers[markerType].append(marker)

    return marker


class Marker():
  def __init__(self, position, markerType, container, scale, minimap, baseScale):
    # type: (Tuple[float, float, float], str, str, float, plugins.MinimapPlugin, float) -> Marker
    self.__position = position
    self.__markerType = markerType
    self.__container = container
    self.__minimap = minimap
    self.__baseScale = baseScale
    self.__scale = scale

    self.handle = self.__minimap.addEntry(self.__markerType, self.__container, self.__createMatrix(),
                                          active=True, transformProps=settings.TRANSFORM_FLAG.FULL)

  def setPosition(self, position):
    # type: (Tuple[float, float]) -> None
    self.__position = position
    self.__minimap.setMatrix(self.handle, self.__createMatrix())
    
  def setScale(self, scale):
    # type: (float) -> None
    self.__scale = scale
    self.__minimap.setMatrix(self.handle, self.__createMatrix())

  def setActive(self, active):
    # type: (bool) -> None
    self.__minimap.setActive(self.handle, active)

  def invoke(self, methodName, *args):
    # type: (str, *any) -> None
    self.__minimap.invoke(self.handle, methodName, *args)

  def remove(self):
    self.__minimap.delEntry(self.handle)

  def __createMatrix(self):
    size = self.__baseScale * self.__scale
    pos = Vector3(self.__position[0], 0, self.__position[1])
    return minimap_utils.makePositionAndScaleMatrix(Vector3(pos), (size, 1.0, size))

class WorldMarker():

  __MARKER_TYPE_BY_SYMBOL = {
    MARKER_SYMBOL_NAME.NAVIGATION_MARKER: CommonMarkerType.LOCATION,
  }

  def __init__(self, position, markerSymbol, manager):
    # type: (Tuple[float, float], str, MarkersManager) -> WorldMarker

    self.__position = position
    self.__markerSymbol = markerSymbol
    self.__manager = manager

    matrix = createTranslationMatrix(self.__getTerrainHeightAt(position))
    self.handle = self.__manager.createMarker(self.__markerSymbol, matrix, True, self.__MARKER_TYPE_BY_SYMBOL[self.__markerSymbol])

  def setPosition(self, position):
    # type: (Tuple[float, float]) -> None
    self.__position = position
    self.__manager.setMarkerMatrix(self.handle, createTranslationMatrix(self.__getTerrainHeightAt(position)))

  def setActive(self, active):
    # type: (bool) -> None
    self.__manager.setMarkerActive(self.handle, active)

  def setFocus(self, focus):
    # type: (bool) -> None
    self.__manager.setMarkerObjectInFocus(self.handle, focus)

  def setRenderInfo(self, minScale, bounds, innerBounds, cullDistance, markerBoundsScale):
    self.__manager.setMarkerRenderInfo(self.handle, minScale, bounds, innerBounds, cullDistance, markerBoundsScale)

  def setLocationOffset(self, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
    self.__manager.setMarkerLocationOffset(self.handle, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)
  
  def setSticky(self, sticky):
    # type: (bool) -> None
    self.__manager.setMarkerSticky(self.handle, sticky)

  def remove(self):
    self.__manager.destroyMarker(self.handle)

  def __getTerrainHeightAt(self, position):
    # type: (Tuple[float, float]) -> Tuple[float, float, float]
    x = position[0]
    z = position[1]
    spaceID = BigWorld.player().spaceID
    collisionWithTerrain = BigWorld.wg_collideSegment(spaceID, Vector3(x, 1000.0, z), Vector3(x, -1000.0, z), 128)
    return collisionWithTerrain.closestPoint if collisionWithTerrain is not None else (x, 0, z)