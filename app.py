from flask import Flask, render_template, request

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

if __name__ == "__main__":
    app.run(debug=True)
