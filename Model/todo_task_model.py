
from Dao.todo import Todo


class TodoTaskModel:
    """
       View wrapper for passing `todo` task data back to the front end html template
       """
    def __init__(self, todo:Todo):
        datetime_format = '%Y-%m-%d %H:%M:%S(UTC)'
        self.id = todo.id
        self.title = todo.title
        self.content = todo.content
        self.completed = todo.completed
        self.pub_date = todo.pub_date.strftime(datetime_format)

