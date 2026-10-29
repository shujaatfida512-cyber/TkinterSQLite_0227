import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "prediction_diabetes.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                blood_sugar REAL NOT NULL,
                BMI REAL NOT NULL,
                parental_history TEXT NOT NULL,
                prediction_results TEXT NOT NULL
            )
        """)


def save_patient(patient_name, age, blood_sugar, bmi, parental_history, result):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO patients
                (patient_name, age, blood_sugar, BMI, parental_history, prediction_results)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_name, age, blood_sugar, bmi, parental_history, result))


def get_all_patients():
    with get_connection() as conn:
        return conn.execute("""
            SELECT id, patient_name, age, blood_sugar, BMI,
                   parental_history, prediction_results
            FROM patients
            ORDER BY id DESC
        """).fetchall()

def predict_risk(blood_sugar, bmi, parental_history):
    """Simple educational rules; not a medical diagnosis."""
    if blood_sugar >= 200:
        if bmi >= 30 or parental_history == "Yes":
            return "Very High"
        return "High"

    if 140 <= blood_sugar < 200:
        if bmi >= 30 and parental_history == "Yes":
            return "High"
        return "Moderate"

    if bmi >= 30:
        if parental_history == "Yes":
            return "Moderate"
        return "Alert"

    if parental_history == "Yes":
        return "Caution"

    return "Low"


RISK_COLORS = {
    "Low": "#2e7d32",
    "Caution": "#558b2f",
    "Alert": "#ef6c00",
    "Moderate": "#f9a825",
    "High": "#e65100",
    "Very High": "#c62828",
}

