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
    import qtgui_rc

    class MainWindow(PySide.QtGui.QMainWindow):

        def __init__(self):
            super(MainWindow, self).__init__()

            self.textEdit = QtGui.QTextEdit()
            self.setCentralWidget(self.textEdit)

            self.createActions()
            self.createMenus()
            self.createToolBars()
            self.createStatusBar()
            self.createDockWindows()

            self.readSettings()

            self.textEdit.document().contentsChanged.connect(self.documentWasModified)

            self.setUnifiedTitleAndToolBarOnMac(True)
            self.updateChangeFile()

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
            iconGet = self.style().standardIcon

            self.actNewFile = QtGui.QAction(
                QtGui.QIcon(':/images/nemoa_logo.png'),
                "&New", self,
                shortcut = "Ctrl+N",
                statusTip = "Create a new workspace",
                triggered = self.menuNewFile)

            self.actOpenFile = QtGui.QAction(
                iconGet(QtGui.QStyle.SP_FileDialogNewFolder),
                '&Open...', self,
                shortcut = "Ctrl+O",
                statusTip = "Open an existing workspace",
                triggered = self.menuOpenFile)

            self.actSaveFile = QtGui.QAction(
                QtGui.QIcon.fromTheme('document-save'),
                #iconGet(QtGui.QStyle.SP_DialogSaveButton),
                '&Save', self,
                shortcut = "Ctrl+S",
                statusTip = "Save the workspace to disk",
                triggered = self.menuSaveFile)

            self.actSaveAsFile = QtGui.QAction(
                'Save as...', self,
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
            self.fileMenu.addAction(self.actSaveAsFile)
            self.fileMenu.addAction(self.actPrintFile)
            self.fileMenu.addSeparator()
            self.fileMenu.addAction(self.actCloseFile)
            self.fileMenu.addAction(self.actExit)

            self.viewMenu = self.menuBar().addMenu("&View")

            self.aboutMenu = self.menuBar().addMenu("&Help")
            self.aboutMenu.addAction(self.actAbout)

        def createStatusBar(self):
            self.statusBar().showMessage("Ready")

        def createToolBars(self):
            self.fileToolBar = self.addToolBar("File")
            self.fileToolBar.addAction(self.actNewFile)
            self.fileToolBar.addAction(self.actOpenFile)
            self.fileToolBar.addAction(self.actSaveFile)

            #self.editToolBar = self.addToolBar("Edit")
            #self.editToolBar.addAction(self.cutAct)
            #self.editToolBar.addAction(self.copyAct)
            #self.editToolBar.addAction(self.pasteAct)

        def createDockWindows(self):

            dock = QtGui.QDockWidget("Resource", self)
            dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea \
                | QtCore.Qt.RightDockWidgetArea)
            widget = QtGui.QWidget(dock)
            self.amountLabel = QtGui.QLabel('Amount')
            self.amountLabel2 = QtGui.QLabel('bla')
            self.checkbox1 = QtGui.QCheckBox("Checkbox1")
            self.checkbox2 = QtGui.QCheckBox("Checkbox2")
            self.listTest = QtGui.QListWidget()
            self.treeWidget = QtGui.QTreeWidget(widget)

            self.treeWidget.setColumnCount( 1 )
            self.treeWidget.setHeaderLabels( ('objects', ) )
            self.treeWidget.itemDoubleClicked.connect(self.doShowObject)

            ## Add Items:
            #self.treeWidget.resizeColumnToContents(0)
            #self.treeWidget.addTopLevelItems(itemList)
            #model = QtGui.QFileSystemModel()
            #model.setRootPath( QtCore.QDir.currentPath() )
            #self.treeWidget.setModel(model)

            self.button1 = QtGui.QPushButton("Show")
            self.button1.clicked.connect(self.doShowObject)
            self.button2 = QtGui.QPushButton("Edit")
            self.button3 = QtGui.QPushButton("New")
            self.button4 = QtGui.QPushButton("Import")
            self.button5 = QtGui.QPushButton("Export")
            self.button6 = QtGui.QPushButton("Delete")
            grid = QtGui.QGridLayout()
            grid.setSpacing(0)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.addWidget(self.button1, 1, 0)
            grid.addWidget(self.button2, 1, 1)
            grid.addWidget(self.button3, 1, 2)
            grid.addWidget(self.button4, 1, 3)
            grid.addWidget(self.button5, 1, 4)
            grid.addWidget(self.button6, 1, 5)
            grid.addWidget(self.treeWidget, 0, 0, 1, -1)
            self.setLayout(grid)
            widget.setLayout(grid)
            dock.setWidget(widget)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

            dock = QtGui.QDockWidget("Datasets", self)
            dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea \
                | QtCore.Qt.RightDockWidgetArea)
            self.dockDatasetList = QtGui.QListWidget(dock)
            self.dockDatasetList.setDragEnabled(True)
            #self.dockDatasetList.setAcceptDrops(True)
            self.dockDatasetList.setIconSize(QtCore.QSize(32, 32))
            self.dockDatasetList.setAlternatingRowColors(True)
            dock.setWidget(self.dockDatasetList)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
            self.viewMenu.addAction(dock.toggleViewAction())

            dock = QtGui.QDockWidget("Networks", self)
            dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea \
                | QtCore.Qt.RightDockWidgetArea)
            self.dockNetworkList = QtGui.QListWidget(dock)
            self.dockNetworkList.setDragEnabled(True)
            #self.dockNetworkList.setAlternatingRowColors(True)
            self.dockNetworkList.setIconSize(QtCore.QSize(32, 32))
            self.dockNetworkList.setAlternatingRowColors(True)
            self.dockNetworkList.currentTextChanged.connect(
                self.dockNetworkListChanged)
            dock.setWidget(self.dockNetworkList)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
            self.viewMenu.addAction(dock.toggleViewAction())

            dock = QtGui.QDockWidget("Systems", self)
            dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea \
                | QtCore.Qt.RightDockWidgetArea)
            self.dockSystemList = QtGui.QListWidget(dock)
            self.dockSystemList.setDragEnabled(True)
            #self.dockSystemList.setAlternatingRowColors(True)
            self.dockSystemList.setIconSize(QtCore.QSize(32, 32))
            self.dockSystemList.setAlternatingRowColors(True)
            dock.setWidget(self.dockSystemList)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
            self.viewMenu.addAction(dock.toggleViewAction())

        def dockNetworkListChanged(self, name):
            if not name: return None


        def doShowObject(self, *args, **kwargs):
            print self.treeWidget.currentItem()
            print 'hi'

            #network = nemoa.network.open(name)
            #network.show()

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
                "<i>%s</i>" % (aversion, adesc, acopyright, amail,
                amail, alicense, acredits))

            QtGui.QMessageBox.about(self, "About Nemoa", text)

        def updateChangeFile(self):

            #text = ''
            #for key, val in nemoa.list().items():
                #if not val: continue
                #text += '%s: %s\n' % (key, ', '.join(val))
            #self.textEdit.setText(text)

            self.updateResourcesDock()
            self.updateWindowTitle()

        def updateResourcesDock(self):

            self.treeWidget.clear()
            self.treeWidget.setDragEnabled(True)
            objectList = ['models', 'datasets', 'networks', 'systems', 'scripts']
            itemList = []
            for topItem in objectList:
                knownlist = nemoa.list(topItem)
                topLevelItem = QtGui.QTreeWidgetItem(topItem)
                topLevelItem.setText(0, topItem.title())
                topLevelItem.setIcon(0, QtGui.QIcon(":/images/nemoa_logo.png"))
                self.treeWidget.addTopLevelItem(topLevelItem)
                if not knownlist:
                    topLevelItem.setDisabled(True)
                    continue
                for childItem in knownlist:
                    child = QtGui.QTreeWidgetItem(topLevelItem)
                    child.setText(0, childItem.title())

            self.dockDatasetList.clear()
            self.dockDatasetList.addItems(nemoa.list('datasets'))
            self.dockNetworkList.clear()
            self.dockNetworkList.addItems(nemoa.list('networks'))
            self.dockSystemList.clear()
            self.dockSystemList.addItems(nemoa.list('systems'))

        def menuCloseFile(self):
            nemoa.close()
            self.updateChangeFile()

        def menuOpenFile(self):
            path = nemoa.path('basepath', 'user')
            options = QtGui.QFileDialog.DontResolveSymlinks \
                | QtGui.QFileDialog.ShowDirsOnly
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                "test", path, options)
            if not directory: return False
            name = nemoa.common.ospath.basename(directory)
            if not nemoa.open(name): return False
            self.updateChangeFile()

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
