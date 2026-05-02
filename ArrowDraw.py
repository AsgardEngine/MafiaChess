import bge
import bpy
from MouseEvents import MouseEvents
from ImportManagerEvents import ImportManagerEvents as IME
from collections import OrderedDict

class ArrowDraw(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.scene = self.object.scene
        self.objects = self.object.scene.objects
        
        MouseEvents.instance.register_observer(self)
        self.all_Arrows = []
        self.current_arrow = None
        self.start_square = None

    def onLeftClick(self):
        self.removeArrows()

    def onRightClick(self, objHit):
        if not 'Square' in objHit:
            return
        self.createArrowMesh(objHit)

    def onReleaseRightClick(self, objHit):
        if not self.current_arrow:
            return
        if not objHit or not 'Square' in objHit:
            arrow = self.current_arrow
            self.current_arrow = None
            arrow.endObject()
            return
        
        arrow = self.current_arrow.blenderObject     
        arrow.modifiers["Arrow"]["Input_3"][0] = objHit.worldPosition.x
        arrow.modifiers["Arrow"]["Input_3"][2] = objHit.worldPosition.z
        arrow.update_tag()

        start_x = arrow.modifiers["Arrow"]["Input_2"][0]
        start_z = arrow.modifiers["Arrow"]["Input_2"][2]
        end_x = arrow.modifiers["Arrow"]["Input_3"][0]
        end_z = arrow.modifiers["Arrow"]["Input_3"][2]

        if self.arrowExist(start_x, start_z, end_x, end_z): 
            arrow = self.current_arrow
            self.current_arrow = None
            arrow.endObject()
        else: 
            self.all_Arrows.append(self.current_arrow)

        self.current_arrow = None
    
    def arrowExist(self, s_x, s_z, e_x, e_z):
        for arrow in self.all_Arrows:
            start_x = arrow.blenderObject.modifiers["Arrow"]["Input_2"][0]
            start_z = arrow.blenderObject.modifiers["Arrow"]["Input_2"][2]
            end_x = arrow.blenderObject.modifiers["Arrow"]["Input_3"][0]
            end_z = arrow.blenderObject.modifiers["Arrow"]["Input_3"][2]
            if start_x == s_x and start_z == s_z and end_x == e_x and end_z == e_z:
                self.all_Arrows.remove(arrow)
                arrow.endObject()
                return True
        return False

    def createArrowMesh(self, square):
        curve_data = bpy.data.curves.new(name="Arrow", type='CURVE')
        arrow = bpy.data.objects.new("Arrow", curve_data)

        collection = bpy.data.collections["GameCollection"]
        collection.objects.link(arrow)

        modifier = arrow.modifiers.new("Arrow", "NODES")
        modifier.node_group = bpy.data.node_groups["Template_Arrow"]

        converted_arrow = self.object.scene.convertBlenderObject(arrow)
        converted_arrow['Arrow'] = True

        arrow.modifiers["Arrow"]["Input_2"][0] = square.worldPosition.x
        arrow.modifiers["Arrow"]["Input_2"][2] = square.worldPosition.z
        arrow.update_tag()

        self.current_arrow = converted_arrow
    
    def setArrowHeadPosition(self):
        self.current_arrow.blenderObject.modifiers["Arrow"]["Input_3"][0] = MouseEvents.X
        self.current_arrow.blenderObject.modifiers["Arrow"]["Input_3"][2] = MouseEvents.Z
        self.current_arrow.blenderObject.update_tag()

    def removeArrows(self):
        if self.current_arrow:
            arrow = self.current_arrow
            self.current_arrow = None
            arrow.endObject()
        
        for arrow in self.objects:
            if 'Arrow' in arrow:
                arrow.endObject()
        self.all_Arrows = []

    def update(self): 
        if self.current_arrow:
            self.setArrowHeadPosition()