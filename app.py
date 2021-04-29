#!/usr/bin/python3
from flask import request, Flask, render_template, redirect, flash, session
import numpy as np
import pymysql
from passlib.hash import sha512_crypt

app = Flask(__name__)
app.secret_key = "b'J\xcb\x01V{/4\xab\x1e\xd5\xbd\xbb\x9b\xe2\xba\xc0'"
model, types, columns = 0, 0, 0


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    global types, columns
    price = 0
    if request.method == 'POST':
        area = request.form['area']
        BHK = request.form['BHK']
        sqft = request.form['sqft']
        house_type = request.form['type']
        price = predict_value(area, house_type, BHK, sqft)
    return render_template('predict.html', area=columns[3:], house_type=types, predict="active", price=price)

@app.route('/submit_data', methods=['GET', 'POST'])
def submit_data():
    if request.method == "GET":
        if 'username' in session:
            global types, columns
            return render_template('submit_data.html', area=columns[3:], house_type=types, sd="active")
        else:
            flash("User must be logged in to access that page.", 'alert')
            return redirect('/login')
    elif request.method == "POST":
        area = request.form['area']
        BHK = request.form['BHK']
        sqft = request.form['sqft']
        house_type = request.form['type']
        price = float(request.form['price'])

        connection, cursor = createConnection()
        executeQuery(f'INSERT INTO data VALUES(default, {BHK}, {sqft}, "{area}", "{house_type}", {price});', connection, cursor)
        
        flash('Data submitted successfully!', 'info')
        return redirect('/submit_data')
        

@app.route('/signup', methods=['GET', 'POST'])
def register():
    """Rendering and backend of the register page"""
    if request.method == 'POST':
        uname = request.form['uname'].strip().lower()
        email = request.form['email'].strip().lower()
        passwd = request.form['passwd'].strip()
        cpasswd = request.form['cpasswd'].strip()
        
        connection, cursor = createConnection()
        result = executeQuery(f'SELECT * FROM users WHERE username="{uname}"', connection, cursor)

        if result != ():
            flash('Username is taken!', 'error')
            return redirect('/signup')
        elif passwd != cpasswd:
            flash('Both passwords do not match', 'alert')
            return redirect('/signup')
        else:
            passwd = sha512_crypt.hash(passwd)
            executeQuery(f'INSERT INTO users values(default, "{uname}", "{passwd}", "{email}", "user");', connection, cursor)
            flash("Successfully registered!", 'info')
            return redirect('/signup')
    elif request.method == 'GET':
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rendering and backend of the login page"""
    if request.method == 'POST':
        uname = request.form['uname'].strip().lower()
        passwd = request.form['passwd'].strip()
        connection, cursor = createConnection()
        result = executeQuery(f'SELECT password FROM users WHERE username="{uname}";', connection, cursor)
        if result == ():
            flash("User not found!", "error")
            return redirect('/login')
        else:
            if sha512_crypt.verify(passwd, result[0][0]):
                flash("Successfully logged in!", "info")
                session['username'] = uname
                
                result = executeQuery(f"SELECT type FROM users WHERE username='{uname}'", connection, cursor)
                if result[0][0] == 'admin':
                    session['admin'] = uname

                return redirect('/login')
            else:
                flash("Wrong password", "error")
                return redirect('/login')
    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user from session"""
    session.pop('username', None)
    if 'admin' in session:
        session.pop('admin', None)
    flash("Successfully logged out!", "info")
    return redirect('/login')

@app.route('/display')
def display():
    if 'username' in session:
        connection, cursor = createConnection()
        result = executeQuery("SELECT * FROM data;", connection, cursor)
        return render_template('display.html', disp="active", data=result)
    else:
        flash("User must be logged in to access that page.", 'alert')
        return redirect('/login')

@app.route('/process', methods=['GET'])
def approve():
    action = request.args.get('action')
    row_id = request.args.get('id')
    connection, cursor = createConnection()
    if action == "accept":
        result = executeQuery("SELECT * FROM data WHERE id={}".format(row_id), connection, cursor)[0]
        result = ",".join(list(map(str, [result[3], result[4], result[1], result[2], result[-1], 'L'])))
        with open('static/data.csv', 'a') as f:
            f.write(result + '\n')
        flash('Successfully added the row into the database', 'info')
    elif action == "reject":
        flash('Data has been rejected successfully!', 'info')
    executeQuery("DELETE FROM data WHERE id={}".format(row_id), connection, cursor)
    return redirect('/display')


def predict_value(area: list, house_type: list, BHK: int, sqft: int) -> str:
    """Runs the ML model for given set of parameters and returns the predicted value"""
    global model, types, columns

    y = np.zeros(len(columns))
    y[:3] = types.index(house_type), BHK, sqft
    y[columns.index(area)] = 1

    price = model.predict(y.reshape(1, -1))
    return "{:.2f}".format(price[0])

def createConnection():
    """Returns connection and cursor for the database"""
    connection = pymysql.connect(
            host='localhost',
            user='root',
            passwd='1234',
            database='hpp')
    cursor = connection.cursor()
    return connection, cursor

def executeQuery(query: str, connection: object, cursor: object) -> tuple:
    """Executes the query for the given connection and cursor. At the end commits the changes to the database."""
    cursor.execute(query)
    connection.commit()
    return cursor.fetchall()

def load_data():
    import os
    import pickle
    global model, types, columns

    if not os.path.isfile('static/model.pickle'):
        import model_generation
        print("Model generated")

    model = pickle.load(open('static/model.pickle', 'rb'))
    types = open('static/types.csv').read().split(',')
    columns = open('static/unique.csv').read().split(',')

if __name__ == "__main__":
    load_data()
    app.run(debug=True)
