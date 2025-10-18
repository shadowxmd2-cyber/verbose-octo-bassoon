from flask import Flask, render_template_string, request, redirect, session
import requests

app = Flask(__name__)
app.secret_key = 'Gx7@pL92#kT!'

API_KEY = 'a893ab9c6efabc870d271e0f2c19016b'
TELEGRAM_BOT_TOKEN = '8106750141:AAGLbi-JZb0vhdMH3bMcbeX8L3IpdcJenxM'
TELEGRAM_CHAT_ID = '1720283336'

# Simple in-memory users
users = {}

# HTML templates embedded
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weather Check</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body { background: linear-gradient(to right, #00c6ff, #0072ff); color: #fff; }
.card { background: rgba(255,255,255,0.1); border-radius: 20px; }
.btn-custom { background: #ffcc00; color: #000; font-weight: bold; }
</style>
</head>
<body>
<div class="container py-5">
    <h1 class="text-center mb-4">Weather Check Portal</h1>
    <p class="text-center">Welcome, <b>{{ username }}</b></p>

    <div class="row justify-content-center mb-4">
        <div class="col-md-6">
            <form method="POST" class="d-flex gap-2">
                <input type="text" name="city" class="form-control" placeholder="Enter city" required>
                <button class="btn btn-custom">Check</button>
            </form>
        </div>
    </div>

    {% if weather %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card p-4 text-center mb-3 shadow-lg">
                <h2>{{ weather.name }}</h2>
                <p>{{ weather.weather[0].description }}</p>
                <h3>{{ weather.main.temp }}°C</h3>
                <p>Humidity: {{ weather.main.humidity }}% | Wind: {{ weather.wind.speed }} m/s</p>
                {% if rain %}
                    <p>🌧 Next rain expected at: {{ rain.dt_txt }}</p>
                {% endif %}
            </div>
        </div>
    </div>
    {% endif %}

    <div class="text-center mt-4">
        <a href="/logout" class="btn btn-light">Logout</a>
    </div>

    <p class="text-center mt-5">Developed by <b>Kavindu Induwara</b> & Team 🌍</p>
</div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body { background: linear-gradient(to right, #00c6ff, #0072ff); color: #fff; } .card { background: rgba(255,255,255,0.1); border-radius: 20px; }</style>
</head>
<body>
<div class="container py-5 d-flex justify-content-center">
    <div class="card p-4 col-md-4">
        <h2 class="text-center mb-3">Login</h2>
        <form method="POST" class="d-flex flex-column gap-2">
            <input type="text" name="username" class="form-control" placeholder="Username" required>
            <input type="password" name="password" class="form-control" placeholder="Password" required>
            <button class="btn btn-warning mt-2">Login</button>
        </form>
        <p class="text-center mt-2"><a href="/register" class="text-white">Register</a></p>
    </div>
</div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Register</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body { background: linear-gradient(to right, #00c6ff, #0072ff); color: #fff; } .card { background: rgba(255,255,255,0.1); border-radius: 20px; }</style>
</head>
<body>
<div class="container py-5 d-flex justify-content-center">
    <div class="card p-4 col-md-4">
        <h2 class="text-center mb-3">Register</h2>
        <form method="POST" class="d-flex flex-column gap-2">
            <input type="text" name="username" class="form-control" placeholder="Username" required>
            <input type="password" name="password" class="form-control" placeholder="Password" required>
            <button class="btn btn-warning mt-2">Register</button>
        </form>
        <p class="text-center mt-2"><a href="/login" class="text-white">Login</a></p>
    </div>
</div>
</body>
</html>
"""

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    weather_data = None
    rain_forecast = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            weather_data = requests.get(url).json()
            if 'coord' in weather_data:
                lat, lon = weather_data['coord']['lat'], weather_data['coord']['lon']
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
                forecast_data = requests.get(forecast_url).json()
                rain_forecast = next((f for f in forecast_data['list'] if 'rain' in f), None)
            # Telegram message
            msg = f"User {session['username']} checked weather for {city}"
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}")
    return render_template_string(INDEX_HTML, weather=weather_data, rain=rain_forecast, username=session['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            return "User already exists"
        users[username] = password
        return redirect('/login')
    return render_template_string(REGISTER_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['username'] = username
            return redirect('/')
        return "Invalid credentials"
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
