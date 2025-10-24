from flask import Flask, redirect, url_for, render_template, request, session
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Cho phép HTTP khi chạy local
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# --- Cấu hình đăng nhập Google ---
google_bp = make_google_blueprint(
    client_id="CLIENT_ID_CỦA_BẠN",
    client_secret="CLIENT_SECRET_CỦA_BẠN",
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# --- Trang chủ ---
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
            tong_tien = "Lỗi nhập dữ liệu!"
    return render_template("index.html", username=username, tong_tien=tong_tien)

# --- Khi người dùng đăng nhập bằng Google ---
@app.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))  # <-- dòng này chính xác

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        info = resp.json()
        session["username"] = info["email"]
        return redirect(url_for("home"))
    return "Đăng nhập Google thất bại!"

# --- Đăng xuất ---
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
