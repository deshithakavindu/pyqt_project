from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QLabel
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

class BookScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Book Price Tracker")
        self.setGeometry(100, 100, 600, 400)

        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Button
        self.scrape_btn = QPushButton("Scrape Books")
        self.scrape_btn.clicked.connect(self.scrape_books)
        layout.addWidget(self.scrape_btn)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)

    def scrape_books(self):
        self.status_label.setText("Scraping...")
        driver = webdriver.Chrome()
        all_books = []

        for page in range(1, 4):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            driver.get(url)

            titles = driver.find_elements(By.TAG_NAME, "h3")
            prices = driver.find_elements(By.CLASS_NAME, "price_color")

            for t, p in zip(titles, prices):
                all_books.append([t.text, p.text])

        driver.quit()
        self.status_label.setText("Scraping Complete ✅")

        # Show in table
        self.table.setRowCount(len(all_books))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Title", "Price"])

        for row, (title, price) in enumerate(all_books):
            self.table.setItem(row, 0, QTableWidgetItem(title))
            self.table.setItem(row, 1, QTableWidgetItem(price))

        # Optional: Save to CSV
        with open("books.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Price"])
            writer.writerows(all_books)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookScraperApp()
    window.show()
    sys.exit(app.exec_())