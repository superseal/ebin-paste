import os
from flask import Flask, render_template, url_for, request, make_response, Markup, abort, redirect, session
from werkzeug import secure_filename
import sqlite3

from source_code import syntax_highlight

db = sqlite3.connect("data.db", check_same_thread=False)
cursor = db.cursor()
app = Flask(__name__)

##### Paste URLs #####
index = 0

def load_index():
    global index
    cursor.execute("SELECT n FROM count;")
    index = cursor.fetchone()[0]

def update_index():
    global index
    cursor.execute("DELETE FROM count;")
    cursor.execute("VACUUM;")
    index += 1
    cursor.execute("INSERT INTO count VALUES (?)", (index,))
    db.commit()
    return index

def index_hash(index):
    return hex(index)[2:]

##### Web interface #####
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/paste", methods=["POST"])
def paste_upload():
    paste_id = update_index()
    paste_index = index_hash(paste_id)

    content = request.form["content"]
    lang = request.form["lang"]
    tags = request.form["tags"].split(",")
    title = request.form["title"]
    if not title:
        title = "Untitled"
    cursor.execute("INSERT INTO paste VALUES (?, ?, ?, ?, datetime('now'))", 
            (paste_index, title, content, lang))
    for tag in tags:
        cursor.execute("INSERT INTO tags VALUES (?, ?)", (paste_index, tag))
    db.commit()

    return redirect(url_for("paste_load", index=paste_index))
    
@app.route("/<index>")
def paste_load(index):
    cursor.execute("SELECT content, lang FROM paste WHERE id=?;", (index,))
    result = cursor.fetchone()
    cursor.execute("SELECT tag FROM tags WHERE id=?", (index,))
    paste_tags = [c[0] for c in cursor.fetchall()]
    raw_arg = request.args.get("raw")

    if result:
        content, lang = result
        if raw_arg == "":
            response = make_response(content)
            response.headers["Content-Type"] = "text/plain; charset=utf-8"
            return response
        else:
            formatted_content = Markup(syntax_highlight(content, lang))
            return render_template("paste.html", paste=formatted_content, tags=paste_tags)
    else:
        abort(404)

@app.route("/tag/<tag>")
def tag_load(tag):
    cursor.execute("""SELECT paste.date, paste.title, paste.id, paste.lang FROM tags 
            JOIN paste ON paste.id = tags.id WHERE tag = ? GROUP BY paste.id;""", (tag,))
    tagged_pastes = cursor.fetchall()
    return render_template("taglist.html", tag_title=tag, tagged_pastes=tagged_pastes)

@app.route("/file-up", methods=["POST"])
def file_upload():
    username = request.cookies.get('username')
    upload = request.files["upload"]
    upload.save("./uploads/{}".format(secure_filename(upload.filename)))
    return render_template("up.html" )

####
load_index()
if __name__ == "__main__":
    app.run()
