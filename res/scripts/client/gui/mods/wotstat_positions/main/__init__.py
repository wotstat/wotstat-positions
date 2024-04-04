from typing import List, Tuple  # noqa: F401

class IPositionRequester(object):
  def start(self):
    pass

  def stop(self):
    pass

class IPositionDrawer(object):
  def drawPoints(self, points):
    # type: (List[PositionPoint]) -> None
    pass

  def drawPolygons(self, polygons):
    # type: (List[PositionArea]) -> None
    pass

  def drawIdealPoints(self, points):
    # type: (List[PositionPoint]) -> None
    pass

  def clear(self):
    pass

  def reset(self):
    pass

class PositionPoint(object):
  def __init__(self, efficiency, position):
    # type: (float, Tuple[float, float]) -> None
    self.efficiency = efficiency
    self.position = position

class PositionArea(object):
  def __init__(self, efficiency, area):
    # type: (float, List[Tuple[float, float]]) -> None
    self.efficiency = efficiency
    self.area = area
    self.bbox = None

  def getBbox(self):
    # type: () -> Tuple[Tuple[float, float], Tuple[float, float]]

    if self.bbox is not None:
      return self.bbox

    min_x = min([point[0] for point in self.area])
    min_y = min([point[1] for point in self.area])
    max_x = max([point[0] for point in self.area])
    max_y = max([point[1] for point in self.area])

    self.bbox = ((min_x, min_y), (max_x, max_y))
    return self.bbox
  
  def isPointInPolygon(self, point):
    # type: (Tuple[float, float]) -> bool
    x, y = point
    n = len(self.area)
    inside = False
    
    bbox = self.getBbox()
    if x < bbox[0][0] or x > bbox[1][0] or y < bbox[0][1] or y > bbox[1][1]:
      return False

    p1x, p1y = self.area[0]
    for i in range(n + 1):
      p2x, p2y = self.area[i % n]
      if y > min(p1y, p2y):
        if y <= max(p1y, p2y):
          if x <= max(p1x, p2x):
            if p1y != p2y:
              xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
              if p1x == p2x or x <= xinters:
                inside = not inside
      p1x, p1y = p2x, p2y

    return inside