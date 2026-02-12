"""
Web Module Routes

Part of WebDisplay
System Web Module

License: MIT license

Author: C2311231

Notes:
"""

from flask import Blueprint, send_from_directory
import os
bp = Blueprint("web_v2", __name__)


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def catch_all(path):
    base_dir = os.path.dirname(__file__)
    return send_from_directory(os.path.join(base_dir, "ui/webdisplay/dist"), "index.html")

def get_blueprint():
    return bp