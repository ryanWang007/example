"""Mini Lookbook: Flask + SQLite，本地 CRUD 入门项目。"""
from pathlib import Path
import secrets
import sqlite3

from flask import Flask, abort, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config.update(
    SECRET_KEY=secrets.token_hex(32),
    DATABASE=Path(__file__).parent / "instance" / "lookbook.db",
    MAX_CONTENT_LENGTH=64 * 1024,
)


def get_db():
    """每个请求使用一个连接；首次访问时自动创建数据库和表。"""
    if "db" not in g:
        path = Path(app.config["DATABASE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                occasion TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            )
        """)
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def protect_forms():
    """表单令牌用于防止其他网站偷偷提交修改请求。"""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    if request.method == "POST":
        token = request.form.get("csrf_token", "")
        if not secrets.compare_digest(token, session["csrf_token"]):
            abort(400, description="表单已过期，请刷新页面再试。")


def get_outfit(outfit_id):
    outfit = get_db().execute(
        "SELECT * FROM outfits WHERE id = ?", (outfit_id,)
    ).fetchone()
    if outfit is None:
        abort(404)
    return outfit


def read_form():
    """后端也检查输入，不能只依赖 HTML 的 required。"""
    outfit = {key: request.form.get(key, "").strip()
              for key in ("title", "occasion", "notes")}
    error = None
    if not outfit["title"] or not outfit["occasion"]:
        error = "请填写穿搭名称和适用场合。"
    elif len(outfit["title"]) > 80 or len(outfit["occasion"]) > 40 or len(outfit["notes"]) > 1000:
        error = "名称最多 80 字，场合最多 40 字，备注最多 1000 字。"
    return outfit, error


# R = Read：读取全部记录并显示首页。
@app.get("/")
def index():
    outfits = get_db().execute("SELECT * FROM outfits ORDER BY id DESC").fetchall()
    return render_template("index.html", outfits=outfits)


# C = Create：GET 显示表单，POST 保存新记录。
@app.route("/outfits/new", methods=["GET", "POST"])
def create():
    outfit = {"title": "", "occasion": "", "notes": ""}
    error = None
    if request.method == "POST":
        outfit, error = read_form()
        if error is None:
            db = get_db()
            db.execute("INSERT INTO outfits (title, occasion, notes) VALUES (?, ?, ?)",
                       (outfit["title"], outfit["occasion"], outfit["notes"]))
            db.commit()
            return redirect(url_for("index"))
    return render_template("form.html", outfit=outfit, error=error, editing=False), 400 if error else 200


# U = Update：先查到旧记录，再显示/保存编辑表单。
@app.route("/outfits/<int:outfit_id>/edit", methods=["GET", "POST"])
def edit(outfit_id):
    outfit = get_outfit(outfit_id)
    error = None
    if request.method == "POST":
        outfit, error = read_form()
        if error is None:
            db = get_db()
            db.execute("UPDATE outfits SET title = ?, occasion = ?, notes = ? WHERE id = ?",
                       (outfit["title"], outfit["occasion"], outfit["notes"], outfit_id))
            db.commit()
            return redirect(url_for("index"))
    return render_template("form.html", outfit=outfit, error=error, editing=True), 400 if error else 200


# D = Delete：删除必须通过 POST，打开一个链接不会直接删数据。
@app.post("/outfits/<int:outfit_id>/delete")
def delete(outfit_id):
    get_outfit(outfit_id)
    db = get_db()
    db.execute("DELETE FROM outfits WHERE id = ?", (outfit_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
