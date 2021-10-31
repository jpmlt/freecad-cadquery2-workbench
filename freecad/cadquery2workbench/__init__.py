"""__init__.py is loaded when opening FreeCAD."""
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
from .version import __version__
import FreeCAD

# path
ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
EXAMPLESPATH = os.path.join(os.path.dirname(__file__), "examples")
TEMPLATESPATH = os.path.join(os.path.dirname(__file__), "templates")

# module name
MODULENAME = 'cadquery2-freecad-workbench'


# Set sane defaults for FreeCAD-stored settings if they haven't been set yet
has_run_before = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetBool("runBefore")

if not has_run_before:
    print("Set up default cadquery2-freecad-workbench parameters")
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetString("executeKeybinding", "F9")
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetString("validateKeybinding", "F4")
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetString("rebuildKeybinding", "F5")
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("executeOnSave", False)
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("showLineNumbers", True)
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("allowReload", False)

    # Make sure we don't overwrite someone's existing settings
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("runBefore", True)
