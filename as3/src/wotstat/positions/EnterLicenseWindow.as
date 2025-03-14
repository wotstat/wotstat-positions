package wotstat.positions {
  import net.wg.infrastructure.base.AbstractWindowView;
  import net.wg.gui.components.controls.TextInput;
  import net.wg.gui.components.controls.SoundButton;
  import flash.events.MouseEvent;
  import scaleform.clik.events.InputEvent;

  public class EnterLicenseWindow extends AbstractWindowView {

    public var py_enterLicense:Function;
    public var py_cancel:Function;
    public var py_t:Function;

    private var licenseInput:TextInput;
    private var applyButton:SoundButton;
    private var cancelButton:SoundButton;

    public function EnterLicenseWindow() {
      super();
    }

    override protected function onPopulate():void {
      super.onPopulate();
      width = 401;
      height = 46;
      window.title = py_t('enterLicense.title');
      window.useBottomBtns = false;

      licenseInput = addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
              width: 290,
              height: 30,
              x: 8,
              y: 10,
              defaultText: py_t('enterLicense.inputPlaceholder')
            })) as TextInput;

      licenseInput.defaultTextFormat.italic = false;
      licenseInput.defaultTextFormat.color = 0x959587;
      licenseInput.addEventListener(InputEvent.INPUT, onInputInputHandler);

      applyButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
              width: 90,
              height: 25,
              x: 303,
              y: 12.5,
              label: py_t('enterLicense.apply'),
              enabled: false
            })) as SoundButton;
      applyButton.addEventListener(MouseEvent.CLICK, onApplyButtonClick);
    }

    private function onApplyButtonClick(event:MouseEvent):void {
      py_enterLicense(licenseInput.text);
    }

    private function onInputInputHandler(event:InputEvent):void {
      applyButton.enabled = licenseInput.text.length > 0;
    }
  }
}