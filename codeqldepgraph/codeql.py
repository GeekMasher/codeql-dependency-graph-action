import os
import glob
import shutil
import subprocess

CODEQL_LOCATIONS = [
    "codeql",
    # gh cli
    "gh codeql",
    # Actions
    "/opt/hostedtoolcache/CodeQL/*/x64/codeql/codeql",
    # VSCode install
    "/home/codespace/.vscode-remote/data/User/globalStorage/github.vscode-codeql/*/codeql/codeql",
]

CODEQL_DATABASE_LOCATIONS = [".codeql/db", "/home/runner/work/_temp/codeql_databases/"]


def find_codeql() -> str:
    """Find the CodeQL executable"""
    for codeql in CODEQL_LOCATIONS:
        codeql = glob.glob(codeql)
        # test if the glob found anything
        if codeql:
            # test command works
            try:
                subprocess.run([codeql[0], "--version"], stdout=subprocess.PIPE)
                return codeql[0]
            except Exception as err:
                pass

    raise Exception("Could not find CodeQL executable")


def find_codeql_databases() -> list:
    """Find CodeQL databases"""
    results = []
    for codeql_database in CODEQL_DATABASE_LOCATIONS:
        path = glob.glob(codeql_database)
        if path:
            results.append(path[0])
    return results


class CodeQL:
    def __init__(self, database: str, language: str, codeql_path: str = None):
        self.database = database
        self.language = language

        self.codeql_path = codeql_path or find_codeql()
        self.databases = []

    def find_language(self) -> str:
        """Find the language of the CodeQL database"""
        # find db folder
        db = glob.glob(os.path.join(self.database), "db-*")
        if db:
            return db[0].split("-")[1]

        raise Exception("Could not find CodeQL database language")

    def run_query(self, query):
        """Run a CodeQL query"""
        return subprocess.run(
            [
                self.codeql_path,
                "query",
                "run",
                query,
                "--database",
                self.database,
                "--language",
                self.language,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
