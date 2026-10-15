from flask import Flask, render_template_string, request, redirect, url_for, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smart-library-phase2"

DATA_FILE = "bookings.json"
TOTAL_SEATS = 50


def load_bookings():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_bookings(bookings):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(bookings, file, indent=4)


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smart Library | Seat Reservation</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f6fb;
    color: #172033;
}
header {
    background: #153b66;
    color: white;
    padding: 24px 16px;
    text-align: center;
}
header h1 { margin: 0 0 8px; }
header p { margin: 0; color: #dce9f8; }
.container { max-width: 1000px; margin: 24px auto; padding: 0 16px; }
.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 22px;
}
.card, .panel {
    background: white;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 3px 12px #14213d10;
}
.card { text-align: center; }
.number { font-size: 28px; font-weight: bold; margin-top: 8px; }
.available-text { color: #15803d; }
.occupied-text { color: #dc2626; }
.seats {
    display: grid;
    grid-template-columns: repeat(10, minmax(0, 1fr));
    gap: 8px;
    margin: 18px 0;
}
.seat {
    border: 0;
    border-radius: 7px;
    padding: 12px 0;
    color: white;
    font-weight: bold;
    cursor: pointer;
}
.free { background: #16a34a; }
.taken { background: #dc2626; cursor: not-allowed; }
.legend { display: flex; gap: 18px; flex-wrap: wrap; margin: 14px 0; }
.legend span { display: flex; align-items: center; gap: 7px; }
.dot { width: 13px; height: 13px; border-radius: 4px; display: inline-block; }
form { display: grid; gap: 12px; }
label { font-weight: bold; font-size: 14px; }
input, select {
    width: 100%;
    padding: 11px;
    margin-top: 5px;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    font-size: 15px;
}
button.submit {
    background: #153b66;
    color: white;
    border: 0;
    padding: 13px;
    border-radius: 7px;
    cursor: pointer;
    font-size: 15px;
}
.message { padding: 12px; border-radius: 7px; margin-bottom: 12px; background: #e0f2fe; }
.booking { border-bottom: 1px solid #e5e7eb; padding: 12px 0; }
.booking:last-child { border-bottom: 0; }
.cancel {
    background: #fee2e2;
    color: #b91c1c;
    border: 0;
    border-radius: 5px;
    padding: 7px 10px;
    cursor: pointer;
}
footer { text-align: center; padding: 24px; color: #64748b; }
@media (max-width: 600px) {
    .seats { grid-template-columns: repeat(5, minmax(0, 1fr)); }
    .stats { grid-template-columns: 1fr; }
    .number { font-size: 23px; }
}
</style>
</head>
<body>

<header>
    <h1>📚 Smart Library</h1>
    <p>Seat Management & Reservation System</p>
</header>

<div class="container">

{% with messages = get_flashed_messages() %}
{% for message in messages %}
<div class="message">{{ message }}</div>
{% endfor %}
{% endwith %}

<div class="stats">
    <div class="card">
        Available Seats
        <div class="number available-text">{{ available }}</div>
    </div>
    <div class="card">
        Occupied Seats
        <div class="number occupied-text">{{ occupied }}</div>
    </div>
    <div class="card">
        Total Seats
        <div class="number">{{ total }}</div>
    </div>
</div>

<div class="panel">
    <h2>Choose Your Seat</h2>
    <div class="legend">
        <span><i class="dot" style="background:#16a34a"></i> Available</span>
        <span><i class="dot" style="background:#dc2626"></i> Occupied</span>
    </div>

    <div class="seats">
    {% for seat in range(1, total + 1) %}
        {% if seat|string in bookings %}
            <button class="seat taken" disabled title="Occupied">S{{ seat }}</button>
        {% else %}
            <button class="seat free" type="button"
                    onclick="document.getElementById('seat').value='{{ seat }}';
                    document.getElementById('booking-form').scrollIntoView({behavior:'smooth'});">
                S{{ seat }}
            </button>
        {% endif %}
    {% endfor %}
    </div>
</div>

<div class="panel" id="booking-form" style="margin-top:22px">
    <h2>Book a Seat</h2>
    <form method="POST" action="/book">
        <label>Seat Number
            <select name="seat" id="seat" required>
                {% for seat in range(1, total + 1) %}
                    {% if seat|string not in bookings %}
                    <option value="{{ seat }}">Seat {{ seat }}</option>
                    {% endif %}
                {% endfor %}
            </select>
        </label>

        <label>Full Name
            <input name="name" maxlength="80" required placeholder="Enter your name">
        </label>

        <label>Mobile Number
            <input name="mobile" required pattern="[0-9]{10}"
                   maxlength="10" minlength="10" placeholder="10-digit mobile number">
        </label>

        <label>User Type
            <select name="user_type" required>
                <option>Student</option>
                <option>Faculty</option>
            </select>
        </label>

        <label>Duration
            <select name="duration" required>
                <option value="1">1 Hour</option>
                <option value="2">2 Hours</option>
                <option value="3">3 Hours</option>
                <option value="4">4 Hours</option>
            </select>
        </label>

        <button class="submit" type="submit">Confirm Booking</button>
    </form>
</div>

<div class="panel" style="margin-top:22px">
    <h2>Current Bookings</h2>
    {% if bookings %}
        {% for seat, booking in bookings.items() %}
        <div class="booking">
            <strong>Seat {{ seat }} — {{ booking.name }}</strong><br>
            <small>
                {{ booking.user_type }} |
                {{ booking.duration }} hour(s) |
                Booked: {{ booking.time }}
            </small>
            <form method="POST" action="/cancel/{{ seat }}" style="margin-top:8px">
                <button class="cancel" type="submit">Cancel Booking</button>
            </form>
        </div>
        {% endfor %}
    {% else %}
        <p>No bookings yet. All seats are available.</p>
    {% endif %}
</div>

</div>
<footer>Smart Library Seat Management System | C++ & DSA Project</footer>
</body>
</html>
"""


@app.route("/")
def home():
    bookings = load_bookings()
    return render_template_string(
        PAGE,
        bookings=bookings,
        total=TOTAL_SEATS,
        occupied=len(bookings),
        available=TOTAL_SEATS - len(bookings)
    )


@app.route("/book", methods=["POST"])
def book():
    bookings = load_bookings()

    try:
        seat = int(request.form.get("seat", "0"))
        duration = int(request.form.get("duration", "0"))
    except ValueError:
        flash("Invalid seat number or duration.")
        return redirect(url_for("home"))

    name = request.form.get("name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    user_type = request.form.get("user_type", "")

    if not 1 <= seat <= TOTAL_SEATS:
        flash("Invalid seat number.")
    elif not name or len(name) > 80:
        flash("Please enter a valid name.")
    elif not mobile.isdigit() or len(mobile) != 10:
        flash("Enter a valid 10-digit mobile number.")
    elif duration not in (1, 2, 3, 4):
        flash("Please select a valid duration.")
    elif user_type not in ("Student", "Faculty"):
        flash("Invalid user type.")
    elif str(seat) in bookings:
        flash("Sorry, this seat is already booked.")
    else:
        bookings[str(seat)] = {
            "name": name,
            "mobile": mobile,
            "user_type": user_type,
            "duration": duration,
            "time": datetime.now().strftime("%d-%m-%Y %I:%M %p")
        }
        save_bookings(bookings)
        flash(f"Seat {seat} booked successfully!")

    return redirect(url_for("home"))


@app.route("/cancel/<int:seat>", methods=["POST"])
def cancel(seat):
    bookings = load_bookings()

    if str(seat) in bookings:
        del bookings[str(seat)]
        save_bookings(bookings)
        flash(f"Seat {seat} booking cancelled.")
    else:
        flash("This seat has no active booking.")

    return redirect(url_for("home"))


if __name__ == "__main__":
 app.run(host="0.0.0.0", port=5000, debug=False)