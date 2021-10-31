""" Update Cadquery CodeEditor ColorScheme and Font
    from FreeCAD Python Editor Settings """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License
import FreeCAD as App

from PySide2.QtCore import QObject
from PySide2.QtGui import QFont

class Freecad_Editor_Settings(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.parent = parent
        self.param = App.ParamGet("User parameter:BaseApp/Preferences/Editor")
        self.param.Attach(self)
        
        self.fontname = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetString("Font")
        self.fontsize = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetInt("FontSize")
        # self.indentsize = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetInt("IndentSize")
        self.text = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Text")/256
        self.keyword = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Keyword")/256
        self.operator = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Operator")/256
        self.defname = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Define name")/256
        self.classname = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Class name")/256
        self.string = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("String")/256
        self.comment = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Comment")/256
        self.numbers = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Number")/256
        self.curlinehighlight = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Current line highlight")/256
        
    def onChange(self, grp, strParam):
        if strParam == 'Font' or strParam == 'FontSize':
            self.fontname = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetString("Font")
            self.fontsize = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetInt("FontSize")
            self.parent.editor.setFont(QFont(self.fontname, self.fontsize))

        if strParam == 'Text':
            self.text = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Text")/256
            self.parent.editor.set_stylesheet()
        
        if strParam == 'Keyword':
            self.keyword = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Keyword")/256
        
        if strParam == 'Operator':
            self.operator = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Operator")/256
        
        if strParam == 'Define name':
            self.defname = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Define name")/256
        
        if strParam == 'Class name':
            self.classname = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Class name")/256
        
        if strParam == 'String':
            self.string = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("String")/256
        
        if strParam == 'Comment':
            self.comment = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Comment")/256
        
        if strParam == 'Number':
            self.numbers = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Number")/256
        
        if strParam == 'Current line highlight':
            self.curlinehighlight = App.ParamGet("User parameter:BaseApp/Preferences/Editor").GetUnsigned("Current line highlight")/256

        self.parent.editor.highlighter.setColorScheme()
        self.parent.editor.highlighter.setRules()
        self.parent.editor.highlighter.rehighlight()
