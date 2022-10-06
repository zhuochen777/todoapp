import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://zhuochen@localhost:5432/todoapp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
# link SQLAlchemy to flask app
migrate = Migrate(app, db)

# create Todo table model
# child model
class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    list_id = db.Column(db.Integer, db.ForeignKey("todolists.id"), nullable = False)
    # set up foreign key constraint on child model, list_id - some parent id, "todolists.id" - "parentTableName.primaryKey"


    def __repr__(self):
        return f"<Todo {self.id} is {self.description}>"

# parent model
class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), nullable = False)
    todos = db.relationship("Todo", backref = "list", lazy = True)
    # todos - name of the children (plural), "Todo" - name of child class, name of the backref returns the parent object that child object belongs to

#db.create_all()

# create a route that listens request to todos/create with post method
@app.route("/todos/create", methods=["POST"])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()["description"]
        todo = Todo(description = description)
        db.session.add(todo)
        db.session.commit()
        body["description"] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        abort(500)
        # rise an HTTPException for an Internal Server Error
        # route handler should always return something or raise an intentional exception


@app.route("/todos/<todoId>/set-completed", methods=["POST"])
def set_completed_todo(todoId):
    try:
        completed = request.get_json()["completed"]
        todo = Todo.query.get(todoId)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))

@app.route("/todos/<todoId>/delete", methods=["DELETE"])
def delete_todo(todoId):
    try:
        todo = Todo.query.get(todoId)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({"success": True})

@app.route("/lists/<list_id>")
def get_list_todo(list_id):
    return render_template("index.html",
    lists = TodoList.query.all(),
    active_list = TodoList.query.get(list_id),
    todos = Todo.query.filter_by(list_id = list_id).order_by("id").all())
    # order_by("id") so that records are listed by id even after webpage refreshes


@app.route("/")
def index():
    return redirect(url_for("get_list_todo", list_id = 1))

if __name__=="__main__":
    app.run(debug=True)
