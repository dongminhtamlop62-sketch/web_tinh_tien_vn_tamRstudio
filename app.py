from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
import os, json

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Cho phép HTTP khi test local
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# --- Cấu hình đăng nhập Google ---
google_bp = make_google_blueprint(
    client_id="CLIENT_ID_CUA_BAN",
    client_secret="CLIENT_SECRET_CUA_BAN",
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# --- Hàm đọc & ghi người dùng ---
def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# --- Trang chủ ---
@app.route("/", methods=["GET", "POST"])
def home():
    username = session.get("username")
    tong_tien = None
    lich_su = []

    users = load_users()

    # Nếu người dùng đã đăng nhập, lấy lịch sử của họ
    if username and username in users:
        lich_su = users[username].get("lich_su", [])

    if request.method == "POST":
        try:
            gia = float(request.form["gia"])
            so_luong = int(request.form["so_luong"])
            tong_tien = gia * so_luong
            tong_tien_str = f"{tong_tien:,.0f}".replace(",", ".")

            # Lưu vào lịch sử nếu đã đăng nhập
            if username:
                users = load_users()
                if username not in users:
                    users[username] = {"username": username, "password": None, "lich_su": []}
                users[username]["lich_su"].append({
                    "gia": gia,
                    "so_luong": so_luong,
                    "tong": tong_tien
                })
                save_users(users)

            return render_template("index.html", username=username, tong_tien=tong_tien_str, lich_su=users[username]["lich_su"] if username else [])

        except:
            tong_tien = "❌ Lỗi nhập dữ liệu!"

    return render_template("index.html", username=username, tong_tien=tong_tien, lich_su=lich_su)

# --- Đăng ký ---
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

# --- Đăng nhập ---
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

# --- Đăng nhập Google ---
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

# --- Đăng xuất ---
@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("google_oauth_token", None)
    return redirect(url_for("home"))
# --- Xóa lịch sử tính tiền ---
@app.route("/clear_history")
def clear_history():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    users = load_users()
    if username in users:
        users[username]["lich_su"] = []  # Xóa toàn bộ lịch sử
        save_users(users)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

