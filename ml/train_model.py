import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor

import joblib


# Load dataset
data = pd.read_csv(
    "dataset/student_mental_health_burnout.csv"
)


# Features
X = data[[
    'daily_study_hours',
    'daily_sleep_hours',
    'anxiety_score',
    'screen_time_hours'
]]


# Burnout target
y_burnout = data['burnout_level']


# Productivity score creation
# (custom calculated target)

data['productivity_score'] = (
    data['daily_study_hours'] * 10
    + data['attendance_percentage'] * 0.3
    + data['cgpa'] * 5
    - data['anxiety_score'] * 2
)

y_productivity = data['productivity_score']


# Split burnout data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_burnout,
    test_size=0.2,
    random_state=42
)


# Burnout Model
burnout_model = RandomForestClassifier(
    n_estimators=20,
    max_depth=5
)
burnout_model.fit(
    X_train,
    y_train
)


# Productivity Model
productivity_model = RandomForestRegressor(
    n_estimators=20,
    max_depth=5
)
productivity_model.fit(
    X,
    y_productivity
)


# Save models
joblib.dump(
    burnout_model,
    "burnout_model.pkl"
)

joblib.dump(
    productivity_model,
    "productivity_model.pkl"
)

print("Models trained successfully!")