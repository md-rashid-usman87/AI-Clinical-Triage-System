import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
import os
# Classical / Symbolic AI (Rule-Based Expert System   Knowledge Base   Inference Engine   Heuristic Risk Classification
class DatabaseManager:
    def __init__(self, db_name="clinical_triage_vault.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS triage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    patient_name TEXT,
                    age INTEGER,
                    gender TEXT,
                    vitals TEXT,
                    symptoms TEXT,
                    top_diagnosis TEXT,
                    confidence REAL,
                    risk_level TEXT
                )
            """)
            conn.commit()

    def save_record(self, name, age, gender, vitals_str, symptoms_str, diagnosis, confidence, risk):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO triage_logs (timestamp, patient_name, age, gender, vitals, symptoms, top_diagnosis, confidence, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ts, name, age, gender, vitals_str, symptoms_str, diagnosis, confidence, risk))
            conn.commit()

    def fetch_all_records(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, patient_name, age, top_diagnosis, confidence, risk_level FROM triage_logs ORDER BY id DESC")
            return cursor.fetchall()


class EnterpriseClinicalAI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Clinical Triage & Health Diagnostics Hub")
        self.root.geometry("1240x820")
        self.root.minsize(1120, 750)
        self.root.configure(bg="#0B132B")

        self.db = DatabaseManager()
        self.last_generated_report = ""

        # Comprehensive Clinical Knowledge Base
        self.knowledge_base = [
            {
                "condition": "Severe Acute Respiratory Syndrome (SARS-CoV / ARDS)",
                "symptoms": {"High Fever", "Dry Cough", "Dyspnea / Shortness of Breath", "Extreme Fatigue"},
                "vital_rules": {"spo2_max": 93, "temp_min": 101.0},
                "risk": "CRITICAL EMERGENCY",
                "color": "#EF4444",
                "badge_bg": "#7F1D1D",
                "action": "Immediate ICU isolation, continuous arterial SpO2 telemetry, arterial blood gas analysis."
            },
            {
                "condition": "Hypertensive Crisis & Vascular Strain",
                "symptoms": {"Severe Headache", "Chest Pain / Tightness", "Dizziness / Vertigo", "Blurred Vision"},
                "vital_rules": {"bp_sys_min": 170},
                "risk": "CRITICAL EMERGENCY",
                "color": "#EF4444",
                "badge_bg": "#7F1D1D",
                "action": "Administer IV antihypertensives under continuous hemodynamic monitoring. Prevent encephalopathy."
            },
            {
                "condition": "Acute Bronchial Asthma Exacerbation",
                "symptoms": {"Wheezing / Stridor", "Chest Pain / Tightness", "Dyspnea / Shortness of Breath", "Dry Cough"},
                "vital_rules": {"spo2_max": 94, "hr_min": 105},
                "risk": "HIGH RISK",
                "color": "#F97316",
                "badge_bg": "#7C2D12",
                "action": "Immediate nebulization with beta-2 agonists and oral/IV systemic corticosteroids."
            },
            {
                "condition": "Cardiovascular Sepsis / Tachycardic Shock",
                "symptoms": {"High Fever", "Extreme Fatigue", "Dizziness / Vertigo", "Nausea / Vomiting"},
                "vital_rules": {"hr_min": 115, "temp_min": 102.0},
                "risk": "HIGH RISK",
                "color": "#F97316",
                "badge_bg": "#7C2D12",
                "action": "Initiate IV broad-spectrum fluid resuscitation. Blood lactate assay and blood culture stat."
            },
            {
                "condition": "Severe Neurological Migraine / Hemrania",
                "symptoms": {"Severe Headache", "Nausea / Vomiting", "Photophobia / Light Sensitivity", "Dizziness / Vertigo"},
                "vital_rules": {},
                "risk": "MODERATE PRIORITY",
                "color": "#F59E0B",
                "badge_bg": "#78350F",
                "action": "Prescribe triptans/analgesics. Patient rest in sensory-isolated, low-stimulus room."
            },
            {
                "condition": "Acute Gastroenteritis with Dehydration",
                "symptoms": {"Abdominal Cramps", "Nausea / Vomiting", "Extreme Fatigue", "High Fever"},
                "vital_rules": {"hr_min": 100},
                "risk": "MODERATE PRIORITY",
                "color": "#F59E0B",
                "badge_bg": "#78350F",
                "action": "Electrolyte panel testing and aggressive oral/IV rehydration (Ringer's Lactate / ORS)."
            },
            {
                "condition": "Seasonal Upper Respiratory Tract Infection (URTI)",
                "symptoms": {"Sore Throat", "Runny Nose / Congestion", "Dry Cough", "High Fever"},
                "vital_rules": {},
                "risk": "LOW RISK",
                "color": "#10B981",
                "badge_bg": "#064E3B",
                "action": "Symptomatic treatment: antipyretics, saline gargles, decongestants. Self-limiting in 5-7 days."
            }
        ]

        self.symptoms_pool = [
            "High Fever", "Dry Cough", "Dyspnea / Shortness of Breath", "Severe Headache",
            "Chest Pain / Tightness", "Sore Throat", "Dizziness / Vertigo", "Extreme Fatigue",
            "Nausea / Vomiting", "Runny Nose / Congestion", "Abdominal Cramps", "Photophobia / Light Sensitivity",
            "Wheezing / Stridor", "Muscle / Joint Myalgia"
        ]
        self.symptom_vars = {}

        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background="#1C2541",
            foreground="#E2E8F0",
            fieldbackground="#1C2541",
            font=("Segoe UI", 9)
        )
        style.configure("Treeview.Heading",
            background="#0B132B",
            foreground="#38BDF8",
            font=("Segoe UI", 9, "bold")
        )
        style.map("Treeview", background=[("selected", "#2563EB")])

        style.configure("Triage.Horizontal.TProgressbar",
            troughcolor="#1C2541",
            background="#38BDF8",
            bordercolor="#0B132B"
        )

    def build_ui(self):
        # ---------------- 1. Top Enterprise Control Bar ----------------
        top_bar = tk.Frame(self.root, bg="#1C2541", height=75)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        brand_frame = tk.Frame(top_bar, bg="#1C2541")
        brand_frame.pack(side=tk.LEFT, padx=25, pady=10)

        tk.Label(
            brand_frame, text="⚕️ AI Clinical Triage & Diagnostic System",
            font=("Segoe UI", 16, "bold"), fg="#2FD8B3", bg="#1C2541"
        ).pack(anchor="w")

        tk.Label(
            brand_frame, text="Multimodal Forward-Chaining Inference | Physiological Vitals Correlation | SQLite Vault",
            font=("Segoe UI", 9), fg="#91B141", bg="#1C2541"
        ).pack(anchor="w")

        btn_box = tk.Frame(top_bar, bg="#1C2541")
        btn_box.pack(side=tk.RIGHT, padx=20, pady=12)

        tk.Button(
            btn_box, text="📁 Patient Audit Logs", font=("Segoe UI", 9, "bold"),
            bg="#3B82F6", fg="black", activebackground="#2563EB", cursor="hand2",
            relief=tk.FLAT, padx=12, pady=6, command=self.open_history_window
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_box, text="💾 Export Audit Report", font=("Segoe UI", 9, "bold"),
            bg="#12F848", fg="black", activebackground="#12F848", cursor="hand2",
            relief=tk.FLAT, padx=12, pady=6, command=self.export_report
        ).pack(side=tk.LEFT, padx=6)

        # ---------------- 2. Split Workspace ----------------
        workspace = tk.Frame(self.root, bg="#0B132B")
        workspace.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Left Column: Inputs (Patient Details, Vitals, Checkboxes)
        left_pane = tk.Frame(workspace, bg="#0B132B", width=460)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 15))

        # Card A: Demographics
        demo_card = tk.LabelFrame(
            left_pane, text=" 1. Patient Demographics ",
            font=("Segoe UI", 10, "bold"), fg="#F90606", bg="#1C2541", bd=1, relief=tk.SOLID
        )
        demo_card.pack(fill=tk.X, pady=(0, 10), ipady=5, padx=2)

        tk.Label(demo_card, text="Name:", font=("Segoe UI", 9, "bold"), fg="#FEFEFE", bg="#1C2541").grid(row=0, column=0, padx=10, pady=4, sticky="w")
        self.ent_name = tk.Entry(demo_card, font=("Segoe UI", 9), bg="#FEFFFF", fg="#000000", insertbackground="white", bd=1, relief=tk.SOLID, width=18)
        self.ent_name.grid(row=0, column=1, padx=4, pady=4)
        self.ent_name.insert(0, "Rashid Usman")

        tk.Label(demo_card, text="Age:", font=("Segoe UI", 9, "bold"), fg="#FEFFFF", bg="#1C2541").grid(row=0, column=2, padx=8, pady=4, sticky="w")
        self.ent_age = tk.Entry(demo_card, font=("Segoe UI", 9), bg="#FEFFFF", fg="#000000", insertbackground="white", bd=1, relief=tk.SOLID, width=6)
        self.ent_age.grid(row=0, column=3, padx=4, pady=4)
        self.ent_age.insert(0, "22")

        tk.Label(demo_card, text="Gender:", font=("Segoe UI", 9, "bold"), fg="#FEFFFF", bg="#1C2541").grid(row=1, column=0, padx=10, pady=4, sticky="w")
        self.combo_gender = ttk.Combobox(demo_card, values=["Male", "Female", "Other"], state="readonly", width=16)
        self.combo_gender.grid(row=1, column=1, padx=4, pady=4)
        self.combo_gender.current(0)

        # Card B: Physiological Vitals Telemetry
        vitals_card = tk.LabelFrame(
            left_pane, text=" 2. Physiological Vitals Telemetry ",
            font=("Segoe UI", 10, "bold"), fg="#F90606", bg="#1C2541", bd=1, relief=tk.SOLID
        )
        vitals_card.pack(fill=tk.X, pady=(0, 10), ipady=5, padx=2)

        tk.Label(vitals_card, text="Heart Rate (BPM):", font=("Segoe UI", 9), fg="#FEFFFF", bg="#1C2541").grid(row=0, column=0, padx=10, pady=4, sticky="w")
        self.ent_hr = tk.Entry(vitals_card, font=("Segoe UI", 9), bg="#0B132B", fg="#FEFFFF", width=8, insertbackground="white", bd=1)
        self.ent_hr.grid(row=0, column=1, padx=4, pady=4)
        self.ent_hr.insert(0, "82")

        tk.Label(vitals_card, text="SpO2 (% Saturation):", font=("Segoe UI", 9), fg="#FEFFFF", bg="#1C2541").grid(row=0, column=2, padx=10, pady=4, sticky="w")
        self.ent_spo2 = tk.Entry(vitals_card, font=("Segoe UI", 9), bg="#0B132B", fg="#FEFFFF", width=8, insertbackground="white", bd=1)
        self.ent_spo2.grid(row=0, column=3, padx=4, pady=4)
        self.ent_spo2.insert(0, "98")

        tk.Label(vitals_card, text="Systolic BP (mmHg):", font=("Segoe UI", 9), fg="#FEFFFF", bg="#1C2541").grid(row=1, column=0, padx=10, pady=4, sticky="w")
        self.ent_bp = tk.Entry(vitals_card, font=("Segoe UI", 9), bg="#0B132B", fg="#FEFFFF", width=8, insertbackground="white", bd=1)
        self.ent_bp.grid(row=1, column=1, padx=4, pady=4)
        self.ent_bp.insert(0, "120")

        tk.Label(vitals_card, text="Temp (°F):", font=("Segoe UI", 9), fg="#FEFFFF", bg="#1C2541").grid(row=1, column=2, padx=10, pady=4, sticky="w")
        self.ent_temp = tk.Entry(vitals_card, font=("Segoe UI", 9), bg="#0B132B", fg="#FEFFFF", width=8, insertbackground="white", bd=1)
        self.ent_temp.grid(row=1, column=3, padx=4, pady=4)
        self.ent_temp.insert(0, "98.6")

        # Card C: Symptom Check-Matrix
        sym_card = tk.LabelFrame(
            left_pane, text=" 3. Observed Pathological Signs ",
            font=("Segoe UI", 10, "bold"), fg="#F90606", bg="#1C2541", bd=1, relief=tk.SOLID
        )
        sym_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10), ipady=5, padx=2)

        # Scrollable symptom list container
        sym_canvas = tk.Canvas(sym_card, bg="#1C2541", highlightthickness=0)
        sym_scroll = ttk.Scrollbar(sym_card, orient="vertical", command=sym_canvas.yview)
        scrollable_frame = tk.Frame(sym_canvas, bg="#1C2541")

        scrollable_frame.bind("<Configure>", lambda e: sym_canvas.configure(scrollregion=sym_canvas.bbox("all")))
        sym_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        sym_canvas.configure(yscrollcommand=sym_scroll.set)

        sym_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        sym_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for sym in self.symptoms_pool:
            var = tk.BooleanVar(value=False)
            self.symptom_vars[sym] = var
            chk = tk.Checkbutton(
                scrollable_frame, text=sym, variable=var,
                font=("Segoe UI", 9), fg="#F1F5F9", bg="#1C2541",
                activebackground="#1C2541", activeforeground="#38BDF8",
                selectcolor="#0B132B", cursor="hand2"
            )
            chk.pack(anchor="w", padx=10, pady=2)

        # Action Trigger
        tk.Button(
            left_pane, text="🚀 EXECUTE MULTIMODAL INFERENCE", font=("Segoe UI", 11, "bold"),
            bg="#2563EB", fg="white", activebackground="#1D4ED8", cursor="hand2",
            relief=tk.FLAT, pady=8, command=self.process_inference
        ).pack(fill=tk.X, pady=(0, 4))

        tk.Button(
            left_pane, text="Reset Fields", font=("Segoe UI", 9),
            bg="#5386CD", fg="#FFFFFF", activebackground="#475569", cursor="hand2",
            relief=tk.FLAT, pady=4, command=self.reset_all
        ).pack(fill=tk.X)

        # Right Column: Diagnostic & Analytical Workspace
        right_pane = tk.Frame(workspace, bg="#1C2541", bd=1, relief=tk.SOLID)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Analytical KPI Dashboard Strip
        kpi_strip = tk.Frame(right_pane, bg="#161F38", height=90)
        kpi_strip.pack(fill=tk.X, padx=12, pady=12)

        # Confidence Card
        c_box = tk.Frame(kpi_strip, bg="#0B132B", padx=15, pady=8, bd=1, relief=tk.SOLID)
        c_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        tk.Label(c_box, text="DIAGNOSTIC CERTAINTY", font=("Segoe UI", 8, "bold"), fg="#F90606", bg="#0B132B").pack(anchor="w")
        self.lbl_confidence = tk.Label(c_box, text="0.0%", font=("Segoe UI", 24, "bold"), fg="#38BDF8", bg="#0B132B")
        self.lbl_confidence.pack(anchor="w")

        # Triage Priority Card
        p_box = tk.Frame(kpi_strip, bg="#0B132B", padx=15, pady=8, bd=1, relief=tk.SOLID)
        p_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
        tk.Label(p_box, text="TRIAGE CLASSIFICATION", font=("Segoe UI", 8, "bold"), fg="#F90606", bg="#0B132B").pack(anchor="w")
        self.lbl_risk_badge = tk.Label(p_box, text="STANDBY", font=("Segoe UI", 12, "bold"), fg="#94A3B8", bg="#1C2541", padx=8, pady=3)
        self.lbl_risk_badge.pack(anchor="w", pady=(4, 0))

        # Vitals Anomaly Indicator
        v_box = tk.Frame(kpi_strip, bg="#0B132B", padx=15, pady=8, bd=1, relief=tk.SOLID)
        v_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))
        tk.Label(v_box, text="VITALS DERANGEMENT", font=("Segoe UI", 8, "bold"), fg="#F90606", bg="#0B132B").pack(anchor="w")
        self.lbl_vitals_status = tk.Label(v_box, text="NORMAL", font=("Segoe UI", 12, "bold"), fg="#10B981", bg="#0B132B")
        self.lbl_vitals_status.pack(anchor="w", pady=(4, 0))

        # Progress bar
        self.prog_bar = ttk.Progressbar(right_pane, style="Triage.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.prog_bar.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Differential Diagnosis Table
        diff_frame = tk.LabelFrame(
            right_pane, text=" Differential Diagnoses Hierarchy (Ranked by Evidence Overlap) ",
            font=("Segoe UI", 9, "bold"), fg="#F90606", bg="#1C2541", bd=1, relief=tk.SOLID
        )
        diff_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        self.tree = ttk.Treeview(diff_frame, columns=("Rank", "Condition", "Confidence", "Action Risk"), show="headings", height=3)
        self.tree.heading("Rank", text="#")
        self.tree.heading("Condition", text="Clinical Condition")
        self.tree.heading("Confidence", text="Score (%)")
        self.tree.heading("Action Risk", text="Triage Level")
        self.tree.column("Rank", width=35, anchor="center")
        self.tree.column("Condition", width=290, anchor="w")
        self.tree.column("Confidence", width=85, anchor="center")
        self.tree.column("Action Risk", width=140, anchor="center")
        self.tree.pack(fill=tk.X, padx=8, pady=6)

        # Monospace Clinical Audit Terminal
        term_frame = tk.LabelFrame(
            right_pane, text=" Comprehensive Clinical Audit Log & Triage Directive ",
            font=("Segoe UI", 9, "bold"), fg="#F90606", bg="#1C2541", bd=1, relief=tk.SOLID
        )
        term_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.txt_terminal = tk.Text(
            term_frame, font=("Consolas", 9), bg="#070D1F", fg="#E2E8F0",
            bd=0, padx=10, pady=10, wrap=tk.WORD, insertbackground="white"
        )
        self.txt_terminal.pack(fill=tk.BOTH, expand=True)

    def analyze_vitals(self, hr, spo2, bp_sys, temp):
        anomalies = []
        is_critical = False

        if spo2 < 92:
            anomalies.append(f"Severe Hypoxemia (SpO2: {spo2}%)")
            is_critical = True
        elif spo2 < 95:
            anomalies.append(f"Mild Hypoxemia (SpO2: {spo2}%)")

        if bp_sys >= 170:
            anomalies.append(f"Severe Hypertension Stage-3 ({bp_sys} mmHg)")
            is_critical = True
        elif bp_sys >= 140:
            anomalies.append(f"Pre-Hypertension Stage-1 ({bp_sys} mmHg)")

        if hr >= 120:
            anomalies.append(f"Critical Tachycardia ({hr} BPM)")
            is_critical = True
        elif hr >= 100:
            anomalies.append(f"Elevated Tachycardia ({hr} BPM)")

        if temp >= 102.5:
            anomalies.append(f"Hyperpyrexia ({temp} °F)")
            is_critical = True
        elif temp >= 100.4:
            anomalies.append(f"Pyrexia/Fever ({temp} °F)")

        return anomalies, is_critical

    def process_inference(self):
        name = self.ent_name.get().strip()
        age_str = self.ent_age.get().strip()
        gender = self.combo_gender.get()

        if not name or not age_str:
            messagebox.showwarning("Validation Error", "Patient Name and Age are required fields.")
            return

        try:
            age = int(age_str)
            hr = float(self.ent_hr.get())
            spo2 = float(self.ent_spo2.get())
            bp_sys = float(self.ent_bp.get())
            temp = float(self.ent_temp.get())
        except ValueError:
            messagebox.showerror("Format Error", "Vitals and Age must be numeric values.")
            return

        selected_symptoms = {sym for sym, var in self.symptom_vars.items() if var.get()}
        if not selected_symptoms:
            messagebox.showwarning("Observation Warning", "Please tick at least one pathological symptom.")
            return

        # 1. Evaluate Vitals Anomalies
        vitals_anomalies, vital_critical_flag = self.analyze_vitals(hr, spo2, bp_sys, temp)

        # 2. Multi-Condition Ranking Inference
        ranked_diagnoses = []
        for rule in self.knowledge_base:
            req = rule["symptoms"]
            matched = selected_symptoms.intersection(req)
            score = (len(matched) / len(req)) * 100.0

            # Vitals Cross-Rule Weighting
            vr = rule["vital_rules"]
            if "spo2_max" in vr and spo2 <= vr["spo2_max"]:
                score += 15.0
            if "temp_min" in vr and temp >= vr["temp_min"]:
                score += 10.0
            if "bp_sys_min" in vr and bp_sys >= vr["bp_sys_min"]:
                score += 20.0
            if "hr_min" in vr and hr >= vr["hr_min"]:
                score += 10.0

            score = min(100.0, score)
            ranked_diagnoses.append((score, rule))

        ranked_diagnoses.sort(key=lambda x: x[0], reverse=True)
        top_score, top_rule = ranked_diagnoses[0]

        # Override triage level if vitals are critical
        if vital_critical_flag and top_score > 35.0:
            final_risk = "CRITICAL EMERGENCY"
            final_color = "#EF4444"
            final_badge = "#7F1D1D"
        else:
            final_risk = top_rule["risk"] if top_score >= 45.0 else "INCONCLUSIVE / LOW"
            final_color = top_rule["color"] if top_score >= 45.0 else "#10B981"
            final_badge = top_rule["badge_bg"] if top_score >= 45.0 else "#064E3B"

        # 3. Update Visual KPIs
        self.lbl_confidence.config(text=f"{top_score:.1f}%")
        self.prog_bar['value'] = top_score
        self.lbl_risk_badge.config(text=f" {final_risk} ", fg=final_color, bg=final_badge)

        if vitals_anomalies:
            self.lbl_vitals_status.config(text="ANOMALY DETECTED", fg="#EF4444")
        else:
            self.lbl_vitals_status.config(text="ALL NORMAL", fg="#10B981")

        # 4. Populate Differential Hierarchy Table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, (sc, item_rule) in enumerate(ranked_diagnoses[:3], start=1):
            self.tree.insert("", "end", values=(i, item_rule["condition"], f"{sc:.1f}%", item_rule["risk"]))

        # 5. Build Comprehensive Clinical Audit Report
        vitals_summary = f"HR: {hr} BPM | SpO2: {spo2}% | Systolic: {bp_sys} mmHg | Temp: {temp} °F"
        symptoms_summary = ", ".join(sorted(selected_symptoms))

        report = []
        report.append("================================================================================")
        report.append(f" NEURO-TRIAGE CLINICAL AUDIT REPORT | {name.upper()} (AGE: {age} | {gender.upper()})")
        report.append("================================================================================")
        report.append(f"Assessment Timestamp    : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Recorded Vitals         : {vitals_summary}")
        report.append(f"Observed Pathology      : {symptoms_summary}\n")

        report.append("[PHYSIOLOGICAL VITALS SCREENING]")
        if vitals_anomalies:
            for anom in vitals_anomalies:
                report.append(f"  ! ALERT: {anom}")
        else:
            report.append("  * Vitals within acceptable physiological baseline.")
        report.append("")

        report.append("[PRIMARY AI DIAGNOSTIC IMPRESSION]")
        report.append(f"  Condition : {top_rule['condition'] if top_score >= 40.0 else 'Non-Specific Symptom Complex'}")
        report.append(f"  Certainty : {top_score:.1f}% | Assessed Risk: {final_risk}\n")

        report.append("[ACTIONABLE CLINICAL MANAGEMENT DIRECTIVE]")
        report.append(f"  Directive : {top_rule['action'] if top_score >= 40.0 else 'Advise outpatient consultation and clinical observation.'}\n")

        report.append("================================================================================")
        report.append("* Disclaimer: Automated Decision Support Engine for Clinical Academic Triage.")

        self.last_generated_report = "\n".join(report)
        self.txt_terminal.delete("1.0", tk.END)
        self.txt_terminal.insert(tk.END, self.last_generated_report)

        # 6. Database Storage
        self.db.save_record(
            name, age, gender, vitals_summary, symptoms_summary,
            top_rule['condition'] if top_score >= 40.0 else 'Inconclusive',
            top_score, final_risk
        )

    def export_report(self):
        if not self.last_generated_report:
            messagebox.showwarning("Export Void", "Please run an inference assessment before exporting.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")],
            initialfile=f"Clinical_Triage_{self.ent_name.get().strip().replace(' ', '_')}.txt"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.last_generated_report)
            messagebox.showinfo("Export Successful", f"Patient clinical report successfully archived to:\n{file_path}")

    def open_history_window(self):
        hist_win = tk.Toplevel(self.root)
        hist_win.title("Patient Clinical Audit Vault (SQLite3 Records)")
        hist_win.geometry("900x450")
        hist_win.configure(bg="#0B132B")

        tk.Label(
            hist_win, text="Archived Clinical Triage Evaluations",
            font=("Segoe UI", 12, "bold"), fg="#38BDF8", bg="#0B132B"
        ).pack(pady=10)

        cols = ("ID", "Timestamp", "Name", "Age", "Top Diagnosis", "Confidence", "Risk")
        hist_tree = ttk.Treeview(hist_win, columns=cols, show="headings")

        for c in cols:
            hist_tree.heading(c, text=c)

        hist_tree.column("ID", width=40, anchor="center")
        hist_tree.column("Timestamp", width=140, anchor="center")
        hist_tree.column("Name", width=140, anchor="w")
        hist_tree.column("Age", width=50, anchor="center")
        hist_tree.column("Top Diagnosis", width=260, anchor="w")
        hist_tree.column("Confidence", width=90, anchor="center")
        hist_tree.column("Risk", width=140, anchor="center")

        records = self.db.fetch_all_records()
        for r in records:
            hist_tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], f"{r[5]:.1f}%", r[6]))

        hist_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def reset_all(self):
        for var in self.symptom_vars.values():
            var.set(False)
        self.lbl_confidence.config(text="0.0%")
        self.prog_bar['value'] = 0
        self.lbl_risk_badge.config(text="STANDBY", fg="#94A3B8", bg="#1C2541")
        self.lbl_vitals_status.config(text="NORMAL", fg="#10B981")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.txt_terminal.delete("1.0", tk.END)
        self.last_generated_report = ""

if __name__ == "__main__":
    root = tk.Tk()
    app = EnterpriseClinicalAI(root)
    root.mainloop()