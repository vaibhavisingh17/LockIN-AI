from flask import Flask, render_template, request, redirect, session, send_file
from database.db import db
from database.models import User, StudySession

import joblib
import pandas as pd

from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

app.secret_key = "studysense_secret_key"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root123@localhost/studysense_ai'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Load ML models
burnout_model = joblib.load("burnout_model.pkl")
productivity_model = joblib.load("productivity_model.pkl")


# -----------------------------------
# HOME PAGE
# -----------------------------------

@app.route('/')
def home():
    return render_template("signup.html")


# -----------------------------------
# SIGNUP
# -----------------------------------

@app.route('/signup', methods=['POST'])
def signup():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already exists"

    user = User(
        name=name,
        email=email,
        password=password
    )

    db.session.add(user)
    db.session.commit()

    return redirect('/login')


# -----------------------------------
# LOGIN PAGE
# -----------------------------------

@app.route('/login')
def login_page():
    return render_template("login.html")


# -----------------------------------
# LOGIN USER
# -----------------------------------

@app.route('/login_user', methods=['POST'])
def login_user():

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(
        email=email,
        password=password
    ).first()

    if user:

        session['user_id'] = user.id

        return redirect('/dashboard')

    else:
        return "Invalid email or password"


# -----------------------------------
# LOGOUT
# -----------------------------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# -----------------------------------
# DASHBOARD
# -----------------------------------

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    sessions = StudySession.query.filter_by(
        user_id=session['user_id']
    ).all()

    study_data = [s.study_hours for s in sessions]
    sleep_data = [s.sleep_hours for s in sessions]
    mood_data = [s.mood for s in sessions]
    distraction_data = [s.distractions for s in sessions]

    total_sessions = len(sessions)

    avg_study = 0
    avg_sleep = 0

    if total_sessions > 0:

        avg_study = round(
            sum(s.study_hours for s in sessions) / total_sessions,
            2
        )

        avg_sleep = round(
            sum(s.sleep_hours for s in sessions) / total_sessions,
            2
        )

    return render_template(
        'dashboard.html',
        sessions=sessions,
        study_data=study_data,
        sleep_data=sleep_data,
        mood_data=mood_data,
        distraction_data=distraction_data,
        total_sessions=total_sessions,
        avg_study=avg_study,
        avg_sleep=avg_sleep,
        alerts=[]
    )


# -----------------------------------
# TIMETABLE PAGE
# -----------------------------------

@app.route('/timetable')
def timetable_page():

    if 'user_id' not in session:
        return redirect('/login')

    timetable = session.get('timetable', [])

    return render_template(
        'timetable.html',
        timetable=timetable
    )


# -----------------------------------
# SUBMIT + ML PREDICTION
# -----------------------------------

@app.route('/submit', methods=['POST'])
def submit():

    if 'user_id' not in session:
        return redirect('/login')

    study_hours = float(request.form['study_hours'])
    sleep_hours = float(request.form['sleep_hours'])
    mood = int(request.form['mood'])
    distractions = int(request.form['distractions'])

    # Save study session
    study_session = StudySession(
        user_id=session['user_id'],
        study_hours=study_hours,
        sleep_hours=sleep_hours,
        mood=mood,
        distractions=distractions,
        created_at=datetime.now()
    )

    db.session.add(study_session)
    db.session.commit()

    # ML Input
    prediction_data = pd.DataFrame([{
        'daily_study_hours': study_hours,
        'daily_sleep_hours': sleep_hours,
        'anxiety_score': mood,
        'screen_time_hours': distractions
    }])

    # Predictions
    burnout_prediction = burnout_model.predict(
        prediction_data
    )

    productivity_prediction = productivity_model.predict(
        prediction_data
    )

    # -----------------------------------
    # SMART ALERT SYSTEM
    # -----------------------------------

    alerts = []

    if burnout_prediction[0] == "High":

        alerts.append(
            "⚠ High burnout risk detected"
        )

    if sleep_hours < 5:

        alerts.append(
            "⚠ Sleep levels critically low"
        )

    if distractions > 7:

        alerts.append(
            "⚠ High distraction pattern detected"
        )

    if mood < 4:

        alerts.append(
            "⚠ Mood trend indicates stress buildup"
        )

    if productivity_prediction[0] < 50:

        alerts.append(
            "⚠ Productivity levels dropping significantly"
        )

    if alerts == []:

        alerts.append(
            "✅ Your wellness indicators look healthy"
        )

    # -----------------------------------
    # AI TIMETABLE GENERATOR
    # -----------------------------------

    timetable = []

    if sleep_hours < 5:

        timetable.append("7:00 AM - Wake up and hydration")
        timetable.append("8:00 AM - Light revision session")
        timetable.append("9:00 AM - Breakfast and recovery break")

    else:

        timetable.append("6:00 AM - Morning exercise")
        timetable.append("7:00 AM - Deep focus study session")
        timetable.append("9:00 AM - Breakfast break")

    if study_hours >= 8:

        timetable.append("10:00 AM - High priority study block")
        timetable.append("12:00 PM - Long relaxation break")
        timetable.append("2:00 PM - Practice questions session")

    else:

        timetable.append("10:00 AM - Moderate study session")
        timetable.append("12:00 PM - Short break")
        timetable.append("2:00 PM - Revision session")

    if mood < 5:

        timetable.append("4:00 PM - Meditation / stress recovery")
        timetable.append("5:00 PM - Light study tasks")

    else:

        timetable.append("4:00 PM - Productive study sprint")
        timetable.append("6:00 PM - Skill improvement session")

    if distractions > 5:

        timetable.append("7:00 PM - Phone-free study session")
        timetable.append("8:00 PM - Digital detox break")

    else:

        timetable.append("7:00 PM - Revision and mock tests")

    if sleep_hours < 6:

        timetable.append("10:00 PM - Early sleep recovery")

    else:

        timetable.append("11:00 PM - Maintain healthy sleep schedule")

    # -----------------------------------
    # AI RECOMMENDATION ENGINE
    # -----------------------------------

    recommendation = ""

    if sleep_hours < 5:
        recommendation += "Increase sleep hours. "

    if distractions > 5:
        recommendation += "Reduce distractions during study sessions. "

    if mood < 5:
        recommendation += "Maintain better study-life balance. "

    if study_hours > 8:
        recommendation += "Avoid overstudying to prevent burnout. "

    if recommendation == "":
        recommendation = "Your study habits look balanced."

    # Store for session
    session['prediction'] = str(burnout_prediction[0])

    session['productivity'] = str(
        round(productivity_prediction[0], 2)
    )

    session['recommendation'] = recommendation

    session['timetable'] = timetable


    # Fetch sessions
    sessions = StudySession.query.filter_by(
        user_id=session['user_id']
    ).all()

    # Analytics
    study_data = [s.study_hours for s in sessions]
    sleep_data = [s.sleep_hours for s in sessions]
    mood_data = [s.mood for s in sessions]
    distraction_data = [s.distractions for s in sessions]

    total_sessions = len(sessions)

    avg_study = 0
    avg_sleep = 0

    if total_sessions > 0:

        avg_study = round(
            sum(s.study_hours for s in sessions) / total_sessions,
            2
        )

        avg_sleep = round(
            sum(s.sleep_hours for s in sessions) / total_sessions,
            2
        )

    return render_template(
        'dashboard.html',
        prediction=burnout_prediction[0],
        productivity=round(productivity_prediction[0], 2),
        recommendation=recommendation,
        timetable=timetable,
        alerts=alerts,
        sessions=sessions,
        study_data=study_data,
        sleep_data=sleep_data,
        mood_data=mood_data,
        distraction_data=distraction_data,
        total_sessions=total_sessions,
        avg_study=avg_study,
        avg_sleep=avg_sleep
    )


# -----------------------------------
# PDF REPORT
# -----------------------------------

@app.route('/download_report')
def download_report():

    pdf_file = "StudySense_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "StudySense AI Report",
            styles['Title']
        )
    )

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            f"Burnout Prediction: {session.get('prediction', 'N/A')}",
            styles['BodyText']
        )
    )

    content.append(
        Paragraph(
            f"Productivity Score: {session.get('productivity', 'N/A')}%",
            styles['BodyText']
        )
    )

    content.append(
        Paragraph(
            f"Recommendation: {session.get('recommendation', 'N/A')}",
            styles['BodyText']
        )
    )

    doc.build(content)

    return send_file(
        pdf_file,
        as_attachment=True
    )


# -----------------------------------
# RUN APP
# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)