package wotstat.positions {
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.data.constants.generated.LAYER_NAMES;
  import net.wg.gui.components.containers.MainViewContainer;
  import net.wg.gui.battle.views.BaseBattlePage;
  import flash.display.DisplayObject;
  import flash.display.Sprite;
  import net.wg.gui.battle.views.minimap.Minimap;
  import net.wg.gui.battle.views.minimap.EpicMinimap;
  import flash.display.Graphics;
  import flash.events.MouseEvent;
  import net.wg.gui.components.controls.Image;
  import flash.geom.Matrix;

  public class MinimapOverlay extends AbstractView {

    private static const VISIBILITY_ALWAYS:String = 'ALWAYS';
    private static const VISIBILITY_MOUSE_OVER:String = 'MOUSE_OVER';
    private static const VISIBILITY_NEVER:String = 'NEVER';

    private const SPOT_POINT_SCALE_THRESHOLD:Number = 0.75;
    private const MOUSE_DIRECTION_THRESHOLD:Number = 0.04;
    private const VEHICLE_DIRECTION_THRESHOLD:Number = 0.04;

    public var py_log:Function;

    private var isInitialized:Boolean = false;
    private var isRegistered:Boolean = false;

    private var spotPoints:Sprite = new Sprite();
    private var miniSpotPoints:Sprite = new Sprite();
    private var spotDirections:Sprite = new Sprite();

    private var minimapContainer:Sprite = null;
    private var heatmap:Heatmap = new Heatmap(0xFFFF00, 250, -1);
    private var popularHeatmap:Heatmap = new Heatmap(0x62f4ff, 250, -1);

    private var overlayWidth:Number = 1;
    private var overlayHeight:Number = 1;

    private var hits:Vector.<Vector.<Object>> = new Vector.<Vector.<Object>>();
    private var spotPointsData:Vector.<Object> = new Vector.<Object>();
    private var spotPointImage:Image = new Image();

    private var spotPointsDisplayMode:String = VISIBILITY_ALWAYS;
    private var miniSpotPointsDisplayMode:String = VISIBILITY_MOUSE_OVER;

    private var mouseShouldDropSpotRays:Boolean = true;
    private var vehicleShouldDropSpotRays:Boolean = true;

    private var vehiclePosition:Array = [10000, 10000];
    private var lastMouseOverMinimap:Boolean = false;

    public function MinimapOverlay() {
      super();
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      spotPointImage.source = "wotstatPositionsAssets/spot-point.png";
    }

    override protected function onDispose():void {
      App.instance.removeEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      heatmap.dispose();
      popularHeatmap.dispose();
      super.onDispose();
    }

    override protected function configUI():void {
      super.configUI();
      spotPoints.cacheAsBitmap = true;
      miniSpotPoints.cacheAsBitmap = true;
      setup();
    }

    private function getBattlePage():BaseBattlePage {
      var viewContainer:MainViewContainer = App.containerMgr.getContainer(LAYER_NAMES.LAYER_ORDER.indexOf(LAYER_NAMES.VIEWS)) as MainViewContainer;
      if (viewContainer == null)
        return null;

      for (var i:int = 0; i < viewContainer.numChildren; ++i) {
        var child:DisplayObject = viewContainer.getChildAt(i);

        if (child is BaseBattlePage)
          return child as BaseBattlePage;
      }

      return null;
    }

    private function setup():void {
      if (isInitialized || !isRegistered)
        return;

      var battlePage:BaseBattlePage = getBattlePage();
      if (battlePage == null)
        return;

      isInitialized = true;

      if (battlePage.minimap is Minimap) {
        var minimap:Minimap = battlePage.minimap as Minimap;
        var index:int = minimap.entriesContainer.getChildIndex(minimap.entriesContainer.flags);
        minimap.entriesContainer.addChildAt(popularHeatmap, index);
        minimap.entriesContainer.addChildAt(heatmap, index + 1);
        minimap.entriesContainer.addChildAt(spotDirections, index + 2);
        minimap.entriesContainer.addChildAt(miniSpotPoints, index + 3);
        minimap.entriesContainer.addChildAt(spotPoints, index + 4);

        minimapContainer = minimap.background;
        overlayWidth = minimap.entriesContainer.flags.width;
        overlayHeight = minimap.entriesContainer.flags.width;

        heatmap.x = spotPoints.x = popularHeatmap.x = spotDirections.x = miniSpotPoints.x = -overlayWidth / 2;
        heatmap.y = spotPoints.y = popularHeatmap.y = spotDirections.y = miniSpotPoints.y = -overlayHeight / 2;

      }
      else if (battlePage.minimap is EpicMinimap) {
        var epicMinimap:EpicMinimap = battlePage.minimap as EpicMinimap;
        epicMinimap.background.addChild(popularHeatmap);
        epicMinimap.background.addChild(heatmap);
        epicMinimap.background.addChild(spotDirections);
        epicMinimap.background.addChild(miniSpotPoints);
        epicMinimap.background.addChild(spotPoints);

        minimapContainer = epicMinimap.entriesContainer;
        overlayHeight = epicMinimap.background.originalHeight;
        overlayWidth = epicMinimap.background.originalWidth;
      }

      heatmap.setSize(overlayWidth, overlayHeight);
      popularHeatmap.setSize(overlayWidth, overlayHeight);
    }

    private function unsetup():void {
      if (!isInitialized)
        return;

      var battlePage:BaseBattlePage = getBattlePage();
      if (battlePage == null)
        return;

      isInitialized = false;

      if (battlePage.minimap is Minimap) {
        var minimap:Minimap = battlePage.minimap as Minimap;
        minimap.entriesContainer.removeChild(popularHeatmap);
        minimap.entriesContainer.removeChild(heatmap);
        minimap.entriesContainer.removeChild(spotDirections);
        minimap.entriesContainer.removeChild(miniSpotPoints);
        minimap.entriesContainer.removeChild(spotPoints);
      }
      else if (battlePage.minimap is EpicMinimap) {
        var epicMinimap:EpicMinimap = battlePage.minimap as EpicMinimap;
        epicMinimap.background.removeChild(popularHeatmap);
        epicMinimap.background.removeChild(heatmap);
        epicMinimap.background.removeChild(spotDirections);
        epicMinimap.background.removeChild(miniSpotPoints);
        epicMinimap.background.removeChild(spotPoints);
      }
    }

    public function as_setupSpotPoints(points:Array):void {
      if (spotPoints == null)
        return;

      spotPointsData = new Vector.<Object>();
      hits = new Vector.<Vector.<Object>>();
      for (var i:int = 0; i < points.length; i++) {
        var point:Object = points[i];
        var pos:Array = convert(point.position[0], point.position[1]);

        var hit:Vector.<Object> = new Vector.<Object>();

        for (var j:int = 0; j < point.hits.length; j++) {
          var spot:Object = point.hits[j];
          var spotPos:Array = convert(spot[0], spot[1]);
          hit.push([spotPos[0], spotPos[1], 0.2 + spot[2]]);
        }

        spotPointsData.push([pos[0], pos[1], point.position[2]]);
        hits.push(hit);
      }

      redrawSpotPoints();
      redrawSpotDirections();
    }

    public function as_setupHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (heatmap == null)
        return;

      heatmap.setupHeatmap(x, y, weight, multiplier);
    }

    public function as_setupPopularHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (popularHeatmap == null)
        return;

      popularHeatmap.setupHeatmap(x, y, weight, multiplier);
    }

    public function as_setRelativeVehiclePosition(x:Number, y:Number):void {
      vehiclePosition = [x, 1 - y];
      redrawSpotDirections();
    }

    public function as_clear():void {
      heatmap.clear();
      popularHeatmap.clear();
      spotPointsData = new Vector.<Object>();
      hits = new Vector.<Vector.<Object>>();
      redrawSpotPoints();
      redrawSpotDirections();
    }

    public function as_setHeatmapLimit(limit:uint):void {
      if (heatmap)
        heatmap.setLimit(limit);

      if (popularHeatmap)
        popularHeatmap.setLimit(limit);
    }

    public function as_setHeatmapVisible(visible:Boolean):void {
      if (heatmap == null)
        return;

      heatmap.visible = visible;
    }

    public function as_setPopularHeatmapVisible(visible:Boolean):void {
      if (popularHeatmap == null)
        return;

      popularHeatmap.visible = visible;
    }

    public function as_setSpotPointsVisible(mode:String):void {
      if (spotPoints == null)
        return;

      spotPointsDisplayMode = mode;
      updateSpotPointsVisibility();
      redrawSpotDirections();
    }

    public function as_setMiniSpotPointsVisible(mode:String):void {
      if (miniSpotPoints == null)
        return;

      miniSpotPointsDisplayMode = mode;
      updateSpotPointsVisibility();
      redrawSpotDirections();
    }

    public function as_setVehicleShouldDropSpotRays(visible:Boolean):void {
      vehicleShouldDropSpotRays = visible;
      redrawSpotDirections();
    }

    public function as_setMouseShouldDropSpotRays(visible:Boolean):void {
      mouseShouldDropSpotRays = visible;
      redrawSpotDirections();
    }

    public function as_register():void {
      isRegistered = true;
      setup();
    }

    public function as_unregister():void {
      isRegistered = false;
      unsetup();
    }

    private function updateSpotPointsVisibility():void {
      if (spotPoints == null || miniSpotPoints == null)
        return;

      miniSpotPoints.visible = miniSpotPointsDisplayMode == VISIBILITY_ALWAYS ||
        (miniSpotPointsDisplayMode == VISIBILITY_MOUSE_OVER && lastMouseOverMinimap);

      spotPoints.visible = spotPointsDisplayMode == VISIBILITY_ALWAYS ||
        (spotPointsDisplayMode == VISIBILITY_MOUSE_OVER && lastMouseOverMinimap) || miniSpotPoints.visible;
    }

    private function convert(x:Number, y:Number):Array {
      return [x * overlayWidth, overlayHeight - y * overlayHeight];
    }

    private function drawSpotPoint(ctx:Graphics, x:Number, y:Number, weight:Number):void {
      const targetWidth:Number = 15 * weight;
      const scale:Number = targetWidth / spotPointImage.bitmapData.width;
      const offsetX:Number = x - targetWidth / 2;
      const offsetY:Number = y - targetWidth / 2;

      const matrix:Matrix = new Matrix();
      matrix.scale(scale, scale);
      matrix.translate(offsetX, offsetY);

      ctx.beginBitmapFill(spotPointImage.bitmapData, matrix, false, true);
      ctx.drawRect(offsetX, offsetY, targetWidth, targetWidth);
      ctx.endFill();
    }

    private function redrawSpotPoints():void {
      var ctxB:Graphics = spotPoints.graphics;
      ctxB.clear();

      var ctxM:Graphics = miniSpotPoints.graphics;
      ctxM.clear();

      for (var i:int = 0; i < spotPointsData.length; i++) {
        drawSpotPoint(
            spotPointsData[i][2] > SPOT_POINT_SCALE_THRESHOLD ? ctxB : ctxM,
            spotPointsData[i][0],
            spotPointsData[i][1],
            spotPointsData[i][2]
          );
      }
    }

    private function redrawSpotDirections():void {
      if (spotDirections == null)
        return;

      var ctx:Graphics = spotDirections.graphics;
      ctx.clear();

      if (!mouseShouldDropSpotRays && !vehicleShouldDropSpotRays)
        return;

      var x:Number = spotPoints.mouseX / overlayWidth;
      var y:Number = spotPoints.mouseY / overlayHeight;

      const mouseThresholdSqr:Number = MOUSE_DIRECTION_THRESHOLD * MOUSE_DIRECTION_THRESHOLD;
      const vehicleThresholdSqr:Number = VEHICLE_DIRECTION_THRESHOLD * VEHICLE_DIRECTION_THRESHOLD;

      for (var i:uint = 0; i < hits.length; i++) {
        const hit:Vector.<Object> = hits[i];

        const pX:Number = spotPointsData[i][0] / overlayWidth;
        const pY:Number = spotPointsData[i][1] / overlayHeight;

        const mouseDistanceSqr:Number = Math.pow(x - pX, 2) + Math.pow(y - pY, 2);
        const vehicleDistanceSqr:Number = Math.pow(vehiclePosition[0] - pX, 2) + Math.pow(vehiclePosition[1] - pY, 2);

        if ((mouseDistanceSqr > mouseThresholdSqr || !mouseShouldDropSpotRays) &&
            (vehicleDistanceSqr > vehicleThresholdSqr || !vehicleShouldDropSpotRays))
          continue;

        const mouseDistance:Number = Math.sqrt(mouseDistanceSqr);
        const vehicleDistance:Number = Math.sqrt(vehicleDistanceSqr);

        const alpha:Number = Math.max(
            Math.min(mouseShouldDropSpotRays ? 1 : 0, 1 - Math.max(0, mouseDistance - 0.02) / 0.02),
            Math.min(vehicleShouldDropSpotRays ? 1 : 0, 1 - Math.max(0, vehicleDistance - 0.02) / 0.02)
          );

        for (var j:int = 0; j < hit.length; j++) {
          var spot:Object = hit[j];
          ctx.lineStyle(0.3, 0xFFEAB8, Math.min(1, Math.max(0, alpha * spot[2])));
          ctx.moveTo(pX * overlayWidth, pY * overlayHeight);
          ctx.lineTo(spot[0], spot[1]);
        }

        ctx.lineStyle();
        if (spotPointsData[i][2] > SPOT_POINT_SCALE_THRESHOLD && !spotPoints.visible ||
            spotPointsData[i][2] <= SPOT_POINT_SCALE_THRESHOLD && !miniSpotPoints.visible)
          drawSpotPoint(ctx, spotPointsData[i][0], spotPointsData[i][1], spotPointsData[i][2]);
      }
    }

    private function onMouseMove(e:MouseEvent):void {
      if (minimapContainer == null)
        return;

      const x:Number = minimapContainer.mouseX / minimapContainer.width;
      const y:Number = minimapContainer.mouseY / minimapContainer.height;

      const mouseOverMinimap:Boolean = x >= 0 && x <= 1 && y >= 0 && y <= 1;
      const isChanged:Boolean = lastMouseOverMinimap != mouseOverMinimap;
      lastMouseOverMinimap = mouseOverMinimap;

      if (isChanged || mouseOverMinimap) {
        redrawSpotDirections();
      }

      if (isChanged) {
        updateSpotPointsVisibility();
      }
    }
  }
}