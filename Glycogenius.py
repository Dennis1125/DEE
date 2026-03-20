import customtkinter as ctk
import numpy as np
from datetime import datetime
import csv
import pyperclip
import random
from tkinter import messagebox

# --- THEME CONSTANTS ---
APP_NAME = "GLYCOGENIUS"
ACCENT_BLUE = "#00d2ff"      
ELECTRIC_PURPLE = "#7b61ff"  
BG_MAIN = "#0b0f19"          
BG_CARD = "#161e2d"          
BG_SIDEBAR = "#070a13"       
SUCCESS_GREEN = "#10b981"
WARNING_YELLOW = "#f59e0b"
DANGER_RED = "#ef4444"
STAR_GOLD = "#facc15"
NEON_BORDER = "#1e293b"      

class DiabetesPredictor:
    def __init__(self):
        self.medians = np.array([3.0, 117.0, 72.0, 23.0, 30.5, 32.0, 0.37, 29.0])
        self.stds = np.array([3.3, 31.9, 19.3, 15.9, 115.2, 7.8, 0.33, 11.7])
        self.intercept = -1.5
        self.weights = np.array([0.4, 1.1, -0.1, 0.1, 0.2, 0.7, 0.5, 0.2])
        self.features = ['pregnancies', 'glucose', 'blood_pressure', 'skin_thickness', 'insulin', 'bmi', 'dpf', 'age']

    def predict(self, data_dict):
        raw_values = []
        for i, feat in enumerate(self.features):
            val = data_dict[feat]
            try:
                raw_values.append(float(val) if str(val).strip() != "" else self.medians[i])
            except:
                raw_values.append(self.medians[i])
        
        scaled = (np.array(raw_values) - self.medians) / self.stds
        prob = 1 / (1 + np.exp(-(self.intercept + np.dot(scaled, self.weights))))
        
        if prob >= 0.65: return prob, "CRITICAL", DANGER_RED
        elif prob >= 0.35: return prob, "ELEVATED", WARNING_YELLOW
        return prob, "OPTIMAL", SUCCESS_GREEN

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} Ultra")
        self.geometry("1200x850")
        self.predictor = DiabetesPredictor()
        self.history = []
        self.last_result = None
        
        self.configure(fg_color=BG_MAIN)
        self.show_login()

    def update_clock(self):
        if hasattr(self, 'time_label'):
            now = datetime.now()
            self.time_label.configure(text=now.strftime("%H:%M:%S"))
            self.date_label.configure(text=now.strftime("%A, %d %B"))
            self.after(1000, self.update_clock)

    def show_login(self):
        for w in self.winfo_children(): w.destroy()
        frame = ctk.CTkFrame(self, width=400, height=540, corner_radius=30, fg_color=BG_CARD, border_width=2, border_color=NEON_BORDER)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="G", font=("Helvetica", 80, "bold"), text_color=ELECTRIC_PURPLE).pack(pady=(40, 0))
        ctk.CTkLabel(frame, text=APP_NAME, font=("Impact", 35), text_color="white").pack()
        self.u_entry = ctk.CTkEntry(frame, width=300, height=50, placeholder_text="Practitioner ID", fg_color=BG_MAIN)
        self.u_entry.pack(pady=10)
        self.p_entry = ctk.CTkEntry(frame, width=300, height=50, placeholder_text="Access Key", show="*", fg_color=BG_MAIN)
        self.p_entry.pack(pady=10)
        ctk.CTkButton(frame, text="SECURE LOGIN", command=self.show_main, width=300, height=55, corner_radius=15, fg_color=ELECTRIC_PURPLE).pack(pady=40)

    def show_main(self):
        for w in self.winfo_children(): w.destroy()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=BG_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(sidebar, text="GLYCOGENIUS", font=("Impact", 28), text_color=ACCENT_BLUE).pack(pady=40)
        
        self.time_label = ctk.CTkLabel(sidebar, text="", font=("Helvetica", 22, "bold"), text_color="white")
        self.time_label.pack()
        self.date_label = ctk.CTkLabel(sidebar, text="", font=("Helvetica", 13), text_color="#64748b")
        self.date_label.pack(pady=(0, 40))
        
        ctk.CTkButton(sidebar, text="EXPORT SESSION", fg_color=BG_CARD, command=self.export_to_csv).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="SYSTEM SHUTDOWN", fg_color="#1e293b", text_color=DANGER_RED, command=self.quit).pack(side="bottom", pady=20, padx=20, fill="x")
        self.update_clock()

        self.tab_view = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color=ELECTRIC_PURPLE)
        self.tab_view.grid(row=0, column=1, padx=30, pady=10, sticky="nsew")
        self.tab_diag = self.tab_view.add("Analysis Core")
        self.tab_logs = self.tab_view.add("Database")

        self.setup_diagnostic_tab()
        self.setup_logs_tab()

    def setup_diagnostic_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_diag, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # Patient Info Section
        p_frame = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=15)
        p_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(p_frame, text="PATIENT NAME:", text_color=ACCENT_BLUE).grid(row=0, column=0, padx=20, pady=15)
        self.p_name = ctk.CTkEntry(p_frame, width=250, placeholder_text="Enter Full Name", fg_color=BG_MAIN)
        self.p_name.grid(row=0, column=1, padx=10)
        
        ctk.CTkLabel(p_frame, text="CASE ID:", text_color=ACCENT_BLUE).grid(row=0, column=2, padx=20)
        self.p_id = ctk.CTkEntry(p_frame, width=150, fg_color=BG_MAIN)
        self.p_id.insert(0, f"GX-{random.randint(1000,9999)}")
        self.p_id.grid(row=0, column=3, padx=10)

        # Vitals Grid
        form = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=20, border_width=1, border_color=NEON_BORDER)
        form.pack(fill="x", pady=5)
        self.entries = {}
        fields = [("Pregnancies", "pregnancies"), ("Glucose", "glucose"), ("Blood Pressure", "blood_pressure"), 
                  ("Skin Thickness", "skin_thickness"), ("Insulin", "insulin"), ("BMI", "bmi"), 
                  ("Pedigree", "dpf"), ("Age", "age")]

        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 2)
            ctk.CTkLabel(form, text=label, text_color="#94a3b8").grid(row=row, column=col*2, padx=20, pady=12, sticky="e")
            e = ctk.CTkEntry(form, width=150, fg_color=BG_MAIN)
            e.grid(row=row, column=col*2+1, padx=20, pady=12)
            self.entries[key] = e

        # Action Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        ctk.CTkButton(btn_frame, text="START NEURAL SCAN", height=50, fg_color=ACCENT_BLUE, text_color=BG_MAIN, 
                      font=("Helvetica", 16, "bold"), command=self.run_prediction).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="CLEAR", width=100, height=50, fg_color="#334155", command=self.reset_form).pack(side="left", padx=5)

        # Result Card with Progress Bar
        self.res_card = ctk.CTkFrame(container, corner_radius=25, fg_color="#070a13", border_width=2, border_color=NEON_BORDER)
        self.res_card.pack(fill="x", pady=10)
        
        self.res_text = ctk.CTkLabel(self.res_card, text="SYSTEM READY", font=("Courier New", 22, "bold"), text_color="#334155")
        self.res_text.pack(pady=(20, 5))
        
        self.progress = ctk.CTkProgressBar(self.res_card, width=600, height=15, fg_color=BG_MAIN, progress_color=ACCENT_BLUE)
        self.progress.set(0)
        self.progress.pack(pady=10)

        # Stars
        star_frame = ctk.CTkFrame(self.res_card, fg_color="transparent")
        star_frame.pack(pady=15)
        self.star_btns = []
        for i in range(1, 6):
            b = ctk.CTkButton(star_frame, text="★", width=40, fg_color="transparent", font=("Helvetica", 28), text_color="#1e293b", hover=False, command=lambda x=i: self.set_rating(x))
            b.pack(side="left")
            self.star_btns.append(b)

    def setup_logs_tab(self):
        self.log_textbox = ctk.CTkTextbox(self.tab_logs, fg_color="#05070a", font=("Consolas", 14), text_color="#cbd5e1")
        self.log_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_textbox.insert("0.0", f"{'CASE ID':<10} | {'NAME':<15} | {'RISK':<10} | {'PROB':<8} | {'RANK'}\n" + "—"*70 + "\n")

    def reset_form(self):
        for entry in self.entries.values(): entry.delete(0, 'end')
        self.p_name.delete(0, 'end')
        self.p_id.delete(0, 'end')
        self.p_id.insert(0, f"GX-{random.randint(1000,9999)}")
        self.progress.set(0)
        self.res_text.configure(text="SYSTEM READY", text_color="#334155")

    def run_prediction(self):
        try:
            name = self.p_name.get() or "Unknown"
            cid = self.p_id.get() or "N/A"
            data = {k: v.get() for k, v in self.entries.items()}
            prob, risk, color = self.predictor.predict(data)
            
            # Update UI
            self.res_text.configure(text=f"{risk} RISK: {prob:.1%}", text_color=color)
            self.res_card.configure(border_color=color)
            self.progress.set(prob)
            self.progress.configure(progress_color=color)
            
            entry = {"id": cid, "name": name, "risk": risk, "prob": f"{prob:.1%}", "rating": 0}
            self.history.append(entry)
            self.last_result = entry
            self.refresh_logs()
        except:
            messagebox.showerror("Error", "Check vital inputs for non-numeric characters.")

    def set_rating(self, score):
        for i, b in enumerate(self.star_btns): b.configure(text_color=STAR_GOLD if i < score else "#1e293b")
        if self.last_result:
            self.last_result['rating'] = score
            self.refresh_logs()

    def refresh_logs(self):
        self.log_textbox.delete("3.0", "end")
        for item in self.history:
            stars = "★" * item['rating']
            row = f"{item['id']:<10} | {item['name']:<15} | {item['risk']:<10} | {item['prob']:<8} | {stars}\n"
            self.log_textbox.insert("end", row)

    def export_to_csv(self):
        if not self.history: return
        filename = f"Clinic_Export_{datetime.now().strftime('%H%M')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "risk", "prob", "rating"])
            writer.writeheader()
            writer.writerows(self.history)
        messagebox.showinfo("Exported", f"Data saved to {filename}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
