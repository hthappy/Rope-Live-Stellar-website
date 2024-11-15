import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import hashlib
import uuid

def get_machine_code():
    machine_id = str(uuid.getnode())
    return hashlib.md5(machine_id.encode()).hexdigest()

class LicenseGenerator:
    def __init__(self, master):
        self.master = master
        master.title("License Generator")
        master.geometry("340x300")
        #在屏幕中间显示
        master.geometry("+{}+{}".format(master.winfo_screenwidth()//2-340//2, master.winfo_screenheight()//2-300//2))
        master.resizable(False, False)

        style = ttk.Style()
        style.theme_use('clam')

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        ttk.Label(main_frame, text="Machine Code:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.machine_code_entry = ttk.Entry(main_frame, width=40)
        self.machine_code_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(main_frame, text="Valid Days:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.valid_days_entry = ttk.Entry(main_frame, width=10)
        self.valid_days_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.valid_days_entry.insert(0, "30")  # Default value

        generate_button = ttk.Button(main_frame, text="Generate License Key", command=self.generate_license)
        generate_button.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(main_frame, text="Generated License Key:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.license_key_entry = ttk.Entry(main_frame, width=40, state='readonly')
        self.license_key_entry.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        copy_button = ttk.Button(main_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_button.grid(row=7, column=0, sticky=(tk.W, tk.E))

        for child in main_frame.winfo_children(): 
            child.grid_configure(padx=5)

    def generate_license(self):
        machine_code = self.machine_code_entry.get().strip()
        try:
            valid_days = int(self.valid_days_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")
            return

        if not machine_code:
            messagebox.showerror("Error", "Please enter a machine code.")
            return

        expiration_date = datetime.now() + timedelta(days=valid_days)
        expiration_date_str = expiration_date.strftime("%Y-%m-%d")
        
        secret_key = "your_secret_key_here"  # 替换为您的密钥
        activation_code = machine_code + expiration_date_str + hashlib.md5((machine_code + expiration_date_str + secret_key).encode()).hexdigest()

        self.license_key_entry.config(state='normal')
        self.license_key_entry.delete(0, tk.END)
        self.license_key_entry.insert(0, activation_code)
        self.license_key_entry.config(state='readonly')

    def copy_to_clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.license_key_entry.get())
        messagebox.showinfo("Success", "License key copied to clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LicenseGenerator(root)
    root.mainloop()
