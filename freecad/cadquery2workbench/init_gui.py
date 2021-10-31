"""init_gui.py is loaded each time the CadQuery workbench is activate in FreeCAD."""
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
import FreeCAD as App
import FreeCADGui as Gui
import cadquery as cq
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QDockWidget
from freecad.cadquery2workbench import ICONPATH
from freecad.cadquery2workbench import cadquery_dockwidget


class CadQuery2_Workbench(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    MenuText = "CadQuery"
    ToolTip = "CadQuery v2 FreeCAD Workbench"
    Icon = os.path.join(ICONPATH, "CQ_Logo.svg")

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        App.Console.PrintMessage("Switching to CadQuery Workbench\n")
        msg = QApplication.translate(
                "cqCodeWidget",
                "CadQuery " + cq.__version__ + "\r\n"
                "          A python parametric CAD scripting framework based on OCCT\r\n"
                "          Author: Originally written by David Cowden (v1)\r\n"
                "                  OCCT implementation by Adam Arbanczyk (v2)\r\n"
                "          License: Apache-2.0\r\n"
                "          Website: https://github.com/CadQuery/cadquery\r\n",
                None)
        App.Console.PrintMessage(msg)
        
    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        # Getting the main window will allow us to start setting things up the way we want
        # Force to show the Report View
        mw = Gui.getMainWindow()
        dockWidgets = mw.findChildren(QDockWidget)
        
        cqDockWidget_isopened = False
        for widget in dockWidgets:
            if widget.objectName() == "Report view":
                widget.setVisible(True)
            elif widget.objectName() == "CadQuery Editor":
                cqDockWidget_isopened = True
                widget.setVisible(True)
        
        if not cqDockWidget_isopened:
            cqDockWidget = cadquery_dockwidget.CadqueryDockWidget()
            mw.addDockWidget(Qt.RightDockWidgetArea, cqDockWidget)

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        pass


Gui.addWorkbench(CadQuery2_Workbench())

