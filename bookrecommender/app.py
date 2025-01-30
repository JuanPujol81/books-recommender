from flask import Flask, render_template, request
from books import books
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return '<Book %r>' % self.title





app = Flask(__name__)

@app.route('/')
def home(): 
    query = request.args.get('query', '').lower()
    if query:
        filtered_books = [book for book in books if query in book['title'].lower()]
    else:
        filtered_books = books  
    return render_template('index.html', books=filtered_books)

if __name__ == '__main__':
    app.run(debug=True)