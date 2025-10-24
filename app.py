from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import json, os

app = Flask(__name__)
app.secret_key = "my_secret_key"  # cần cho session

USERS_FILE = "users.json"

# ---- Đọc / ghi dữ liệu người dùng ----
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ---- Trang chủ (tính tiền) ----
@app.route("/", methods=["GET", "POST"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    username = session["username"]
    user_data = users.get(username, {"lich_su": []})
    tong_tien = None

    if request.method == "POST":
        try:
            gia = float(request.form["gia"])
            so_luong = int(request.form["so_luong"])
            tong_tien = gia * so_luong
            thoi_gian = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

            user_data["lich_su"].append({
                "gia": gia,
                "so_luong": so_luong,
                "tong": tong_tien,
                "thoi_gian": thoi_gian
            })

            users[username] = user_data
            save_users(users)
        except ValueError:
            tong_tien = "Dữ liệu không hợp lệ."

    return render_template("index.html", username=username,
                           tong_tien=tong_tien, lich_su=user_data["lich_su"])

# ---- Xóa lịch sử ----
@app.route("/clear")
def clear_history():
    if "username" not in session:
        return redirect(url_for("login"))
    users = load_users()
    username = session["username"]
    users[username]["lich_su"] = []
    save_users(users)
    return redirect(url_for("home"))

# ---- Đăng ký ----
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if username in users:
            return "Tên người dùng đã tồn tại!"
        users[username] = {"password": password, "lich_su": []}
        save_users(users)
        return redirect(url_for("login"))
    return render_template("register.html")

# ---- Đăng nhập ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Sai tên hoặc mật khẩu!"
    return render_template("login.html")

# ---- Đăng xuất ----
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
