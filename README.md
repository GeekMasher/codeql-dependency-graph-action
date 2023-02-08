# codeql-dependency-graph-action

CodeQL Dependency Graph Action

## Usage

```yaml
- name: CodeQL Dependency Graph
  uses: geekmasher/codeql-dependency-graph-action@v0.1
```

**Sample Action Workflow**

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v2
  with:
    languages: ${{ matrix.language }}

  # autobuild or manual build

- name: CodeQL Dependency Graph
  uses: geekmasher/codeql-dependency-graph-action@v0.1

- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v2
```

## Features

| Language   | Query                                   | Completeness               |
| ---------- | --------------------------------------- | -------------------------- |
| C/C++      | :white_check_mark: [query](./ql/cpp)    | :large_orange_diamond: [1] |
| C#         | :red_circle:                            |                            |
| Go         | :red_circle:                            |                            |
| Java       | :white_check_mark: [query](./ql/java)   | :white_check_mark: [2]     |
| JavaScript | :red_circle:                            |                            |
| Python     | :white_check_mark: [query](./ql/python) | :large_orange_diamond: [3] |
| Ruby       | :red_circle:                            |                            |

*Notes:*

1. C/C++ information is incomplete. The query is able to some data on dependencies, but the information is not complete. This is due to the fact that the CodeQL C/C++ extractor does not extract all the information needed to build a complete the dependency information.
2. Java information is pretty complete. Both Gradle and Maven are supported well.
3. Python's data is incomplete. Not all the information is available to build a complete dependency graph.
