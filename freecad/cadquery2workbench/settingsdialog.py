""" the Settings Dialog specific to cadquery2-freecad-workbench """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import os
import FreeCAD as App
import FreeCADGui as Gui

from PySide2.QtCore import Qt, Slot, QSize
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QSpinBox, QCheckBox
from PySide2.QtWidgets import QDialogButtonBox, QBoxLayout, QGridLayout
from PySide2.QtWidgets import QWidget, QGroupBox, QRadioButton, QVBoxLayout
from PySide2.QtWidgets import QDockWidget
from PySide2.QtGui import QIcon, QPixmap

from freecad.cadquery2workbench import MODULENAME
from freecad.cadquery2workbench import ICONPATH

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.resize(200, 150)
        self.setWindowTitle('Settings')
        self.initUI()
        
    def initUI(self):
        excutekeybinding = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetString("executeKeybinding")
        validatekeybinding = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetString("validateKeybinding")
        rebuildkeybinding = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetString("rebuildKeybinding")
        executeOnSave = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetBool("executeOnSave")
        showLineNumbers = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetBool("showLineNumbers")
        allowReload = App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetBool("allowReload")
        
        execute_key_binding = QLabel('Execute Key-binding')
        self.ui_execute_key_binding = QLineEdit()
        self.ui_execute_key_binding.setText(excutekeybinding)
        
        validate_key_binding = QLabel('Validate Key-binding')
        self.ui_validate_key_binding = QLineEdit()
        self.ui_validate_key_binding.setText(validatekeybinding)
        
        rebuild_key_binding = QLabel('Rebuild Key-binding')
        self.ui_rebuild_key_binding = QLineEdit()
        self.ui_rebuild_key_binding.setText(rebuildkeybinding)
        
        execute_on_save = QLabel('Execute on Save')
        self.execute_on_save = QCheckBox()
        self.execute_on_save.setChecked(executeOnSave)
        
        show_line_numbers = QLabel('Show Line Numbers')
        self.show_line_numbers = QCheckBox()
        self.show_line_numbers.setChecked(showLineNumbers)
        
        allow_reload = QLabel('Allow Reload')
        self.allow_reload = QCheckBox()
        self.allow_reload.setChecked(allowReload)
        
        self.buttons = QDialogButtonBox();
        self.buttons.setOrientation(Qt.Horizontal)
        self.buttons.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttons.layout().setDirection(QBoxLayout.LeftToRight)
        self.buttons.accepted.connect(self.acceptSettings)
        self.buttons.rejected.connect(self.reject)
        
        # The settings Layout
        grid = QGridLayout()
        grid.setContentsMargins(10, 10, 10, 10)
        grid.addWidget(execute_key_binding, 0, 0)
        grid.addWidget(self.ui_execute_key_binding, 0, 1)
        grid.addWidget(validate_key_binding, 1, 0)
        grid.addWidget(self.ui_validate_key_binding, 1, 1)
        grid.addWidget(rebuild_key_binding, 2, 0)
        grid.addWidget(self.ui_rebuild_key_binding, 2, 1)
        grid.addWidget(execute_on_save, 3, 0)
        grid.addWidget(self.execute_on_save, 3, 1)
        grid.addWidget(show_line_numbers, 4, 0)
        grid.addWidget(self.show_line_numbers, 4, 1)
        grid.addWidget(allow_reload, 5, 0)
        grid.addWidget(self.allow_reload, 5, 1)
        
        gridWidget = QWidget()
        gridWidget.setLayout(grid)
        
        # The Radio Buttons DockWidget Layout
        groupBox = QGroupBox("DockWidget Layout")
        
        self.radio1 = QRadioButton("Left Top\r\nRight Top")
        self.radio2 = QRadioButton("Left Top\r\nRight Bottom")
        self.radio3 = QRadioButton("Left Bottom\r\nRight Top")
        self.radio4 = QRadioButton("Left Bottom\r\nRight Bottom")
        
        self.radio1.setIcon(QIcon(QPixmap(os.path.join(ICONPATH, "dock_layout_1.png"))))
        self.radio2.setIcon(QIcon(QPixmap(os.path.join(ICONPATH, "dock_layout_2.png"))))
        self.radio3.setIcon(QIcon(QPixmap(os.path.join(ICONPATH, "dock_layout_3.png"))))
        self.radio4.setIcon(QIcon(QPixmap(os.path.join(ICONPATH, "dock_layout_4.png"))))
        
        self.radio1.setIconSize(QSize(64, 64))
        self.radio2.setIconSize(QSize(64, 64))
        self.radio3.setIconSize(QSize(64, 64))
        self.radio4.setIconSize(QSize(64, 64))
        
        # find actual layout to set default radio button checked
        self.get_dock_layout()
        
        grid = QGridLayout()
        grid.setContentsMargins(10, 10, 10, 10)
        grid.addWidget(self.radio1, 0, 0)
        grid.addWidget(self.radio2, 0, 1)
        grid.addWidget(self.radio3, 1, 0)
        grid.addWidget(self.radio4, 1, 1)
        # grid.addStretch(1)
        groupBox.setLayout(grid)
        
        # Final Layout
        vbox = QVBoxLayout()
        vbox.addWidget(gridWidget)
        vbox.addWidget(groupBox)
        vbox.addWidget(self.buttons)
        self.setLayout(vbox)
    
    def radio_toggled(self):
        for radio in [self.radio1, self.radio2, self.radio3, self.radio4]:
            if radio.isChecked():
                self.set_dock_layout(radio)
    
    def get_dock_layout(self):
        mw = Gui.getMainWindow()
        topleft = mw.corner(Qt.TopLeftCorner)
        bottomleft = mw.corner(Qt.BottomLeftCorner)
        topright = mw.corner(Qt.TopRightCorner)
        bottomright = mw.corner(Qt.BottomRightCorner)
        
        if topleft == Qt.DockWidgetArea.LeftDockWidgetArea and \
                bottomleft == Qt.DockWidgetArea.BottomDockWidgetArea and \
                topright == Qt.DockWidgetArea.RightDockWidgetArea and \
                bottomright == Qt.DockWidgetArea.BottomDockWidgetArea:
            self.radio1.setChecked(True)
            
        elif topleft == Qt.DockWidgetArea.LeftDockWidgetArea and \
                bottomleft == Qt.DockWidgetArea.BottomDockWidgetArea and \
                topright == Qt.DockWidgetArea.RightDockWidgetArea and \
                bottomright == Qt.DockWidgetArea.RightDockWidgetArea:
            self.radio2.setChecked(True)
            
        elif topleft == Qt.DockWidgetArea.LeftDockWidgetArea and \
                bottomleft == Qt.DockWidgetArea.LeftDockWidgetArea and \
                topright == Qt.DockWidgetArea.RightDockWidgetArea and \
                bottomright == Qt.DockWidgetArea.BottomDockWidgetArea:
            self.radio3.setChecked(True)
            
        elif topleft == Qt.DockWidgetArea.LeftDockWidgetArea and \
                bottomleft == Qt.DockWidgetArea.LeftDockWidgetArea and \
                topright == Qt.DockWidgetArea.RightDockWidgetArea and \
                bottomright == Qt.DockWidgetArea.RightDockWidgetArea:
            self.radio4.setChecked(True)
            
        else:
            self.radio1.setChecked(True)
        
    def set_dock_layout(self, radio):
        # get DockWidgets
        mw = Gui.getMainWindow()
        
        # set layout 
        if radio == self.radio1:
            # set DockWidget Layout Left Top - Right Top
            mw.setCorner(Qt.TopLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
            mw.setCorner(Qt.BottomLeftCorner, Qt.DockWidgetArea.BottomDockWidgetArea)
            mw.setCorner(Qt.TopRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
            mw.setCorner(Qt.BottomRightCorner, Qt.DockWidgetArea.BottomDockWidgetArea)
            
        elif radio == self.radio2:
            # set DockWidget Layout Left Top - Right Bottom
            mw.setCorner(Qt.TopLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
            mw.setCorner(Qt.BottomLeftCorner, Qt.DockWidgetArea.BottomDockWidgetArea)
            mw.setCorner(Qt.TopRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
            mw.setCorner(Qt.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
            
        elif radio == self.radio3:
            # set DockWidget Layout Left Bottom - Right Top
            mw.setCorner(Qt.TopLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
            mw.setCorner(Qt.BottomLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
            mw.setCorner(Qt.TopRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
            mw.setCorner(Qt.BottomRightCorner, Qt.DockWidgetArea.BottomDockWidgetArea)
            
        elif radio == self.radio4:
            # set DockWidget Layout Left Bottom - Right Bottom
            mw.setCorner(Qt.TopLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
            mw.setCorner(Qt.BottomLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
            mw.setCorner(Qt.TopRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
            mw.setCorner(Qt.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)
    
    @Slot(int)
    def acceptSettings(self):
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetString("executeKeybinding", self.ui_execute_key_binding.text())
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetString("validateKeybinding", self.ui_validate_key_binding.text())
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetString("rebuildKeybinding", self.ui_rebuild_key_binding.text())
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("executeOnSave", self.execute_on_save.checkState())
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("showLineNumbers", self.show_line_numbers.checkState())
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).SetBool("allowReload", self.allow_reload.checkState())
        
        self.radio_toggled()
        
        self.accept()
        
