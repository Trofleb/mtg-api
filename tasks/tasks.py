# demo.py
from huey import SqliteHuey, crontab

from tasks.ifetch_dataset import i_fetch_dataset

huey = SqliteHuey(filename="./db/huey.db")


@huey.periodic_task(crontab(minute="0", hour="12"))
def update_db():
    i_fetch_dataset()
