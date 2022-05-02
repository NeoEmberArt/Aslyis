bl_info = {
    "name": "Wag",
    "description": "WAG!!!",
    "author": "NeoEmberArts",
    "version": (1, 0),
    "blender": (2, 9, 0),
    "location": "View 3D > Properties Panel",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Animation",
}
# Libraries
import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
from array import *
import math
fr = False
class WagPannel(Panel):
    bl_space_type = "VIEW_3D"
    #bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "Wag"
    bl_category = "Wag Animation"
    def draw(self, context):
        scn = context.scene
        settings = scn.wagAnim
        layout = self.layout
        col = layout.column(align=True)
        row = layout.row(align=True)
        row.scale_y = 1.5
        col.label(text="Settings")
        col.prop(settings, 'power')
        col.prop(settings, 'speed')
        col.label(text="Animation Axis")
        col.prop(settings, 'x')
        col.prop(settings, 'y')
        col.prop(settings, 'z')
        col.label(text="Frame Range")
        col.prop(settings, 'frr')
        if context.scene.wagAnim.frr:
            row.prop(settings, 'fromm')
            row.prop(settings, 'to')
        layout.use_property_split = True
        layout.use_property_decorate = False
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)
        col = flow.column()
        row = layout.row(align=True)
        row.scale_y = 1.5
        col.label(text="BUTTONS!!!")
        col.operator("animation.test", text="Quick Preview", icon="SEQ_LUMA_WAVEFORM")
        row.operator("animation.create", text="Bake", icon="SEQ_LUMA_WAVEFORM")
controlPoint = "NONE"
class WAG_OT_Create(Operator):
    bl_idname = "animation.create"
    bl_label = "Bake Animation"
    bl_description = "Bake the wags animation"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context) -> bool:
        return context.scene.wagAnim.x or context.scene.wagAnim.y or context.scene.wagAnim.z
    def execute(self, context):
        if context.scene.wagAnim.fromm > context.scene.wagAnim.to:
            context.scene.wagAnim.fromm = context.scene.wagAnim.to
        global boneN
        boneN = []
        tailPos = []
        bn = bpy.context.selected_pose_bones
        power = context.scene.wagAnim.power
        curl = context.scene.wagAnim.curl
        offset = context.scene.wagAnim.offset
        speed = context.scene.wagAnim.speed
        for x in bn:
            x.id_data.data.bones[x.name].select = False
        s = bpy.context.scene.frame_start
        f = bpy.context.scene.frame_end
        if context.scene.wagAnim.frr:
            s = context.scene.wagAnim.fromm
            f = context.scene.wagAnim.to + 1
        bpy.context.scene.frame_current = s
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        for i in range(s,f):
            it = 0
            for x in bn:
                it = it + 1
                x.id_data.data.bones[x.name].select = True
                if (context.scene.wagAnim.x):
                    bpy.ops.transform.rotate(value=math.radians(math.sin(1.5-i/speed) * (power/10)), orient_axis='X')
                if (context.scene.wagAnim.y):
                    bpy.ops.transform.rotate(value=math.radians(math.sin(1.5-i/speed) * (power/10)), orient_axis='Y')
                if (context.scene.wagAnim.z):
                    bpy.ops.transform.rotate(value=math.radians(math.sin(1.5-i/speed) * (power/10)), orient_axis='Z')
                bpy.ops.anim.keyframe_insert_menu(type='Rotation')
                x.id_data.data.bones[x.name].select = False
            bpy.context.scene.frame_current = bpy.context.scene.frame_current +1
            bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        self.report({'INFO'}, 'I have wag now!!!')
        return {'FINISHED'}
def oops(self, context):
    self.layout.label(text="Undo before baking!!!")
class test(Operator):
    bl_idname = "animation.test"
    bl_label = "Test"
    bl_description = "See the farthest the armature will sway - Undo before you bake!"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context) -> bool:
        return context.scene.wagAnim.x or context.scene.wagAnim.y or context.scene.wagAnim.z
    def execute(self, context):
        global x
        x = True
        global boneN
        boneN = []
        tailPos = []
        bn = bpy.context.selected_pose_bones
        bpy.context.scene.frame_current = bpy.context.scene.frame_start
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        power = context.scene.wagAnim.power
        curl = context.scene.wagAnim.curl
        offset = context.scene.wagAnim.offset
        it = 0
        if context.scene.wagAnim.fromm > context.scene.wagAnim.to:
            context.scene.wagAnim.fromm = context.scene.wagAnim.to
        for x in bn:
            x.id_data.data.bones[x.name].select = True
            if (context.scene.wagAnim.x):
                bpy.ops.transform.rotate(value=math.radians(0.5* power), orient_axis='X')
            if (context.scene.wagAnim.y):
                bpy.ops.transform.rotate(value=math.radians(0.5* power), orient_axis='Y')
            if (context.scene.wagAnim.z):
                bpy.ops.transform.rotate(value=math.radians(0.5* power), orient_axis='Z')
            x.id_data.data.bones[x.name].select = False     
        bpy.context.window_manager.popup_menu(oops, title="ATTENTION", icon='ERROR')
        self.report({'INFO'}, 'Undo before baking!!!')
        return {'FINISHED'}
class wagAnimSettings(PropertyGroup):
    power : IntProperty(
        name = "Power",
        description = "Power of the wag",
        default = 1,
        step = 1,
        min = 1,
        max = 50
        )
    curl : IntProperty(
        name = "Curl",
        description = "Curl of the wag",
        default = 1,
        step = 1,
        min = 1,
        max = 500
        )
    offset : IntProperty(
        name = "Offset",
        description = "Offset of the wag",
        default = 1,
        step = 1,
        min = 1,
        max = 500
        )
    speed : IntProperty(
        name = "speed",
        description = "slow down the wag",
        default = 1,
        step = 1,
        min = 1,
        max = 500
        )
    fromm : IntProperty(
        name = "From: ",
        description = "slow down the wag",
        default = 1,
        step = 1,
        min = -100,
        max = 5000
        )
    to : IntProperty(
        name = "To: ",
        description = "slow down the wag",
        default = 1,
        step = 1,
        min = -100,
        max = 5000
        )
    x : BoolProperty(
        name = "X axis",
        description = "X axis",
        default = False
        )
    y : BoolProperty(
        name = "Y axis",
        description = "Y axis",
        default = False
        )
    z : BoolProperty(
        name = "Z axis",
        description = "Z axis",
        default = True
        )
    frr : BoolProperty(
        name = "Use Frame Range",
        description = "use a frame range",
        default = True
        )

#Classes
classes = (
    WagPannel,
    WAG_OT_Create,
    test,
    wagAnimSettings
    )
register, unregister = bpy.utils.register_classes_factory(classes)

# Register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.wagAnim = PointerProperty(type=wagAnimSettings)

# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.wagAnim

if __name__ == "__main__":
    register()
