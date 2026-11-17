# Adding research projects

[← Research overview](../README.md)

The profile is a concise research index. Each computational project has one
maintained repository containing its research context, code, inputs and outputs.
Documentation-led experiments may remain under `projects/` until runnable assets
are ready to share.

## Homepage block

Use the same order for every project: **title → research question → computation →
result or system output → methods → links**. Aim for 70–100 English words and
update the Chinese profile at the same time. Describe what the system or analysis
does; a separate personal-contribution section is unnecessary.

```markdown
### Place or system — Research topic

One sentence stating the research question.

- Describe the data or experimental scope.
- Explain the implemented computation or system.
- Give a verified result or concrete output.

**Method · Method · Method**

Research & repository · Run the analysis
```

Replace the final line with links to existing resources. Put the block between
the `selected-research` comment markers in both profile READMEs.

## Project repository

Adapt the [project README template](../templates/project/README.md). Keep runnable
entry points and environment files at the root, computation in `src/`, numerical
inputs with a field dictionary in `data/`, and results used for verification in
`reference/`. Add `tests/`, `examples/`, `assets/` and `docs/` when they serve the work.

Keep code in one maintained location. When relocating a project, preserve its old
README page with links to the new repository and update incoming profile links.
Original authorship, data definitions and reuse terms remain with each project.

## Before listing a project

1. Check the Markdown, figures, links and numerical claims.
2. Run the documented commands in the stated environment and inspect their outputs.
3. Record the tested scope; distinguish raw-data workflows from table-based reproduction.
4. Add a methods-table entry only when it links to an actual implementation.

Keep approximately four to six selected projects on the homepage as the portfolio
grows. A separate project index can hold the full list. Add projects when ready;
the layout has no fixed project count or empty placeholder blocks.
