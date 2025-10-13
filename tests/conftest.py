# GD ADDED just to temporarily run the test without modifying the database
import os
import pytest
import database
from app import create_app

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path):
    """Create a new DB for each test"""

    test_db = tmp_path / "test.db"
    database.DATABASE = str(test_db) 

    database.init_database()

    yield

# from flask website
@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
