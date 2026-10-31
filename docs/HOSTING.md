# Hosting guide: free web hosting for the portfolio

As of 2026-10-31. Free tiers change often, so check each host's own page before you rely on a limit.

## The short answer

**InfinityFree cannot run the Flask version.** Its free plan is PHP and MySQL hosting. It can host the **static version** of this site, which is plain HTML and needs no Python.

| You want | Use this version | Free hosts that work |
| --- | --- | --- |
| The simplest, fastest, most reliable showcase | Static (`python build.py`) | InfinityFree, GitHub Pages, GitLab Pages, Cloudflare Pages, Netlify |
| The Flask app itself running live | Flask (`gunicorn app:app`) | PythonAnywhere (free, with limits), Render (free, sleeps when idle) |

**Recommendation:** host the static version. It loads in one request (38 KB, Lighthouse 100 in all four categories on a local test), it never goes to sleep, and there is no server to patch. Use the Flask version locally for editing and, if you want, on one of the Flask hosts as a live demo.

What is verified and what is not is marked in each section. "Verified" means I opened the host's page or forum thread; "not verified" means it comes from search snippets or general knowledge and you should confirm it in the host's current documentation.

---

## Part 1: Build the static version

You need Python 3.10 or newer on your own computer. The host does not need Python.

```text
cd website
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python build.py                    # writes build/index.html
```

What you get:

- `build/index.html`: the whole page, with the CSS and JavaScript inside it.
- `build/static/img/`: only if you added project images.
- `build/.nojekyll`: an empty file that GitHub Pages needs so it serves files as they are.

Open `build/index.html` by double-clicking it to check it. It must look the same as `python app.py` at http://127.0.0.1:5000, apart from the CV and blog links, which the single page leaves out.

Options:

```text
python build.py --out public                         # another output folder
python build.py --full                               # also exports /cv and the blog as separate pages
python build.py --full --base-path /portfolio        # for a host that serves the site under /portfolio/
```

Rebuild every time you change `content.yaml`, a post, or an image. The build deletes and recreates the output folder, but it refuses to touch a folder that is not empty and does not already contain a previous build.

---

## Part 2: Host the static version

### Option A: InfinityFree

Upload steps are verified against one how-to article ([DEV Community guide](https://dev.to/billy_de_cartel/hosting-a-website-on-infinity-free-for-free-192f)); the FTP route and default-file details are not covered there.

1. Create an account at InfinityFree, then create a **hosting account**. Name it after the site, not after yourself.
2. Add a domain. Use the **Subdomain** tab for a free InfinityFree address, or the **Custom domain** tab for your own. A custom domain needs its nameservers pointed at InfinityFree.
3. Open the hosting account's control panel and use the **Online File Manager** (or an FTP client with the credentials shown in the account settings).
4. Open the `htdocs` folder. If it holds a placeholder page from InfinityFree, delete or overwrite it so your `index.html` is the one served.
5. Upload the **contents** of `build/`: `index.html` goes directly in `htdocs`, not in a subfolder. If you have project images, upload `static/img/` too, keeping the same folder names.
6. Visit your address. It should show the finished page.

You do not need a MySQL database or any PHP for this site. Skip those steps.

Things to know:

- A reader of the how-to article reported long downtime on InfinityFree. That is one anecdote, but it is a reason to keep a second copy (see GitHub Pages below) if the site matters for a job search.
- Free hosts sometimes add their own banner or script to pages. Check the live page before you share the link.
- Updating the site means re-uploading the changed files.

### Option B: GitHub Pages (not verified: standard behaviour, check GitHub's docs)

1. Create a GitHub repository, for example `portfolio`.
2. Build the site and put the **contents** of `build/` (including `.nojekyll`) in a branch such as `gh-pages`, or in a `docs/` folder on `main`.
3. In the repository's **Settings, Pages**, choose that branch or folder as the source.
4. The site appears at `https://<your-username>.github.io/<repository>/`. The single page uses only relative links, so a sub-path like this works.

### Option C: GitLab Pages (not verified; not run on a runner)

Your repository already has a `.gitlab-ci.yml`. A job named `pages` that writes the site into a folder called `public` is the GitLab convention:

```yaml
pages:
  stage: deploy
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - python build.py --out public
  artifacts:
    paths: [public]
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

You would also need to add `deploy` to the `stages:` list. **Check the Pages access setting before you push:** a site on GitLab Pages can be public even when the repository is private, and your `content.yaml` holds your email address.

### Option D: Cloudflare Pages or Netlify (not verified)

Both can serve a folder of static files. Connect the repository, set the build command to `pip install -r requirements.txt && python build.py --out public`, and the output folder to `public`. Or skip the build step on their side and upload the `build/` folder by hand.

---

## Part 3: Host the Flask version

### Option E: PythonAnywhere (free)

Limits are verified from PythonAnywhere's [free account page](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/): **1 web app with 1 web worker, 1-month expiry, 100 CPU seconds, 512 MiB disk, 2 consoles**. The page does not say how renewal works or what outbound internet access is allowed, so confirm both in their help before you depend on the site.

Steps are verified from PythonAnywhere's [Flask page](https://help.pythonanywhere.com/pages/Flask/):

1. **Upload the project.** Use the **Files** tab to upload a zip of the `website` folder (leave out `.venv`, `.git`, `build`, `.lighthouseci`) and unzip it in a Bash console. These steps assume it ends up at `/home/<username>/website`.
2. **Create a virtualenv** in a Bash console, then install the requirements:
   ```text
   mkvirtualenv portfolio --python=python3.12
   pip install -r /home/<username>/website/requirements.txt
   ```
   Use the same Python version in the next step. `requirements.txt` does not include the test tools, which you do not need on the server.
3. **Create the web app.** On the **Web** tab choose **Add a new web app**, then **Manual configuration**, with that same Python version.
4. **Set the virtualenv path** on the Web tab to `/home/<username>/.virtualenvs/portfolio`.
5. **Edit the WSGI file** (the link near the top of the Web tab). Replace its Flask section with:
   ```python
   import sys
   path = '/home/<username>/website'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```
   This site's `app.py` already keeps `app.run()` inside `if __name__ == "__main__":`, which PythonAnywhere requires. Calling it at import time would crash the app.
6. **Reload** the web app from the Web tab (not covered on the page I opened; the Web tab has a reload button). Your site is at `<username>.pythonanywhere.com`.
7. **Optional, not verified:** add a static files mapping on the Web tab, URL `/static/` to `/home/<username>/website/static/`, so the host serves the CSS and JavaScript directly. The app serves them itself if you skip this.

After you change `content.yaml`, upload the new file and reload the web app.

Note on the dev.to import: if you set `writing.devto_username`, the app fetches your posts when it starts. Free PythonAnywhere accounts may restrict outbound internet access (one competitor's page says so; PythonAnywhere's own page does not mention it). If the import is blocked, the site still starts and logs "dev.to import skipped". Use hand-written `writing.links` instead.

### Option F: Render (free web service)

Limits are verified from Render's [free tier page](https://render.com/docs/free): the service **spins down after 15 minutes without traffic and takes about a minute to wake**; **750 free instance hours per calendar month**; the local filesystem is **not kept** across restarts and redeploys; there is no shell access. For a portfolio, the first visitor after a quiet period waits about a minute, which undercuts the fast-page work. Bandwidth and build-minute allowances are not stated on that page.

Setup (not verified: standard Render workflow, check the dashboard wording):

1. Push the project to GitHub or GitLab.
2. In Render, create a **Web Service** from the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
5. Deploy. Render gives you an `onrender.com` address.

Render does not read the `Procfile`, so set the start command in the dashboard. Because the filesystem is not kept, `content.yaml` changes must go through the repository and a redeploy.

### Hosts that no longer have a usable free tier (not verified: from search snippets, not opened)

Search results report that Fly.io has no free tier for new users, that Koyeb closed its free plan to new users in February 2026, and that Heroku has no free tier. I did not find a source for Vercel running this Flask app, so I have not listed it.

---

## Before you publish: checklist

- [ ] Replace the placeholder email (`your-email@example.com`) and the GitHub, LinkedIn and Credly links in `content.yaml`. The page still has the `your-handle` placeholders.
- [ ] Decide whether you want your real email in the page. It is visible in the HTML to anyone and to spam crawlers. A contact form needs a service this site does not have.
- [ ] Replace or delete the dummy "Example: my first dev.to post (replace me)" entry under `writing.links`.
- [ ] Rewrite the case-study text in your own words. It is dummy copy built from your CV.
- [ ] Add the one real number to your current role's ingestion bullet (there is a `TODO` at the top of `content.yaml`).
- [ ] Add project images to `static/img/` if you have them, then rebuild.
- [ ] Run `python -m pytest` and `python build.py`. Open `build/index.html` in a browser at desktop and phone width.
- [ ] Do not publish your phone number or home address. The site does not include them.

---

## Troubleshooting

| What you see | Likely cause | Fix |
| --- | --- | --- |
| The page has no styling | The static page lost its inlined CSS, or a Flask host cannot find `/static/` | Rebuild with `python build.py`; on a Flask host, check the static mapping or that the `static` folder was uploaded |
| InfinityFree shows its own default page | `index.html` is in a subfolder, or the placeholder page is still there | Put `index.html` directly in `htdocs` and remove the placeholder |
| Project images are missing | `static/img/` was not uploaded, or the file names differ in case | Upload the folder with the same names; hosts on Linux are case-sensitive |
| Links are broken under a sub-path (`/portfolio/`) | Using `--full` without a base path | `python build.py --full --base-path /portfolio` |
| 502 or 504 on PythonAnywhere | `app.run()` called at import, a wrong WSGI import, or a missing virtualenv path | Check the WSGI file matches the snippet above and read the error log on the Web tab |
| `No module named yaml` (or flask) | The virtualenv path is not set on the Web tab, or requirements were not installed in it | Set the path, then `pip install -r requirements.txt` inside that virtualenv |
| Posts from dev.to are missing | Import blocked, wrong username, or the app was not restarted | Check the log for "dev.to import skipped"; use `writing.links`; reload the app |
| Edits to `content.yaml` do not appear | Static: not rebuilt or re-uploaded. Flask: not reloaded | Rebuild and re-upload, or reload the web app |
| Slow first load on Render | The free service was asleep | Expected on the free tier; use the static version for the showcase |
| `build failed: ... does not look like a previous build` | `--out` points at a folder with other files in it | Choose a new or empty folder |

---

## Sources

Pages I opened:

- InfinityFree forum thread, [Does InfinityFree support Python?](https://forum.infinityfree.com/t/does-infintyfree-support-python/117556): members say Python is not supported on free plans and that paid plans come from iFastNet, a separate company.
- DEV Community, [Hosting a website on InfinityFree](https://dev.to/billy_de_cartel/hosting-a-website-on-infinity-free-for-free-192f): upload steps and the downtime comment.
- PythonAnywhere, [Free account features](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/) and [Deploying a Flask app](https://help.pythonanywhere.com/pages/Flask/).
- Render, [Free tier limits](https://render.com/docs/free).

Search results I did not open (treat as unconfirmed): other InfinityFree forum threads on Python and Flask support, Render's article on free tiers in 2026, snippets about Fly.io, Koyeb and Heroku, and a competitor's page about PythonAnywhere's outbound access.
