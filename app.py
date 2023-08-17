import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import locale
from config import config
import flask_login


app = Flask(__name__)
app.secret_key = config['secret_key']

locale.setlocale(locale.LC_TIME, 'de_DE')

if not os.path.exists(config['upload_folder']):
    os.makedirs(config['upload_folder'])

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

users = config['users'] # WIP!!!

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',status='')

    email = request.form['email']
    if email in users and request.form['hashedPassword'] == users[email]['hashedPassword']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('redirect.html',status='Login erfolgreich.',page=url_for('admin'))

    return render_template('login.html',status='Das Passwort und/oder Nutzername ist nicht korrekt.')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login')), 401


def delete_old_files():
    # Fetch dates that are older than today and are valid dates
    old_dates = [
        file_name.split(".")[0] for file_name in os.listdir(config['upload_folder'])
        if file_name.endswith(".html") and not is_valid_date(file_name.split(".")[0])
    ]

    # Delete the corresponding HTML files
    for date in old_dates:
        file_path = os.path.join(config['upload_folder'], f"{date}.html")
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/')
def get_substitution_plans():
    delete_old_files()

    current_date = datetime.now().strftime('%Y-%m-%d')
    upcoming_dates = [file_name.split(".")[0] for file_name in os.listdir(config['upload_folder']) if file_name.endswith(".html") and file_name.split(".")[0] >= current_date]
    upcoming_dates.sort()

    # Get the HTML data for the current and next plans
    plan_data = []
    for date in upcoming_dates[:2]:
        file_path = os.path.join(config['upload_folder'], f"{date}.html")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                html_data = file.read()
            
            # Convert Date Format
            date = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %d.%m.%Y')  
            
            plan_data.append({'date': date, 'html': html_data})

    return render_template('public_page.html', plans=plan_data)

@app.route('/admin')
@flask_login.login_required
def admin():
    delete_old_files()
    return render_template('admin_page.html')

def is_valid_date(date):
    # Check if the date has the format 'YYYY-MM-DD'
    try:
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return False

    # Check if the parsed date is not in the past (before the current date)
    current_date = datetime.now().date()
    if parsed_date.date() < current_date:
        return False

    return True

@app.route('/upload', methods=['POST'])
def upload_file():
    date = request.form.get('date')
    if not date or not is_valid_date(date):
        return jsonify({'error': 'Datum muss existieren und darf nicht in der Vergangenheit liegen.'}), 400

    file = request.files['file']
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in {'html'}:
        file_path = os.path.join(config['upload_folder'], f"{date}.html")
        file.save(file_path)

        return jsonify({'message': 'Die Datei wurde erfolgreich hochgeladen.'}), 200
    return jsonify({'error': 'Falsches Dateiformat oder keine Datei angegeben.'}), 400

if __name__ == '__main__':
    # Use Gunicorn as the WSGI server
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=True)
