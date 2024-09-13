bl_info = {
    "name": "To-Do List Add-on",
    "description": "A simple task management system for Blender with Firebase integration.",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "3D View > Sidebar > To-Do List",
    "warning": "Public Demo - BETA", 
    "doc_url": "https://youtu.be/v96W-lCEZ6w", 
    "tracker_url": "https://github.com/NeoEmberArt/Aslyis/issues?q=is%3Aissue+is%3Aopen",
    "support": "COMMUNITY",  # Can be 'OFFICIAL', 'COMMUNITY', or 'TESTING'
    "category": "3D View",
    "author": "NeoEmberArts"
}

#MAIN CODE
import bpy
import subprocess
import sys
import webbrowser


# Ensure requests is installed in Blender's Python environment
try:
    import requests
except ImportError:
    # Install the requests package using Blender's Python interpreter
    subprocess.check_call([bpy.app.binary_path_python, "-m", "pip", "install", "requests"])
    import requests  # Retry importing after installation

import json
tasks_cache = {}
cache = {}
cached = False
# Firebase configuration
DEFAULT_FIREBASE_URL = "https://neocomm-79cc3-default-rtdb.firebaseio.com/tasks.json"

class TODOListAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    firebase_url: bpy.props.StringProperty(
        name="Firebase URL",
        description="Enter the Firebase Realtime Database URL",
        default="",
    )
    firebase_rules: bpy.props.StringProperty(
        name="Firebase Security Rules",
        description="Paste Firebase security rules here",
        default='{"rules": {".read": true,".write": true}}'
    )
    step: bpy.props.IntProperty(default=1)
    def draw(self, context):
        layout = self.layout
        # Step 1: Create Firebase Project
        if self.step == 1:
            layout.label(text="Step 1: Create Firebase Project")
            row = layout.row()
            row.operator("wm.visit_firebase", text="Visit Firebase")
            row.operator("wm.next_step", text="Done")

        # Step 2: Create Realtime Database
        elif self.step == 2:
            layout.label(text="Step 2: Create a Realtime Database")
            row = layout.row()
            row.operator("wm.visit_tutorial", text="Tutorial")
            row.operator("wm.next_step", text="Done")

        # Step 3: Set Database Rules and URL
        elif self.step == 3:
            layout.label(text="Step 3: Set Rules and Enter Firebase URL")
            layout.label(text="Copy and Paste the following security rules")
            layout.prop(self, "firebase_rules", text="Firebase Security Rules")
            layout.prop(self, "firebase_url", text="Firebase URL here: ")
            layout.operator("wm.refresh_database", text="Save and load database")

        # Step 4: Choose to Import Demo Data or Use Empty Database
        elif self.step == 4:
            layout.label(text="Step 4: Choose to Import Demo Data or Use Empty Database")
            row = layout.row()
            row.operator("wm.import_demo_data", text="Import Demo Data")
            row.operator("wm.use_empty_database", text="Use Empty Database")

        # Final Step: Enter Firebase URL and Refresh Database
        elif self.step == 5:
            layout.prop(self, "firebase_url", text="Firebase URL")
            #layout.prop(self, "username", text="Username")
            #layout.operator("wm.refresh_database", text="Refresh Database")


# Operator to go to Firebase Console
class WM_OT_VisitFirebase(bpy.types.Operator):
    bl_idname = "wm.visit_firebase"
    bl_label = "Visit Firebase Console"

    def execute(self, context):
        webbrowser.open("https://console.firebase.google.com/")
        return {'FINISHED'}


# Operator to go to tutorial (YouTube link)
class WM_OT_VisitTutorial(bpy.types.Operator):
    bl_idname = "wm.visit_tutorial"
    bl_label = "Visit Realtime Database Tutorial"

    def execute(self, context):
        webbrowser.open("https://youtu.be/v96W-lCEZ6w")
        return {'FINISHED'}


# Operator to advance to the next step in the preferences
class WM_OT_NextStep(bpy.types.Operator):
    bl_idname = "wm.next_step"
    bl_label = "Next Step"

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__name__].preferences
        prefs.step += 1
        return {'FINISHED'}

def ensure_demo_data():
    global cached
    cached = False
    tasks = load_tasks()
    cached = False
    if not tasks or not any(tasks.values()):
        print("No tasks found or tasks are empty, posting demo data.")
        firebase_url = get_firebase_url()
        response = requests.put(firebase_url, json=json.loads(demo_data))
    else:
        print("Tasks are already present in Firebase.")

# Operator to refresh database (placeholder function)
class WM_OT_RefreshDatabase(bpy.types.Operator):
    bl_idname = "wm.refresh_database"
    bl_label = "Refresh Database"

    def execute(self, context):
        # Placeholder function for refreshing the database
        self.report({'INFO'}, "Database Refreshed ()")
        prefs = bpy.context.preferences.addons[__name__].preferences
        prefs.step=5
        new_url = get_firebase_url()
        ensure_demo_data()
        print(f"Updated Firebase URL: {new_url}")
        # Clear cache and refresh tasks with the new URL
        global tasks_cache
        tasks_cache.clear()  # Clear the cache
        global cached
        cached = False
        load_tasks() 
        self.report({'INFO'}, "Tasks refreshed from Firebase")
        return {'FINISHED'}


# Operator to import demo data
class WM_OT_ImportDemoData(bpy.types.Operator):
    bl_idname = "wm.import_demo_data"
    bl_label = "Import Demo Data"
    def execute(self, context):
        # Placeholder function for importing demo data
        self.report({'INFO'}, "Importing Demo Data (placeholder)")
        prefs = bpy.context.preferences.addons[__name__].preferences
        prefs.step = 5
        return {'FINISHED'}


# Operator to use an empty database
class WM_OT_UseEmptyDatabase(bpy.types.Operator):
    bl_idname = "wm.use_empty_database"
    bl_label = "Use Empty Database"

    def execute(self, context):
        # Placeholder function for using an empty database
        self.report({'INFO'}, "Using Empty Database (placeholder)")
        prefs = bpy.context.preferences.addons[__name__].preferences
        prefs.step = 5
        # Get the updated Firebase URL
        new_url = get_firebase_url()
        print(f"Updated Firebase URL: {new_url}")
        # Clear cache and refresh tasks with the new URL
        global tasks_cache
        tasks_cache.clear()  # Clear the cache
        load_tasks()  # Reload tasks from the new Firebase URL
        self.report({'INFO'}, "Firebase URL updated and tasks reloaded.")
        return {'FINISHED'}

# Demo data as a string
demo_data = '''
{
    "assignment": [
      {
        "completed": false,
        "description": "THISSSS Description",
        "title": "Default Task",
        "priority": "Low"
      }
    ],
    "completed": [
      {
        "claimed_by": "User A",
        "description": "Default Description",
        "title": "Default Completed Task",
        "priority": "Medium"
      }
    ],
    "in_progress": [
      {
        "completed": false,
        "description": "Default Description",
        "title": "Default In Progress Task",
        "priority": "High"
      }
    ]
}
'''
def load_tasks():
    global cached
    global cache
    
    if cached:
        if isinstance(cache, dict) and 'tasks' in cache:
            return cache['tasks']
        return cache
    else:
        firebase_url = get_firebase_url()
        try:
            response = requests.get(firebase_url)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'tasks' in data:
                    cache = data['tasks']
                else:
                    cache = data
                cached = True
                return cache
            else:
                print("Failed to load tasks from Firebase")
                return {}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}
# Helper functions to load and save tasks from Firebase
def get_firebase_url():
    prefs = bpy.context.preferences.addons[__name__].preferences
    return prefs.firebase_url + "/tasks.json"



def save_tasks(tasks):
    firebase_url = get_firebase_url()
    response = requests.put(firebase_url, json=tasks)
    if response.status_code == 200:
        print("Tasks successfully saved to Firebase")
    else:
        print("Failed to save tasks to Firebase")



class TODOListSettings(bpy.types.PropertyGroup):
    current_tab: bpy.props.StringProperty(name="Current Tab", default="assignment")
    current_task_id: bpy.props.IntProperty(name="Current Task ID", default=-1)
    task_title: bpy.props.StringProperty(name="Task Title", default="")
    task_description: bpy.props.StringProperty(name="Task Description", default="")
    task_priority: bpy.props.StringProperty(name="Task Priority", default="")

class TODORefreshTasksOperator(bpy.types.Operator):
    bl_idname = "todo.refresh_tasks"
    bl_label = "Refresh Tasks"

    def execute(self, context):
        ensure_demo_data()
        new_url = get_firebase_url()
        print(f"Updated Firebase URL: {new_url}")
        # Clear cache and refresh tasks with the new URL
        global tasks_cache
        tasks_cache.clear()  # Clear the cache
        global cached
        cached = False
        load_tasks() 
        self.report({'INFO'}, "Tasks refreshed from Firebase")
        return {'FINISHED'}



class TODOListPanel(bpy.types.Panel):
    bl_label = "To-Do List"
    bl_idname = "PT_TODO_LIST"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'To-Do List'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.todo_list_settings
        current_tab = settings.current_tab
        current_task_id = settings.current_task_id
        layout.operator(WM_OT_RefreshTasks.bl_idname, text="Refresh Tasks")
        if current_task_id == -1:  # No task selected, show the task list
            row = layout.row(align=True)
            for tab_name in ['assignment', 'in_progress', 'completed']:
                if tab_name == current_tab:
                    row.operator("todo.set_tab", text=tab_name.title(), emboss=True, icon='CHECKMARK').tab_name = tab_name
                else:
                    row.operator("todo.set_tab", text=tab_name.title()).tab_name = tab_name

            tasks = load_tasks()
            if current_tab == 'assignment':
                self.draw_column(layout, "Assignment", tasks.get('assignment', []), "todo.view_task", "todo.claim_task")
            elif current_tab == 'in_progress':
                self.draw_column(layout, "In Progress", tasks.get('in_progress', []), "todo.view_task", "todo.complete_task")
            elif current_tab == 'completed':
                self.draw_column(layout, "Completed", tasks.get('completed', []), "todo.view_task")
        else:
            task = self.load_task(settings.current_task_id, settings.current_tab)
            if task:
                box = layout.box()
                box.label(text=f"Title: {task.get('title', 'N/A')}")
                box = layout.box()
                box.label(text=f"Priority: {task.get('priority', 'N/A')}")

                # Create a box for description with text wrapping
                box = layout.box()
                box.label(text="Description:")
                text_box = box.box()
                text_box.label(text=task.get('description', 'No Description'), icon='TEXT')
                text_box.scale_y = 2.0  # Adjust for vertical space if needed

                row = layout.row()
                row.operator("todo.back_to_list", text="Back")
                if current_tab == 'assignment':
                    row.operator("todo.claim_task", text="Claim").task_id = settings.current_task_id
                elif current_tab == 'in_progress':
                    row.operator("todo.complete_task", text="Complete").task_id = settings.current_task_id

    def draw_column(self, layout, column_title, tasks, *operator_ids):
        col = layout.column()
        col.label(text=column_title)
        box = col.box()  # Frame the column
        box.label(text="Tasks")
        for task_id, task in enumerate(tasks):
            row = box.row(align=True)
            task_title = task.get('title', 'No Title')
            task_priority = task.get('priority', 'N/A')

            # Create a row with title and priority
            title_row = row.row(align=True)
            title_row.label(text=task_title, icon='TEXT')  # Title with an icon
            
            # Add priority box beside the title
            priority_box = title_row.box()
            priority_box.label(text=f"{task_priority}", icon='INFO')

            for operator_id in operator_ids:
                op = row.operator(operator_id, text=operator_id.split('.')[-1].replace('_', ' ').title())
                op.task_id = task_id

    def load_task(self, task_id, category):
        tasks = load_tasks()
        if category in tasks and 0 <= task_id < len(tasks[category]):
            return tasks[category][task_id]
        return None

class WM_OT_RefreshTasks(bpy.types.Operator):
    bl_idname = "wm.refresh_tasks"
    bl_label = "Refresh Tasks"

    def execute(self, context):
        global cached
        cached = False
        load_tasks()
        self.report({'INFO'}, "Tasks have been refreshed.")
        return {'FINISHED'}


        
class TODOAdminPanel(bpy.types.Panel):
    bl_label = "Admin Panel"
    bl_idname = "PT_TODO_ADMIN"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'To-Do List'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.todo_list_settings
        current_tab = settings.current_tab

        # Load tasks from your defined function
        tasks = load_tasks()

        # Check if the current tab has tasks
        if current_tab in tasks:
            task_list = tasks[current_tab]

            for idx, task in enumerate(task_list):
                row = layout.row()
                row.label(text=f"Task: {task.get('title', 'No Title')}")

                # Operators for moving tasks
                row.operator("todo.admin_move_task_up", text="Up").task_index = idx
                row.operator("todo.admin_move_task_down", text="Down").task_index = idx
                row.operator("todo.move_task_left", text="Left").task_id = idx
                row.operator("todo.move_task_right", text="Right").task_id = idx



class TODOAdminMoveTaskUpOperator(bpy.types.Operator):
    bl_idname = "todo.admin_move_task_up"
    bl_label = "Move Task Up"
    task_index: bpy.props.IntProperty()

    def execute(self, context):
        tasks = load_tasks()
        current_tab = context.scene.todo_list_settings.current_tab
        
        if current_tab not in tasks:
            return {'CANCELLED'}

        task_list = tasks[current_tab]
        if self.task_index > 0:
            # Swap with the task above
            task_list[self.task_index], task_list[self.task_index - 1] = task_list[self.task_index - 1], task_list[self.task_index]
            save_tasks(tasks)
            return {'FINISHED'}
        return {'CANCELLED'}

class TODOAdminMoveTaskDownOperator(bpy.types.Operator):
    bl_idname = "todo.admin_move_task_down"
    bl_label = "Move Task Down"
    task_index: bpy.props.IntProperty()

    def execute(self, context):
        tasks = load_tasks()
        current_tab = context.scene.todo_list_settings.current_tab
        
        if current_tab not in tasks:
            return {'CANCELLED'}

        task_list = tasks[current_tab]
        if self.task_index < (len(task_list) - 1):
            # Swap with the task below
            task_list[self.task_index], task_list[self.task_index + 1] = task_list[self.task_index + 1], task_list[self.task_index]
            save_tasks(tasks)
            return {'FINISHED'}
        return {'CANCELLED'}



class TODOAdminMoveTaskLeftOperator(bpy.types.Operator):
    bl_idname = "todo.move_task_left"
    bl_label = "Move Task Left"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        global cached
        cached = False
        tasks = load_tasks()
        
        if settings.current_tab == 'in_progress':
            task = tasks['in_progress'].pop(self.task_id)
            # Check for 'assignment'; if it doesn't exist, initialize it
            if 'assignment' not in tasks:
                tasks['assignment'] = []
            tasks['assignment'].append(task)
        elif settings.current_tab == 'completed':
            task = tasks['completed'].pop(self.task_id)
            # Check for 'in_progress'; if it doesn't exist, initialize it
            if 'in_progress' not in tasks:
                tasks['in_progress'] = []
            tasks['in_progress'].append(task)
        elif settings.current_tab == 'assignment':
            tasks['assignment'].pop(self.task_id)

        save_tasks(tasks)
        return {'FINISHED'}



class TODOAdminMoveTaskRightOperator(bpy.types.Operator):
    bl_idname = "todo.move_task_right"
    bl_label = "Move Task Right"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        global cached
        cached = False
        tasks = load_tasks()
        
        if settings.current_tab == 'assignment':
            task = tasks['assignment'].pop(self.task_id)
            # Check for 'in_progress'; if it doesn't exist, initialize it
            if 'in_progress' not in tasks:
                tasks['in_progress'] = []
            tasks['in_progress'].append(task)
        elif settings.current_tab == 'in_progress':
            task = tasks['in_progress'].pop(self.task_id)
            # Check for 'completed'; if it doesn't exist, initialize it
            if 'completed' not in tasks:
                tasks['completed'] = []
            tasks['completed'].append(task)
        elif settings.current_tab == 'completed':
            tasks['completed'].pop(self.task_id)

        save_tasks(tasks)
        return {'FINISHED'}


class TODOCreateTaskPanel(bpy.types.Panel):
    bl_label = "Task Creator"
    bl_idname = "PT_TODO_CREATE_TASK"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'To-Do List'

    def draw(self, context):
        layout = self.layout

        # Task Creator UI Elements
        row = layout.row()
        row.prop(context.scene, "task_title", text="Title")

        row = layout.row()
        row.prop(context.scene, "task_description", text="Description")

        row = layout.row()
        row.prop(context.scene, "task_priority", text="Priority")

        row = layout.row()
        row.operator("todo.add_task", text="Add")


class TODOAddTaskOperator(bpy.types.Operator):
    bl_idname = "todo.add_task"
    bl_label = "Add Task"

    def execute(self, context):
        # Retrieve task input values from the scene
        title = context.scene.task_title
        description = context.scene.task_description
        priority = context.scene.task_priority

        # Check for necessary values (not empty)
        if not title:
            self.report({'WARNING'}, "Task title cannot be empty.")
            return {'CANCELLED'}
        if not priority:
            self.report({'WARNING'}, "Task priority cannot be empty.")
            return {'CANCELLED'}

        global cached
        cached = False
        tasks = load_tasks()

        # Ensure 'assignment' exists
        if 'assignment' not in tasks:
            tasks['assignment'] = []

        # Create the new task object
        new_task = {
            'title': title,
            'description': description,
            'priority': priority,
            'completed': False
        }

        # Append the new task to the 'assignment' list
        tasks['assignment'].append(new_task)

        # Save tasks to Firebase
        save_tasks(tasks)

        # Reset input fields, using a valid default for priority
        context.scene.task_title = ""
        context.scene.task_description = ""
        context.scene.task_priority = 'Medium'  # Set to a valid enum value

        return {'FINISHED'}



class TODOSetTabOperator(bpy.types.Operator):
    bl_idname = "todo.set_tab"
    bl_label = "Set Tab"
    tab_name: bpy.props.StringProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        settings.current_tab = self.tab_name
        return {'FINISHED'}


class TODOViewTaskOperator(bpy.types.Operator):
    bl_idname = "todo.view_task"
    bl_label = "View Task"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        settings.current_task_id = self.task_id
        return {'FINISHED'}


class TODOBackToListOperator(bpy.types.Operator):
    bl_idname = "todo.back_to_list"
    bl_label = "Back to List"

    def execute(self, context):
        settings = context.scene.todo_list_settings
        settings.current_task_id = -1  # Reset task view
        return {'FINISHED'}


class TODOClaimTaskOperator(bpy.types.Operator):
    bl_idname = "todo.claim_task"
    bl_label = "Claim Task"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        task_id = self.task_id
        global cached
        cached = False
        tasks = load_tasks()
        task = tasks['assignment'].pop(task_id)
        tasks['in_progress'].append(task)
        save_tasks(tasks)
        return {'FINISHED'}


class TODOCompleteTaskOperator(bpy.types.Operator):
    bl_idname = "todo.complete_task"
    bl_label = "Complete Task"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        task_id = self.task_id
        global cached
        cached = False
        tasks = load_tasks()
        task = tasks['in_progress'].pop(task_id)
        tasks['completed'].append(task)
        save_tasks(tasks)
        return {'FINISHED'}

# Operator to handle preference change and update the database with the new URL
class TODOUpdateFirebaseURLOperator(bpy.types.Operator):
    bl_idname = "todo.update_firebase_url"
    bl_label = "Update Firebase URL"

    def execute(self, context):
        # Get the updated Firebase URL
        new_url = get_firebase_url()
        print(f"Updated Firebase URL: {new_url}")

        # Clear cache and refresh tasks with the new URL
        global tasks_cache
        tasks_cache.clear()  # Clear the cache
        global cached
        cached = False
        load_tasks()  # Reload tasks from the new Firebase URL
        self.report({'INFO'}, "Firebase URL updated and tasks reloaded.")
        return {'FINISHED'}



# Registration
classes = (
    WM_OT_VisitFirebase,
    WM_OT_VisitTutorial,
    WM_OT_NextStep,
    WM_OT_RefreshDatabase,
    WM_OT_ImportDemoData,
    WM_OT_UseEmptyDatabase,
    WM_OT_RefreshTasks,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(TODOListSettings)
    bpy.utils.register_class(TODORefreshTasksOperator)
    bpy.utils.register_class(TODOListPanel)
    bpy.utils.register_class(TODOAdminPanel)
    bpy.utils.register_class(TODOCreateTaskPanel)
    bpy.utils.register_class(TODOAddTaskOperator)
    bpy.utils.register_class(TODOSetTabOperator)
    bpy.utils.register_class(TODOViewTaskOperator)
    bpy.utils.register_class(TODOBackToListOperator)
    bpy.utils.register_class(TODOClaimTaskOperator)
    bpy.utils.register_class(TODOCompleteTaskOperator)
    bpy.utils.register_class(TODOAdminMoveTaskUpOperator)
    bpy.utils.register_class(TODOAdminMoveTaskDownOperator)
    bpy.utils.register_class(TODOAdminMoveTaskLeftOperator)
    bpy.utils.register_class(TODOAdminMoveTaskRightOperator)
    bpy.utils.register_class(TODOListAddonPreferences)
    

    bpy.types.Scene.todo_list_settings = bpy.props.PointerProperty(type=TODOListSettings)

    # Register properties for Task Creator
    bpy.types.Scene.task_title = bpy.props.StringProperty(name="Task Title", default="")
    bpy.types.Scene.task_description = bpy.props.StringProperty(name="Task Description", default="")
    bpy.types.Scene.task_priority = bpy.props.EnumProperty(
        name="priority",
        items=[('Low', "Low", ""),
               ('Medium', "Medium", ""),
               ('High', "High", "")]
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(TODOListSettings)
    bpy.utils.unregister_class(TODOListPanel)
    bpy.utils.unregister_class(TODOAdminPanel)
    bpy.utils.unregister_class(TODOCreateTaskPanel)
    bpy.utils.unregister_class(TODOAddTaskOperator)
    bpy.utils.unregister_class(TODOSetTabOperator)
    bpy.utils.unregister_class(TODOViewTaskOperator)
    bpy.utils.unregister_class(TODOBackToListOperator)
    bpy.utils.unregister_class(TODOClaimTaskOperator)
    bpy.utils.unregister_class(TODOCompleteTaskOperator)
    bpy.utils.unregister_class(TODOAdminMoveTaskUpOperator)
    bpy.utils.unregister_class(TODOAdminMoveTaskDownOperator)
    bpy.utils.unregister_class(TODOAdminMoveTaskLeftOperator)
    bpy.utils.unregister_class(TODOAdminMoveTaskRightOperator)
    bpy.utils.unregister_class(TODOListAddonPreferences)
    bpy.utils.unregister_class(TODORefreshTasksOperator)

    del bpy.types.Scene.todo_list_settings
    del bpy.types.Scene.task_title
    del bpy.types.Scene.task_description
    del bpy.types.Scene.task_priority

if __name__ == "__main__":
    register()
