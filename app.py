from flask import Flask, render_template, request, redirect, url_for, flash
import os
import psycopg2
import psycopg2.extras
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# ----------------------------
# File upload settings
# ----------------------------
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------
# Database connection
# ----------------------------
def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(database_url)

# ----------------------------
# Create table if not exists
# ----------------------------
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            image_url VARCHAR(255)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

# ----------------------------
# Routes
# ----------------------------
@app.route("/")
@app.route("/menu")
def menu():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name, price, image_url FROM menu_items ORDER BY id;")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("menu.html", items=items)

@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "").strip()
        file = request.files.get("image_file")
        image_path = None

        if not name or not price:
            flash("Name and price are required!", "error")
            return redirect(url_for("add_item"))

        try:
            price_val = float(price)
        except ValueError:
            flash("Price must be a number.", "error")
            return redirect(url_for("add_item"))

        # Handle image upload
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = f"/static/uploads/{filename}"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO menu_items (name, price, image_url) VALUES (%s, %s, %s);",
            (name, price_val, image_path)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash(" Item added!", "success")
        return redirect(url_for("menu"))

    return render_template("add_item.html")

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM menu_items WHERE id = %s;", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash(" Item deleted!", "info")
    return redirect(url_for("menu"))

@app.route("/update/<int:item_id>", methods=["GET", "POST"])
def update_item(item_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT id, name, price, image_url FROM menu_items WHERE id=%s;", (item_id,))
    item = cur.fetchone()
    if not item:
        flash("Item not found.", "error")
        cur.close()
        conn.close()
        return redirect(url_for("menu"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "").strip()
        file = request.files.get("image_file")
        image_path = item["image_url"]  # keep current image if no new upload

        if not name or not price:
            flash("Name and price are required!", "error")
            return redirect(url_for("update_item", item_id=item_id))

        try:
            price_val = float(price)
        except ValueError:
            flash("Price must be a number.", "error")
            return redirect(url_for("update_item", item_id=item_id))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = f"/static/uploads/{filename}"

        cur.execute(
            "UPDATE menu_items SET name=%s, price=%s, image_url=%s WHERE id=%s;",
            (name, price_val, image_path, item_id)
        )
        conn.commit()
        flash(" Item updated!", "success")
        cur.close()
        conn.close()
        return redirect(url_for("menu"))

    cur.close()
    conn.close()
    return render_template("update_item.html", item=item)


# ----------------------------
# Routes details each item 
# ----------------------------


@app.route("/menu/<int:item_id>")
def item_details(item_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM menu_items WHERE id=%s;", (item_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()

    if not item:
        flash("Item not found.", "error")
        return redirect(url_for("menu"))

    return render_template("item_details.html", item=item)


if __name__ == "__main__":
    app.run(debug=True)
