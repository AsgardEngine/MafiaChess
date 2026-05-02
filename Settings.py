import bge
import bpy
from Audio import Audio
from ImportManagerEvents import ImportManagerEvents
from MouseEvents import MouseEvents
from collections import OrderedDict

class Settings(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])    
    
    def start(self, args):
        self.scene_name = self.object.scene.name
        self.scene = self.object.scene
        MouseEvents.instance.register_observer(self)
        ImportManagerEvents.instance.register_observer(self)
        self.current_slider = None
        self.current_slider_value = None
        self.debugVisible = False

        self.settings_node = None

        self.displayFullScreen()

    def displayFullScreen(self):
        bge.render.setFullScreen(True)
        x, y = bge.render.getDisplayDimensions()
        bge.render.setWindowSize(x, y)

    def newImport(self):
        self.settings_node = bpy.data.node_groups["Chess_Settings"]
        self.settings_node.nodes["Bloom_node"].boolean = bpy.data.scenes[self.scene_name].eevee.use_bloom
        self.settings_node.nodes["Vsync_node"].boolean = bge.render.getVsync() == 1
        self.settings_node.nodes["Full_screen_node"].boolean = bge.render.getFullScreen()
        self.settings_node.nodes["Debug_node"].boolean = False
        self.settings_node.nodes["Sound_node"].outputs[0].default_value = float(0.2)
        self.settings_node.nodes["FPS_node"].outputs[0].default_value = float(0.40)
    
    def onClickButton(self, btn):
        if btn.endswith("_slider"): self.onClickSlider(btn)
        elif btn == "Settings_Bloom_checkbox": self.setBloom(btn)
        elif btn == "Settings_FullScreen_checkbox": self.setFullScreen(btn)
        elif btn == "Settings_Vsync_checkbox": self.setVsync(btn)
        elif btn == "Settings_Debug_checkbox": self.setDebug(btn)        

    def setDebug(self, btn):
        self.debugVisible = not self.debugVisible
        bge.render.showFramerate(self.debugVisible) 
        bge.render.showProfile(self.debugVisible)
        self.settings_node.nodes["Debug_node"].boolean = self.debugVisible

    def setVsync(self, btn):
        if bge.render.getVsync() == 1:
            bge.render.setVsync(bge.render.VSYNC_OFF)
            self.settings_node.nodes["Vsync_node"].boolean = False
        else:
            bge.render.setVsync(bge.render.VSYNC_ON)
            self.settings_node.nodes["Vsync_node"].boolean = True
    
    def setFullScreen(self, btn):
        if bge.render.getFullScreen(): bge.render.setFullScreen(False)
        else: self.displayFullScreen()
        self.settings_node.nodes["Full_screen_node"].boolean = bge.render.getFullScreen()
    
    def setBloom(self, btn):
        bpy.data.scenes[self.scene_name].eevee.use_bloom = not bpy.data.scenes[self.scene_name].eevee.use_bloom
        self.settings_node.nodes["Bloom_node"].boolean = bpy.data.scenes[self.scene_name].eevee.use_bloom
    
    def onClickSlider(self, slider):
        print(f'SLIDER')
        self.current_slider = slider
        print(f'0')
        a = Audio.instance.getVolume()
        print(f'1')
        f = ((bge.logic.getLogicTicRate() - 10)/50)
        print(f'2')
        self.current_slider_value = a if self.current_slider == "Settings_Sound_slider" else f
        print(f'VALUE {self.current_slider_value}')
        
    def onReleaseLeftClick(self):
        self.current_slider = None
    
    def setFPS(self):
        level = self.getSliderLevel()
        self.settings_node.nodes["FPS_node"].outputs[0].default_value = level
        bge.logic.setLogicTicRate(round(level * 50 + 10))

    def setSoundVolume(self):
        level = self.getSliderLevel()
        self.settings_node.nodes["Sound_node"].outputs[0].default_value = level
        Audio.instance.volumeChange(level)

    def getSliderLevel(self):
        return min(max((self.current_slider_value - MouseEvents.ChangeInX/2), 0), 1)
    
    def setSliderPosition(self):
        if self.current_slider:
            if self.current_slider == "Settings_Sound_slider": self.setSoundVolume()
            elif self.current_slider == "Settings_FPS_slider": self.setFPS()                

    def update(self):
        self.setSliderPosition()