import logging

from loguru import logger
from flask import Flask, render_template, url_for, request, redirect, abort, make_response
from sqlalchemy.orm import sessionmaker

from Dao.todo import Todo
from Dao.base import Base
from Dao.db_secrets import get_secret
from Model.todo_task_model import TodoTaskModel
from config import *
from sqlalchemy import create_engine, select

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(exception=record.exc_info)
        # collect all logs from everywhere
        logger_opt.log(record.levelno, record.getMessage())
        # setting up

app = Flask(__name__)

# configure loguru integration with flask and SQLAlchemy
# create a loguru logger
logger.start("./logs/application.log", level="INFO", format="{time} {level} {message}",
             backtrace=True, rotation="25MB", enqueue=True)

# set SQLAlchemy library to log into the loguru logger
logging.getLogger('sqlalchemy').addHandler(InterceptHandler())

# set flask library to log into loguru logger
app.logger.addHandler(logging.StreamHandler())

# To run locally, comment the below line
db_username, dp_password = get_secret()


"""
Setup database connection and create table todo_items if not already exists
"""
db_conf = {
    "host": DATABASE_URI,
    "port": DATABASE_PORT,
    "database": DATABASE_NAME,
    "user": db_username,
    "password": dp_password,
    # to run the app locally, get the user and password value from AWS SecretsManager by
    # clicking on `Retrieve secret value`
    # and replace the "user" and "password" values below
    # uncomment the below 2 lines
    # "user": "TO BE CHANGED",
    # "password": "TO BE CHANGED",
    # then comment the below lines

}
engine_string = "postgresql://{user}:{password}@{host}:{port}/{database}".format(**db_conf)
# **db_conf : have key, * : no key
# set echo=True so the DAO layer will print the SQL commands executed

engine = create_engine(engine_string, echo=True)
Session = sessionmaker(bind=engine)
logger.info("Creating database tables")
Base.metadata.create_all(bind=engine)

@logger.catch
@app.route("/ping")
def ping():
    """
    Health check method for load balancing health check
    Simply return 200 successful response code since this function would work when the server is up and healthy
    :return:
    """
    return make_response("Success", 200)

@logger.catch
@app.route("/tasks", methods=["GET"])
def get_tasks():
# the bridge between us and database, only for relational database, tcp, it maintains consistently
# non-relational, http, tcp will be broken after the http communication ends
    logger.info("Received GET request to /tasks")
    with Session() as session:
        statement = select(Todo).order_by(Todo.pub_date)
        tasks = session.execute(statement).all()
        task_models = __transfer_models(tasks)
        return render_template("index.html", tasks=task_models)

@logger.catch
@app.route("/tasks", methods=["POST"])
def create_task():
    logger.info("Received POST request to /tasks")
    if request.method == "POST":
        task_title = request.form["title"]
        task_content = request.form["content"]
        logger.info("Received POST request with task title {} and task content: {}", task_title,task_content)

        new_task = Todo(title=task_title, content=task_content)
        with Session() as sql_session:
            try:
                sql_session.add(new_task)
                sql_session.commit()
                logger.info("Successfully created task {}", new_task)
                return redirect("/tasks")
            except Exception as e:
                logger.exception("Error when creating task {}", request.form)
                return "There is an issue"


@logger.catch
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    logger.info("Received DELETE request to /tasks", task_id)
    with Session() as sql_session:
        try:
            statement = select(Todo).where(Todo.id == task_id)
            task = sql_session.execute(statement).first()
        except Exception as e:
            logger.exception("Error when trying to get task with id {} from database", task_id)
            abort(404)

        try:
            sql_session.delete(task[0])
            sql_session.commit()
            logger.info("Successfully deleted task {}", task[0])
            return redirect("/tasks", code=303)
        except Exception as e:
            logger.exception("Error when trying to delete task {}", task[0])
            return "There is a problem while deleting"
@logger.catch
@app.route("/tasks/<int:task_id>", methods=["POST"])

def update_task(task_id):
    logger.info("Received POST request to /tasks", task_id)
    with Session() as sql_session:
        try:
            statement = select(Todo).where(Todo.id == task_id)
            task = sql_session.execute(statement).first()
            task[0].title = request.form["title"]
            task[0].content = request.form["content"]
            sql_session.commit()
            logger.info("Successfully updated task {}", task[0])
            return redirect ("/tasks", code=303)
        except Exception as e:
            logger.exception("Error when trying to update task {}", task[0])
            abort(404)

@logger.catch
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_update_task(task_id):
    logger.info("Received GET request to /tasks", task_id)
    with Session() as session:
        statement = select(Todo).where(Todo.id == task_id)
        task = session.execute(statement).first()
        task_model = TodoTaskModel(task[0])
        statement = select(Todo).order_by(Todo.pub_date)
        tasks = session.execute(statement).all()
        task_models = __transfer_models(tasks)

    return render_template("index.html", updates=task_models, tasks=task_model)

def __transfer_models(tasks: [Todo]) -> [TodoTaskModel]:
    task_models = []
    for task in tasks:
        # the ORM object is contained in the index 0 of the result returned by SQLAlchemy
        task_models.append(TodoTaskModel(task[0]))
    return task_models

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
    # change the port to avoid the clash sometimes


