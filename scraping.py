from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QLabel, QLineEdit
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv,os
from PyQt5.QtGui import QColor



class BookScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Book Price Tracker")
        self.setGeometry(100, 100, 600, 400)

        self.all_books = []
        self.old_prices = {}

        if os.path.exists("books.csv"):
          with open("books.csv", "r", encoding="utf-8") as f:
           next(f)
           for line in f:
            title, price = line.strip().split(",")
            self.old_prices[title] = price

            
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Input
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("Enter number of pages (e.g. 3)")
        layout.addWidget(self.page_input)

        # Button
        self.scrape_btn = QPushButton("Scrape Books")
        self.scrape_btn.clicked.connect(self.scrape_books)
        layout.addWidget(self.scrape_btn)

        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.resizeColumnsToContents()


        # Sort button
        self.sort_btn = QPushButton("Sort by Price")
        self.sort_btn.clicked.connect(self.sort_data)
        layout.addWidget(self.sort_btn)

    def sort_data(self):
        self.all_books.sort(key=lambda x: float(x[1][1:]))
        self.update_table(self.all_books)

    def scrape_books(self):
        self.status_label.setText("Scraping...")

        pages_text = self.page_input.text()
        if not pages_text.isdigit():
            self.status_label.setText("Enter valid number ❌")
            return

        pages = int(pages_text)

        driver = webdriver.Chrome()
        self.all_books = []

        for page in range(1, pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            driver.get(url)

            titles = driver.find_elements(By.TAG_NAME, "h3")
            prices = driver.find_elements(By.CLASS_NAME, "price_color")

            for t, p in zip(titles, prices):
                self.all_books.append([t.text, p.text])

        driver.quit()

        self.update_table(self.all_books)
        self.status_label.setText("Scraping Complete ✅")

        # Save CSV
        with open("books.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Price"])
            writer.writerows(self.all_books)

    def update_table(self, data):
     self.table.setRowCount(len(data))
     self.table.setColumnCount(2)
     self.table.setHorizontalHeaderLabels(["Title", "Price"])

     for row, (title, price) in enumerate(data):
        self.table.setItem(row, 0, QTableWidgetItem(title))
        item = QTableWidgetItem(price)

        # Compare with old prices
        if title in self.old_prices:
            old_price = float(self.old_prices[title][1:])
            new_price = float(price[1:])

            if new_price < old_price:
                item.setBackground(QColor("lightgreen"))  # 🟢 cheaper
            elif new_price > old_price:
                item.setBackground(QColor("red"))         # 🔴 more expensive
            else:
                item.setBackground(QColor("yellow"))      # 🟡 same price

        self.table.setItem(row, 1, item)

     self.table.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookScraperApp()
    window.show()
    sys.exit(app.exec_())