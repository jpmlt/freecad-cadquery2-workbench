""" some FreeCAD method """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
from random import random
import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtCore
from PySide2.QtWidgets import QMdiArea, QPlainTextEdit
from PySide2.QtGui import QIcon


def clearActive3DView(view3D):
    """Clears the currently active 3D view so that we can re-render"""
    for obj in view3D.Objects:
        view3D.removeObject(obj.Name)
    view3D.recompute()


def getActive3DView(view3D, cqWinEd, filename):
    """Gets the active 3D view is script already run, otherwise create a new 3D view."""
    filename = os.path.basename(filename).split('.py')[0]
    
    # Search a 3D view: view3D
    listdoc = App.listDocuments()
    ad = None
    mdiWin = None
    for doc in listdoc.values():
        if doc == view3D:
            ad = doc
            
    # No one found, we need to create a new one
    if ad == None:
        ad = App.newDocument('view3D_' + filename)
        
        # In case FreeCAD do not succeed to create it with given docname
        if ad == None:
            App.Console.PrintError("[shared.getActive3DView]Unable to create a 3D view with given name: " + filename + "\r\n")
            return None

        # Theoritically after App.newDocument, the current SubWindow is the one we just created
        cqWinEd.view3DApp = ad

        mw = Gui.getMainWindow()
        mdi = mw.findChild(QMdiArea)
        mdiWin = mdi.currentSubWindow()
        cqWinEd.view3DMdi = mdiWin
        
        # As we create a new 3D view, excute is first time
        cqWinEd.firstexecute = True
        
        # As setfilename is set after activation of the subwindow need to activate again
        # cqWinEd.activated()
    
    # if 3D view were already existing, it may be not the mdi active window
    # TO BE FIXED : when user switch to full mode the view3DMdi is no longer valid
    mw = Gui.getMainWindow()
    mdi = mw.findChild(QMdiArea)
    mdi.setActiveSubWindow(cqWinEd.view3DMdi)
    
    return ad
