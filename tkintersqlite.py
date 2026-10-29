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

def validate_form():
    name = name_entry.get().strip()
    age_text = age_entry.get().strip()
    sugar_text = sugar_entry.get().strip()
    bmi_text = bmi_entry.get().strip()
    history = history_combo.get().strip()

    if not name:
        messagebox.showwarning("Invalid input", "Please enter the patient's name.")
        name_entry.focus_set()
        return None

    try:
        age = int(age_text)
        if not 1 <= age <= 120:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Invalid input", "Age must be a whole number from 1 to 120.")
        age_entry.focus_set()
        return None

    try:
        blood_sugar = float(sugar_text)
        if not 1 <= blood_sugar <= 1000:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Invalid input", "Blood sugar must be a number between 1 and 1000 mg/dL.")
        sugar_entry.focus_set()
        return None

    try:
        bmi = float(bmi_text)
        if not 10 <= bmi <= 100:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Invalid input", "BMI must be a number between 10 and 100.")
        bmi_entry.focus_set()
        return None

    if history not in ("Yes", "No"):
        messagebox.showwarning("Invalid input", "Please select parental history: Yes or No.")
        history_combo.focus_set()
        return None

    return name, age, blood_sugar, bmi, history


def clear_form():
    name_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    sugar_entry.delete(0, tk.END)
    bmi_entry.delete(0, tk.END)
    history_combo.set("")
    result_label.config(text="Prediction result will appear here.", fg="#263238")
    name_entry.focus_set()


def on_predict_and_save():
    data = validate_form()
    if data is None:
        return

    name, age, blood_sugar, bmi, history = data
    result = predict_risk(blood_sugar, bmi, history)

    result_label.config(
        text=f"Risk Level: {result}",
        fg=RISK_COLORS[result]
    )

    try:
        save_patient(name, age, blood_sugar, bmi, history, result)
    except sqlite3.Error as error:
        messagebox.showerror("Database error", f"Could not save patient data.\n{error}")
        return

    messagebox.showinfo(
        "Saved",
        f"Prediction completed and patient data saved.\n\n"
        f"Result: {result}\n\n"
        "This is an educational estimate, not a medical diagnosis."
    )


def view_data():
    records = get_all_patients()

    window = tk.Toplevel(root)
    window.title("Patient History")
    window.geometry("1000x420")
    window.transient(root)

    heading = tk.Label(
        window, text="Saved Patient History",
        font=("Arial", 15, "bold")
    )
    heading.pack(pady=10)

    columns = (
        "id", "patient_name", "age", "blood_sugar",
        "BMI", "parental_history", "prediction_results"
    )
    table_frame = tk.Frame(window)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
    scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal")

    history_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    scrollbar_y.config(command=history_table.yview)
    scrollbar_x.config(command=history_table.xview)

    headings = {
        "id": "ID",
        "patient_name": "Patient Name",
        "age": "Age",
        "blood_sugar": "Blood Sugar (mg/dL)",
        "BMI": "BMI",
        "parental_history": "Parental History",
        "prediction_results": "Prediction Result",
    }
    widths = {
        "id": 55, "patient_name": 180, "age": 65,
        "blood_sugar": 140, "BMI": 75,
        "parental_history": 130, "prediction_results": 150
    }

    for col in columns:
        history_table.heading(col, text=headings[col])
        history_table.column(col, width=widths[col], anchor="center")

    for record in records:
        history_table.insert("", tk.END, values=record)

    history_table.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    if not records:
        tk.Label(window, text="No patient records have been saved yet.").pack(pady=4)

    tk.Button(window, text="Close", command=window.destroy, width=12).pack(pady=8)

init_db()

root = tk.Tk()
root.title("Diabetes Risk Prediction")
root.geometry("620x570")
root.minsize(580, 540)
root.configure(bg="#f4f7fb")

title_label = tk.Label(
    root,
    text="Diabetes Risk Prediction",
    font=("Arial", 19, "bold"),
    bg="#f4f7fb",
    fg="#17365d"
)