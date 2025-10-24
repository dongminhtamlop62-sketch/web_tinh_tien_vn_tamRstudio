from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = "supersecret"

# --- Hàm quản lý người dùng ---
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- Trang chính ---
@app.route("/", methods=["GET", "POST"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    user = users.get(session["username"], {"lich_su": []})
    tong_tien = None

    if request.method == "POST":
        try:
            gia = float(request.form["gia"])
            so_luong = int(request.form["so_luong"])
            tong_tien = gia * so_luong
            user["lich_su"].append({
                "gia": gia,
                "so_luong": so_luong,
                "tong": tong_tien
            })
            users[session["username"]] = user
            save_users(users)
        except ValueError:
            tong_tien = "Lỗi: nhập không hợp lệ"

    return render_template("index.html", tong_tien=tong_tien, lich_su=user["lich_su"])

# --- Đăng nhập ---
@app.route("/login", methods=["GET", "POST"])
def login():
    users = load_users()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Sai tài khoản hoặc mật khẩu!"

    return render_template("login.html")

# --- Đăng ký ---
@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_users()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "Tài khoản đã tồn tại!"
        else:
            users[username] = {"password": password, "lich_su": []}
            save_users(users)
            return redirect(url_for("login"))
    return render_template("register.html")

# --- Đăng xuất ---
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
