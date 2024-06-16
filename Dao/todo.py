from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from Dao.base import Base


class Todo(Base):
    __tablename__ = 'todo_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    completed: Mapped[int] = mapped_column(Integer, default=0)
    pub_date: Mapped[datetime] = mapped_column(DateTime, dafault= datetime.now)

    def __repr__(self):
        return ("Task: id: {/%r}  title:{%s}, content:{%s} publication_date:{%s}>" %
                (self.id, self.title, self.content, self.pub_date))

