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

    class Example(PySide.QtGui.QMainWindow):

        def __init__(self):
            super(Example, self).__init__()

            self.initUI()

        def initUI(self):

            self.textEdit = QtGui.QTextEdit()
            self.setCentralWidget(self.textEdit)
            self.statusBar()

            openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
            openFile.setShortcut('Ctrl+O')
            openFile.setStatusTip('Open Workspace')
            openFile.triggered.connect(self.getOpenWorkspace)

            menubar = self.menuBar()
            fileMenu = menubar.addMenu('&File')
            fileMenu.addAction(openFile)

            self.setGeometry(300, 300, 350, 300)
            self.setWindowTitle('Nemoa')
            self.show()

        def getOpenWorkspace(self):

            path = nemoa.path('basepath', 'user')
            options = QtGui.QFileDialog.DontResolveSymlinks \
                | QtGui.QFileDialog.ShowDirsOnly
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                "test",
                path, options)
            if not directory: return False
            name = nemoa.common.ospath.basename(directory)
            if not nemoa.open(name): return False
            self.setWindowTitle(name.title())
            text = ''
            for key, val in nemoa.list().items():
                if not val: continue
                text += '%s: %s\n' % (key, ', '.join(val))
            self.textEdit.setText(text)

    nemoa.set('mode', 'silent')
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
