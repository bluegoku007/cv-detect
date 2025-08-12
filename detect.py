import re
import spacy
import pdfplumber
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

logging.getLogger("pdfminer").setLevel(logging.ERROR)
nlp = spacy.load("fr_core_news_sm")

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def count_keyword(text, keyword):
    return len(re.findall(rf"\b{keyword}\b", text, re.IGNORECASE))

def detect_name_with_fallback(text):
    false_positives = {"linkedin", "github", "kubernetes", "docker", "azure", "html", "css"}
    doc = nlp(text)
    candidates = [ent.text for ent in doc.ents if ent.label_ == "PER" and ent.text.lower() not in false_positives]

    if candidates:
        for cand in candidates:
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", cand):
                return cand

    for line in text.split("\n"):
        line = line.strip()
        if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", line) and line.lower() not in false_positives:
            return line

    return None

def open_folder():
    folderpath = filedialog.askdirectory(title="Select folder containing CV PDFs")
    if not folderpath:
        return
    try:
        set_processing(True)
        root.update_idletasks()

        keywords = [kw.strip() for kw in keyword_entry.get().split(",") if kw.strip()]
        if not keywords:
            messagebox.showwarning("Input needed", "Please enter at least one keyword.")
            set_processing(False)
            return
        
        pdf_files = [f for f in os.listdir(folderpath) if f.lower().endswith(".pdf")]
        if not pdf_files:
            messagebox.showinfo("No PDFs found", "No PDF files found in the selected folder.")
            set_processing(False)
            return
        
        all_results = []
        for pdf_file in pdf_files:
            full_path = os.path.join(folderpath, pdf_file)
            cv_text = extract_text_from_pdf(full_path)
            name = detect_name_with_fallback(cv_text)

            has_keywords = any(count_keyword(cv_text, kw) > 0 for kw in keywords)
            name_display = (name or "Not found")
            if has_keywords:
                name_display += " ✅"

            result_lines = [f"File: {pdf_file}", f"Candidate Name: {name_display}", "Keyword counts:"]
            for kw in keywords:
                count = count_keyword(cv_text, kw)
                result_lines.append(f"  '{kw}': {count} times")
            result_lines.append("")  # empty line between files
            all_results.extend(result_lines)
        
        set_result_text("\n".join(all_results))
        set_processing(False)
    except Exception as e:
        set_processing(False)
        messagebox.showerror("Error", f"Failed to process folder:\n{e}")

def open_single_file():
    filepath = filedialog.askopenfilename(
        filetypes=[("PDF Files", "*.pdf")],
        title="Select a CV PDF file"
    )
    if not filepath:
        return
    try:
        set_processing(True)
        root.update_idletasks()

        cv_text = extract_text_from_pdf(filepath)
        keywords = [kw.strip() for kw in keyword_entry.get().split(",") if kw.strip()]
        if not keywords:
            messagebox.showwarning("Input needed", "Please enter at least one keyword.")
            set_processing(False)
            return
        
        name = detect_name_with_fallback(cv_text)
        has_keywords = any(count_keyword(cv_text, kw) > 0 for kw in keywords)
        name_display = (name or "Not found")
        if has_keywords:
            name_display += " ✅"
        
        results = [f"Candidate Name: {name_display}", "Keyword counts:"]
        for kw in keywords:
            count = count_keyword(cv_text, kw)
            results.append(f"  '{kw}': {count} times")
        
        set_result_text("\n".join(results))
        set_processing(False)
    except Exception as e:
        set_processing(False)
        messagebox.showerror("Error", f"Failed to process file:\n{e}")

def set_result_text(text):
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, text)
    result_text.config(state='disabled')

def set_processing(is_processing):
    if is_processing:
        progress_bar.grid()
        progress_bar.start()
        open_file_btn.config(state='disabled')
        open_folder_btn.config(state='disabled')
    else:
        progress_bar.stop()
        progress_bar.grid_remove()
        open_file_btn.config(state='normal')
        open_folder_btn.config(state='normal')

# GUI setup
root = tk.Tk()
root.title("CV Analyzer")
root.geometry("700x500")
root.configure(bg="#f5f5f5")

style = ttk.Style()
style.theme_use('clam')

style.configure('TButton', font=('Segoe UI', 11), padding=6)
style.configure('TLabel', background="#f5f5f5", font=('Segoe UI', 11))
style.configure('TEntry', font=('Segoe UI', 11))
style.configure('Horizontal.TProgressbar', thickness=10)

frame = tk.Frame(root, bg="#f5f5f5", padx=20, pady=20)
frame.pack(fill="both", expand=True)

keyword_label = ttk.Label(frame, text="Keywords to count (comma separated):")
keyword_label.grid(row=0, column=0, sticky="w")

keyword_entry = ttk.Entry(frame)
keyword_entry.insert(0, "React, Docker, Kubernetes")
keyword_entry.grid(row=0, column=1, sticky="ew", padx=(10,0))

buttons_frame = tk.Frame(frame, bg="#f5f5f5")
buttons_frame.grid(row=1, column=0, columnspan=2, pady=15)

open_file_btn = ttk.Button(buttons_frame, text="Open Single CV PDF", command=open_single_file)
open_file_btn.pack(side="left", padx=5)

open_folder_btn = ttk.Button(buttons_frame, text="Open Folder with CV PDFs", command=open_folder)
open_folder_btn.pack(side="left", padx=5)

progress_bar = ttk.Progressbar(frame, mode='indeterminate', style='Horizontal.TProgressbar')
progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
progress_bar.grid_remove()

result_frame = tk.Frame(frame, bg="#eaeaea", bd=1, relief="sunken")
result_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")

result_text = tk.Text(result_frame, wrap="word", font=("Consolas", 11), state='disabled', bg="white")
result_text.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
scrollbar.pack(side="right", fill="y")

result_text['yscrollcommand'] = scrollbar.set

frame.columnconfigure(1, weight=1)
frame.rowconfigure(3, weight=1)

root.mainloop()
