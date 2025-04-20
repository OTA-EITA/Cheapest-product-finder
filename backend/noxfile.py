import nox
import os

# Python 3.11を主に使用
PYTHON_VERSIONS = ["3.11"]

@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """
    全テストを実行
    """
    # PYTHONPATH設定
    session.env['PYTHONPATH'] = os.getcwd()

    session.install("-r", "requirements.txt")
    session.install("pytest", "pytest-cov", "pytest-mock", "httpx")
    session.run(
        "pytest", 
        "tests/", 
        "--cov=services", 
        "--cov=scraping", 
        "--cov-report=term", 
        "--cov-report=html"
    )

# 他のセッションは以前と同じ
@nox.session(python=PYTHON_VERSIONS)
def lint(session):
    """
    コードの静的解析
    """
    session.install("flake8", "black", "isort")
    session.run("black", "--check", ".")
    session.run("isort", "--check", ".")
    session.run("flake8", "services", "scraping", "tests")

# ... (他のセッションは省略)
