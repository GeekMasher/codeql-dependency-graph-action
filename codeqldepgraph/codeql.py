import os
import glob
import json
import logging
import subprocess

__HERE__ = os.path.dirname(os.path.abspath(__file__))
__ROOT__ = os.path.abspath(os.path.join(__HERE__, ".."))

CODEQL_LOCATIONS = [
    "codeql",
    # gh cli
    "gh codeql",
]
# Actions
CODEQL_LOCATIONS.extend(glob.glob("/opt/hostedtoolcache/CodeQL/*/x64/codeql/codeql"))
# VSCode install
CODEQL_LOCATIONS.extend(
    glob.glob(
        "/home/codespace/.vscode-remote/data/User/globalStorage/github.vscode-codeql/*/codeql/codeql"
    )
)

CODEQL_DATABASE_LOCATIONS = [
    # local db
    ".codeql/db",
    # Actions
    "/home/runner/work/_temp/codeql_databases/",
]

CODEQL_TEMP = os.path.join("/tmp", "codeqldepgraph")

logger = logging.getLogger("codeql")


def find_codeql() -> str:
    """Find the CodeQL executable"""
    for codeql in CODEQL_LOCATIONS:
        try:
            with open(os.devnull) as null:
                subprocess.run([codeql, "--version"], stdout=null, stderr=null)
            return codeql
        except Exception as err:
            pass
        print(f" >> {codeql}")

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
    def __init__(self, database: str, codeql_path: str = None):
        self.database = database
        self.name = os.path.basename(database)

        self.codeql_path = codeql_path or find_codeql()
        self.language = self.find_language()

        self.pack_name = f"codeql-depgraph-{self.language}"

        if not os.path.exists(CODEQL_TEMP):
            os.makedirs(CODEQL_TEMP)

    def find_language(self) -> str:
        """Find the language of the CodeQL database"""
        db = glob.glob(os.path.join(self.database, "db-*"))

        if db:
            return db[0].split("-")[-1]

        raise Exception("Could not find CodeQL database language")

    def run(self, query):
        """Run a CodeQL query"""
        local_query = os.path.join(__ROOT__, "ql", self.language, query)
        if os.path.exists(local_query):
            full_query = local_query
        elif os.path.exists(query):
            full_query = query
        else:
            full_query = f"{self.pack_name}:{query}"

        logger.debug(f"Running query: {full_query}")

        resultBqrs = os.path.join(
            self.database,
            "results",
            self.pack_name,
            query.replace(":", "/").replace(".ql", ".bqrs"),
        )

        cmd = [
            self.codeql_path,
            "database",
            "run-queries",
            # use all the threads on system
            "--threads",
            "0",
            self.database,
            full_query,
        ]
        logger.debug(f"Running: {' '.join(cmd)}")

        output_std = os.path.join(CODEQL_TEMP, "runquery.txt")
        with open(output_std, "wb") as std:
            subprocess.run(cmd, stdout=std, stderr=std)

        return self.readRows(resultBqrs)

    def readRows(self, bqrsFile: str) -> list:
        generatedJson = os.path.join(CODEQL_TEMP, "out.json")
        output_std = os.path.join(CODEQL_TEMP, "rows.txt")

        logger.debug(f"Reading rows from: {bqrsFile}")

        if not os.path.exists(bqrsFile):
            logger.error(f"Could not find bqrs file: {bqrsFile}")
            logger.error(f"Make sure the query was ran successfully")
            return []

        cmd = [
            self.codeql_path,
            "bqrs",
            "decode",
            "--format",
            "json",
            "--output",
            generatedJson,
            bqrsFile,
        ]

        with open(output_std, "wb") as std:
            subprocess.run(
                cmd,
                stdout=std,
                stderr=std,
            )

        if not os.path.exists(generatedJson):
            logger.error(f"Could not find generated JSON file: {generatedJson}")
            logger.error(f"Make sure the query was ran successfully")
            with open(output_std, "r") as std:
                logger.error(std.read())
            return []

        with open(generatedJson) as f:
            results = json.load(f)

        try:
            results["#select"]["tuples"]
        except KeyError:
            raise Exception("Unexpected JSON output - no tuples found")

        rows = []
        for tup in results["#select"]["tuples"]:
            rows.extend(tup)

        return rows

    def __str__(self) -> str:
        return f"CodeQL(language='{self.language}', path='{self.database}')"
