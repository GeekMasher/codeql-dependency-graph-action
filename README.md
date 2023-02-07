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
