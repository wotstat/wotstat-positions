package wotstat.positions {
  import flash.display.Sprite;
  import flash.display.Graphics;
  import flash.events.Event;

  public class Heatmap extends Sprite {
    private var heatmap:Vector.<Object> = new Vector.<Object>();
    private var currentIndex:int = 0;
    private var multiplier:Number = 1;
    private var targetWidth:int = 0;
    private var targetHeight:int = 0;
    private var color:uint = 0;
    private var step:uint = 0;
    private var limit:int = 0;

    public function Heatmap(color:uint, step:uint = 250, limit:int = -1) {
      this.color = color;
      this.step = step;
      this.limit = limit;
      cacheAsBitmap = true;
      App.instance.addEventListener(Event.ENTER_FRAME, onFrame);
    }

    public function dispose():void {
      App.instance.removeEventListener(Event.ENTER_FRAME, onFrame);
    }

    public function setSize(width:int, height:int):void {
      targetWidth = width;
      targetHeight = height;
    }

    public function setLimit(limit:int):void {
      this.limit = limit;
    }

    public function setupHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (x.length != y.length || x.length != weight.length || y.length != weight.length)
        return;

      heatmap = new Vector.<Object>();
      for (var i:int = 0; i < x.length; i++) {
        heatmap.push([x[i], y[i], weight[i]]);
      }
      this.multiplier = multiplier;
      currentIndex = 0;
      graphics.clear();
    }

    public function clear():void {
      heatmap = new Vector.<Object>();
      currentIndex = 0;
      graphics.clear();
    }

    private function drawHeatmapDot(x:Number, y:Number, weight:Number):void {
      graphics.beginFill(color, Math.max(0, Math.min(1, weight * 2)));
      var size:Number = weight * targetWidth * multiplier;
      graphics.drawRect(x * targetWidth - size / 2, targetHeight - (y * targetHeight) - size / 2, size, size);
    }

    private function onFrame(e:Event):void {
      if (currentIndex >= heatmap.length)
        return;

      if (currentIndex >= limit && limit >= 0)
        return;

      var ctx:Graphics = graphics;
      for (var i:int = 0; i < step && currentIndex < heatmap.length && (currentIndex < limit || limit < 0); i++) {
        drawHeatmapDot(
            heatmap[currentIndex][0],
            heatmap[currentIndex][1],
            heatmap[currentIndex][2]
          );
        currentIndex++;
      }
    }
  }
}