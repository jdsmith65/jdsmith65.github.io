# Jared D. Smith — personal website

A small, independent academic website prepared for GitHub Pages. The site uses static HTML and CSS. It has no JavaScript dependencies, tracking, paid theme, database, or institutional hosting requirement.

## Make routine updates

Most changes happen in **`content/site.json`**. It contains the profile, publications, working papers, teaching, and concise CV.

1. Open that file on GitHub and choose the pencil icon.
2. Change the relevant text, title, status, DOI, or link. Preserve the quotes, commas, and square brackets.
3. Commit the change to `main`. The included workflow builds and publishes the site automatically after checks pass.

For a new paper, copy an existing entry in the appropriate list. A publication uses a DOI without the `https://doi.org/` prefix. Additional paper links use a label and complete HTTPS URL. Working papers with no public link can keep an empty `links` list. A blank `coauthors` field denotes sole authorship, so change it only when that is intended.

Update `profile.updated` when changing the website and `profile.cv_date` when refreshing the CV. Replacing the source CV elsewhere on the computer does **not** silently change the website; its revisions must be reconciled into this content file.

The Scholar link appears when `profile.scholar_url` contains a URL. It is temporarily omitted because the existing page and September CV use different profile IDs.

The photo is `assets/jared-smith.jpg`; design is in `assets/style.css`; layout is in `scripts/build.py`. All hosted assets belong to this repository. The homepage and concise HTML CV are generated from the same content, so publication updates only need to be made once. The CV can be saved to PDF using the browser's Print menu. The site does not distribute the source CV's named student-advising records.

## Publish for the first time

1. Use a GitHub repository you own. For an account homepage, name it `YOUR-USERNAME.github.io`; an existing project repository works too.
2. Place the website files at the repository root, including `.github/workflows/pages.yml`, and exclude `SOURCE_NOTES.md`. Use `main` as the branch name, or update the workflow's two branch settings.
3. In **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
4. Push to `main`, or run **Publish website** from the Actions tab. The deploy job should finish successfully before treating the site as published.

Only `dist/` is uploaded to Pages. The content source, build scripts, and documentation remain in the repository but are not part of the published website. A public GitHub repository still makes all committed files publicly readable. Copy only the website files, not the parent CV folder. Keep `SOURCE_NOTES.md` local; it is excluded from Git and from the prepared upload package.

Official setup references: [Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site) and [configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). The deployment actions follow GitHub's [static Pages workflow](https://github.com/actions/starter-workflows/blob/main/pages/static.yml), checked October 3, 2026.

## Preview locally

Python 3.9 or later is sufficient. No package installation is needed.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Open `http://127.0.0.1:8765/`. After editing content or styling, rerun the build and refresh. The generated `dist` folder is ignored by Git because GitHub builds it on each update.

The build/check commands were run locally. GitHub publication still requires a successful hosted workflow run.
