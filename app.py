from flask import Flask
from project.scraping import scrape_books
from flask import render_template

app = Flask(__name__)


@app.route("/")
def home():
    books = scrape_books(2)
    return render_template("index.html", books=books)


@app.route("/scrape")
def scrape():
    books = scrape_books(2)
    return str(books)

if __name__ == "__main__":
    app.run(debug=True)