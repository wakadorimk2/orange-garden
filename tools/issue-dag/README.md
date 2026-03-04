# Issue DAG

This directory contains a deterministic snapshot of issue dependencies for
`wakadorimk2/personal-mcp-core` issues `70` through `80`.

## Edge direction

`A -> B` means issue `A` blocks issue `B`.

## Refresh data

Run the generator from the repository root:

```bash
python3 tools/issue-dag/generate_issue_dag.py
```

The script uses `gh api graphql` to fetch issue metadata and writes:

- `issues.json`
- `issue_dag.dot`
- `issue_dag.svg` and `issue_dag.png` when Graphviz `dot` is installed

If the dependency graph contains a cycle, the script prints the cycle path and
stops before rendering images.

## Render locally

If `dot` is installed, the generator renders SVG and PNG automatically.

To render manually:

```bash
dot -Tsvg tools/issue-dag/issue_dag.dot -o tools/issue-dag/issue_dag.svg
dot -Tpng tools/issue-dag/issue_dag.dot -o tools/issue-dag/issue_dag.png
```

Ubuntu install:

```bash
sudo apt-get update && sudo apt-get install -y graphviz
```
