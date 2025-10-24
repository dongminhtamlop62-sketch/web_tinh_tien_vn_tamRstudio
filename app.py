from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
lich_su = []  # lưu tạm trong bộ nhớ (reset khi restart)

@app.route("/", methods=["GET", "POST"])
def home():
    tong_tien = None
    if request.method == "POST":
        try:
            gia = float(request.form["gia"])
            so_luong = int(request.form["so_luong"])
            tong_tien = gia * so_luong
            lich_su.append({
                "gia": gia,
                "so_luong": so_luong,
                "tong": tong_tien
            })
        except ValueError:
            tong_tien = "Vui lòng nhập số hợp lệ."
    return render_template("index.html", tong_tien=tong_tien, lich_su=lich_su)

@app.route("/clear")
def clear_history():
    """Xóa toàn bộ lịch sử tính tiền"""
    lich_su.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
