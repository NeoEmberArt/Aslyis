# Snake Motion
With [SnakeMotion](https://raw.githubusercontent.com/NeoEmberArt/Aslyis/main/Addons/SnakeMotion.py), you can easily and quickly make a snake slither with a few clicks and animating just **1** object. (it can't get easier than this)

# Installation
* Download SnakeMotion.py
* Go to Edit > Preferences > Addons > Install
* Select the addon. After install, activate it by clicking the check box

# How to use
* ***Select an armature*** and go into pose mode
* ***Select the bones*** you want to use (preferably all)
	* Bones that aren't selected will be available for manual animating
	* Make sure the root bone (bone that will move the entire armature) is selected or the armature will not move
* Click **Setup**
* The empty that is selected will be the Controller/driver. A keyframe is allready added
* ***Animate the empty***
* Click **Bake**
* Watch your masterpiece slither

> **ProTip:** Bones must stay as a single line; If it splits/branches, you may get some funky results

# Common issues
### Bones are rotating but the armature is not moving
- Make sure that the root bone is selected.
### How to know if the root bone is selected
- Select the first bone in the armature. Move it and if the armature moves then that's the root bone. If you cannot find it, make sure all bones are not hidden
### What if the root bone is in the center of the model
- Try recreating the armature; If you have a root bone in the middle then only half of the model will be animated; the other half may jitter or do nothing
### What if I press "Unhide" and then undo
- Redo
> Ctrl + Shift + Z
### What if I pressed Bake and undid it
- You cannot rebake it, you will have to either start over or **REDO**
> Ctrl + Shift + Z
### I clicked bake and blender is not responding
- Don't panic, this is normal; just wait and it will respond
- Time varies and unfortunately it's unavoidable in the current version of SnakeMotion
### I keep getting sharp corner movements
- Cant be fixed yet, My suggestion is more bones or less sharp turning
### I got an error
- Great, report it and I will investigate
### How do i report an error?
- [Report the error here](https://github.com/NeoEmberArt/Aslyis/issues/new/choose)

###### Part of project [Asylis](https://github.com/NeoEmberArt/Aslyis)
