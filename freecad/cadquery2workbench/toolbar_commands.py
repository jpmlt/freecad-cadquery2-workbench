""" Commands triggered by the ToolBar Buttons from Cadquery Dock Widget """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
import FreeCAD as App
import FreeCADGui as Gui

from PySide2.QtWidgets import QFileDialog, QDialog, QDockWidget
from PySide2.QtCore import QObject

from freecad.cadquery2workbench import MODULENAME
from freecad.cadquery2workbench import TEMPLATESPATH
from freecad.cadquery2workbench import settingsdialog
from freecad.cadquery2workbench import cadquery_dockwidget
from freecad.cadquery2workbench import shared

class Toolbar_Commands(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.parent = parent
        
    def cmd_new_script(self):
        """CadQuery's command to start a new script file."""
        
        script_file = 'script_template.py'
        filename = os.path.join(TEMPLATESPATH, script_file)
        
        App.Console.PrintMessage("New script using template file"
                                 + script_file + "\r\n")
        App.Console.PrintMessage("Please save this template file as another " +
                                 "name before creating any others.\r\n")
        
        # First check if current script isModified() 
        if self.parent.editor.document().isModified():
            if not self.parent.cmd.aboutSave(title="Going to Create a New Script"):
                return

        # ok so clear parameters before opening new script
        self.parent.cqvarseditor.clearParameters()
        self.parent.cmd.open_file(filename)
                
    def cmd_open_script(self):
        """CadQuery's command to open a script file."""
        # First check if current script isModified() 
        if self.parent.editor.document().isModified():
            if not self.parent.cmd.aboutSave(title="Going to Open a New Script"):
                return
        
        # ok so clear parameters before opening new script
        self.parent.cqvarseditor.clearParameters()
        
        # then open dialog        
        fileDlg = QFileDialog.getOpenFileName(self.parent.mw,
                        self.parent.mw.tr("Open CadQuery Script"),
                        self.parent.cmd.previous_path,
                        self.parent.mw.tr("CadQuery Files (*.py)"))
        filename = fileDlg[0]
        
        # Make sure the user didn't click cancel
        if filename and os.path.isfile(filename):
            self.parent.cmd.previous_path = os.path.dirname(filename)
            self.parent.cmd.open_file(filename)
    
    def cmd_save_script(self):
        """CadQuery's command to save a script file"""
        if self.parent.cmd.save():
            # Execute the script if the user has asked for it
            if App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                        .GetBool("executeOnSave"):
                self.cmd_rebuild_script()
    
    def cmd_saveas_script(self):
        """CadQuery's command to save-as a script file"""
        if self.parent.cmd.saveAs():
            # Execute the script if the user has asked for it
            if App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                        .GetBool("executeOnSave"):
                self.cmd_rebuild_script()
                
    def cmd_validate_script(self):
        """Checks the script for the user without executing it
           and populates the variable editor, if needed"""
        self.parent.cmd.execute(action='Validate')
        
    def cmd_execute_script(self):
        """CadQuery's command to execute a script file"""
        self.parent.cmd.execute(action='Execute')

        # Expand Tree View if there are groups
        self.cmd_expand_tree()
        
    def cmd_rebuild_script(self):
        """CadQuery's command to rebuild a script file
           Execute do not rebuild the parameters editor even if script file changed
           Using Rebuild it will do it"""
        self.parent.cmd.execute(action='Rebuild')
    
    def cmd_clear_output(self):
        """Opens a settings dialog, allowing the user to change
           the settings for this workbench"""
        mw = Gui.getMainWindow()
        
        reportView = mw.findChild(QDockWidget, "Report view")
        
        # Clear the view because it gets overwhelmed sometimes and won't scroll to the bottom
        reportView.widget().clear()
        
    def cmd_settings(self):
        """Opens a settings dialog, allowing the user to change
           the settings for this workbench"""
        oldshowLineNumbers = App.ParamGet("User parameter:BaseApp/Preferences/Mod/"
                                        + MODULENAME).GetBool("showLineNumbers")
        win = settingsdialog.SettingsDialog()
        
        if win.exec_() == QDialog.Accepted:
            # check if showLineNumbers changed
            showLineNumbers = App.ParamGet("User parameter:BaseApp/Preferences/Mod/"
                                        + MODULENAME).GetBool("showLineNumbers")
            if showLineNumbers != oldshowLineNumbers:
                self.parent.editor.lineNumberArea.setVisible(showLineNumbers)
        
    def cmd_open_examples(self):
        """Opens a list view of Caqdquery Examples"""
        win = cadquery_dockwidget.CadqueryExamples(self.parent)
        win.show()


    def cmd_expand_tree(self):
        """Expand the tree view of each Group if any
           Don´t find a FreeCAD command for that
           Placing this code inside Execute doesn't work, don´t know why
        """
        # Expand Tree View if there are groups
        # get FreeCAD 3D view
        activeDoc = shared.getActive3DView(self.parent.view3DApp, self.parent, self.parent.filename)
        # activeDoc = App.ActiveDocument
        for obj in activeDoc.Objects:
            if type(obj) == App.DocumentObjectGroup:
                # Gui.Selection.addSelection(activeDoc.Name,obj.Group[0].Name)
                Gui.activeDocument(). \
                    scrollToTreeItem(Gui.activeDocument().getObject(obj.Group[0].Name))
