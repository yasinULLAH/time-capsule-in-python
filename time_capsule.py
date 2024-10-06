import os
import subprocess
import pandas as pd
from cryptography.fernet import Fernet
import datetime
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def install(package):
    subprocess.call(['pip', 'install', package])

libraries = ['cryptography', 'pandas', 'matplotlib']
for lib in libraries:
    install(lib)

class SecureTimeCapsule:
    def __init__(self):
        self.entries = pd.DataFrame(columns=['Date', 'Content', 'OpenDate', 'IsOpened', 'Reflection'])
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def add_entry(self, content, open_date, reflection):
        date = datetime.datetime.now()
        encrypted_content = self.cipher.encrypt(content.encode()).decode()
        encrypted_reflection = self.cipher.encrypt(reflection.encode()).decode()
        self.entries = pd.concat([self.entries, pd.DataFrame({
            'Date': [date],
            'Content': [encrypted_content],
            'OpenDate': [open_date],
            'IsOpened': [False],
            'Reflection': [encrypted_reflection]
        })], ignore_index=True)

    def open_capsule(self, index):
        if datetime.datetime.now() >= self.entries.loc[index, 'OpenDate']:
            self.entries.loc[index, 'IsOpened'] = True
            return self.cipher.decrypt(self.entries.loc[index, 'Content'].encode()).decode()
        return "This capsule is not ready to be opened yet."

    def get_reflection_prompt(self):
        prompts = [
            "What's the most important thing you learned this year?",
            "What are you most grateful for right now?",
            "What's your biggest goal for the next year?",
            "What's a challenge you overcame recently?",
            "What's a memory you want to preserve from this moment?"
        ]
        return random.choice(prompts)

    def blast_from_past(self):
        opened_entries = self.entries[self.entries['IsOpened']]
        if not opened_entries.empty:
            random_entry = opened_entries.sample(n=1).iloc[0]
            content = self.cipher.decrypt(random_entry['Content'].encode()).decode()
            reflection = self.cipher.decrypt(random_entry['Reflection'].encode()).decode()
            return f"Date: {random_entry['Date']}\nContent: {content}\nReflection: {reflection}"
        return "No opened entries available."

    def save_capsule(self, filename):
        self.entries.to_csv(filename, index=False)

    def load_capsule(self, filename):
        self.entries = pd.read_csv(filename)

    def visualize_entries(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.entries['Date'], self.entries.index, marker='o')
        plt.title('Time Capsule Entries Over Time')
        plt.xlabel('Date')
        plt.ylabel('Entry Number')
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt.gcf()

class TimeCapsuleGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Personal Time Capsule Creator")
        self.capsule = SecureTimeCapsule()

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.master, text="Add Entry", command=self.add_entry_window).pack()
        tk.Button(self.master, text="Open Capsule", command=self.open_capsule_window).pack()
        tk.Button(self.master, text="Blast from the Past", command=self.blast_from_past).pack()
        tk.Button(self.master, text="Visualize Entries", command=self.visualize_entries).pack()
        tk.Button(self.master, text="Save Capsule", command=self.save_capsule).pack()
        tk.Button(self.master, text="Load Capsule", command=self.load_capsule).pack()

    def add_entry_window(self):
        window = tk.Toplevel(self.master)
        window.title("Add Entry")

        tk.Label(window, text="Content:").pack()
        content_entry = tk.Text(window, height=5, width=30)
        content_entry.pack()

        tk.Label(window, text="Open Date (YYYY-MM-DD):").pack()
        open_date_entry = tk.Entry(window)
        open_date_entry.pack()

        reflection_prompt = self.capsule.get_reflection_prompt()
        tk.Label(window, text=f"Reflection: {reflection_prompt}").pack()
        reflection_entry = tk.Text(window, height=3, width=30)
        reflection_entry.pack()

        tk.Button(window, text="Submit", command=lambda: self.submit_entry(content_entry.get("1.0", tk.END), open_date_entry.get(), reflection_entry.get("1.0", tk.END), window)).pack()

    def submit_entry(self, content, open_date, reflection, window):
        try:
            open_date = datetime.datetime.strptime(open_date, "%Y-%m-%d")
            self.capsule.add_entry(content, open_date, reflection)
            messagebox.showinfo("Success", "Entry added successfully!")
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

    def open_capsule_window(self):
        window = tk.Toplevel(self.master)
        window.title("Open Capsule")

        tk.Label(window, text="Entry Index:").pack()
        index_entry = tk.Entry(window)
        index_entry.pack()

        tk.Button(window, text="Open", command=lambda: self.open_capsule(int(index_entry.get()), window)).pack()

    def open_capsule(self, index, window):
        try:
            content = self.capsule.open_capsule(index)
            messagebox.showinfo("Capsule Content", content)
            window.destroy()
        except IndexError:
            messagebox.showerror("Error", "Invalid index.")

    def blast_from_past(self):
        content = self.capsule.blast_from_past()
        messagebox.showinfo("Blast from the Past", content)

    def visualize_entries(self):
        fig = self.capsule.visualize_entries()
        window = tk.Toplevel(self.master)
        window.title("Entry Visualization")
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def save_capsule(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if filename:
            self.capsule.save_capsule(filename)
            messagebox.showinfo("Success", "Capsule saved successfully!")

    def load_capsule(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.capsule.load_capsule(filename)
            messagebox.showinfo("Success", "Capsule loaded successfully!")

if __name__ == '__main__':
    root = tk.Tk()
    app = TimeCapsuleGUI(root)
    root.mainloop()