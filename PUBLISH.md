# Putting this on GitHub Pages

Three ways, pick one.

## 1. The script (fastest)

Needs the GitHub CLI once: `brew install gh && gh auth login`

```bash
cd path/to/mh-liver-pathways
./publish.sh                 # or: ./publish.sh some-other-repo-name
```

It creates a public repo, pushes, and enables Pages. It prints the site URL at
the end. The first build takes a minute or two.

## 2. By hand, with git

```bash
cd path/to/mh-liver-pathways
git init && git add -A && git commit -m "Liver tumour pathway consoles"
git branch -M main
git remote add origin https://github.com/<you>/mh-liver-pathways.git
git push -u origin main
```

Then: repo → **Settings → Pages** → Source **Deploy from a branch**, branch
**main**, folder **/ (root)** → Save.

## 3. No command line at all

On github.com: **New repository** → name it, **Public**, create. On the empty
repo page click **uploading an existing file**, drag in everything from this
folder (keep the subfolders), commit. Then Settings → Pages as above.

## What the URLs look like

```
https://<you>.github.io/mh-liver-pathways/          landing page
https://<you>.github.io/mh-liver-pathways/hcc/      and crlm/ icca/ hilar/ nelm/
```

## Before you share the link

GitHub Pages is world-readable — anyone with the URL can read all five
pathways, and a public repo is browsable by anyone. The pages carry an
"under development" banner and a status note, but nothing restricts who sees
them. If you need it private, Pages on a private repo requires GitHub Pro or a
Team plan; the alternative is to keep sharing the Claude artifact links, which
are private until you share them.
