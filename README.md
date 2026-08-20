# JAM Dance Academy — Flask app

Real, server-backed photo uploads (not stuck in one browser's storage) plus
the enquiry form, running as a proper Flask app.

## Why this version

The previous single-file HTML version saved uploaded photos in the
browser's `localStorage` — which meant photos only showed up for whoever
uploaded them, on that one device, and could vanish depending on the
browser. This version saves photos as real files on the server, so:

- Anyone can upload from their phone (camera or photo library)
- Every visitor sees the same photos, from any device
- Photos persist properly — no more disappearing uploads

## Project structure

```
jam-flask/
├── app.py                    # routes, site text, upload handling
├── requirements.txt
├── Procfile                  # for gunicorn on Render/Railway
├── templates/index.html      # Jinja2 template
└── static/
    ├── css/style.css
    ├── js/main.js
    ├── logo.jpg
    └── uploads/              # uploaded photos land here (auto-created)
```

## Run locally

```bash
pip install -r requirements.txt
flask --app app run --debug
```

Visit http://127.0.0.1:5000 — click any "+" button to upload a photo from
your computer, refresh, and it's still there.

## Editing site text

All copy (headings, class descriptions, founder bio, contact info) lives
in the `SITE_CONTENT` dict near the top of `app.py`. Edit there — the
template just renders it.

## How photo upload works

- Each photo slot has a fixed id (e.g. `about-visual`, `founder-photo`,
  `bollywood-dance`, `community-tile-1` … `community-tile-5`).
- Uploading calls `POST /upload/<id>` with the image as form data.
- The server resizes it (max 1400px on the long edge), compresses it as a
  JPEG, and saves it to `static/uploads/<id>.jpg`, overwriting any
  previous photo in that slot.
- The homepage checks which files exist in `static/uploads/` each time it
  renders, so uploads show up immediately for every visitor.
- There's no login/permission check on uploads — anyone with the link can
  replace a photo. Fine for a small single-instructor site; say the word
  if you'd like a simple password gate added before this goes fully public.

## Developing entirely from a phone

You don't need Python on your phone. The usual approach:

1. **Put this folder in a GitHub repo.** You can create/edit files
   directly in GitHub's web interface from a phone browser (or the GitHub
   mobile app) — no local Python needed.
2. **Connect the repo to a free host** like Render.com or Railway.app.
   Both auto-detect `requirements.txt` and `Procfile` and deploy on every
   push — all done from your phone browser.
3. **Test on the live URL** the host gives you, right from your phone.

For small text edits (changing a sentence in `app.py`), GitHub's mobile
editor is enough. For anything more involved, come back here and I can
generate the updated files for you to paste in.

## Enquiry form (email delivery)

The enquiry form posts to [FormSubmit.co](https://formsubmit.co) — a free
service that requires no signup, but does require a one-time activation:

**The first-ever submission triggers an activation email to
`jamdance.be@gmail.com`.** Someone needs to open that email and click the
confirmation link before submissions start arriving normally. This can't
be automated — it has to be done once by whoever owns that inbox.

Once activated:
- Submissions email straight to `jamdance.be@gmail.com`
- The sender gets an automatic acknowledgement email
- Replying in Gmail goes straight back to the enquirer (Reply-To is set
  automatically from their email field)

## Deploying

- **Render / Railway** — connect the GitHub repo, they detect
  `requirements.txt` and `Procfile` automatically.
- **PythonAnywhere** — upload the folder, point a WSGI app at `app.py`.
- Don't use `flask run` in production — the `Procfile` runs `gunicorn`
  instead, which is what these hosts use automatically.

One thing to know: on some free hosting tiers, the filesystem resets on
each deploy/restart, which would wipe `static/uploads/`. If your host does
this (check their docs), you'll want a persistent disk add-on or to move
uploads to something like S3 — happy to wire that up if you hit this.
