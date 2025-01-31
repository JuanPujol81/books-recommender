from flask import Flask, render_template, request
from books import books
from models import db, Book


app = Flask(__name__)
# Configurar SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

# Crear la base de datos
with app.app_context():
    if not Book.query.first():  # Solo agrega si la BD está vacía
        sample_books = [
            Book(title="1984", author="George Orwell", genre="Dystopian", year=2003, description="A dystopian social science fiction novel and cautionary tale by George Orwell."),
            Book(title="To Kill a Mockingbird", author="Harper Lee", genre="Fiction", year=1960, description="A novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature."),
            Book(title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Classic", year=1925, description="A novel by American writer F. Scott Fitzgerald. Set in the Jazz Age on Long Island, the novel depicts narrator Nick Carraway's interactions with mysterious millionaire Jay Gatsby and Gatsby's obsession to reunite with his former lover, Daisy Buchanan."),
        ]
        db.session.add_all(sample_books)
        db.session.commit()
    db.create_all()

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