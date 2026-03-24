from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time


def scrape_books(pages):
   
    options = Options()
    # REMOVE headless → to SEE browser
    # options.add_argument("--headless")  

    # Optional: start maximized
   

    # 👉 Setup driver (auto install)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    books = []

    for page in range(1, pages + 1):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        driver.get(url)

        time.sleep(1)  # small wait to load page

        titles = driver.find_elements(By.CSS_SELECTOR, "h3 a")
        prices = driver.find_elements(By.CLASS_NAME, "price_color")

        for t, p in zip(titles, prices):
            title = t.get_attribute("title")  # full title
            price = p.text

            if isinstance(title, str) and isinstance(price, str):
                books.append((title, price))

    time.sleep(2)  
    driver.quit()

    return books