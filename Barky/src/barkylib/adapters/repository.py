import json
import traceback
from abc import ABC, abstractmethod
from datetime import datetime

# making use of type hints: https://docs.python.org/3/library/typing.html
from typing import List, Set

from barkylib.adapters.orm import mapper_registry
from barkylib.domain.models import Bookmark
from barkylib.domain import models
from collections import UserDict


class AbstractRepository(ABC):
    def __init__(self):
        self.seen = set()

    @abstractmethod
    def add_one(bookmark) -> None:
        raise NotImplementedError("Derived classes must implement add_one")

    @abstractmethod
    def add_many(bookmarks) -> None:
        raise NotImplementedError("Derived classes must implement add_many")

    @abstractmethod
    def delete_one(bookmark) -> None:
        raise NotImplementedError("Derived classes must implement delete_one")

    @abstractmethod
    def delete_many(bookmarks) -> None:
        raise NotImplementedError("Derived classes must implement delete_many")

    @abstractmethod
    def get(self, id: int) -> Bookmark:
        raise NotImplementedError("Derived classes must implement update")

    @abstractmethod
    def update(bookmark) -> int:
        raise NotImplementedError("Derived classes must implement update")

    @abstractmethod
    def update_many(bookmarks) -> int:
        raise NotImplementedError("Derived classes must implement update_many")

    @abstractmethod
    def find_first(query) -> Bookmark:
        raise NotImplementedError("Derived classes must implement find_first")

    @abstractmethod
    def find_all(query) -> list[Bookmark]:
        raise NotImplementedError("Derived classes must implement find_all")


# sqlalchemy stuff
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData


class SqlAlchemyRepository(AbstractRepository):
    """
    Uses guidance from the basic SQLAlchemy 2.0 tutorial:
    https://docs.sqlalchemy.org/en/20/tutorial/index.html
    """

    def __init__(self, session, connection_string=None) -> None:
        super().__init__()
        self.Session = session
        # self.engine = None
        # print('***********connection_string****************')
        # print(connection_string)
        # # create db connection
        # if connection_string is not None:
        #     self.engine = create_engine(connection_string)
        # else:
        #     # let's default to in-memory for now
        #     self.engine = create_engine(f"sqlite:///../bookmarks.db", echo=True)
        #
        # # ensure tables are there
        # mapper_registry.metadata.create_all(self.engine)
        #
        # # obtain session
        # # the session is used for all transactions
        # if session is not None:
        #     self.Session = session
        # else:
        #     self.Session = sessionmaker(bind=self.engine)

    def __del__(self):
        self.Session.commit()
        self.Session.close()

    def add_one(self, bookmark: Bookmark) -> None:
        bookmarks = list()
        if bookmark:
            bookmarks.append(bookmark)
            self.add_many(bookmarks)

    def add_many(self, bookmarks: list[Bookmark]) -> None:
        if bookmarks:
            self.Session.add_all(bookmarks)
            self.Session.commit()

    def delete_one(self, bookmark: Bookmark) -> None:
        bookmarks = list()
        if bookmark:
            bookmarks.append(bookmark)

        self.delete_many(bookmarks)

    def delete_many(self, bookmarks: list[Bookmark]) -> None:
        if bookmarks:

            ids = list()
            for bookmark in bookmarks:
                try:
                    ids.append(bookmark.id)
                except Exception as e:
                    ids.append(bookmark['id'])

            if ids:
                stmt = delete(Bookmark).where(Bookmark.id.in_(ids))
                self.Session.execute(stmt)
                self.Session.commit()

    def get(self, id: int) -> Bookmark:
        bookmark = self.find_first(select(Bookmark).where(Bookmark.id == id))
        if bookmark:
            self.seen.add(bookmark)

        return bookmark

    def update(self, bookmark) -> int:
        if bookmark is None:
            return 400
        else:
            bookmarks = list()
            bookmarks.append(bookmark)
            return self.update_many(bookmarks)

    def update_many(self,  bookmarks: list[models.Bookmark]) -> int:
        if bookmarks is None or not bookmarks:
            return 400
        else:
            try:
                for bookmark in bookmarks:
                    bId = None

                    try:
                        bId = bookmark['id']
                    except Exception as e:
                        bId = bookmark.id

                    if bId is not None:
                        bmark = bookmark._asdict() if type(bookmark) is Bookmark else bookmark
                        stmt = update(models.Bookmark).where(models.Bookmark.id == bId).values(bmark)
                        self.Session.execute(stmt)
                        self.Session.commit()
                    if bId is None:
                        raise Exception(f'No bookmark Id was found!')

                return 200
            except Exception as e:
                print(e)
                return 400

    def find_first(self, query) -> Bookmark:
        if query is None:
            bookmarks = None
        else:
            bookmarks = self.find_all(query)

        if bookmarks:
            return bookmarks[0]
        else:
            return None

    def find_all(self, query) -> list[Bookmark]:

        query = select(Bookmark) if query is None else query
        bookmarks = self.Session.scalars(query).all()

        if bookmarks:
            for bookmark in bookmarks:
                self.seen.add(bookmark)

        return bookmarks
