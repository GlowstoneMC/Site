# coding=utf-8
import importlib
import inspect
import logging
import os

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ultros_site.config import Config
from ultros_site.database.common import DeclarativeBase

__author__ = "Gareth Coles"
CURRENT_DIR = os.path.dirname(__file__)
log = logging.getLogger("Database")

if CURRENT_DIR[-1] == "/":
    SCHEMA_DIR = CURRENT_DIR + "database/schema/"
else:
    SCHEMA_DIR = CURRENT_DIR + "/database/schema/"


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.make_session = None

        self.config = Config()

    def create_engine(self):
        log.info("Creating database engine...")
        url = self.config.database_url

        try:
            self.engine = create_engine(url, echo=self.config.debug)
            self.make_session = sessionmaker(self.engine)
        except Exception as e:
            log.critical("Unable to set up database")
            log.exception("")
            exit(1)

    def create_session(self) -> Session:
        return self.make_session()

    @contextmanager
    def session(self):
        """
        >>> with database_manager.session() as s:
        ...     user = User(...)
        ...     s.add(user)
        ...

        If there's an unhandled exception, the session will be rolled back for
        you.
        """

        session = self.create_session()

        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            log.warning("Error detected in session context manager: %s", e)
            raise
        finally:
            session.close()

    def load_schema(self):
        log.info("Loading schema...")
        log.info("")

        for filename in os.listdir(SCHEMA_DIR):
            path = SCHEMA_DIR + filename

            if not os.path.isfile(path):
                continue

            if not path.endswith(".py"):
                continue

            module_name = "ultros_site.database.schema.{}".format(
                os.path.basename(path).split(".py", 1)[0]
            )

            if module_name.endswith("__init__"):
                continue

            log.info("Loading module: %s", module_name)

            try:
                module_obj = importlib.import_module(module_name)

                for name, clazz in inspect.getmembers(module_obj):
                    try:
                        if inspect.isclass(clazz):
                            if clazz == DeclarativeBase:
                                continue

                            if name.startswith("__") and name.endswith("__"):
                                continue

                            if issubclass(clazz, DeclarativeBase):
                                log.info("-> Loaded schema class: %s", name)
                    except Exception as e:
                        log.info("   -> Failed to load: %s", e)
            except Exception as e:
                log.info("Failed to load schema: %s", e)
            log.info("")
