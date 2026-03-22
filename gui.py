from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Counter App")
        self.count = 0

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()

        self.label = QLabel("0")
        self.button = QPushButton("Increase")

        self.button.clicked.connect(self.increase)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

        central.setLayout(layout)

    def increase(self):
        self.count += 1
        self.label.setText(str(self.count))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())