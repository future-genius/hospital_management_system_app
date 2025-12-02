import os

# Find the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """
    Basic configuration settings for the Hospital Management System.
    All values can be overridden by environment variables when needed.
    """

    SECRET_KEY = os.environ.get("HMS_SECRET") or "change-this-secret-key"

    # Create database path if not provided externally
    db_path = os.environ.get("HMS_DATABASE")
    if not db_path:
        db_file = os.path.join(BASE_DIR, "instance", "hospital.db")
        db_path = f"sqlite:///{db_file}"

    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pagination fallback value
    ITEMS_PER_PAGE = 20
