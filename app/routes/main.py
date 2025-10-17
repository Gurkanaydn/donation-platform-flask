from flask import Blueprint, render_template

main_bp = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    url_prefix=""
)

@main_bp.route("/")
def home():
    return render_template("index.html")
