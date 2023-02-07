import os
import json
import argparse

from codeqldepgraph.codeql import CodeQL, find_codeql, find_codeql_databases
from codeqldepgraph.dependencies import parseDependencies, exportDependencies
from codeqldepgraph.octokit import Octokit

parser = argparse.ArgumentParser(
    description="Generate a dependency graph for a CodeQL database."
)

parser.add_argument("-sha", default=os.environ.get("GITHUB_SHA"), help="Commit SHA")
parser.add_argument("-ref", default=os.environ.get("GITHUB_REF"), help="Commit ref")

parser_github = parser.add_argument_group("GitHub")
parser_github.add_argument(
    "-r",
    "--github-repo",
    default=os.environ.get("GITHUB_REPOSITORY"),
    help="GitHub repository",
)
parser_github.add_argument(
    "--github-instance",
    default=os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
    help="GitHub instance",
)
parser_github.add_argument(
    "--github-token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub API token"
)

parser_codeql = parser.add_argument_group("CodeQL")
parser_codeql.add_argument("--codeql-path", help="CodeQL executable")
parser_codeql.add_argument("--codeql-pack", help="CodeQL pack")
parser_codeql.add_argument(
    "--codeql-database",
    help="CodeQL database",
)
parser_codeql.add_argument("--codeql-language", help="CodeQL language")


if __name__ == "__main__":
    args = parser.parse_args()
    owner, repo = args.github_repo.split("/", 1)
    # TODO: support GitHub Enterprise
    github = Octokit(owner=owner, repo=repo, token=args.github_token)

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
            database,
            codeql_path,
        )
        print(codeql)

        codeql_results = codeql.run("Dependencies.ql")
        results = parseDependencies(codeql_results)

        print(f"Found {len(results)} dependencies.")

        depgraph = exportDependencies(
            results,
            # git sha and ref
            sha=args.sha,
            ref=args.ref,
            # source is the codeql database
            source=database,
        )

        github.submitDependencies(depgraph)

    print("Done!")
