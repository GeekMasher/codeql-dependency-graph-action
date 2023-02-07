import argparse

import os
from codeqldepgraph.codeql import CodeQL, find_codeql, find_codeql_databases

parser = argparse.ArgumentParser(
    description="Generate a dependency graph for a CodeQL database."
)

parser_github = parser.add_argument_group("GitHub")
parser_github.add_argument("--github-token", help="GitHub API token")
parser_github.add_argument("--github-repo", help="GitHub repository")
parser_github.add_argument("--github-instance", help="GitHub instance")

parser_codeql = parser.add_argument_group("CodeQL")
parser_codeql.add_argument("--codeql-path", help="CodeQL executable")
parser_codeql.add_argument(
    "--codeql-database",
    help="CodeQL database",
)
parser_codeql.add_argument("--codeql-language", help="CodeQL language")


if __name__ == "__main__":
    args = parser.parse_args()

    codeql_path = args.codeql_path or find_codeql()

    # Find all CodeQL databases
    databases = []
    if args.codeql_database:
        databases.append(args.codeql_database)
    else:
        databases = find_codeql_databases()

    if not databases:
        print("No CodeQL databases found.")
        exit(1)

    for database in databases:
        codeql = CodeQL(
            args.codeql_database,
            codeql_path,
        )
