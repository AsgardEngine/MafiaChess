import bge
import bpy
from MouseEvents import MouseEvents
from ImportManagerEvents import ImportManagerEvents
from collections import OrderedDict

class Mouse(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.scene = self.object.scene
        self.objects = self.object.scene.objects
        self.cursorStartPosition = 0
        self.active = False
        self.currentObjectHit = None
        self.currentObject = None
        self.currentSquare = None
        ImportManagerEvents.instance.register_observer(self)
    
    def newImport(self):        
        raycast_plane = self.objects["Raycast_plane"]
        raycast_plane["Raycast_plane"] = True
        raycast_plane.visible = False
        self.active = True
                
    def raycastObject(self):
        cam = self.scene.active_camera
        mPos = bge.logic.mouse.position
        sVec = cam.getScreenVect(mPos[0], mPos[1])
        target = cam.worldPosition - sVec
        
        objHit, _, _ = self.object.rayCast(target, cam, 5000, "Clickable", 1, 1, 0)
        _, hotPos, _ = self.object.rayCast(target, cam, 5000, "Raycast_plane", 1, 1, 0)
        
        if objHit: MouseEvents.Over = objHit.name
        else: MouseEvents.Over = ''

        if not self.currentSquare:
            if objHit and objHit != self.currentObjectHit:
                self.currentObjectHit = objHit
                MouseEvents.Hold = objHit.name
            elif not objHit and self.currentObjectHit:
                self.currentObjectHit = None
                MouseEvents.Hold = ""

        mouse = bge.logic.mouse.inputs
        keyboard = bge.logic.keyboard.inputs

        if bge.logic.KX_INPUT_JUST_ACTIVATED in mouse[bge.events.LEFTMOUSE].queue:
            MouseEvents.Click = True
            MouseEvents.instance.onLeftClick()
            self.onLeftClick(objHit)

        if bge.logic.KX_INPUT_JUST_RELEASED in mouse[bge.events.LEFTMOUSE].queue:
            MouseEvents.Click = False
            self.onReleaseLeftClick(objHit)

        if bge.logic.KX_INPUT_JUST_ACTIVATED in mouse[bge.events.RIGHTMOUSE].queue:
            MouseEvents.Click = True
            self.onRightClick(objHit)

        if bge.logic.KX_INPUT_JUST_RELEASED in mouse[bge.events.RIGHTMOUSE].queue:
            MouseEvents.Click = False                     
            MouseEvents.instance.onReleaseRightClick(objHit)            
        
        if hotPos[0]:
            MouseEvents.X = hotPos[0]
            MouseEvents.Z = hotPos[2]
            MouseEvents.ChangeInX = self.cursorStartPosition - MouseEvents.X

        if bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.LEFTARROWKEY].queue:
            MouseEvents.instance.onLeftArrow()
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.RIGHTARROWKEY].queue:
            MouseEvents.instance.onRightArrow()
        if bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.UPARROWKEY].queue:
            MouseEvents.instance.onUpArrow()
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.DOWNARROWKEY].queue:
            MouseEvents.instance.onDownArrow()
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.SPACEKEY].queue:
            MouseEvents.instance.onSpace()
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.FIVEKEY].queue:
            MouseEvents.instance.onReleaseButton("Q_btn")
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.FOURKEY].queue:
            MouseEvents.instance.onReleaseButton("R_btn")
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.THREEKEY].queue:
            MouseEvents.instance.onReleaseButton("B_btn")
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.TWOKEY].queue:
            MouseEvents.instance.onReleaseButton("N_btn")
        elif bge.logic.KX_INPUT_JUST_ACTIVATED in keyboard[bge.events.CKEY].queue:
            MouseEvents.instance.onReleaseButton("C_key_btn")
        
    def onLeftClick(self, objHit):
        self.cursorStartPosition = MouseEvents.X
        if objHit:
            if 'Square' in objHit:
                self.currentSquare = objHit
                MouseEvents.instance.onClickPiece(objHit)
            else:
                self.currentObject = objHit
                MouseEvents.instance.onClickButton(objHit.name)
            
            bpy.data.node_groups["Chess_Mouse"].nodes["click"].boolean = True
            
    def onReleaseLeftClick(self, objHit):
        MouseEvents.instance.onReleaseLeftClick()
        if self.currentSquare and 'Square' in objHit:
            MouseEvents.instance.onReleasePiece(self.currentSquare['Square'], objHit['Square'])
            self.currentSquare = None
        elif self.currentSquare:
            MouseEvents.instance.onCancelPiece(self.currentSquare)
            self.currentSquare = None
        elif objHit and objHit == self.currentObject:
            MouseEvents.instance.onReleaseButton(objHit.name)
            self.currentObject = None
        bpy.data.node_groups["Chess_Mouse"].nodes["click"].boolean = False
    
    def onRightClick(self, objHit):
        MouseEvents.instance.onRightClick(objHit)
        if self.currentSquare:
            MouseEvents.instance.onCancelPiece(self.currentSquare)
            self.currentSquare = None
        else:
            self.currentObject = None

        bpy.data.node_groups["Chess_Mouse"].nodes["click"].boolean = False

    def update(self): 
        if not self.active:            
            return
        self.raycastObject()