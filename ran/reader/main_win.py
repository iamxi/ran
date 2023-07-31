import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        """修改主窗口名字"""
        self.setWindowTitle("然")
        """添加按钮控件"""
        button = QPushButton("Press Me!")

        """使按钮控件在窗口居中"""
        self.setCentralWidget(button)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()