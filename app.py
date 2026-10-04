import os
from datetime import datetime, timezone

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render provides DATABASE_URL; locally we fall back to SQLite.
db_url = os.environ.get("DATABASE_URL", "sqlite:///library.db")
# Force the psycopg2 driver (newer SQLAlchemy defaults to psycopg3, which we don't install)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Student details, set as environment variables in Render (STUDENT_NAME, STUDENT_ID)
STUDENT_NAME = os.environ.get("STUDENT_NAME", "Student Name")
STUDENT_ID = os.environ.get("STUDENT_ID", "Student ID")


class Book(db.Model):
    # Own table name, so it never clashes with other apps sharing the same database
    __tablename__ = "library_books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(60), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    added_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )


with app.app_context():
    db.create_all()


def student_context():
    return dict(student_name=STUDENT_NAME, student_id=STUDENT_ID)


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "all")

    query = Book.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Book.title.ilike(like), Book.author.ilike(like), Book.genre.ilike(like))
        )
    if status == "available":
        query = query.filter_by(available=True)
    elif status == "borrowed":
        query = query.filter_by(available=False)

    books = query.order_by(Book.title.asc()).all()
    total = Book.query.count()
    available_count = Book.query.filter_by(available=True).count()
    return render_template(
        "index.html",
        books=books,
        q=q,
        status=status,
        total=total,
        available_count=available_count,
        borrowed_count=total - available_count,
        **student_context(),
    )


@app.route("/add", methods=["POST"])
def add():
    book = Book(
        title=request.form["title"].strip(),
        author=request.form["author"].strip(),
        genre=request.form["genre"].strip(),
        year=int(request.form["year"]),
    )
    db.session.add(book)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    book = db.get_or_404(Book, id)
    if request.method == "POST":
        book.title = request.form["title"].strip()
        book.author = request.form["author"].strip()
        book.genre = request.form["genre"].strip()
        book.year = int(request.form["year"])
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", b=book, **student_context())


@app.route("/toggle/<int:id>", methods=["POST"])
def toggle(id):
    book = db.get_or_404(Book, id)
    book.available = not book.available
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    book = db.get_or_404(Book, id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
