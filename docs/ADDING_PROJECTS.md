# Adding research projects

[← Profile](../README.md) · [Research portfolio](RESEARCH_OVERVIEW.md)

## Profile layout

Keep the profile README to three plain paragraphs: academic affiliation; research
and computation with a few project links; CV, contact and language switch. Detailed
methods, results and education belong in the research overview or project pages.
Update the English and Chinese profiles together.

Keep the CV PDF in the [CV repository](https://github.com/leolinnnn/CV), using
`Zihao_Lin_CV.pdf` as its stable filename. Replace that file and update the version
date in its README when publishing a revised CV.

Projects are displayed through GitHub's native pinned repositories below the
README. Pins are account settings, not Markdown cards. Keep the profile concise
as the portfolio grows; add a short inline link only when it helps describe the work.

## Detailed research overview

Add the project between the `selected-research` comment markers in
[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) and
[RESEARCH_OVERVIEW.zh-CN.md](RESEARCH_OVERVIEW.zh-CN.md). Use this order:
title → research question → three concise statements about scope, computation
and results → methods → repository and run links. Update the methods table there
only when a new implementation supports the entry.

## Project repository

Adapt the [project README template](../templates/project/README.md). Keep runnable
entry points and environment files at the root, computation in `src/`, numerical
inputs with field definitions in `data/`, and archived verification targets in
`reference/`. Add `tests/`, `examples/`, `assets/` and `docs/` when useful.

Keep one maintained copy of the code. Preserve old README paths as forwarding
pages when moving a project. Manuscript authorship, data definitions, figure
provenance and reuse terms remain with the project.

Documentation-led experiments can remain under `projects/`; link the relevant
page from the profile or research overview until runnable assets are available.

## Before listing a project

1. Check the Markdown, figures, links and numerical claims.
2. Run the documented commands when executable code changes.
3. Describe the verified scope and any required external inputs.
4. Choose the most useful public repositories to pin. GitHub supports up to six
   repositories and gists; no empty cards or fixed number of projects is required.

[GitHub instructions for pinning](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile)
