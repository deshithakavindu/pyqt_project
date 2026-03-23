from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QLabel
import sys
from PyQt5.QtGui import QIcon,QFont,QPixmap
from PyQt5.QtCore import Qt #  Qt for aligment


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(" App")
        self.setWindowIcon(QIcon("download.jpeg"))
        self.setGeometry(700, 300, 500, 500)




        label = QLabel("hiii",self)
        label.setFont(QFont("Arial",30))
        label.setGeometry(0,0,500,100)
        label.setStyleSheet("color: blue;"
                            "background-color:green;"
                            "font-weight:bold;"
                            "font-style:italic;"
                            "text-decoration:underline;")
    
        
        label.setAlignment(Qt.AlignCenter)
        # Button
        self.button = QPushButton("Click Me", self)
        self.button.move(150, 120)

        # Connect event
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        print("Button clicked 🚀")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())