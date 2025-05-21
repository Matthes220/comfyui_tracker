import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

MYSQL_CONFIG = {
    'host': os.environ.get("MYSQL_HOST"),
    'user': os.environ.get("MYSQL_USER"),
    'password': os.environ.get("MYSQL_PASSWORD"),
    'database': os.environ.get("MYSQL_DATABASE"),
    'charset': 'utf8mb4'
}
