import requests
import pymysql
from config import GITHUB_TOKEN, MYSQL_CONFIG

def connect_db():
    return pymysql.connect(**MYSQL_CONFIG)

def search_github_projects():
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    query = 'comfyui in:name,description,readme'
    per_page = 100
    page = 1
    all_repos = []

    while True:
        url = f"https://api.github.com/search/repositories?q={query}&per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("GitHub API Error:", response.status_code, response.json())
            break

        data = response.json()
        repos = data.get('items', [])
        if not repos:
            break

        all_repos.extend(repos)
        page += 1

    return all_repos

def upsert_repo(repo):
    conn = connect_db()
    cursor = conn.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS github_repos (
        id INT PRIMARY KEY AUTO_INCREMENT,
        repo_name VARCHAR(255),
        html_url VARCHAR(512) UNIQUE,
        description TEXT,
        created_at DATETIME,
        updated_at DATETIME,
        pushed_at DATETIME,
        language VARCHAR(50),
        stargazers_count INT,
        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """
    cursor.execute(sql)

    sql_insert = """
    INSERT INTO github_repos (repo_name, html_url, description, created_at, updated_at, pushed_at, language, stargazers_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        description = VALUES(description),
        updated_at = VALUES(updated_at),
        pushed_at = VALUES(pushed_at),
        language = VALUES(language),
        stargazers_count = VALUES(stargazers_count)
    """

    values = (
        repo['full_name'],
        repo['html_url'],
        repo['description'],
        repo['created_at'],
        repo['updated_at'],
        repo['pushed_at'],
        repo['language'],
        repo['stargazers_count']
    )

    cursor.execute(sql_insert, values)
    conn.commit()
    cursor.close()
    conn.close()

def run():
    repos = search_github_projects()
    print(f"发现 {len(repos)} 个仓库")
    for repo in repos:
        upsert_repo(repo)
    print("同步完成")

if __name__ == "__main__":
    run()
