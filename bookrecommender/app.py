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
    query = request.args.get('query', '')  # Obtén el texto del input de búsqueda
    if query:
        # Filtra los libros por título
        filtered_books = [book for book in books if query.lower() in book['title'].lower()]
    else:
        filtered_books = books  # Si no hay búsqueda, muestra todos los libros
    return render_template('index.html', books=filtered_books)


def index():
    return "Welcome to the Book Recommender!"

if __name__ == '__main__':
    app.run(debug=True)