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

    from PySide import QtGui
    import sys

    class MainWindow(PySide.QtGui.QMainWindow):

        def __init__(self):
            super(MainWindow, self).__init__()

            self.createActions()
            self.createMenus()

            self.initUI()

        def createActions(self):
            self.actNewFile = QtGui.QAction(
                "&New", self,
                shortcut = "Ctrl+N",
                statusTip = "Create new Workspace",
                triggered = self.menuNewFile)
            self.actOpenFile = QtGui.QAction(
                QtGui.QIcon('open.png'), '&Open', self,
                shortcut = "Ctrl+O",
                statusTip = "Open Workspace",
                triggered = self.menuOpenFile)
            self.actPrintFile = QtGui.QAction(
                "&Print", self,
                shortcut = QtGui.QKeySequence.Print,
                statusTip = "Print the document",
                triggered = self.menuPrintFile)
            self.actSaveFile = QtGui.QAction(
                '&Save', self,
                shortcut = "Ctrl+S",
                statusTip = "Save Workspace",
                triggered = self.menuSaveFile)
            self.actExit = QtGui.QAction(
                "E&xit", self,
                shortcut = "Ctrl+X",
                statusTip = "Quit nemoa",
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
            self.fileMenu.addAction(self.actExit)

            self.itemMenu = self.menuBar().addMenu("&Item")
            self.itemMenu.addSeparator()

            self.aboutMenu = self.menuBar().addMenu("&Help")
            self.aboutMenu.addAction(self.actAbout)

        def initUI(self):

            self.textEdit = QtGui.QTextEdit()
            self.setCentralWidget(self.textEdit)
            self.statusBar()

            self.setGeometry(300, 300, 350, 300)
            self.setWindowTitle('Nemoa')
            self.show()

        def menuAbout(self):
            amail = nemoa.about('email')
            aversion = nemoa.about('version')
            acopyright = nemoa.about('copyright')
            adesc = nemoa.about('description').replace('\n', '<br>')
            acredits = '</i>, <i>'.join(nemoa.about('credits'))
            alicense = nemoa.about('license')

            text = ("""
                <h1>nemoa</h1>
                <b>version</b> %s<br>
                <i>%s</i>
                <h3>Copyright</h3>
                %s <a href = "mailto:%s">&lt;%s&gt;</a>
                <h3>License</h3>
                This software may be used under the terms of the
                %s as published by the
                <a href="https://gnu.org/licenses/gpl.html">
                Free Software Foundation</a>.
                <h3>Credits</h3>
                <i>%s</i>
                """ % (aversion, adesc, acopyright, amail, amail,
                alicense, acredits)).replace('                ', '')

            QtGui.QMessageBox.about(self, "About Nemoa", text)

        def menuOpenFile(self):
            path = nemoa.path('basepath', 'user')
            options = QtGui.QFileDialog.DontResolveSymlinks \
                | QtGui.QFileDialog.ShowDirsOnly
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                "test", path, options)
            if not directory: return False
            name = nemoa.common.ospath.basename(directory)
            if not nemoa.open(name): return False
            self.setWindowTitle(name.title())
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
    ex = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
