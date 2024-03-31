

class IPositionRequester(object):
  def start(self):
    pass

  def stop(self):
    pass

class IPositionDrawer(object):
  def drawPoints(self, efficency, points):
    pass

  def drawPolygons(self, polygons):
    pass

  def drawIdealPoints(self, points):
    pass

  def clear(self):
    pass