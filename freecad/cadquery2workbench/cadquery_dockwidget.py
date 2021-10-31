""" Cadquery CodeEditor DockWidget"""
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
import FreeCAD as App
import FreeCADGui as Gui

from PySide2.QtWidgets import QDockWidget, QMainWindow, QAction, QToolBar
from PySide2.QtWidgets import QLineEdit, QGridLayout, QWidget, QScrollArea
from PySide2.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QLabel
from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QFont, QIcon, QPixmap, QKeySequence

from freecad.cadquery2workbench import cadquery_codeeditor
from freecad.cadquery2workbench import toolbar_commands
from freecad.cadquery2workbench import script_commands
from freecad.cadquery2workbench import freecad_editor_settings
from freecad.cadquery2workbench import MODULENAME
from freecad.cadquery2workbench import EXAMPLESPATH


# ------------------------------------------------------------------------------
""" Main Class - Cadquery DockWidget with a ToolBar """
# ------------------------------------------------------------------------------
class CadqueryDockWidget(QDockWidget):
    def __init__(self):
        QDockWidget.__init__(self, "CadQuery Editor")
        self.setObjectName("CadQuery Editor")
        self.tbcmd = toolbar_commands.Toolbar_Commands(self)
        self.cmd = script_commands.Script_Commands(self)
        self.fcedset = freecad_editor_settings.Freecad_Editor_Settings(self)
        
        self.mainWin = QMainWindow()
        
        # the toolbar
        toolbar = QToolBar("CadqueryDockWidget Tool Bar")
        toolbar.setMovable(False)
        self.createActions(toolbar)
        self.mainWin.addToolBar(toolbar)
        
        # the editor is set as centralWidget
        self.editor = cadquery_codeeditor.CodeEditor(self)
        self.mainWin.setCentralWidget(self.editor)
        
        # add our Variables Editor as a docked Widget
        self.cqvarseditor = CadqueryVariablesDockWidget("CadQuery Variables Editor", self)
        self.mainWin.addDockWidget(Qt.BottomDockWidgetArea, self.cqvarseditor)
        self.setWidget(self.mainWin)
        
        # EventFilter to catch the app exit signal
        self.mw = Gui.getMainWindow()
        self.mw.installEventFilter(self)
        
        # Signal and slot
        self.editor.textChanged.connect(self.ismodifed)
        
        # some variables
        self.filename = ''          # store full path of opened file
        self.view3DMdi = None       # the MDI 3D view in GUI 
        self.view3DApp = None       # the Document 3D view in App
        self.show_debug = False     # Toggle Show/Hide Debug Object when Execute
        
        # At startup Open a New Script
        self.tbcmd.cmd_new_script()
        
    # --------------------------------------------------------------------------
    # --------- ToolBar --------------------------------------------------------
    # --------------------------------------------------------------------------
    def createActions(self, toolbar):
        self.newAct = QAction(QIcon(QPixmap(":/icons/TextDocument.svg")),
                         "New Script (Alt+Shift+N)", self.mainWin)
        self.newAct.setShortcut(QKeySequence("Alt+Shift+N"))
        self.newAct.setStatusTip("Starts a new CadQuery script")
        self.newAct.triggered.connect(self.tbcmd.cmd_new_script)
        toolbar.addAction(self.newAct)
    
        self.openAct = QAction(QIcon(QPixmap(":/icons/document-open.svg")),
                         "Open Script (Alt+Shift+O)", self.mainWin)
        self.openAct.setShortcut(QKeySequence("Alt+Shift+O"))
        self.openAct.setStatusTip("Open a new CadQuery script")
        self.openAct.triggered.connect(self.tbcmd.cmd_open_script)
        toolbar.addAction(self.openAct)

        self.saveAct = QAction(QIcon(QPixmap(":/icons/document-save.svg")),
                         "Save Script (Alt+Shift+S)", self.mainWin)
        self.saveAct.setShortcut(QKeySequence("Alt+Shift+S"))
        self.saveAct.setStatusTip("Save the CadQuery script to disk")
        self.saveAct.triggered.connect(self.tbcmd.cmd_save_script)
        toolbar.addAction(self.saveAct)

        self.saveasAct = QAction(QIcon(QPixmap(":/icons/document-save-as.svg")),
                         "Save Script As", self.mainWin)
        self.saveasAct.setShortcut("")
        self.saveasAct.setStatusTip("Saves the CadQuery script to disk in a " +
                               "location other than the original")
        self.saveasAct.triggered.connect(self.tbcmd.cmd_saveas_script)
        toolbar.addAction(self.newAct)
        toolbar.addAction(self.openAct)
        toolbar.addAction(self.saveAct)
        toolbar.addAction(self.saveasAct)
        
        toolbar.addSeparator()
        
        strKey = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                    .GetString("validateKeybinding") 
        self.validateAct = QAction(QIcon(QPixmap(":/icons/button_valid.svg")),
                         "Validate Script (" + strKey + ")", self.mainWin)
        self.validateAct.setShortcut(QKeySequence(strKey))
        self.validateAct.setStatusTip("Validates a CadQuery script")
        self.validateAct.triggered.connect(self.tbcmd.cmd_validate_script)
        toolbar.addAction(self.validateAct)
        
        strKey = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                    .GetString("executeKeybinding")
        self.executeAct = QAction(QIcon(QPixmap(":/icons/media-playback-start.svg")),
                         "Execute Script (" + strKey + ")", self.mainWin)
        self.executeAct.setShortcut(QKeySequence(strKey))
        self.executeAct.setStatusTip("Executes a CadQuery script")
        self.executeAct.triggered.connect(self.tbcmd.cmd_execute_script)
        toolbar.addAction(self.executeAct)
        
        strKey = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME) \
                    .GetString("rebuildKeybinding")
        self.rebuildAct = QAction(QIcon(QPixmap(":/icons/view-refresh.svg")),
                         "Rebuild Script (" + strKey + ")", self.mainWin)
        self.rebuildAct.setShortcut(QKeySequence(strKey))
        self.rebuildAct.setStatusTip("Rebuilds a CadQuery script")
        self.rebuildAct.triggered.connect(self.tbcmd.cmd_rebuild_script)
        toolbar.addAction(self.rebuildAct)

        self.debugAct = QAction(QIcon(QPixmap(":/icons/tree-pre-sel.svg")),
                         "Toggle Debug Script", self.mainWin)
        self.debugAct.setShortcut("")
        self.debugAct.setStatusTip("Toggle Show/Hide Debug Object on the script")
        self.debugAct.setCheckable(True)
        self.debugAct.setChecked(False)
        self.debugAct.triggered.connect(self.toggle_debug_script)
        toolbar.addAction(self.debugAct)

        toolbar.addSeparator()

        self.clearAct = QAction(QIcon(QPixmap(":/icons/button_invalid.svg")),
                         "Clear Output (Alt+Shift+C)", self.mainWin)
        self.clearAct.setShortcut(QKeySequence("Alt+Shift+C"))
        self.clearAct.setStatusTip("Clears the script output from the Reports view")
        self.clearAct.triggered.connect(self.tbcmd.cmd_clear_output)
        toolbar.addAction(self.clearAct)

        self.settingsAct = QAction(QIcon(QPixmap(":/icons/preferences-general.svg")),
                         "Settings", self.mainWin)
        self.settingsAct.setShortcut("")
        self.settingsAct.setStatusTip("Opens the settings dialog")
        self.settingsAct.triggered.connect(self.tbcmd.cmd_settings)
        toolbar.addAction(self.settingsAct)
        
        toolbar.addSeparator()
        
        self.examplesAct = QAction(QIcon(QPixmap(":/icons/document-python.svg")),
                         "Examples", self.mainWin)
        self.examplesAct.setShortcut("")
        self.examplesAct.setStatusTip("Opens Cadquery Script Examples")
        self.examplesAct.triggered.connect(self.tbcmd.cmd_open_examples)
        toolbar.addAction(self.examplesAct)
        
        self.expandtreeAct = QAction(QIcon(QPixmap(":/icons/sel-instance.svg")),
                         "Expand Tree Groups", self.mainWin)
        self.expandtreeAct.setShortcut("")
        self.expandtreeAct.setStatusTip("Expand the tree view of each Group")
        self.expandtreeAct.triggered.connect(self.tbcmd.cmd_expand_tree)
        toolbar.addAction(self.expandtreeAct)
        
        
    # --------------------------------------------------------------------------
    # --------- Signal & Slot --------------------------------------------------
    # --------------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is self.mw and event.type() == QEvent.Close:
            if not self.on_exit():
                event.ignore()
                return True
        return super(CadqueryDockWidget, self).eventFilter(obj, event)

    def on_exit(self):
        # First check if current script isModified() 
        if self.editor.document().isModified():
            if not self.cmd.aboutSave(title="Application is closing"):
                return False
        return True
            
    def ismodifed(self):
        self.saveAct.setEnabled(self.editor.document().isModified())
        
        if self.editor.document().isModified():
            self.setWindowTitle(self.objectName() + " - " +
                                os.path.basename(self.filename) + "*")
        else:
            self.setWindowTitle(self.objectName() + " - " +
                                os.path.basename(self.filename))

    def toggle_debug_script(self):
        self.show_debug = self.debugAct.isChecked()
        
        
# ------------------------------------------------------------------------------
""" The Dock Widget to show the Variables found on the Scipt """
# ------------------------------------------------------------------------------
class CadqueryVariablesDockWidget(QDockWidget):
    def __init__(self, name, parent):
        QDockWidget.__init__(self, name)
        self.setObjectName("CadQuery Variables Editor")
        self.haveParameters = False
        self.parent = parent
        
        self.populateParameterEditor(parameters={})
        
    def populateParameterEditor(self, parameters):
        gridLayout = QGridLayout()
        # Create a widget we can put the layout in and add a scrollbar
        newWidget = QWidget()
        newWidget.setLayout(gridLayout)
        
        line = 1
        self.haveParameters = False
        
        if len(parameters) > 0:
            self.haveParameters = True
            # Add controls for all the parameters so that they can be edited from the GUI
            for pKey, pVal in list(parameters.items()):
                if type(pVal.default_value) == int or type(pVal.default_value) == float:
                    label = QLabel(pKey)
                    
                    # We want to keep track of this parameter value field so that we can pull its value later when executing
                    value = QLineEdit()
                    value.setText(str(pVal.default_value))
                    value.setObjectName("pcontrol_" + pKey)
                    value.returnPressed.connect(self.paramReturnPressed)

                    # The description of the parameter
                    desc = QLabel(pVal.desc)
                    
                    # Add the parameter control sets, one set per line
                    gridLayout.addWidget(label, line, 0)
                    gridLayout.addWidget(value, line, 1)
                    gridLayout.addWidget(desc, line, 2)
                    
                    line += 1
            
        # Add a scroll bar in case there are a lot of variables in the script
        scrollArea = QScrollArea()
        scrollArea.setWidget(newWidget)

        # Show it in the central Widget
        layout =  QVBoxLayout()
        layout.addWidget(scrollArea)
        
        paramwidget = QWidget()
        paramwidget.setLayout(layout)
        self.setWidget(paramwidget)
        
    def paramReturnPressed(self):
        # Rerun the model
        self.parent.tbcmd.cmd_execute_script()
        
    def clearParameters(self):
        for le in self.findChildren(QLineEdit):
            le.setParent(None)
            le.deleteLater()
        self.populateParameterEditor(parameters={})
        

# ------------------------------------------------------------------------------
""" ListWidget of Cadquery Examples """
# ------------------------------------------------------------------------------
class CadqueryExamples(QDialog):
    def __init__(self, parent=None):
        super(CadqueryExamples, self).__init__(parent)
        self.setModal(True)
        self.resize(400, 600)
        self.setWindowTitle('Cadquery Examples')
        self.dictExamples = {}
        self.parent = parent
        self.initUI()

    def initUI(self):

        newWidget = QListWidget()
        newWidget.itemClicked.connect(self.item_clicked)
        
        # List all of the example files in an order that makes sense
        dirs = []
        exs_dir_path = os.path.join(EXAMPLESPATH, 'FreeCAD')
        dirs = os.listdir(exs_dir_path)
        dirs.sort()
        
        for curFile in dirs:
            text = os.path.basename(curFile)
            self.dictExamples[text] = exs_dir_path = os.path.join(EXAMPLESPATH, 'FreeCAD', text)
            QListWidgetItem(QIcon(QPixmap(":/icons/accessories-text-editor.svg")),
                            text, newWidget)
        
        layout =  QVBoxLayout()
        layout.addWidget(newWidget)
        self.setLayout(layout)
    
    def item_clicked(self, item):
        filename = self.dictExamples[item.text()]
        self.hide()
        # ok so clear parameters before opening new script
        self.parent.cqvarseditor.clearParameters()
        self.parent.cmd.open_file(filename)
        
