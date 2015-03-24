#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def main():

    import nemoa

    try:
        import PySide
    except ImportError:
        return nemoa.log('error',
            """could not execute nemoa gui:
            you have to install pyside.""")

    from PySide import QtGui, QtCore
    import sys

    class MainWindow(PySide.QtGui.QMainWindow):

        def __init__(self):
            super(MainWindow, self).__init__()

            self.textEdit = QtGui.QTextEdit()
            self.setCentralWidget(self.textEdit)

            self.createActions()
            self.createMenus()
            self.createStatusBar()

            self.readSettings()

            self.textEdit.document().contentsChanged.connect(self.documentWasModified)

            self.updateWindowTitle()
            self.setUnifiedTitleAndToolBarOnMac(True)

        def documentWasModified(self):
            self.setWindowModified(self.textEdit.document().isModified())

        def closeEvent(self, event):
            event.accept()
            if self.maybeSave():
                self.writeSettings()
                event.accept()
            else:
                event.ignore()

        def maybeSave(self):
            if self.textEdit.document().isModified():
                ret = QtGui.QMessageBox.warning(self, "Nemoa",
                        "The document has been modified."
                        "\nDo you want to save "
                        "your changes?",
                        QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                        QtGui.QMessageBox.Cancel)
                if ret == QtGui.QMessageBox.Save:
                    return self.save()
                elif ret == QtGui.QMessageBox.Cancel:
                    return False
            return True

        def createActions(self):
            self.actNewFile = QtGui.QAction(
                QtGui.QIcon(':/images/new.png'), "&New", self,
                shortcut = "Ctrl+N",
                statusTip = "Create a new workspace",
                triggered = self.menuNewFile)
            self.actOpenFile = QtGui.QAction(
                QtGui.QIcon(':/images/open.png'), '&Open...', self,
                shortcut = "Ctrl+O",
                statusTip = "Open an existing workspace",
                triggered = self.menuOpenFile)
            self.actSaveFile = QtGui.QAction(
                QtGui.QIcon(':/images/save.png'), '&Save', self,
                shortcut = "Ctrl+S",
                statusTip = "Save the workspace to disk",
                triggered = self.menuSaveFile)
            self.actSaveFile = QtGui.QAction(
                '&Save as...', self,
                statusTip = "Save the workspace under a new name",
                triggered = self.menuSaveFile)
            #2do only show ...
            self.actPrintFile = QtGui.QAction(
                "&Print", self,
                shortcut = QtGui.QKeySequence.Print,
                statusTip = "Print the document",
                triggered = self.menuPrintFile)
            self.actCloseFile = QtGui.QAction(
                "Close", self,
                shortcut = "Ctrl+W",
                statusTip = "Close current workspace",
                triggered = self.menuCloseFile)
            self.actExit = QtGui.QAction(
                "Exit", self,
                shortcut = "Ctrl+Q",
                statusTip = "Exit the application",
                triggered = self.close)
            self.actAbout = QtGui.QAction(
                "About", self,
                triggered = self.menuAbout)

        def createMenus(self):
            self.fileMenu = self.menuBar().addMenu("&File")
            self.fileMenu.addAction(self.actNewFile)
            self.fileMenu.addAction(self.actOpenFile)
            self.fileMenu.addAction(self.actSaveFile)
            self.fileMenu.addAction(self.actPrintFile)
            self.fileMenu.addSeparator()
            self.fileMenu.addAction(self.actCloseFile)
            self.fileMenu.addAction(self.actExit)

            self.aboutMenu = self.menuBar().addMenu("&Help")
            self.aboutMenu.addAction(self.actAbout)

        def createStatusBar(self):
            self.statusBar().showMessage("Ready")

        def readSettings(self):
            settings = QtCore.QSettings("Froot", "Nemoa")
            pos = settings.value("pos", QtCore.QPoint(200, 200))
            size = settings.value("size", QtCore.QSize(400, 400))
            self.resize(size)
            self.move(pos)

        def writeSettings(self):
            settings = QtCore.QSettings("Froot", "Nemoa")
            settings.setValue("pos", self.pos())
            settings.setValue("size", self.size())

        def updateWindowTitle(self):
            self.textEdit.document().setModified(False)
            self.setWindowModified(False)

            if nemoa.get('workspace'):
                shownName = nemoa.get('workspace')
            else:
                shownName = 'untitled'

            self.setWindowTitle("%s[*] - Nemoa" % shownName)

        def menuAbout(self):
            amail = nemoa.about('email')
            aversion = nemoa.about('version')
            acopyright = nemoa.about('copyright')
            adesc = nemoa.about('description').replace('\n', '<br>')
            acredits = '</i>, <i>'.join(nemoa.about('credits'))
            alicense = nemoa.about('license')

            text = (
                "<h1>nemoa</h1>"
                "<b>version</b> %s<br>"
                "<i>%s</i>"
                "<h3>Copyright</h3>"
                "%s <a href = 'mailto:%s'>&lt;%s&gt;</a>"
                "<h3>License</h3>"
                "This software may be used under the terms of the"
                "%s as published by the"
                "<a href='https://gnu.org/licenses/gpl.html'>"
                "Free Software Foundation</a>."
                "<h3>Credits</h3>"
                "<i>%s</i>" % (aversion, adesc, acopyright, amail, amail,
                alicense, acredits))

            QtGui.QMessageBox.about(self, "About Nemoa", text)

        def menuCloseFile(self):
            nemoa.close()
            self.updateWindowTitle()
            self.textEdit.setText('')

        def menuOpenFile(self):
            path = nemoa.path('basepath', 'user')
            options = QtGui.QFileDialog.DontResolveSymlinks \
                | QtGui.QFileDialog.ShowDirsOnly
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                "test", path, options)
            if not directory: return False
            name = nemoa.common.ospath.basename(directory)
            if not nemoa.open(name): return False
            self.updateWindowTitle()
            text = ''
            for key, val in nemoa.list().items():
                if not val: continue
                text += '%s: %s\n' % (key, ', '.join(val))
            self.textEdit.setText(text)

        def menuPrintFile(self):
            pass

        def menuNewFile(self):
            pass

        def menuSaveFile(self):
            pass

    nemoa.set('mode', 'silent')
    app = QtGui.QApplication(sys.argv)
    Window = MainWindow()
    Window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
