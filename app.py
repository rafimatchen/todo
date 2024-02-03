from datetime import datetime

from flask import Blueprint, Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, default=datetime.now)


main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/todos", methods=["GET", "POST"])
def todos():
    if request.method == "POST":
        todo = Task(name=request.form.get("task"))
        db.session.add(todo)
        db.session.commit()
        todos = [todo]
    elif request.method == "GET":
        todos = db.session.execute(db.select(Task).order_by(Task.created)).scalars()

    return render_template("todos.html", todos=todos)


@main.put("/<id>/<status>")
@main.delete("/<id>")
def id(id, status=None):
    if request.method == "PUT":
        status = status != "True"
        db.session.execute(db.update(Task).where(Task.id == id).values(done=status))
    else:
        db.session.execute(db.delete(Task).where(Task.id == id))
    db.session.commit()
    return redirect(url_for("main.todos"), code=303)


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    db.init_app(app)
    app.register_blueprint(main)
    return app
