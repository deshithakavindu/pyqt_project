from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


# ─────────────────────────────────────────────
#  BUILT-IN SITE PRESETS
#  Each preset defines how to scrape one site.
#  Users can also define their own custom config.
# ─────────────────────────────────────────────
SITE_PRESETS = {
    "Books to Scrape": {
        "url_pattern":    "https://books.toscrape.com/catalogue/page-{page}.html",
        "title_selector": ("CSS", "h3 a"),
        "title_attr":     "title",          # use attribute, not .text
        "price_selector": ("CSS", ".price_color"),
        "price_attr":     None,             # use .text
        "next_page":      "pager",          # CSS class of next-page button
        "wait_for":       ".product_pod",   # element to wait for before scraping
    },
    "Custom Website": None,  # user fills manually
}


def _make_driver(headless=True):
    from selenium.webdriver.chrome.options import Options
    opts = Options()
    if headless:
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=opts)


def _get_text(el, attr=None):
    """Get text or attribute value from a Selenium element."""
    if attr:
        return (el.get_attribute(attr) or "").strip()
    return (el.text or "").strip()


# ─────────────────────────────────────────────
#  SCRAPE — PRESET SITE  (books.toscrape.com)
# ─────────────────────────────────────────────
def scrape_books(pages, headless=True):
    """Original scraper for books.toscrape.com"""
    driver = _make_driver(headless)
    books  = []

    try:
        for page in range(1, pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product_pod"))
                )
            except TimeoutException:
                break

            titles = driver.find_elements(By.CSS_SELECTOR, "h3 a")
            prices = driver.find_elements(By.CSS_SELECTOR, ".price_color")

            for t, p in zip(titles, prices):
                title = t.get_attribute("title") or t.text
                price = p.text
                if isinstance(title, str) and isinstance(price, str) and title and price:
                    books.append((title.strip(), price.strip()))
    finally:
        driver.quit()

    return books


# ─────────────────────────────────────────────
#  SCRAPE — CUSTOM WEBSITE
#  config dict keys:
#    url          : full URL or pattern with {page}
#    pages        : number of pages to scrape
#    title_sel    : CSS selector for title element
#    title_attr   : attribute to read (e.g. "title", "data-name") or None for .text
#    price_sel    : CSS selector for price element
#    price_attr   : attribute to read or None for .text
#    wait_sel     : CSS selector to wait for before scraping (optional)
#    headless     : bool (default True)
# ─────────────────────────────────────────────
def scrape_custom(config: dict):
    """
    Generic scraper driven by CSS selectors.
    Returns list of (title, price) tuples.
    Raises ValueError with helpful message on bad config.
    """
    url_pattern = config.get("url")
    pages       = int(config.get("pages", 1))
    title_sel   = config.get("title_sel", "")
    title_attr  = config.get("title_attr", None) or None
    price_sel   = config.get("price_sel", "")
    price_attr  = config.get("price_attr", None) or None
    wait_sel    = config.get("wait_sel", None) or None
    headless    = config.get("headless", True)

    if not url_pattern:
        raise ValueError("URL is required.")
    if not title_sel:
        raise ValueError("Title CSS selector is required.")
    if not price_sel:
        raise ValueError("Price CSS selector is required.")

    driver = _make_driver(headless)
    books  = []
    errors = []

    try:
        for page in range(1, pages + 1):
            # Support {page} placeholder or plain URL
            if "{page}" in url_pattern:
                url = url_pattern.format(page=page)
            else:
                url = url_pattern   # single page site

            driver.get(url)

            # Wait for target element
            if wait_sel:
                try:
                    WebDriverWait(driver, 12).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_sel))
                    )
                except TimeoutException:
                    errors.append(f"Page {page}: timed out waiting for '{wait_sel}'")
                    continue
            else:
                time.sleep(2)   # fallback wait

            title_els = driver.find_elements(By.CSS_SELECTOR, title_sel)
            price_els = driver.find_elements(By.CSS_SELECTOR, price_sel)

            if not title_els:
                errors.append(f"Page {page}: no elements found for title selector '{title_sel}'")
                continue
            if not price_els:
                errors.append(f"Page {page}: no elements found for price selector '{price_sel}'")
                continue

            for t, p in zip(title_els, price_els):
                title = _get_text(t, title_attr)
                price = _get_text(p, price_attr)
                if title and price:
                    books.append((title, price))

    finally:
        driver.quit()

    if errors:
        print("[scraper warnings]", "\n".join(errors))

    return books


# ─────────────────────────────────────────────
#  PREVIEW — test selectors on ONE page
#  Returns up to 5 sample (title, price) pairs
#  so the user can verify before full scrape.
# ─────────────────────────────────────────────
def preview_custom(config: dict):
    """Returns up to 5 rows as a quick selector test."""
    preview_config = dict(config)
    preview_config["pages"] = 1
    results = scrape_custom(preview_config)
    return results[:5]