from flask import Flask, render_template, request
from models import db, Book
from books import books

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    if not Book.query.first():
        sample_books=[Book(title=book['title'], author=book['author'], genre=book['genre'], year=book['year'], description=book['description']) for book in books]
        db.session.add_all(sample_books)
        db.session.commit()
    db.create_all()

@app.route('/')
def home():
    query = request.args.get('query', '')
    if query:
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) |
            (Book.author.ilike(f'%{query}%')) |
            (Book.genre.ilike(f'%{query}%'))
        ).all()
    else:
        books = Book.query.all()

    return render_template('index.html', books=books)
    


def index():
    return "Welcome to the Book Recommender!"

if __name__ == '__main__':
    app.run(debug=True)