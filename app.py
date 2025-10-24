from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
import os, json

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------- Cấu hình Google OAuth ----------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Cho phép chạy HTTP khi test local

google_bp = make_google_blueprint(
    client_id="CLIENT_ID_CUA_BAN",
    client_secret="CLIENT_SECRET_CUA_BAN",
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# ---------------------- Hàm tiện ích ----------------------

def load_users():
    """Đọc danh sách người dùng từ file users.json"""
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    """Lưu danh sách người dùng vào file users.json"""
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# ---------------------- Trang chủ ----------------------

@app.route("/", methods=["GET", "POST"])
def home():
    username = session.get("username")
    tong_tien = None

    if request.method == "POST":
        try:
            gia = float(request.form["gia"])
            so_luong = int(request.form["so_luong"])
            tong_tien = f"{gia * so_luong:,.0f}".replace(",", ".")
        except:
            tong_tien = "❌ Vui lòng nhập số hợp lệ."

    return render_template("index.html", username=username, tong_tien=tong_tien)

# ---------------------- Đăng ký ----------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            return "❌ Mật khẩu nhập lại không khớp!"

        users = load_users()

        if email in users:
            return "⚠️ Email đã tồn tại, vui lòng dùng email khác."

        users[email] = {"username": username, "password": password, "lich_su": []}
        save_users(users)

        session["username"] = email
        return redirect(url_for("home"))

    return render_template("register.html")

# ---------------------- Đăng nhập ----------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        users = load_users()
        if email in users and users[email]["password"] == password:
            session["username"] = email
            return redirect(url_for("home"))
        else:
            return "❌ Sai email hoặc mật khẩu!"

    return render_template("login.html")

# ---------------------- Đăng nhập bằng Google ----------------------

@app.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        info = resp.json()
        email = info["email"]
        name = info.get("name", email.split("@")[0])

        users = load_users()
        if email not in users:
            users[email] = {"username": name, "password": None, "lich_su": []}
            save_users(users)

        session["username"] = email
        return redirect(url_for("home"))
    return "❌ Đăng nhập Google thất bại!"

# ---------------------- Đăng xuất ----------------------

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("google_oauth_token", None)
    return redirect(url_for("home"))

# ---------------------- Chạy app ----------------------

if __name__ == "__main__":
    app.run(debug=True)
