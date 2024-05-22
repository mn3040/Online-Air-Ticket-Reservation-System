from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from flask_session import Session  # To handle server-side sessions
from functools import wraps
from mysql.connector import Error
from datetime import datetime, timedelta
import bcrypt


# def format_datetime(value, format='%Y-%m-%d %H:%M'):
#     """Format a datetime to a string in the given format."""
#     if value is None:
#         return ""
#     return value.strftime(format)


app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)




# app.jinja_env.filters['datetime'] = format_datetime


# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Air Ticket Reservation System"
)
cursor = db.cursor(dictionary=True)


# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def s_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_logged_in' not in session:
            flash('You need to be logged in to view this page.')
            return redirect(url_for('s_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
def home():
    if 'logged_in' in session:
        return render_template('home.html')
    return redirect(url_for('login'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#CUSTOMER LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_address = request.form['email_address']
        password = request.form['password']
        # Fetch the hashed password from the database for the given email address
        cursor.execute("SELECT password FROM Customer WHERE email_address = %s", (email_address,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session.clear()
            session['logged_in'] = True
            session['email_address'] = email_address 
            return redirect(url_for('home'))
        else:
            flash('Invalid email address or password')
    return render_template('login.html')



@app.route("/s_login", methods=['GET', 'POST'])
def s_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Fetch the hashed password from the database for the given username
        cursor.execute("SELECT password FROM Airline_Staff WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['staff_logged_in'] = True
            session['staff_username'] = username  # Save a distinct session variable for staff
            return redirect(url_for('s_home'))  # Redirect to staff home page
        else:
            flash('Invalid username or password')
    return render_template('s_login.html')


@app.route('/s_home')
@s_login_required
def s_home():
    if 'staff_logged_in' in session:
        return render_template('s_home.html')
    return redirect(url_for('s_login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email_address', None)
    return redirect(url_for('logout_page'))

@app.route('/s_logout')
def s_logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('logout_page'))

@app.route('/logout_page')
def logout_page():
    return render_template('logout_page.html')  

@app.route('/airlines', methods=['GET'])
def get_airlines():
    cursor.execute("SELECT * FROM Airline")
    airlines = cursor.fetchall()
    return render_template('airlines.html', airlines=airlines)

@app.route('/airports', methods=['GET'])
def get_airports():
    cursor.execute("SELECT * FROM Airport")
    airports = cursor.fetchall()
    return render_template('airports.html', airports=airports)


@app.route('/c_airlines', methods=['GET'])
@login_required
def get_c_airlines():
    cursor.execute("SELECT * FROM Airline")
    airlines = cursor.fetchall()
    return render_template('c_airlines.html', airlines=airlines)

@app.route('/c_airports', methods=['GET'])
@login_required
def get_c_airports():
    cursor.execute("SELECT * FROM Airport")
    airports = cursor.fetchall()
    return render_template('c_airports.html', airports=airports)


@app.route('/flights_results', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        flight_type = request.form.get('flight_type', 'one_way')
        departure_airport = request.form['departure_airport']
        arrival_airport = request.form['arrival_airport']
        departure_date = request.form['departure_date']

        base_query = """
            SELECT * FROM Flight
            WHERE departure_airport = %s
            AND arrival_airport = %s
            AND departure_date = %s
        """
        params = (departure_airport, arrival_airport, departure_date)

        if flight_type == 'round_trip':
            return_date = request.form['return_date']
            # Query for round-trip requires checking for both outbound and return flights
            cursor.execute(base_query, params)
            outbound_flights = cursor.fetchall()
            cursor.execute(base_query, (arrival_airport, departure_airport, return_date))
            return_flights = cursor.fetchall()
            return render_template('flights_results.html', outbound_flights=outbound_flights, return_flights=return_flights)
        else:
            # Handle one-way trip
            cursor.execute(base_query, params)
            flights = cursor.fetchall()
            return render_template('flights_results.html', flights=flights)

    return render_template('index.html')


@app.route('/status_results', methods=['GET', 'POST'])
def view_status():
    if request.method == 'POST':
        airline_name = request.form['airline_name']
        flight_number = request.form['flight_number']
        departure_date = request.form['departure_date']
        
        cursor.execute("""
            SELECT * FROM Flight 
            WHERE airline_name = %s 
            AND flight_number = %s 
            AND departure_date = %s
            """, (airline_name, flight_number, departure_date))
        
        flights = cursor.fetchall()
        return render_template('status_results.html', flights=flights)
    return render_template('index.html')

@app.route('/purchase_flight', methods=['GET', 'POST'])
@login_required
def purchase_flight():
    # Fetch all flights to display on both GET and POST requests
    cursor.execute("SELECT * FROM Flight")
    flights = cursor.fetchall()

    if request.method == 'POST':
        flight_number = request.form['flight_number']
        email_address = session.get('email_address')  # Assuming user's email is stored in the session when they logged in
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        card_type = request.form['card_type']
        card_number = request.form['card_number']
        name_on_card = request.form['name_on_card']
        expiration_date = request.form['expiration_date']
        date_of_birth = request.form['date_of_birth']
        purchase_date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            # First, get the next ticket_id
            cursor.execute("SELECT MAX(ticket_id) AS max_id FROM Ticket")
            max_id_result = cursor.fetchone()
            next_ticket_id = (max_id_result['max_id'] or 0) + 1

            # Retrieve the necessary flight information
            cursor.execute("""
                SELECT flight_number, departure_date, departure_time, airline_name, base_price_of_ticket
                FROM Flight 
                WHERE flight_number = %s
            """, (flight_number,))
            flight = cursor.fetchone()

            if flight:
                # Calculate the final ticket price
                calculated_ticket_price = flight['base_price_of_ticket']  # Placeholder for actual calculation

                # Insert the new ticket record into the Ticket table
                cursor.execute("""
                    INSERT INTO Ticket (ticket_id, flight_number, departure_date, departure_time, email_address,
                                        first_name, last_name, date_of_birth, calculated_ticket_price,
                                        card_type, card_number, name_on_card, expiration_date, purchase_date_and_time,
                                        airline_name) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_ticket_id, flight['flight_number'], flight['departure_date'], flight['departure_time'], email_address,
                      first_name, last_name, date_of_birth, calculated_ticket_price,
                      card_type, card_number, name_on_card, expiration_date, purchase_date_and_time,
                      flight['airline_name']))

                db.commit()
                flash('Flight purchased successfully!')
                return redirect(url_for('purchase_confirmed'))
            else:
                flash('Flight not found.')
        except Error as err:
            db.rollback()
            flash(f'An error occurred: {err}')

    # Always return the template with flights, handling both initial page load and form submission cases.
    return render_template('purchase_flight.html', flights=flights)


@app.route('/cancel_trip', methods=['GET', 'POST'])
@login_required
def cancel_flight():
    if request.method == 'POST':
        ticket_id = request.form['ticket_id']
        try:
            # Ensure the ticket is cancellable (check date and time conditions here if needed)
            cursor.execute("DELETE FROM Ticket WHERE ticket_id = %s", (ticket_id,))
            db.commit()
            flash('Trip cancelled successfully.')
        except Error as err:
            db.rollback()
            flash(f'An error occurred while cancelling the trip: {err}')
        return redirect(url_for('cancel_success'))

    # Fetch all tickets that are active and eligible for cancellation
    email_address = session['email_address']
    print("hello")
    print(email_address)
    cursor.execute("""
        SELECT * FROM Ticket  WHERE email_address = %s
        AND departure_date > CURDATE()
        ORDER BY departure_date
    """, (email_address,))
    tickets = cursor.fetchall()
    return render_template('cancel_trip.html', tickets=tickets)



"""Cancel Trip: Customer chooses a purchased ticket for a flight that will take place more than 24 hours in the future and cancel the purchase. After cancellation, the ticket will no longer belong to the customer. The ticket will be available again in the system and purchasable by other customers.
"""

@app.route('/ratings_and_comments', methods=['GET', 'POST'])
@login_required
def rate_flight():
    email_address = session.get('email_address')
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        # Data from form submission
        flight_number = request.form['flight_number']
        departure_date = request.form['departure_date']
        departure_time = request.form['departure_time']
        airline_name = request.form['airline_name']
        rating = request.form['rating']
        comment = request.form['comment']

        # Insert new rating into Review table
        cursor.execute("""
            INSERT INTO Review
            (flight_number, email_address, departure_date, departure_time, airline_name, comment, rating) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (flight_number, email_address, departure_date, departure_time, airline_name, comment, rating))
        db.commit()
        flash('Your feedback has been recorded.')

    # Fetch past flights and check if they have been rated
    cursor.execute("""
        SELECT t.ticket_id, t.flight_number, t.departure_date, t.departure_time, t.airline_name,
               r.rating, r.comment
        FROM Ticket t
        LEFT JOIN Review r ON t.flight_number = r.flight_number AND t.email_address = r.email_address AND t.departure_date = r.departure_date
        WHERE t.email_address = %s AND t.departure_date < CURDATE()
    """, (email_address,))
    past_flights = cursor.fetchall()

    return render_template('ratings_and_comments.html', past_flights=past_flights)

@app.route('/track_spending', methods=['GET', 'POST'])
@login_required
def track_spending():
    email_address = session.get('email_address')  # Adjust default as necessary

    if request.method == 'POST':
        # Fetch data based on user input for custom date range
        start_date = request.form['start_date']
        end_date = request.form['end_date']
    else:
        # Default view for the past year
        today = datetime.now().date()
        start_date = (today - timedelta(days=180)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

    # SQL to calculate total spending
    cursor.execute("""
        SELECT SUM(calculated_ticket_price) AS total_spent
        FROM Ticket
        WHERE email_address = %s AND purchase_date_and_time BETWEEN %s AND %s
    """, (email_address, start_date, end_date))
    total_spent = cursor.fetchone()['total_spent'] or 0

    # SQL to fetch month-wise spending
    cursor.execute("""
        SELECT EXTRACT(YEAR FROM purchase_date_and_time) AS year, EXTRACT(MONTH FROM purchase_date_and_time) AS month, SUM(calculated_ticket_price) AS monthly_spent
        FROM Ticket
        WHERE email_address = %s AND purchase_date_and_time >= %s AND purchase_date_and_time <= %s
        GROUP BY year, month
        ORDER BY year, month
    """, (email_address, start_date, end_date))
    monthly_spending = cursor.fetchall()

    return render_template('track_spending.html', total_spent=total_spent, monthly_spending=monthly_spending, start_date=start_date, end_date=end_date)



@app.route('/ratings_and_comments')
@login_required
def load_ratings_page():
    return render_template('ratings_and_comments.html')

@app.route('/purchase_confirmed')
@login_required
def purchase_confirmed():
    return render_template('purchase_confirmed.html')

@app.route('/cancel_success')
@login_required
def cancel_success():
    return render_template('cancel_success.html')


@app.route('/my_flights', methods=['GET'])
@login_required
def view_my_flights():
    email_address = session.get('email_address')
    if not email_address:
        flash('You must be logged in to view this page.')
        return redirect(url_for('login'))

    # Fetch tickets on both GET and POST if the page displays them after POST actions
    cursor.execute("""
        SELECT * FROM Ticket WHERE email_address = %s
        AND departure_date > CURDATE()
        ORDER BY departure_date
    """, (email_address,))
    tickets = cursor.fetchall()
    # print(tickets)
    return render_template('my_flights.html', tickets=tickets)

@app.route('/my_flights')
@login_required
def my_flights():
    return render_template('my_flights.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email_address = request.form['email_address']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        building_number = request.form['building_number']
        street_name = request.form['street_name']
        apartment_number = request.form['apartment_number']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        passport_number = request.form['passport_number']
        passport_expiration = request.form['passport_expiration']
        passport_country = request.form['passport_country']
        date_of_birth = request.form['date_of_birth']
        phone_number = request.form['phone_number']

        cursor = db.cursor()

        # Check if email already exists
        cursor.execute("SELECT email_address FROM Customer WHERE email_address = %s", (email_address,))
        if cursor.fetchone():
            flash('Email address already exists. Please use a different email.')
            return redirect(url_for('register'))  # Redirect to the registration page

        try:
            # Insert into Customer table
            sql_customer = """
                INSERT INTO Customer (email_address, first_name, last_name, password, 
                                      building_number, street_name, apartment_number, 
                                      city, state, zip_code, passport_number, passport_expiration, 
                                      passport_country, date_of_birth)
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
            # Notice the use of hashed_password.decode() since many SQL databases expect string data for VARCHAR
            cursor.execute(sql_customer, (email_address, first_name, last_name, 
                                          hashed_password.decode('utf-8'), building_number, street_name, 
                                          apartment_number, city, state, zip_code, 
                                          passport_number, passport_expiration, 
                                          passport_country, date_of_birth))

            # Insert into customer_phone_number table
            sql_phone = """
                INSERT INTO customer_phone_number (email_address, phone_number)
                VALUES (%s, %s)
                """
            cursor.execute(sql_phone, (email_address, phone_number))

            db.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except Error as err:
            db.rollback()
            flash(f'Error: {err}')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/s_register', methods=['GET', 'POST'])
def s_register():
    if request.method == 'POST':
        email_address = request.form['email_address']
        phone_number = request.form['phone_number']
        username = request.form['username']
        airline_name = request.form['airline_name']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Hash the password
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        
        cursor = db.cursor()

        # Check if username already exists
        cursor.execute("SELECT username FROM airline_staff WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username already exists. Please use a different username.')
            return redirect(url_for('s_register'))

        try:
            # Insert into airline_staff table
            sql_staff = """
                INSERT INTO airline_staff (username, airline_name, password, first_name, last_name, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_staff, (username, airline_name, hashed_password.decode('utf-8'), first_name, last_name, date_of_birth))
            
            # Insert into airline_staff_email_address table
            sql_email = """
                INSERT INTO airline_staff_email_address (email_address, username)
                VALUES (%s, %s)
            """
            cursor.execute(sql_email, (email_address, username))

            # Insert into airline_staff_phone_number table
            sql_phone = """
                INSERT INTO airline_staff_phone_number (phone_number, username)
                VALUES (%s, %s)
            """
            cursor.execute(sql_phone, (phone_number, username))
            
            db.commit()
            flash('Registration successful!')
            return redirect(url_for('s_login'))
        except Error as err:
            db.rollback()
            flash(f'Error: {err}')
            return redirect(url_for('s_register'))
    return render_template('s_register.html')


@app.route('/add_airplane', methods=['GET', 'POST'])
@s_login_required
def add_airplane():
    if request.method == 'POST':
        airplane_id_number = request.form['airplane_id_number']
        airline_name = request.form['airline_name']
        num_seats = request.form['num_seats']
        manufacturing_company = request.form['manufacturing_company']
        model_number = request.form['model_number']  
        manufacturing_date = request.form['manufacturing_date']

        # Check if email already exists
        cursor.execute("SELECT airplane_id_number FROM Airplane WHERE airplane_id_number = %s", (airplane_id_number,))
        if cursor.fetchone():
            flash('Airplane already exists')
            return redirect(url_for('add_airplane'))  
        try:
            # Insert into Customer table
            cursor.execute("""INSERT INTO Airplane (airplane_id_number, airline_name, num_seats, manufacturing_company, model_number, manufacturing_date)
                            VALUES (%s, %s, %s, %s, %s, %s)""",
                            (airplane_id_number, airline_name, num_seats, manufacturing_company, model_number, manufacturing_date))
            
            db.commit()
            flash('Airplane added!')
            return redirect(url_for('add_airplane'))
        except Error as err:
            db.rollback()
            flash(f'Error: {err}')
            return redirect(url_for('add_airplane'))

    cursor.execute("SELECT * FROM Airplane")
    airplanes = cursor.fetchall()
    return render_template('add_airplane.html', airplanes=airplanes)


@app.route('/add_airport', methods=['GET', 'POST'])
@s_login_required
def add_airport():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        country = request.form['country']
        city = request.form['city']
        num_terminals = request.form['num_terminals']
        airport_type = request.form['airport_type']  

        # Check if email already exists
        cursor.execute("SELECT code FROM Airport WHERE code = %s", (code,))
        if cursor.fetchone():
            flash('Airport already exists')
            return redirect(url_for('add_airport'))  
        try:
            # Insert into airport table
            cursor.execute("""INSERT INTO Airport (code, name, city, country, num_terminals, airport_type)
                            VALUES (%s, %s, %s,%s, %s, %s)""",
                            (code, name, city, country, num_terminals, airport_type))
            
            db.commit()
            flash('Airport added!')
            return redirect(url_for('add_airport'))
        except Error as err:
            db.rollback()
            flash(f'Error: {err}')
            return redirect(url_for('add_airport'))

    cursor.execute("SELECT * FROM Airport")
    airports = cursor.fetchall()
    return render_template('add_airport.html', airports=airports)

@app.route('/view_flight_ratings')
@s_login_required
def view_flight_ratings():
    cursor.execute("""
        SELECT flight_number, AVG(rating) AS average_rating, COUNT(rating) AS total_ratings
        FROM Review
        GROUP BY flight_number
        ORDER BY average_rating DESC
    """)
    flights = cursor.fetchall()

    detailed_ratings = {}
    for flight in flights:
        cursor.execute("""
            SELECT rating, comment, email_address
            FROM Review
            WHERE flight_number = %s
        """, (flight['flight_number'],))
        detailed_ratings[flight['flight_number']] = cursor.fetchall()

    return render_template('view_flight_ratings.html', flights=flights, detailed_ratings=detailed_ratings)


@app.route('/change_status', methods=['GET', 'POST'])
@s_login_required
def change_status():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        departure_date = request.form['departure_date']
        departure_time = request.form['departure_time']
        new_status = request.form['new_status']

        try:
            cursor.execute("""
                UPDATE Flight
                SET status = %s
                WHERE flight_number = %s AND departure_date = %s AND departure_time = %s
            """, (new_status, flight_number, departure_date, departure_time))
            db.commit()
            flash('Flight status updated successfully!')
        except Error as err:
            db.rollback()
            flash(f'Error updating flight status: {err}')

    # To display form and current flights
    cursor.execute("SELECT flight_number, departure_date, departure_time, status FROM Flight WHERE departure_date > CURDATE() ORDER BY departure_date, departure_time")
    flights = cursor.fetchall()
    return render_template('change_status.html', flights=flights)
 
@app.route('/change_status')
@s_login_required
def change_status_load():
    return render_template('change_status.html')

@app.route('/view_future_flights', methods=['GET', 'POST'])
@s_login_required
def view_flights():
    airline_name = request.form.get('airline_name')  # Assumes staff's airline name is stored in session
    # Default values for the filters
    start_date = request.form.get('start_date', datetime.now().date().strftime('%Y-%m-%d'))
    end_date = request.form.get('end_date', (datetime.now().date() + timedelta(days=30)).strftime('%Y-%m-%d'))
    departure_airport = request.form.get('departure_airport', '%')
    arrival_airport = request.form.get('arrival_airport', '%')

    query = """
        SELECT *
        FROM Flight f
        WHERE f.airline_name = %s AND f.departure_date BETWEEN %s AND %s
        AND f.departure_airport = %s AND f.arrival_airport = %s
        ORDER BY f.departure_date
    """
    cursor.execute(query, (airline_name, start_date, end_date, departure_airport, arrival_airport))
    flights = cursor.fetchall()

    flight_customer_details = {}
    for flight in flights:
        cursor.execute("""
            SELECT first_name, last_name, email_address
            FROM Ticket t
            WHERE t.flight_number = %s AND t.departure_date = %s
        """, (flight['flight_number'], flight['departure_date']))
        flight_customer_details[flight['flight_number']] = cursor.fetchall()

    return render_template('view_future_flights.html', flights=flights, flight_customer_details=flight_customer_details)


@app.route('/create_new_flights', methods=['GET', 'POST'])
@s_login_required
def create_new_flights():
    if request.method == 'POST':
        try:
            flight_number = request.form['flight_number']
            departure_airport = request.form['departure_airport']
            arrival_airport = request.form['arrival_airport']
            departure_date = request.form['departure_date']
            departure_time = request.form['departure_time']
            airplane_id_number = request.form['airplane_id_number']
            airline_name = request.form['airline_name']
            arrival_date = request.form['arrival_date']
            arrival_time = request.form['arrival_time']
            base_price_of_ticket = request.form['base_price_of_ticket']
            status = request.form['status']

            # Check airport compatibility
            cursor.execute("SELECT airport_type FROM Airport WHERE code = %s", (departure_airport,))
            dep_type = cursor.fetchone()
            cursor.execute("SELECT airport_type FROM Airport WHERE code = %s", (arrival_airport,))
            arr_type = cursor.fetchone()

            if dep_type is None or arr_type is None:
                flash("One of the airports does not exist.")
                return redirect(url_for('create_new_flights'))

            if dep_type['airport_type'] != arr_type['airport_type']:
                flash('Airports must both be either domestic or international.')
                return redirect(url_for('create_new_flights'))

            # Insert new flight
            cursor.execute("""
                INSERT INTO Flight (flight_number, departure_airport, arrival_airport, departure_date, departure_time, airplane_id_number, airline_name, arrival_date, arrival_time, base_price_of_ticket, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (flight_number, departure_airport, arrival_airport, departure_date, departure_time, airplane_id_number, airline_name, arrival_date, arrival_time, base_price_of_ticket, status))
            db.commit()
            flash('Flight created successfully!')
        except mysql.connector.Error as err:
            db.rollback()
            flash(f'Database error: {err}')
        except Exception as e:
            db.rollback()
            flash(f'An unexpected error occurred: {e}')
        return redirect(url_for('create_new_flights'))

    return render_template('create_new_flights.html')

@app.route('/view_revenue', methods=['GET'])
@s_login_required
def view_revenue():
    today = datetime.now()
    today = today.replace(minute=0,second=0,microsecond=0)
    print("today", today)

    last_month_start = (today - timedelta(days=30))
    last_month_start = last_month_start.replace(minute=0,second=0,microsecond=0)
    print("Last month start:", last_month_start)
    last_month_end = today


    last_year_start = (today - timedelta(days=365)).replace(minute=0,second=0,microsecond=0)
    print("Last year start:", last_year_start)

    last_year_end = today

    # Revenue for the last month
    cursor.execute("""
        SELECT SUM(calculated_ticket_price) AS revenue
        FROM Ticket
        WHERE purchase_date_and_time BETWEEN %s AND %s
    """, (last_month_start, last_month_end))
    last_month_revenue = cursor.fetchone()['revenue'] or 0
    print("last_month_revenue", last_month_revenue)

    # Revenue for the last year
    cursor.execute("""
        SELECT SUM(calculated_ticket_price) AS revenue
        FROM Ticket
        WHERE purchase_date_and_time BETWEEN %s AND %s
    """, (last_year_start, last_year_end))
    last_year_revenue = cursor.fetchone()['revenue'] or 0
    print("last_year_revenue", last_year_revenue)
    
    return render_template('view_revenue.html', last_month_revenue=last_month_revenue, last_year_revenue=last_year_revenue)

@app.route('/frequent_customers', methods=['GET', 'POST'])
@s_login_required
def frequent_customers():
    if request.method == 'POST':
        airline_name = request.form['airline_name']
        customer_email = request.form.get('customer_email')

        # Query to find the most frequent customer over the past year for the given airline
        query_most_frequent = """
            SELECT email_address, COUNT(*) as flight_count
            FROM Ticket WHERE airline_name = %s AND departure_date BETWEEN %s AND %s
            GROUP BY email_address
            ORDER BY flight_count DESC
            LIMIT 1
        """
        last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        today_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(query_most_frequent, (airline_name, last_year_date, today_date))
        most_frequent_customer = cursor.fetchone()

        # If a specific customer's email is submitted, fetch their flights
        if customer_email:
            flight_query = """
                SELECT t.*, f.departure_airport, f.arrival_airport, f.departure_date, f.departure_time, f.arrival_date, f.arrival_time, f.status
                FROM Ticket t
                JOIN Flight f ON t.flight_number = f.flight_number
                WHERE t.email_address = %s AND f.airline_name = %s
                ORDER BY f.departure_date DESC
            """
            cursor.execute(flight_query, (customer_email, airline_name))
            customer_flights = cursor.fetchall()
        else:
            customer_flights = None

    else:
        # No POST request, set initial values to None
        most_frequent_customer = None
        customer_flights = None

    return render_template('frequent_customers.html', most_frequent_customer=most_frequent_customer, customer_flights=customer_flights)


@app.route('/schedule_maintenance', methods=['GET', 'POST'])
@s_login_required
def schedule_maintenance():
    if request.method == 'POST':
        airplane_id = request.form['airplane_id']
        start_datetime = datetime.strptime(request.form['start_datetime'], '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(request.form['end_datetime'], '%Y-%m-%dT%H:%M')

        # Check for existing flights scheduled during the maintenance period
        cursor.execute("""
            SELECT * FROM Flight 
            WHERE airplane_id_number = %s AND 
                  (STR_TO_DATE(CONCAT(departure_date, ' ', departure_time), '%%Y-%%m-%%d %%H:%%i') BETWEEN %s AND %s)
        """, (airplane_id, start_datetime, end_datetime))
        flights = cursor.fetchall()
        
        if flights:
            flash('This airplane is scheduled for flights during the maintenance period.')
            return redirect(url_for('schedule_maintenance'))

        # Insert maintenance record
        cursor.execute("""
            INSERT INTO Maintenance (airplane_id_number, start_date_and_time, end_date_and_time)
            VALUES (%s, %s, %s)
        """, (airplane_id, start_datetime, end_datetime))
        db.commit()
        flash('Maintenance scheduled successfully.')
        return redirect(url_for('schedule_maintenance'))

    return render_template('schedule_maintenance.html')


if __name__ == '__main__':
    app.run('127.0.0.1', 5500, debug=True)

