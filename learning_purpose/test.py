from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Form Example")

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()

        # Input field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter your name")

        # Label
        self.label = QLabel("Your name will appear here")

        # Button
        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.show_name)

        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        central.setLayout(layout)

    def show_name(self):
        text = self.input.text()
        self.label.setText(f"Hello {text} 👋")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())