from flask import Flask
from project.database import get_all_books
from project.scraping import scrape_books
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route("/")
def home():
    page = int(request.args.get("page", 1))  # default page 1
    per_page = 10

    all_books = get_all_books()
    total = len(all_books)
    start = (page - 1) * per_page
    end = start + per_page
    books = all_books[start:end]

    total_pages = (total + per_page - 1) // per_page  # ceil division

    return render_template(
        "index.html",
        books=books,
        page=page,
        total_pages=total_pages
    )


@app.route("/scrape")
def scrape():
    books = scrape_books(2)
    return str(books)

if __name__ == "__main__":
    app.run(debug=True)