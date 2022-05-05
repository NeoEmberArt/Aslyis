##############################################################################
#Version 3
# whats new:
# • Use a set frame range
# • Animate whether or not the calculation should run - keyframeable value
# • UI changes
# • Unused settings removed
# • Fixed a rare "divide by zero" error
# • Performance update
###############################################################################
bl_info = {
    "name": "SnakeMotion",
    "description": "Create a serptent animation faster than ever",
    "author": "NeoEmberArts",
    "version": (1, 3),
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
    if len(nodes) == 3: #?
        distanceRate = distance([nodes[0][0],nodes[0][1],nodes[0][2]],[nodes[1][0],nodes[1][1],nodes[1][2]], False)
    # if len(nodes) > 1 and subdivision > 1 and iteration < len(ctrlN)-2:
    #     for tr in range(1, int(distanceRate/(distanceRate/2.00**subdivision) - 2)):
    #         inc = (distanceRate*subdivision) / 2 ** subdivision
    #         objects.append("phantom")
    #         nodes.insert(0,[
    #             nodes[len(nodes)-2][0] + (inc * tr),
    #             nodes[len(nodes)-2][1] + (inc * tr),
    #             nodes[len(nodes)-2][2] + (inc * tr)
    #         ])
    # iteration = iteration + 1

#distance between 3 or 1 vector positions
def distance(v1, v2, single):
    if single:
        return math.sqrt((v2**2) - (v1**2))
    else:
        return math.sqrt(((v2[0] - v1[0])**2) + ((v2[1] - v1[1])**2) + ((v2[2] - v1[2])**2))
 
#used to calculate the distance to travel based on the heads position. Set position reletive to the control
def CalcDist3D(control, node): #DOES NOT DO WELL WITH 0/0
    global nodes
    mp = 0
    if getMouseProg(control) == 0:
        mp = 0
    elif distanceRate == 0:
        mp = 0
    else:
        mp = (getMouseProg(control))/distanceRate
    current = nodes[node]
    #dist = [distance(control[0], nodes[len(nodes)-1][0], True), distance(control[1], nodes[len(nodes)-1][1], True), distance(control[2], nodes[len(nodes)-1][2], True)];
    return [
        nodes[node-1][0] + ((nodes[node][0] - nodes[node-1][0]) * mp),
         nodes[node-1][1] + ((nodes[node][1] - nodes[node-1][1]) * mp),
          nodes[node-1][2] + ((nodes[node][2] - nodes[node-1][2]) * mp)
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
        #col.operator("animation.cancel", text="LOG", icon="CANCEL")
        if wassetup:
            col.operator("animation.cancel", text="CANCEL", icon="CANCEL")
            col.label(text="Settings")
            col.prop(settings, 'keyframe_frequency_setting')
            #col.prop(settings, 'frame_subdivisions')
            col.label(text="Automation")
            col.prop(settings, 'cr')
            if context.scene.snakeAnim.cr:
                col.prop(settings, 'running')
            col.label(text="Frame Range")
            col.prop(settings, 'frr')
            if context.scene.snakeAnim.frr:
                row.prop(settings, 'fromm')
                row.prop(settings, 'to')
            layout.use_property_split = True
            layout.use_property_decorate = False
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)
            col = flow.column()
            row = layout.row(align=True)
            row.scale_y = 1.5
            col.label(text="Actions")
            row.operator("animation.unhide", text="Unhide", icon="HIDE_OFF")
            row.operator("animation.create", text="BAKE", icon="SEQ_LUMA_WAVEFORM")
        else:
            col.label(text="Setup")
            col.operator("animation.setup", text="SETUP", icon="SEQ_CHROMA_SCOPE")
#Setup Button
class snakeCancel(Operator):
    bl_idname = "animation.cancel"
    bl_label = "Cancel Setup"
    bl_description = "Cancel the Setup Process - not recommended"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context) -> bool:
        return True
    def execute(self, context):
        # print(objects)
        # print(nodes)
        # print(distanceRate)
        global wassetup
        wassetup = False
        self.report({'INFO'}, 'Canceled Setup - Empties may still be hidden')
        return {'FINISHED'}
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
        self.report({'INFO'}, 'Setup complete')
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
        self.report({'INFO'}, 'Showing all empties')
        return {'FINISHED'}
#bake the movement by using the function i made. 5+ weeks to get it perfect; Original code hosted here using JS: https://studio.code.org/projects/applab/LQglV4YzaiBRxzp6lHQ3vHNv7kU4Zu5BAJUySyigr4c     
def bake(keyframefreq, subdiv):
    #go to first frame
    s = bpy.context.scene.frame_start
    f = bpy.context.scene.frame_end
    if bpy.context.scene.snakeAnim.frr:
        s = bpy.context.scene.snakeAnim.fromm
        f = bpy.context.scene.snakeAnim.to + 1
    bpy.context.scene.frame_current = s
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)
    for i in range(s,f):
        if (bpy.context.scene.snakeAnim.running or bpy.context.scene.snakeAnim.cr == False):
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
                if len(nodes) > (len(objects)+1):
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
        global distanceRate
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
        #distanceRate = distanceRate / frame_subdivisions
        bake(keyframe_frequency_setting, "frame_subdivisions")
        self.report({'INFO'}, 'Animation complete')
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
        name = "Keyframe Subdivisions",
        description = "Increase the acuracy of the animation if the snake moves more than the distance between the length of the bones in a single frame - will double the amount of calculations each iteration",
        default = 1,
        step = 1,
        min = 1,
        max = 500
        )
    frr : BoolProperty(
        name = "Use Frame Range",
        description = "Only run SnakeMotion durring a set frame range rather than from the start frame to the end",
        default = True
        )
    cr : BoolProperty(
        name = "Animated",
        description = "Animate Calculation Switch",
        default = False
        )
    running : BoolProperty(
        name = "Is Running",
        description = "Animate this value - Turns SnakeMotion on and off at specified frames",
        default = True
        )
    fromm : IntProperty(
        name = "From: ",
        description = "Start frame",
        default = 1,
        step = 1,
        min = -100,
        max = 5000
        )
    to : IntProperty(
        name = "To: ",
        description = "End frame",
        default = 2,
        step = 1,
        min = -100,
        max = 5000
        )
#Classes
classes = (
    SnakeMotionPT,
    snakeCancel,
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
