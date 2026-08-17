from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# Secret key for admin login session
app.secret_key = "car_showroom_secret_key"


# =========================
# DATABASE
# =========================

def create_database():

    connection = sqlite3.connect("showroom.db")

    # Bookings table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            car TEXT NOT NULL,
            booking_type TEXT NOT NULL
        )
    """)

    # Cars table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            price REAL NOT NULL,
            fuel TEXT NOT NULL,
            transmission TEXT NOT NULL,
            year INTEGER NOT NULL,
            image TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    connection = sqlite3.connect("showroom.db")
    connection.row_factory = sqlite3.Row

    cars_data = connection.execute(
        "SELECT * FROM cars"
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        cars=cars_data
    )

# =========================
# CARS
# =========================
@app.route("/cars")
def cars():

    connection = sqlite3.connect("showroom.db")
    connection.row_factory = sqlite3.Row

    cars_data = connection.execute(
        "SELECT * FROM cars"
    ).fetchall()

    connection.close()

    return render_template(
        "cars.html",
        cars=cars_data
    )

# =========================
# CAR DETAILS
# =========================

@app.route("/car-details/<int:car_id>")
def car_details(car_id):

    connection = sqlite3.connect("showroom.db")
    connection.row_factory = sqlite3.Row

    car = connection.execute(
        "SELECT * FROM cars WHERE id = ?",
        (car_id,)
    ).fetchone()

    connection.close()

    if car is None:
        return "Car not found", 404

    return render_template(
        "car_details.html",
        car=car
    )
# =========================
# =========================
# BOOKING
# =========================
# =========================
#
@app.route("/booking", methods=["GET", "POST"])
def booking():

    connection = sqlite3.connect("showroom.db")
    connection.row_factory = sqlite3.Row

    cars_data = connection.execute(
        "SELECT * FROM cars"
    ).fetchall()

    selected_car = request.args.get("car_id")

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        car = request.form["car"]
        booking_type = request.form["booking_type"]

        connection.execute("""
            INSERT INTO bookings
            (name, phone, email, car, booking_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            car,
            booking_type
        ))

        connection.commit()
        connection.close()

        return render_template(
            "booking.html",
            cars=cars_data,
            selected_car=None,
            message="Booking submitted successfully! 🚗"
        )

    connection.close()

    return render_template(
        "booking.html",
        cars=cars_data,
        selected_car=selected_car
    )
# =========================
# ADMIN LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Admin username and password
        if username == "admin" and password == "1234":

            session["admin"] = True

            return redirect("/admin")

        return render_template(
            "login.html",
            error="Invalid username or password ❌"
        )

    return render_template("login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    connection = sqlite3.connect("showroom.db")

    bookings = connection.execute(
        "SELECT * FROM bookings"
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        bookings=bookings
    )


# # =========================
# MANAGE CARS
# =========================

@app.route("/manage-cars")
def manage_cars():

    if not session.get("admin"):
        return redirect("/login")

    connection = sqlite3.connect("showroom.db")
    connection.row_factory = sqlite3.Row
    cars_data = connection.execute(
        "SELECT * FROM cars"
    ).fetchall()

    connection.close()

    return render_template(
        "manage_cars.html",
        cars=cars_data
    )


# =========================
# ADD CAR
# =========================


# =========================
# ADD CAR
# =========================

@app.route("/add-car", methods=["POST"])
def add_car():

    if not session.get("admin"):
        return redirect("/login")

    brand = request.form["brand"]
    model = request.form["model"]
    price = request.form["price"]
    fuel = request.form["fuel"]
    transmission = request.form["transmission"]
    year = request.form["year"]
    image = request.form["image"]

    connection = sqlite3.connect("showroom.db")

    connection.execute("""
        INSERT INTO cars
        (brand, model, price, fuel, transmission, year, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        brand,
        model,
        price,
        fuel,
        transmission,
        year,
        image
    ))

    connection.commit()
    connection.close()

    return redirect("/manage-cars")

# =========================
# MANAGE CARS
# =========================

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")


# =========================
# START APPLICATION
# =========================

# =========================
# ADMIN BOOKINGS
# =========================

@app.route("/admin-bookings")
def admin_bookings():

    if not session.get("admin"):
        return redirect("/login")

    connection = sqlite3.connect("showroom.db")
    connection.row_factory = sqlite3.Row

    bookings_data = connection.execute(
        "SELECT * FROM bookings ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "admin_bookings.html",
        bookings=bookings_data
    )

# =========================
# DELETE BOOKING
# =========================

@app.route("/delete-booking/<int:booking_id>", methods=["POST"])
def delete_booking(booking_id):

    if not session.get("admin"):
        return redirect("/login")

    connection = sqlite3.connect("showroom.db")

    connection.execute(
        "DELETE FROM bookings WHERE id = ?",
        (booking_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/admin-bookings")

if __name__ == "__main__":

    create_database()

    app.run(debug=True)