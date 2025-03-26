import os
import sys

import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect, insert
from flask_sqlalchemy import SQLAlchemy

# Global Variables
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from ontologysim.ProductionSimulation.database.models.Base import Base
from ontologysim.ProductionSimulation.utilities.path_utilities import sanitize_path

SQLITE = "sqlite"

# Table Names
USERS = "users"
ADDRESSES = "addresses"


class DataBase:
    """
    database object for creating methadata and session
    """

    def __init__(
        self, dataBaseURL, username="", password="", dbname="", createDB=False
    ):
        """
        create session and metadata
        :param dataBaseURL:
        :param username:
        :param password:
        :param dbname:
        """

        self.db_engine = None
        self.metadata = None
        self.session = None

        dataBaseURL = dataBaseURL.strip()

        # Check if the database file is within the current working directory.
        # The other URI type will be allowed.
        # NOTE(KC): Adding engine+sqlite will by-pass this.
        if dataBaseURL.startswith("sqlite:///"):
            database_filepath = dataBaseURL.replace("sqlite:///", "")

            try:
                database_filepath = sanitize_path(os.getcwd(), database_filepath)
            except ValueError as e:
                raise ValueError("The database file is not within the current working directory.") from e

            dataBaseURL = "sqlite:///" + str(database_filepath)

        if createDB:
            engine = db.create_engine(dataBaseURL)
            if not database_exists(engine.url):
                create_database(engine.url)

        if dataBaseURL != "":
            self.db_engine = db.create_engine(dataBaseURL)
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.db_engine)
            self.session = self.createSession(self.db_engine)
        else:
            print("DBType is not found in DB_ENGINE")
            self.db_engine = None
            self.metadata = None
            self.session = None

    def createSession(self, db_engine):
        """
        create session
        :param db_engine:
        :return:
        """
        Session = sessionmaker(bind=db_engine)
        session = Session()
        return session

    def create_db_tables(self):
        """
        create all db tables
        :return:
        """
        try:
            Base.metadata.create_all(self.db_engine)
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def execute_query(self, query=""):
        """
        possible to execute query
        :param query:
        :return:
        """
        if query == "":
            return
        print(query)
        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
            except Exception as e:
                print(e)

    def getTables(self):
        """
        print all tables
        :return:
        """
        metadata = MetaData(bind=self.db_engine)
        print(metadata.tables.keys())

    def getTables2(self):
        """
        print schema and columns
        :return:
        """

        inspector = inspect(self.db_engine)
        schemas = inspector.get_schema_names()

        for schema in schemas:
            print("schema: %s" % schema)
            for table_name in inspector.get_table_names(schema=schema):
                print(table_name)
                for column in inspector.get_columns(table_name, schema=schema):
                    print("Column: %s" % column)

    def selectAll(self):
        """
        print all user data
        :return:
        """
        result = self.db_engine.execute("SELECT * FROM user")

        for row in result:
            print(row)

        result.close()

    def selectModelUser(self):
        """
        print all user
        :return:
        """
        print("user")
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute("SELECT * FROM user")
                print(result)
                for row in result:
                    print(row)
            except Exception as e:
                print(e)

    def dropAll(self):
        """
        drop all data and tables
        :return:
        """
        Base.metadata.drop_all(bind=self.db_engine)


"""

db=MyDatabase(SQLITE)
db.create_db_tables()
"""
"""

db.getTables()
db.getTables2()
"""

# db.insert_data()
"""
Base.metadata.create_all(db.db_engine)

#db.getTables()
db.getTables2()
db.selectAll()
#admin = User(username='admin', email='admin@example.com', password="t")
#session.add(admin)
session.commit()

db.selectModelUser()
print(session.query(User).all())
"""
