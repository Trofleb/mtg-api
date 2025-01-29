import os

SUL_HOST = os.getenv("", "https://playground.unityleague.ch")
DATABASE = os.getenv("DATABASE", "mtg")
DATABASE_HOST = os.getenv("DATABASE_HOSTNAME", "localhost")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "root")
DATABASE_PORT = os.getenv("DATABASE_PORT", "27017")
