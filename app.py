from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    tong_tien = None
    if request.method == "POST":
        try:
            gia = float(request.form["gia"])
            so_luong = int(request.form["so_luong"])
            tong_tien = f"{gia * so_luong:,.0f}".replace(",", ".")

        except ValueError:
            tong_tien = "Vui lòng nhập số hợp lệ."
    return render_template("index.html", tong_tien=tong_tien)

if __name__ == "__main__":
    app.run(debug=True)
