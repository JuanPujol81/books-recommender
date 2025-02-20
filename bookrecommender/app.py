from flask import Flask, render_template, request, jsonify
from models import db, Book
from books import books

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()  # Create all tables
    if not Book.query.first():
        sample_books = [
            Book(title=book['title'], author=book['author'], genre=book['genre'], year=book['year'], description=book['description'])
            for book in books
        ]
        db.session.add_all(sample_books)
        db.session.commit()

# Home route that renders the index.html template
# If a query parameter is provided, it filters books by title, author, or genre
# Otherwise, it retrieves all books from the database
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

# Route to delete a book by its ID
# If the book is found, it deletes the book and returns a 204 status code
# If the book is not found, it returns a 404 status code
@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': f'Book with {book_id} deleted'}), 204
    else:
        return jsonify({'message': f'Book with {book_id} not found'}), 404
    

# Route to add a new book to the database
@app.route('/add_book' , methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = Book(title=data['title'], author=data['author'], genre=data['genre'], year=data['year'], description=data['description'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': f'Book {new_book.title} added successfully'}), 201


if __name__ == '__main__':
    app.run(debug=True)