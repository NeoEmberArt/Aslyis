##############################################################################
#Version 2
# whats new:
# • Set-up no longer moves the armature
# • When you click "Setup"
#     -  You are put the frame 1 (or start frame)
#     -  A keyframe is applied to the driver/first empty
# • Bake
#     -  The movement is perfect and all bugs have been fixed (Start jitter, Control/Driver name [no longer needed, automatically added], modifiers set to wrong object)
#     -  Keyframe Offset works now (Subdivisions doesn't yet but will soon)
# • Faster calculation meaning you can bake in around 6 seconds or less with 250 frames (based on testing with an MSI GL65 Leopard)
# • Random bug found when selected a few bones with diferent or random names. May or may not be fixed
# • UI bug fixed (Number inputs are now integers rather than floats)
# • Tutorial/Documentation created
# • Variable names finalized
# • Baking now bakes from the start frame till the end rather than frame 0
# • Comments added everywhere
###############################################################################
bl_info = {
    "name": "SnakeMotion",
    "description": "Create a serptent animation faster than ever",
    "author": "NeoEmberArts",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View 3D > Properties Panel",
    "doc_url": "https://github.com/NeoEmberArt/Aslyis/blob/main/Addons/SnakeMotionTutorial.md",
    "tracker_url": "https://github.com/NeoEmberArt/Aslyis/issues",
    "support": "COMMUNITY",
    "category": "Animation",
}
# Libraries
import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup
from array import *
import math

#global variables
#armature name
armN = "NA"
#armature scale before setup
armS = (0,0,0)
#control point names
ctrlN = []
#For the buttons
wassetup = False
objectsHidden = False
#array to store all node positions
nodes = []
#list of all object names
objects = []
#Distance before anouther node should be spawned/added
distanceRate = 0.0
framee = 0

#functions
def init(name):
    global objects
    global nodes
    global distanceRate
    objects.append(str(name))
    nodes.insert(0, [bpy.data.objects[name].location.x, bpy.data.objects[name].location.y, bpy.data.objects[name].location.z])
    #if there are enough objects calculate the distance Rate
    if len(nodes) == 3:
        distanceRate = distance([nodes[0][0],nodes[0][1],nodes[0][2]],[nodes[1][0],nodes[1][1],nodes[1][2]], False)
 
 
#distance between 3 or 1 vector positions
def distance(v1, v2, single):
    if single:
        return math.sqrt((v2**2) - (v1**2))
    else:
        return math.sqrt(((v2[0] - v1[0])**2) + ((v2[1] - v1[1])**2) + ((v2[2] - v1[2])**2))
 
           
                                               
#used to calculate the distance to travel based on the heads position. Set position reletive to the control
def CalcDist3D(control, node):
    global nodes
    current = nodes[node]
    #dist = [distance(control[0], nodes[len(nodes)-1][0], True), distance(control[1], nodes[len(nodes)-1][1], True), distance(control[2], nodes[len(nodes)-1][2], True)];
    return [
        nodes[node-1][0] + ((nodes[node][0] - nodes[node-1][0]) * (getMouseProg(control))/distanceRate),
         nodes[node-1][1] + ((nodes[node][1] - nodes[node-1][1]) * (getMouseProg(control))/distanceRate),
          nodes[node-1][2] + ((nodes[node][2] - nodes[node-1][2]) * (getMouseProg(control))/distanceRate)
        ]
   
#get head/control progress/percentage it is to reaching the distanceRate
def getMouseProg(mouse):
    global nodes
    return distance(mouse, [
        nodes[len(nodes)-1][0],
         nodes[len(nodes)-1][1],
          nodes[len(nodes)-1][2]],
           False)
 
#move an object and apply a keyframe
def move(name, position, keyframefreq, d):
    global framee
    bpy.data.objects[name].location = (position[0], position[1], position[2])
    if d == 0:
        framee = framee + 1
    if framee >= keyframefreq: #apply keyframe when needed
        bpy.data.objects[name].select_set(True)
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.data.objects[name].select_set(False)
        if d >= len(objects)-1:
            framee = 0

# Panel
class SnakeMotionPT(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "SnakeMotion"
    bl_category = "Snake Animation"
    def draw(self, context):
        #create elements
        scn = context.scene
        settings = scn.snakeAnim
        layout = self.layout
        col = layout.column(align=True)
        row = layout.row(align=True)
        row.scale_y = 1.5
        col.operator("animation.setup", text="SETUP", icon="SEQ_CHROMA_SCOPE")
        col.prop(settings, 'keyframe_frequency_setting')
        col.prop(settings, 'frame_subdivisions')
        layout.use_property_split = True
        layout.use_property_decorate = False
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)
        col = flow.column()
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("animation.unhide", text="Unhide", icon="HIDE_OFF")
        row.operator("animation.create", text="BAKE", icon="SEQ_LUMA_WAVEFORM")
#Setup Button
class SNAKE_OT_Setup(Operator):
    bl_idname = "animation.setup"
    bl_label = "setup for Animation"
    bl_description = "Setup the armature automaticly; Select the bones you want to setup and then click \"SETUP\""
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    #if in pose mode and more than 1 bone is selected
    def poll(cls, context) -> bool:
        return bpy.context.mode == "POSE" and len(bpy.context.selected_pose_bones) > 1
    def execute(self, context):
        global wassetup
        global armN
        global armS
        global ctrlN
        global objectsHidden
        objectsHidden = True
        wassetup = True
        keyframe_frequency_setting = context.scene.snakeAnim.keyframe_frequency_setting
        frame_subdivisions = context.scene.snakeAnim.frame_subdivisions
        boneN = []
        tailPos = []
        #reset variables in case they were allready used
        ctrlN = []
        armN = "None"
        armS = (0,0,0)
        # Get a list of selected objects
        bn = bpy.context.selected_pose_bones
        #go through each bone and get their tail position and reference
        for x in bn:
            boneN.append(x)
            tailPos.append(x.tail)
            #x.bone.select = False
        #get armature name
        armN = bpy.context.selected_objects[0].name
        #get the root bone's head position
        o = bn[0].head
        #get out of pose mode
        bpy.ops.object.posemode_toggle()
        #add empty's to each bone tail postions
        for y in range(len(tailPos)):
            bpy.ops.object.empty_add(type='SPHERE', align='WORLD', location=tailPos[y] , scale=(1, 1, 1))
            bpy.context.object.name = "SnakeCtrl_"+ str(y)
            ctrlN.append("SnakeCtrl_"+ str(y))
        #Create an empty for the movement of the entire armature using the position of the root bone's head position
        bpy.ops.object.empty_add(type='SPHERE', align='WORLD', location=o , scale=(1, 1, 1))
        bpy.context.object.name = "SnakeCtrl_MAIN"
        ctrlN.insert(0,"SnakeCtrl_MAIN")
        #deselect everything
        bpy.ops.object.select_all(action='DESELECT')
        #select the armature
        objectToSelect = bpy.data.objects[armN]
        objectToSelect.select_set(True)    
        bpy.context.view_layer.objects.active = objectToSelect
        #go into pose mode
        bpy.ops.object.posemode_toggle()
        vvv = 0
        # for each bone, apply the modifier "Damped Track"
        for z in boneN:
            #If the first bone/root bone, add a modifier for the main control that moves the armature dorward
            if (vvv == 0):
                z.constraints.new(type="COPY_LOCATION")
                z.constraints["Copy Location"].target = bpy.data.objects["SnakeCtrl_MAIN"]
            #then regardless, add a damped track to the empty attatched to its tail
            z.constraints.new(type="DAMPED_TRACK")
            z.constraints["Damped Track"].target = bpy.data.objects[ctrlN[vvv+1]]
            vvv = vvv + 1
        #get out of pose mode
        bpy.ops.object.posemode_toggle()
        #go to the first frame and apply a keyframe to the main control object
        bpy.context.scene.frame_current = bpy.context.scene.frame_start
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        #deselect everything (Mainly the armature that may still be selected
        bpy.ops.object.select_all(action='DESELECT')
        #select the control that will be used to drive/guide the rest of the empties
        bpy.data.objects[ctrlN[len(ctrlN)-1]].select_set(True)
        #add a keyframe for the position of it on the first frame
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        #keep selected         bpy.data.objects[ctrlN[len(ctrlN)-1]].select_set(False)
        #Make the other empties dissapear
        for w in range(len(ctrlN)):
            if (w != len(ctrlN)-1):
                bpy.data.objects[ctrlN[w]].scale = (0,0,0)
        return {'FINISHED'}

#button to undide all the empties
class SNAKE_OT_Unhide(Operator):
    bl_idname = "animation.unhide"
    bl_label = "Unhde"
    bl_description = "Unhide all the object that where hidden after setting up the armature"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context) -> bool:
        return wassetup and objectsHidden
    def execute(self, context):
        global objectsHidden
        objectsHidden = False
        for x in ctrlN:
            bpy.data.objects[x].scale = (1,1,1)
        return {'FINISHED'}
#bake the movement by using the function i made. 5+ weeks to get it perfect; Original code hosted here using JS: https://studio.code.org/projects/applab/LQglV4YzaiBRxzp6lHQ3vHNv7kU4Zu5BAJUySyigr4c     
def bake(keyframefreq, subdiv):
    #go to first frame
    bpy.context.scene.frame_current = bpy.context.scene.frame_start
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)
    #Go through each frame from start to end
    for i in range(bpy.context.scene.frame_start,bpy.context.scene.frame_end):
        global nodes
        global objects
        #get control position
        mouse = [bpy.data.objects[controlPoint].location.x, bpy.data.objects[controlPoint].location.y, bpy.data.objects[controlPoint].location.z]
        if distance(
            [mouse[0], mouse[1], mouse[2]],
              [nodes[len(nodes)-1][0], nodes[len(nodes)-1][1], nodes[len(nodes)-1][2]],
                False
        ) >= distanceRate:
            # add a new node if the control has moved the distance between two nodes
            nodes.append([mouse[0], mouse[1], mouse[2]])
            #Use "Pooling" to remove unused data to keep things fast
            if len(nodes) > len(objects)+1:
                del nodes[0]
        #go through each object and move them
        for x in range(0, len(objects)):
            move(objects[x],CalcDist3D([mouse[0], mouse[1], mouse[2]],(len(nodes) - 1) - x), keyframefreq, x)
        #go to the next frame
        bpy.context.scene.frame_current = bpy.context.scene.frame_current +1
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)

controlPoint = "NONE"
#button to bake the animation
class SNAKE_OT_Create(Operator):
    bl_idname = "animation.create"
    bl_label = "Bake Animation"
    bl_description = "Bake the snakes animation"
    bl_options = {'REGISTER', 'UNDO'}
    #only allow press if your in object mode and the armature was set up
    @classmethod
    def poll(cls, context) -> bool:
        return (bpy.context.mode == "OBJECT") and wassetup

    def execute(self, context):
	global nodes
	global objects
	nodes = []
	objects = []
        #get settings
        keyframe_frequency_setting = context.scene.snakeAnim.keyframe_frequency_setting
        frame_subdivisions = context.scene.snakeAnim.frame_subdivisions
        global objectsHidden
        global controlPoint
        global wassetup
        wassetup = False
        objectsHidden = False
        #Unhide all the empties if not allready
        for x in ctrlN:
            bpy.data.objects[x].scale = (1,1,1)
        #get control empty/one selected after setup
        controlPoint = ctrlN[len(ctrlN)-1]
        #initiate the empties
        for x in range(len(ctrlN)-1):
            init(ctrlN[(len(ctrlN)-2) - x])
        #BAKE
        bake(keyframe_frequency_setting, 0)
        return {'FINISHED'}

# Settings
class SnakeAnimSettings(PropertyGroup):
    keyframe_frequency_setting : IntProperty(
        name = "Keyframe Frequency",
        description = "Add a keyframe every X frames",
        default = 1,
        step = 1,
        min = 1,
        max = 50
        )
    frame_subdivisions : IntProperty(
        name = "Frame Subdivisions",
        description = "Increase the acuracy of the animation if the snake moves more than the distance between the length of the bones in a single frame; will take longer",
        default = 1,
        step = 1,
        min = 1,
        max = 500
        )
#Classes
classes = (
    SnakeMotionPT,
    SNAKE_OT_Create,
    SNAKE_OT_Setup,
    SNAKE_OT_Unhide,
    SnakeAnimSettings
    )
register, unregister = bpy.utils.register_classes_factory(classes)

# Register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.snakeAnim = PointerProperty(type=SnakeAnimSettings)

# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.snakeAnim

if __name__ == "__main__":
    register()
