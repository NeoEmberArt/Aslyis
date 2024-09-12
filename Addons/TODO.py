bl_info = {
    "name": "To-Do List Add-on",
    "description": "A simple task management system for Blender with Firebase integration.",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D View > Sidebar > To-Do List",
    "warning": "Use Documentation button to go to firebase console",  # Leave empty or add warnings like "Beta version" if applicable
    "doc_url": "https://console.firebase.google.com/u/0/",  # Link to documentation or GitHub
    "tracker_url": "https://your-bug-tracker-url.com",  # Link to issue tracker if needed
    "support": "COMMUNITY",  # Can be 'OFFICIAL', 'COMMUNITY', or 'TESTING'
    "category": "3D View",
    "author": "NeoEmberArts"
}

#MAIN CODE
import bpy
import subprocess
import sys

# Ensure requests is installed in Blender's Python environment
try:
    import requests
except ImportError:
    # Install the requests package using Blender's Python interpreter
    subprocess.check_call([bpy.app.binary_path_python, "-m", "pip", "install", "requests"])
    import requests  # Retry importing after installation

import json

# Firebase configuration
DEFAULT_FIREBASE_URL = "https://projectid.firebaseio.com/tasks.json"

class TODOListAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    firebase_url: bpy.props.StringProperty(
        name="Firebase URL",
        default=DEFAULT_FIREBASE_URL,
        description="URL of the Firebase Realtime Database"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="To-Do List Add-on Settings")
        layout.prop(self, "firebase_url")

# Helper functions to load and save tasks from Firebase
def get_firebase_url():
    prefs = bpy.context.preferences.addons[__name__].preferences
    return prefs.firebase_url

# Cache for tasks
tasks_cache = {}


def load_tasks():
    global tasks_cache
    if not tasks_cache:  # Load tasks only if cache is empty
        response = requests.get(get_firebase_url())
        if response.status_code == 200:
            tasks_cache = response.json()
        else:
            print("Failed to load tasks from Firebase")
            tasks_cache = {}
    return tasks_cache

def save_tasks(tasks):
    response = requests.put(get_firebase_url(), json=tasks)
    if response.status_code == 200:
        print("Tasks successfully saved to Firebase")
    else:
        print("Failed to save tasks to Firebase")

def save_tasks(tasks):
    response = requests.put(get_firebase_url(), json=tasks)
    if response.status_code == 200:
        print("Tasks successfully saved to Firebase")
    else:
        print("Failed to save tasks to Firebase")


class TODOListSettings(bpy.types.PropertyGroup):
    current_tab: bpy.props.StringProperty(name="Current Tab", default='assignment')
    current_task_id: bpy.props.IntProperty(name="Current Task ID", default=-1)  # Use -1 as an initial value to signify no task selected


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
                box.label(text=f"Urgency: {task.get('urgency', 'N/A')}")

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
            row.label(text=task.get('title', 'No Title'), icon='TEXT')  # Title with an icon
            for operator_id in operator_ids:
                op = row.operator(operator_id, text=operator_id.split('.')[-1].replace('_', ' ').title())
                op.task_id = task_id

    def load_task(self, task_id, category):
        tasks = load_tasks()
        if category in tasks and 0 <= task_id < len(tasks[category]):
            return tasks[category][task_id]
        return None


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
        tasks = load_tasks()

        if current_tab in tasks:
            task_list = tasks[current_tab]
            for idx, task in enumerate(task_list):
                row = layout.row()
                row.label(text=f"Task: {task.get('title', 'No Title')}")

                row.operator("todo.move_task_up", text="Up").task_id = idx
                row.operator("todo.move_task_down", text="Down").task_id = idx
                row.operator("todo.move_task_left", text="Left").task_id = idx
                row.operator("todo.move_task_right", text="Right").task_id = idx


class TODOAdminMoveTaskUpOperator(bpy.types.Operator):
    bl_idname = "todo.move_task_up"
    bl_label = "Move Task Up"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        tasks = load_tasks()

        if settings.current_tab in tasks:
            tab_tasks = tasks[settings.current_tab]
            task = tab_tasks.pop(self.task_id)
            new_position = (self.task_id - 1) % len(tab_tasks)
            tab_tasks.insert(new_position, task)
            save_tasks(tasks)
            return {'FINISHED'}
        return {'CANCELLED'}


class TODOAdminMoveTaskDownOperator(bpy.types.Operator):
    bl_idname = "todo.move_task_down"
    bl_label = "Move Task Down"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        tasks = load_tasks()

        if settings.current_tab in tasks:
            tab_tasks = tasks[settings.current_tab]
            task = tab_tasks.pop(self.task_id)
            new_position = (self.task_id + 1) % len(tab_tasks)
            tab_tasks.insert(new_position, task)
            save_tasks(tasks)
            return {'FINISHED'}
        return {'CANCELLED'}


class TODOAdminMoveTaskLeftOperator(bpy.types.Operator):
    bl_idname = "todo.move_task_left"
    bl_label = "Move Task Left"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        tasks = load_tasks()

        if settings.current_tab == 'in_progress':
            task = tasks['in_progress'].pop(self.task_id)
            tasks['assignment'].append(task)
        elif settings.current_tab == 'completed':
            task = tasks['completed'].pop(self.task_id)
            tasks['in_progress'].append(task)
        elif settings.current_tab == 'assignment':  # Remove task if on the first tab
            tasks['assignment'].pop(self.task_id)

        save_tasks(tasks)
        return {'FINISHED'}


class TODOAdminMoveTaskRightOperator(bpy.types.Operator):
    bl_idname = "todo.move_task_right"
    bl_label = "Move Task Right"
    task_id: bpy.props.IntProperty()

    def execute(self, context):
        settings = context.scene.todo_list_settings
        tasks = load_tasks()

        if settings.current_tab == 'assignment':
            task = tasks['assignment'].pop(self.task_id)
            tasks['in_progress'].append(task)
        elif settings.current_tab == 'in_progress':
            task = tasks['in_progress'].pop(self.task_id)
            tasks['completed'].append(task)
        elif settings.current_tab == 'completed':  # Remove task if on the first tab
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
        row.prop(context.scene, "task_urgency", text="Urgency")

        row = layout.row()
        row.operator("todo.add_task", text="Add")


class TODOAddTaskOperator(bpy.types.Operator):
    bl_idname = "todo.add_task"
    bl_label = "Add Task"

    def execute(self, context):
        title = context.scene.task_title
        description = context.scene.task_description
        urgency = context.scene.task_urgency

        tasks = load_tasks()
        new_task = {
            'title': title,
            'description': description,
            'urgency': urgency,
            'completed': False
        }
        tasks['assignment'].append(new_task)
        save_tasks(tasks)
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

        tasks = load_tasks()
        task = tasks['in_progress'].pop(task_id)
        tasks['completed'].append(task)
        save_tasks(tasks)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(TODOListSettings)
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
    bpy.utils.register_class(TODOListAddonPreferences)
    bpy.utils.register_class(TODOAdminMoveTaskRightOperator)

    bpy.types.Scene.todo_list_settings = bpy.props.PointerProperty(type=TODOListSettings)
        # Register properties for Task Creator
    bpy.types.Scene.task_title = bpy.props.StringProperty(name="Task Title")
    bpy.types.Scene.task_description = bpy.props.StringProperty(name="Task Description")
    bpy.types.Scene.task_urgency = bpy.props.EnumProperty(
        name="Urgency",
        items=[('Low', "Low", ""),
               ('Medium', "Medium", ""),
               ('High', "High", "")]
    )


def unregister():
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

    del bpy.types.Scene.todo_list_settings
    del bpy.types.Scene.task_title
    del bpy.types.Scene.task_description
    del bpy.types.Scene.task_urgency


if __name__ == "__main__":
    register()
