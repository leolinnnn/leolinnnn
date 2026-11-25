# Adding research projects

[← Profile](../README.md) · [Research overview](RESEARCH_OVERVIEW.md) · [README template](../templates/project/README.md)

## Profile and CV

Keep the profile README to three plain paragraphs: affiliation; research and
computation with project links; CV, contact and language switch. Update English
and Chinese together when project descriptions change. Detailed methods and
results belong in the independent research repositories.

The [CV repository](https://github.com/leolinnnn/CV) contains its README and the
stable `Zihao_Lin_CV.pdf` filename. Replace the PDF and update its version date
when publishing a revised CV. It does not need the research-code directory layout.

GitHub pins are account settings, separate from README text. Choose repositories
that show distinct computational strengths; new projects do not require new
decorative cards or a longer profile introduction.

## README reading order

Adapt the [template](../templates/project/README.md) in this order:

1. Research question and verified result or system, with a representative figure.
2. Computational workflow, linking inputs to code/assets and verification.
3. Quick start, with an actual entry point and expected output.
4. Repository guide.
5. Validation and scope.
6. Research record and citation.

Keep English as the primary language. Name the research topic or method before
the case-study location. Do not add empty sections or claim capabilities without
available code, native assets or clearly identified documentary evidence.

## File responsibilities

| Location | Use |
| --- | --- |
| Root | README, executable entry points, dependencies, source record, citation and reuse terms |
| `src/` | Reusable research computations |
| `data/` | Input tables and geometries; `README.md` defines observations, units, IDs, producers/consumers and availability |
| `reference/` | Archived expected results, geometry QA, verification records and retained solver logs |
| `assets/` | Documentation figures and screenshots |
| `docs/` | Methods, reproduction and validation; split only when it improves navigation |
| `tests/` | Analytical cases, invariants and meaningful regression checks |
| `outputs/` | Generated artifacts, ignored by Git |

Add project-specific folders when needed: `configs/` for parameters, `models/`
for executed simulation inputs, `unreal/` for native UE assets, `legacy/` for
original historical scripts, and `examples/` for a compact independent example.
Preserve Unreal internal paths. A Blueprint archive does not need empty `src/`,
`data/` or Python dependency files.

Each research repository uses `PROVENANCE.md` and `source_manifest.json`. Manifest
schemas follow the evidence available: source-function identities, file hashes,
or native-asset sizes and paths. A common filename does not imply one schema.

## Research overview and existing links

Add a concise entry between the `selected-research` markers in
[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) and
[RESEARCH_OVERVIEW.zh-CN.md](RESEARCH_OVERVIEW.zh-CN.md): question, scope,
computation, verified result, and repository/run links. Update the methods table
only when the new implementation supports it.

Maintain detailed project documentation in its independent repository. Keep old
profile project pages as forwarding links. Existing profile image copies may
remain as immutable compatibility files for previously shared image URLs.
Preserve manuscript authorship, figure provenance and third-party attribution.

## Before publishing

1. Check local and cross-repository links, figure captions and data definitions.
2. Run the documented commands and existing relevant checks after path changes.
3. Compare moved data and native assets with the previous version's hashes.
4. Review the exact file diff and local README preview before uploading.
5. Record the published commit and verification results after upload.

Keep the separate Research Portfolio GitHub Project private unless its owner
explicitly requests a visibility change.
