Site: https://jinhuaqing.github.io/

## Local setup and preview

**Requirements**

- **Ruby** and **Bundler** (the [`Gemfile`](Gemfile) uses the `github-pages` gem so your local Jekyll version matches GitHub Pages).
- **Python 3** is only needed if you regenerate publications from BibTeX (see [Publications (BibTeX)](#publications-bibtex) below).

**Install Ruby dependencies**

```bash
bundle install
```

**Run a local site with live reload**

```bash
make serve
```

This sets `LANG` and `LC_ALL` to UTF-8 and runs `bundle exec jekyll serve --livereload`. Open **http://127.0.0.1:4000/** (or the URL printed in the terminal).

**Alternative (without Make)**

```bash
export LANG=C.UTF-8 LC_ALL=C.UTF-8
bundle exec jekyll serve --livereload
```

If you change [`_config.yml`](_config.yml), stop the server (Ctrl+C) and start it again so Jekyll reloads configuration.

**What the site uses**

Page content lives under [`_pages/`](_pages/) (home, publications, teaching, talks, etc.), data under [`_data/`](_data/), and static files under [`files/`](files/) and [`images/`](images/). The Jekyll build does **not** read anything under `others/`; that directory is listed in `exclude` in [`_config.yml`](_config.yml) so it is not copied into `_site` if it exists in your clone.

## GitHub Pages deployment

This repository follows the usual **user site** pattern: **`username.github.io`** is built from the **default branch** (often `main`) with the site at the **repository root** (no `docs/` folder).

1. Push your commits to GitHub on the branch that Pages uses (check **Settings → Pages → Build and deployment → Branch**).
2. GitHub Pages runs Jekyll with the same stack as the `github-pages` gem. The live URL is **https://jinhuaqing.github.io/** when the build finishes (refresh after a minute if you do not see updates).

**Continuous integration**

The workflow [`.github/workflows/jekyll.yml`](.github/workflows/jekyll.yml) runs on pushes and pull requests: it installs Ruby and Python, runs `python scripts/bib_to_jekyll.py` after `pip install`, checks that [`_data/publications_generated.yml`](_data/publications_generated.yml) matches the committed file (`git diff --exit-code`), then runs `bundle exec jekyll build`. A failing workflow means the site would not build cleanly; fix errors before merging.

## Publications (BibTeX)

Sources:

- [`bibliography/publications.bib`](bibliography/publications.bib) and [`bibliography/manuscripts.bib`](bibliography/manuscripts.bib) — edit these to add or change papers.
- [`_data/pub_categories.yml`](_data/pub_categories.yml) — section order and which citation keys appear under **Manuscripts** / **Neuroimaging** / etc.
- [`_data/pub_overrides.yml`](_data/pub_overrides.yml) — optional PDF, supplement, code, and extra links keyed by BibTeX entry ID.

After changing any of the above, regenerate the Jekyll data file and commit it:

```bash
make pubs
```

The first run creates a local virtualenv `.venv-bib/`, installs `scripts/requirements-bib.txt`, then runs the generator. You do **not** need to install a separate Python distribution beyond the `python3` already on your Mac.

This writes [`_data/publications_generated.yml`](_data/publications_generated.yml), which [`_pages/publications.md`](_pages/publications.md) uses to render the list.

If you maintain BibTeX in a separate LaTeX CV project, copy updated `.bib` files into [`bibliography/`](bibliography/) here, then run `make pubs` again.
