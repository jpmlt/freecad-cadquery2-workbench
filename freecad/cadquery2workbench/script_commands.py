""" Commands related to Cadquery Script """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
import pathlib
import math as m
from random import random

import FreeCAD as App
import FreeCADGui as Gui
import Part

from PySide2.QtCore import QFileInfo, QTimer, QObject
from PySide2.QtWidgets import QMessageBox, QFileDialog, QLineEdit

from freecad.cadquery2workbench import MODULENAME
from freecad.cadquery2workbench import shared
from freecad.cadquery2workbench import cadquery_model

import cadquery as cq

class Script_Commands(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.parent = parent
        self.file_contents = None
        self.previous_path = os.environ['HOME']
        
        # QTimer to check if file was modified on the disk
        self.fiName = None
        self.timeStamp = None
        self.activity_timer = QTimer()
        self.activity_timer.timeout.connect(self.changed_on_disk)
        
    # open a file
    def open_file(self, filename=None):
        # Before open, check if file exist
        if os.path.isfile(filename):
            # OK so we can open the File
            with open(filename) as f: self.file_contents = f.read()
            self.parent.editor.setPlainText(self.file_contents)
            
            # Watch the file we've opened
            fi = QFileInfo(filename)
            self.fiName = fi.baseName()
            self.timeStamp =  fi.lastModified().toTime_t()
            self.activity_timer.setSingleShot(True)
            self.activity_timer.start(3000)
            
            # setup parent
            self.parent.view3DApp = None
            self.parent.view3DMdi = None
            self.parent.filename = filename
            self.parent.editor.document().setModified(False)
            self.parent.ismodifed()
            self.parent.setWindowTitle(self.parent.objectName() + " - " + os.path.basename(filename))
            
        else:
            App.Console.PrintError("Cannot find file : {0}\r\n".format(filename))
        
    # reload file when changes is made from external editor
    def reload_file(self):
            # re-open our File
            App.Console.PrintWarning("File {0} has been changed on the disk - Reload it\r\n".format(self.parent.filename))
            with open(self.parent.filename) as f: self.file_contents = f.read()
            self.parent.editor.setPlainText(self.file_contents)
            self.parent.editor.document().setModified(False)
            self.parent.ismodifed()
            self.activity_timer.setSingleShot(True)
            self.activity_timer.start(3000)
            
    # Connect to QTimer to catch when file change on the disk
    def changed_on_disk(self):
        fi = QFileInfo(self.parent.filename)
        fiName = fi.baseName()
        timeStamp =  fi.lastModified().toTime_t()
        if (timeStamp != self.timeStamp):   #  or fiName != self.fiName
            # reset our Timer
            self.activity_timer.stop()
            self.timeStamp = timeStamp
            self.fiName = fiName

            # if allowReload is set by the user don´t prompt reload it in any case
            allowReload = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetBool("allowReload")
            if not allowReload:
                ret = QMessageBox.question(self.parent, self.parent.mw.tr("Modified file"),
                        self.parent.mw.tr("{0}.\n\nThis file has been modified outside of the source editor. Do you want to reload it?".format(self.parent.filename)),
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if ret == QMessageBox.Yes:
                    self.reload_file()   # (self.parent.filename)
                    # Execute the script if the user has asked for it
                    if App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                                .GetBool("executeOnSave"):
                        self.execute(action='Rebuild')
                    return
                    
            else:
                self.reload_file() # (self.parent.filename)
                # Execute the script if the user has asked for it
                if App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                            .GetBool("executeOnSave"):
                    self.execute(action='Rebuild')
                return
                
        self.activity_timer.setSingleShot(True)
        self.activity_timer.start(3000)
    
    # Ask user if need save the changes    
    def aboutSave(self, title):
        ret = QMessageBox.warning(self.parent, title,
                    "{0}\r\n\n".format(self.parent.filename) +
                    "This document has been modified.\r\n" +
                    "Do you want to save your changes?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save)
        
        if ret == QMessageBox.Cancel:
            return False
            
        if ret == QMessageBox.Save:
            if not self.save():
                return False
            
        return True
        
    # Save current file or given filename file
    def save(self, filename=None):
        # Saving current file ?
        if not filename:
            filename = self.parent.filename
            
        # If the code pane doesn't have a filename, we need to present the save as dialog
        if len(filename) == 0 \
                or os.path.basename(filename) == 'script_template.py' \
                or os.path.split(filename)[0].endswith('FreeCAD'):
            App.Console.PrintWarning("You cannot save over a blank file, example file or template file.\r\n")
            return self.saveAs()
            
        self.activity_timer.stop()
        with open(filename, "w") as code_file:
            code_file.write(self.parent.editor.toPlainText())
        
        # Reset the QTimer
        fi = QFileInfo(filename)
        self.fiName = fi.baseName()
        self.timeStamp =  fi.lastModified().toTime_t()
        self.activity_timer.setSingleShot(True)
        self.activity_timer.start(3000)
        
        # Update the status
        self.parent.editor.document().setModified(False)
        self.parent.ismodifed()
        return filename
        
    # Save As method
    def saveAs(self):
        fileDlg = QFileDialog.getSaveFileName(self.parent.mw,
                        self.parent.mw.tr("Save CadQuery Script As"),
                        self.previous_path,
                        self.parent.mw.tr("CadQuery Files (*.py)"))
        filename = fileDlg[0]
        
        # Make sure the user didn't click cancel
        if filename:
            if filename[-3:] != '.py':
                filename += '.py'
            self.previous_path = os.path.dirname(filename)
            savedname = self.save(filename)
            if not savedname:
                return False
                
            else:
                filename = savedname
                # Watch the file we've saved as new path/name
                fi = QFileInfo(filename)
                self.fiName = fi.baseName()
                self.timeStamp =  fi.lastModified().toTime_t()
                self.activity_timer.setSingleShot(True)
                self.activity_timer.start(3000)
                
                # setup parent 
                self.parent.view3DApp = None
                self.parent.view3DMdi = None
                self.parent.filename = filename
                self.parent.editor.document().setModified(False)
                self.parent.ismodifed()
                self.parent.setWindowTitle(self.parent.objectName() + " - " + os.path.basename(filename))
                return filename
            
        return False
    
    # command to validate or execute or rebuild a script file
    def execute(self, action='Execute'):
        scriptText = self.parent.editor.toPlainText().encode('utf-8')
        
        if (b"show_object(" not in scriptText) and  (b"debug(" not in scriptText):
            App.Console.PrintError("Script did not call show_object or debug, no output available. Script must be CQGI compliant to get build output, variable editing and validation.\r\n")
            return
        
        # A repreentation of the CQ script with all the metadata attached
        cqModel = cadquery_model.CQ_Model(scriptText)       # cqgi.parse(scriptText)
        
        # Allows us to present parameters to users later that they can alter
        parameters = cqModel.metadata.parameters
        
        # If paramEditor not yet build or execute with rebuild argument
        if (not self.parent.cqvarseditor.haveParameters) or action=='Rebuild':
            self.parent.cqvarseditor.clearParameters()
            self.parent.cqvarseditor.populateParameterEditor(parameters)
        
        # Build cq object
        build_parameters = {}
        
        # Get the variables from the paramEditor
        dockWidget = self.parent.cqvarseditor
        valueControls = dockWidget.findChildren(QLineEdit)
        for valueControl in valueControls:
            objectName = valueControl.objectName()
            
            # We only want text fields that will have parameter values in them
            if objectName != None and objectName != '' and objectName.find('pcontrol_') >= 0:
                # when doing Execute or Validate, it doesn't rebuild the cqvarseditor
                # however user may have remove a variable in the script
                # so import only variable if they are in the script, ie in parameters
                if objectName.split('pcontrol_')[1] in parameters:
                    # Associate the value in the text field with the variable name in the script
                    # As we pass the parameters through a QLineEdit as a String we loose the type
                    # Then it is convert to a float
                    # However sometimes a value must stay as an int for the script to work properly
                    # Let's try to force the right type
                    val = valueControl.text()
                    try:
                        valtype = int(val)
                    except:
                        try:
                            valtype = float(val)
                        except:
                            valtype = val
                    build_parameters[objectName.replace('pcontrol_', '')] = valtype
        
        build_result = cqModel.build(build_parameters=build_parameters)
        list_objects = []

        # if Settings.report_execute_time:
        #     App.Console.PrintMessage("Script executed in " + str(build_result.buildTime) + " seconds\r\n")

        # Make sure that the build was successful
        if build_result.success:
            # Clean the 3D view if exist (user may have closed the view3D)
            try:
                if self.parent.view3DApp != None:
                    shared.clearActive3DView(self.parent.view3DApp)
            except:
                pass
                
            # Display all the results that the user requested
            for result in build_result.results:
                # Apply options to the show function if any were provided
                name = "Shape_" + str(random())
                group = None
                rgba = (204, 204, 204, 0.0)
                if result.options :
                    # parse the options
                    # object name
                    name = result.options['name'] \
                                if 'name' in result.options \
                                else name
                    
                    # object group
                    group = result.options['group'] \
                                if 'group' in result.options else group
                            
                    # object color
                    # if rgba is defined it superseed any colors or alpha options
                    if 'rgba' in result.options:
                        rgba= result.options['rgba']
                        # rgba provided as a String '#RRGGBB'or '#RRGGBBAA'
                        if type(rgba) == str:
                            rgba = rgba[1:] # remove first char '#'
                            red = int(rgba[0]+rgba[1], 16)
                            green = int(rgba[2]+rgba[3], 16)
                            blue = int(rgba[4]+rgba[5], 16)
                            if len(rgba) > 6:
                                alpha = int(rgba[6]+rgba[7], 16) / 255.0
                            else:
                                alpha = 0.0
                            rgba = (red, green, blue, alpha)
                        # rgba defined as CadQuery Color class
                        elif type(rgba) == cq.Color:
                            r, g, b, a = rgba.toTuple()
                            r *= 255
                            g *= 255
                            b *= 255
                            a = 1 - a
                            rgba = (r, g, b, a)
                        else:
                            # rgba is supposed to be a list (red, green, blue, alpha)
                            pass
                    else:
                        # rgba is not defined check for color and alpha
                        color = result.options['color'] if 'color' in result.options else (204, 204, 204)
                        alpha = result.options['alpha'] if 'alpha' in result.options else 0.0
                        rgba = (color[0], color[1], color[2], alpha)
                        
                # append object to the list of objects
                list_objects.append((result.shape, rgba, name, group))
                
            # if user choose to show render objects
            if self.parent.show_debug:
                for debugObj in build_result.debugObjects:
                    # Apply options to the show function if any were provided
                    if debugObj.options:
                        # parse the options
                        # object name, Mark this as a debug object
                        name = "Debug_" + debugObj.options['name'] \
                                        if 'name' in debugObj.options \
                                        else "Debug_" + str(random())
                        
                        # object group
                        group = debugObj.options['group'] \
                                        if 'group' in debugObj.options else None

                        # force color for Debug object
                        rgba = (255, 0, 0, 0.60)
                        name = debugObj.options['name'] if 'name' in debugObj.options else '_'
                        # Mark this as a debug object
                        name = "Debug_" + name
                        
                    else:
                        name = "Debug_" + str(random())
                        group = None
                        rgba = (255, 0, 0, 0.60)
                        
                    # append object to the list of objects
                    list_objects.append((debugObj.shape, rgba, name, group))
                    
            # show list of objects
            if len(list_objects) > 0 and action != 'Validate':
                self.showInFreeCAD(list_objects)
            
        else:
            App.Console.PrintError("Error executing CQGI-compliant script. " + str(build_result.exception) + "\r\n")
    
    def append_assembly_parts(self, list_objects):
        assy_obj_toremove=[]
        for obj in list_objects:
            cqObject = obj[0]
            rgba = obj[1]
            name = obj[2]
            group = obj[3]
            if len(obj) > 4:
                loc = obj[4]
            else:
                loc = None
            
            # CadQuery Assembly, add each childrens to be rendered to list_objects 
            if type(cqObject) == cq.assembly.Assembly:
                assy_obj_toremove.append(obj)
                # add childrens to list_objects
                loc_parent = None
                for assy in list(cqObject.objects.values()):
                    # color
                    if assy.color:
                        r, g, b, a = assy.color.toTuple()
                        r *= 255
                        g *= 255
                        b *= 255
                        a = 1 - a
                        rgba = (r, g, b, a)
                    else:
                        rgba = (204, 204, 204, 0.0)
                        
                    # location
                    loc_matrix = App.Base.Matrix()
                    if not loc_parent:
                        if assy.loc:
                            loc = assy.loc.toTuple()
                            loc_parent = loc
                        else:
                            loc = ((0, 0, 0), (0, 0, 0))
                            loc_parent = loc
                        
                        trans = loc[0]
                        rot = loc[1]
                        ax, ay, az = rot
                        loc_matrix.rotateX(ax)
                        loc_matrix.rotateY(ay)
                        loc_matrix.rotateZ(az)
                        loc_matrix.move(trans)
                    else:
                        # location of child assy are relative to parent one
                        if assy.loc:
                            loc = assy.loc.toTuple()
                            trans = loc[0]
                            rot = loc[1]
                            ax, ay, az = rot
                            loc_matrix.rotateX(ax)
                            loc_matrix.rotateY(ay)
                            loc_matrix.rotateZ(az)
                            loc_matrix.move(trans)
                            
                        loc = loc_parent
                        trans = loc[0]
                        rot = loc[1]
                        ax, ay, az = rot
                        loc_matrix.rotateX(ax)
                        loc_matrix.rotateY(ay)
                        loc_matrix.rotateZ(az)
                        loc_matrix.move(trans)
                        
                    # append each part of the Assembly
                    list_objects.append((assy.obj, rgba, assy.name, group, loc_matrix))
                
        # remove Assy from list_objects
        for obj in assy_obj_toremove:
            list_objects.pop(list_objects.index(obj))
        
        return list_objects

    def showInFreeCAD(self, list_objects):
        # get FreeCAD 3D view 
        activeDoc = shared.getActive3DView(self.parent.view3DApp, self.parent, self.parent.filename)
        
        # first loop to split Assembly parts
        list_objects = self.append_assembly_parts(list_objects)
        
        for obj in list_objects:
            cqObject = obj[0]
            rgba = obj[1]
            name = obj[2]
            group = obj[3]
            if len(obj) > 4:
                loc = obj[4]
            else:
                loc = None
            
            # CadQuery Assembly
            if type(cqObject) == cq.assembly.Assembly:
                App.Console.PrintError("Only one Sub Level of Assembly Parts is supported yet")
                return
            
            # Make sure we replace any troublesome characters not supported in FreeCAD
            # As we search for existing group below
            if group:
                for ch in ['&', '#', '.', '$', '%', ',', ' ']:
                    if ch in group:
                        group = group.replace(ch, "_")
            
            #Convert our rgba values
            r = rgba[0] / 255.0
            g = rgba[1] / 255.0
            b = rgba[2] / 255.0
            a = int(rgba[3] * 100.0)
            
            # case group was passed in the options
            if group:
                # group is already is activeDoc
                group_exist = False
                for obj in activeDoc.Objects:
                    if type(obj) == App.DocumentObjectGroup and obj.Name == group:
                        group_exist = True
                        
                if not group_exist:
                    # create it
                    activeDoc.Tip = activeDoc.addObject('App::DocumentObjectGroup', group)
                    
                # add newFeature to group
                newFeature = activeDoc.addObject("Part::Feature", name)
                activeDoc.getObject(group).addObject(newFeature)
            
            else:
                # add newFeature to activeDoc
                newFeature = activeDoc.addObject("Part::Feature", name)
            
            #Change our shape's properties accordingly
            newFeature.ViewObject.ShapeColor = (r, g, b)
            newFeature.ViewObject.Transparency = a
            self.tofreecad(cqObject, newFeature)
            # Placement
            if loc:
                newFeature.Placement = App.Placement(loc).multiply(newFeature.Placement)
                # newFeature.Placement = newFeature.Placement.multiply(App.Placement(m))
                
        # All object are added to FreeCAD, recompute    
        activeDoc.recompute()
        
        if self.parent.firstexecute:
            # On the first Execution force the Camera and View settings
            # Then next time keep user view
            Gui.activeDocument().activeView().setCamera('OrthographicCamera{}')
            Gui.activeDocument().activeView().viewIsometric()
            Gui.SendMsgToActiveView("ViewFit")
            self.parent.firstexecute = False
            
        # Expand Tree View if there are groups
        # activeDoc = App.ActiveDocument
        for obj in activeDoc.Objects:
            if type(obj) == App.DocumentObjectGroup:
                # Gui.Selection.addSelection(activeDoc.Name,obj.Group[0].Name)
                Gui.activeDocument(). \
                    scrollToTreeItem(Gui.activeDocument().getObject(obj.Group[0].Name))
                # Gui.Selection.clearSelection()
    
    def tofreecad(self, cqObject, feature):
        # Use a temporary BREP file to get the cadquery shape
        # Use FreeCAD Home directory
        env = os.environ
        temppath = env['FREECAD_USER_HOME'] if 'FREECAD_USER_HOME' in env else env['HOME']
        temppath += '/.FreeCAD/tmp'
        
        # if not exist create the tmp directory
        pathlib.Path(temppath).mkdir(parents=True, exist_ok=True)
        
        # convert to FreeCAD Shape using BRep export/import
        filename = temppath + '/brep'
        
        cqObject.val().exportBrep(filename)
        tmp_shape = Part.Shape()
        tmp_shape.importBrep(filename)
        
        feature.Shape = tmp_shape
