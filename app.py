"""
JAM - Just About Movement
Flask application serving the dance academy's marketing site, handling
photo uploads (saved to disk so every visitor sees them, uploaded from
any device including a phone), and forwarding enquiry form submissions.

Run locally:
    pip install -r requirements.txt
    flask --app app run --debug

Then visit http://127.0.0.1:5000
"""

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session
from PIL import Image, ImageOps

app = Flask(__name__)

# Needed to sign the admin session cookie. Set a real value via the
# SECRET_KEY environment variable in production (Railway → Variables).
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

# The site owner visits the site once with ?admin=<this value> to unlock
# the "+" photo upload buttons in their own browser. Everyone else just
# sees plain photos with no upload controls. Set a real secret via the
# ADMIN_KEY environment variable in Railway → Variables — don't leave the
# default in production.
ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_DIM = 1400          # longest edge, in pixels, after resizing
JPEG_QUALITY = 82
MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15MB raw upload cap (pre-compression)

# Every valid photo placeholder on the site. Uploads to any other id are
# rejected, so this also acts as a whitelist.
PHOTO_IDS = {
    "about-visual",
    "founder-photo",
    "bollywood-dance",
    "bollywood-urban",
    "performances-events",
    "community-tile-1",
    "community-tile-2",
    "community-tile-3",
    "community-tile-4",
    "community-tile-5",
}

# ---------------------------------------------------------------------------
# Site text content. Edit here to update copy — templates just render this.
# ---------------------------------------------------------------------------
SITE_CONTENT = {
    "site": {
        "name": "JAM Dance Academy",
        "meta_description": (
            "JAM Dance Academy - Bollywood Dance Academy in Belgium. "
            "Classes for adults and kids, performances, and events."
        ),
        "instagram": "https://www.instagram.com/jamdance.be",
    },
    "hero": {
        "eyebrow": "Bollywood Dance Academy in Belgium",
    },
    "founder": {
        "name": "Shweta Rajani",
        "role": "Founder & Sole Instructor",
        "paragraphs": [
            "Also known as Beatdropdancer — dance has been part of her life "
            "for as long as she can remember. What started as a passion grew "
            "into a dream: to create a space where people of all ages can "
            "experience the joy, energy, and magic of Indian dance.",
            "As the founder of JAM Dance Academy, she brings Bollywood and "
            "Urban dance to life through fun, energetic classes, "
            "performances, and community events. For her, dance is more than "
            "choreography — it's about confidence, self-expression, "
            "connection, and simply enjoying the moment.",
            "Her goal is to get more people moving, smiling, and JAM-ing. ❤️",
        ],
    },
    "classes": [
        {
            "id": "bollywood-dance",
            "label": "Adults",
            "title": "Bollywood Dance",
            "description": (
                "Immerse yourself in the energetic world of Bollywood dance "
                "— learn vibrant moves and expressions that tell a story "
                "and connect with tradition."
            ),
        },
        {
            "id": "bollywood-urban",
            "label": "Kids & Teens",
            "title": "Bollywood Urban",
            "description": (
                "Where emerging stars find their rhythm. Give your child "
                "more than dance — build confidence, spark creativity, "
                "make new friends, and discover the joy of performing."
            ),
        },
        {
            "id": "performances-events",
            "label": "All levels",
            "title": "Performances & Events",
            "description": (
                "Step beyond the classroom and onto the stage! Every "
                "performance helps build confidence, teamwork, and "
                "unforgettable memories."
            ),
        },
    ],
    "contact": {
        "email": "jamdance.be@gmail.com",
        "phone_display": "+32 467 86 78 43",
        "phone_href": "+32467867843",
        "address": "Gemeentelijke sporthal, Sint-Stevens-Woluwe, 1200",
    },
}


def photo_url(photo_id: str):
    """Return the static URL for a photo if it's been uploaded, else None."""
    path = UPLOAD_DIR / f"{photo_id}.jpg"
    if path.exists():
        # cache-bust with mtime so a re-upload shows immediately everywhere
        return f"/static/uploads/{photo_id}.jpg?v={int(path.stat().st_mtime)}"
    return None


@app.context_processor
def inject_photo_url():
    return {"photo_url": photo_url}


def is_admin() -> bool:
    return session.get("is_admin", False)


@app.route("/")
def index():
    # Visiting with ?admin=<ADMIN_KEY> unlocks upload buttons for this
    # browser going forward (stored in a signed session cookie).
    key = request.args.get("admin")
    if key and key == ADMIN_KEY:
        session["is_admin"] = True
    return render_template("index.html", is_admin=is_admin(), **SITE_CONTENT)


@app.route("/admin-logout")
def admin_logout():
    session.pop("is_admin", None)
    return render_template("index.html", is_admin=False, **SITE_CONTENT)


@app.route("/upload/<photo_id>", methods=["POST"])
def upload_photo(photo_id):
    """Receive a photo from any device (including phone camera/gallery),
    resize + compress it server-side, and save it so every visitor sees it.
    Restricted to the admin session so random visitors can't upload.
    """
    if not is_admin():
        return jsonify(message="Not authorized."), 403

    if photo_id not in PHOTO_IDS:
        return jsonify(message="Unknown photo slot."), 400

    file = request.files.get("photo")
    if not file or file.filename == "":
        return jsonify(message="No photo received."), 400

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > MAX_UPLOAD_BYTES:
        return jsonify(message="Photo is too large (max 15MB)."), 400

    try:
        img = Image.open(file.stream)
        img = ImageOps.exif_transpose(img)  # respect phone camera orientation
        img = img.convert("RGB")
        img.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)

        dest = UPLOAD_DIR / f"{photo_id}.jpg"
        img.save(dest, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    except Exception:
        return jsonify(message="Could not process that image."), 400

    return jsonify(message="Photo saved.", url=photo_url(photo_id)), 200


@app.route("/upload/<photo_id>", methods=["DELETE"])
def delete_photo(photo_id):
    """Remove an uploaded photo, reverting that slot to its default look.
    Restricted to the admin session so random visitors can't delete photos.
    """
    if not is_admin():
        return jsonify(message="Not authorized."), 403

    if photo_id not in PHOTO_IDS:
        return jsonify(message="Unknown photo slot."), 400

    dest = UPLOAD_DIR / f"{photo_id}.jpg"
    if dest.exists():
        dest.unlink()

    return jsonify(message="Photo removed."), 200


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, host="0.0.0.0")
