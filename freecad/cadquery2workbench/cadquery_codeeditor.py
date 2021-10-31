""" the cadquery2 workbench Python Text Editor """
# (c) 2021-2021 Jean-Paul (jpmlt) Apache 2.0 License
# Fork of freecad-cadquery-module made for cadquery1.0 by
# (c) 2014-2018 Jeremy Wright Apache 2.0 License

import os.path
import FreeCAD
from PySide2.QtCore import QSize, QRect, Qt, QRegExp, Slot
from PySide2.QtGui import QPainter, QTextCharFormat, QColor, QFont, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from freecad.cadquery2workbench import MODULENAME
from freecad.cadquery2workbench import pythonSyntax

class LineNumberArea(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.codeEditor = parent

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(),0)

    def paintEvent(self,event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent):
        # super(CodeEditor, self).__init__()
        QPlainTextEdit.__init__(self)
        self.parent = parent
        self.setFont(QFont(self.parent.fcedset.fontname, self.parent.fcedset.fontsize))
        self.lineNumberArea = LineNumberArea(self)
        self.setTabStopWidth(20)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        self.highlighter = pythonSyntax.PythonHighlighter(self.document(), self.parent)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.dirty = False
        
        # Determine if the line number area needs to be shown or not
        lineNumbersCheckedState = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/" + MODULENAME).GetBool("showLineNumbers")
        if lineNumbersCheckedState:
            self.showLineNumberArea()
        else:
            self.hideLineNumberArea()

        # self.overlay = FinderOverlay(self)
        # self.overlay.hide()

        self.set_stylesheet()
        self.initUI()
        
    def set_stylesheet(self):
        color = hex(int(self.parent.fcedset.text))[2:]
        self.setStyleSheet("QPlainTextEdit, QPlainTextEdit:focus \
                            {{ color: #{0}; }}".format(color))
    
    def hideLineNumberArea(self):
        """
        Hides this editor's line number area.
        :return: None
        """
        self.lineNumberArea.setVisible(False)

    def showLineNumberArea(self):
        """
        Shows this editor's line number area.
        :return: None
        """
        self.lineNumberArea.setVisible(True)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while (block.isValid() and top <= event.rect().bottom()):
            if (block.isValid and bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(),
                                 self.fontMetrics().height(),
                                 Qt.AlignCenter, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def lineNumberAreaWidth(self):
        digits = 1
        dMax = max(1, self.blockCount())
        while (dMax >= 10):
            dMax /= 10
            digits += 1
        return 3 + self.fontMetrics().width('9') * digits

    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(),
                  cr.height()))
    
    @Slot(int)
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    @Slot(QRect, int)
    def updateLineNumberArea(self, rect, dy):
        if (dy != 0):
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(),
                                       self.lineNumberArea.width(),
                                       rect.height())
        if (rect.contains(self.viewport().rect())):
            self.updateLineNumberAreaWidth(0)

    @Slot()
    def highlightCurrentLine(self):
        extraSelections = []
        if (not self.isReadOnly()):
            lineColor = QColor(self.parent.fcedset.curlinehighlight)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor=self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
    
    def keyPressEvent(self,event):
        self.dirty = True
        customKey=False
        #AutoTab
        if (event.key()==Qt.Key_Enter or event.key()==16777220):
            customKey=True
            numTab=0
            #new line
            newBlock=self.textCursor().block()
            currLine=newBlock.text()
            tabRE=QRegExp("^[\t]*")
            tabRE.indexIn(currLine)
            numTab=tabRE.matchedLength()
            if (currLine != "" and currLine.strip()[-1] == "{"):
                numTab += 1
            QPlainTextEdit.keyPressEvent(self,event)
            if (numTab > 0):
                tCursor=self.textCursor()
                for _ in range(0,numTab):
                    tCursor.insertText("\t")

                #automatic close brace
                if currLine != "" and currLine.strip()[-1] == "{":
                    tCursor.insertText("\n")
                    for _ in range(0,numTab-1):
                        tCursor.insertText("\t")
                    tCursor.insertText("}")
                    tCursor.movePosition(QTextCursor.PreviousBlock)
                    tCursor.movePosition(QTextCursor.EndOfLine)
                    self.setTextCursor(tCursor)

        if event.key() == Qt.Key_Tab and self.textCursor().hasSelection():
            customKey = True
            selStart=self.textCursor().selectionStart()
            selEnd=self.textCursor().selectionEnd()
            cur=self.textCursor()
            endBlock=self.document().findBlock(selEnd)
            currBlock=self.document().findBlock(selStart)
            while currBlock.position()<=endBlock.position():
                cur.setPosition(currBlock.position())
                cur.insertText("\t")
                currBlock=currBlock.next()

        if event.key() == Qt.Key_Backtab and self.textCursor().hasSelection():
            customKey = True
            selStart = self.textCursor().selectionStart()
            selEnd = self.textCursor().selectionEnd()
            cur = self.textCursor()
            endBlock = self.document().findBlock(selEnd)
            currBlock = self.document().findBlock(selStart)
            while currBlock.position() <= endBlock.position():
                cur.setPosition(currBlock.position())
                if currBlock.text().left(1) == "\t":
                    cur.deleteChar()
                currBlock=currBlock.next()

        # Allow commenting and uncommenting of blocks of code
        if event.key() == Qt.Key_Slash and event.modifiers() == Qt.ControlModifier:
            customKey = True
            selStart = self.textCursor().selectionStart()
            selEnd = self.textCursor().selectionEnd()
            cur = self.textCursor()
            endBlock = self.document().findBlock(selEnd)
            currBlock = self.document().findBlock(selStart)

            while currBlock.position() <= endBlock.position():
                cur.setPosition(currBlock.position())

                if currBlock.text()[0] == "#":
                   cur.deleteChar()

                   # Make sure we remove extra spaces
                   while currBlock.text()[0] == " ":
                        cur.deleteChar()
                else:
                    cur.insertText("# ")

                currBlock = currBlock.next()

        # Open the text finder
        # if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
        #     customKey = True
        #     print("Opening finder...")

        if not customKey:
            QPlainTextEdit.keyPressEvent(self, event)

    def initUI(self):
        pass
