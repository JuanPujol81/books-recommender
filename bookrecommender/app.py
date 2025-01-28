from flask import Flask, render_template, request
from books import books



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