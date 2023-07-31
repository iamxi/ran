import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWebEngineWidgets import QWebEngineView

from ebook_parser.epub_book import *

class MainWindow(QMainWindow):
    def __init__(self, book_path):
        super().__init__()

        self.ebook = EpubBook(book_path)
        
        """修改主窗口名字"""
        self.setWindowTitle(self.ebook.title)

        layout = QHBoxLayout()

        """使按钮控件在窗口居中"""
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        
        tree = self._build_toc_tree()
        layout.addWidget(tree)
        layout.setStretch(0, 2)

        self.webView = QWebEngineView()
        layout.addWidget(self.webView)
        layout.setStretch(1, 8)

    
    @QtCore.Slot()
    def toc_tree_clicked(self, index):
        # self.webView.load(QtCore.QUrl(index.data(QtCore.Qt.UserRole + 1)))
        self.webView.setHtml(self.ebook.get_content((index.data(QtCore.Qt.UserRole + 1))))

    def _build_toc_tree(self) -> QTreeView:
        tree = QTreeView()
        model = QStandardItemModel()
        tree.setModel(model)
        tree.setHeaderHidden(True)
        tree.clicked.connect(self.toc_tree_clicked)

        toc = self.ebook.get_toc()
        for item in toc.items:
            tree_item = QStandardItem(item.text)
            tree_item.setData(item.location, QtCore.Qt.UserRole + 1)
            model.appendRow(tree_item)
            self._build_toc_tree_item(item.clildren, tree_item)
        return tree
    
    def _build_toc_tree_item(self, toc_items, parent_item) -> None:
        if len(toc_items) > 0:
            for item in toc_items:
                tree_item = QStandardItem(item.text)
                tree_item.setData(item.location, QtCore.Qt.UserRole + 1)
                parent_item.appendRow(tree_item)
                self._build_toc_tree_item(item.clildren, tree_item)

def open_epub_viewer():
    app = QApplication(sys.argv)

    window = MainWindow('D://5%的改变.epub')
    window.showFullScreen()

    app.exec()