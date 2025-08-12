import re
import spacy
import pdfplumber
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as tb
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

def clear_treeview():
    for item in treeview.get_children():
        treeview.delete(item)

def insert_row(values, index):
    tag = 'evenrow' if index % 2 == 0 else 'oddrow'
    treeview.insert("", "end", values=values, tags=(tag,))

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

        clear_treeview()

        for idx, pdf_file in enumerate(pdf_files):
            full_path = os.path.join(folderpath, pdf_file)
            cv_text = extract_text_from_pdf(full_path)
            name = detect_name_with_fallback(cv_text)

            has_keywords = any(count_keyword(cv_text, kw) > 0 for kw in keywords)
            name_display = (name or "Not found")
            if has_keywords:
                name_display += " ✅"

            counts_str = ", ".join(f"'{kw}': {count_keyword(cv_text, kw)}" for kw in keywords)
            insert_row((pdf_file, name_display, counts_str), idx)

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
        
        counts_str = ", ".join(f"'{kw}': {count_keyword(cv_text, kw)}" for kw in keywords)

        clear_treeview()
        insert_row((os.path.basename(filepath), name_display, counts_str), 0)

        set_processing(False)
    except Exception as e:
        set_processing(False)
        messagebox.showerror("Error", f"Failed to process file:\n{e}")

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

# --- GUI Setup ---
root = tb.Window(themename="litera")
root.title("CV Analyzer")
root.geometry("800x550")

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

keyword_label = ttk.Label(frame, text="Keywords to count (comma separated):")
keyword_label.grid(row=0, column=0, sticky="w")

keyword_entry = ttk.Entry(frame)
keyword_entry.insert(0, "React, Docker, Kubernetes")
keyword_entry.grid(row=0, column=1, sticky="ew", padx=(10,0))

buttons_frame = ttk.Frame(frame)
buttons_frame.grid(row=1, column=0, columnspan=2, pady=15)

open_file_btn = tb.Button(buttons_frame, text="Open Single CV PDF", bootstyle="success", command=open_single_file)
open_file_btn.pack(side="left", padx=5)

open_folder_btn = tb.Button(buttons_frame, text="Open Folder with CV PDFs", bootstyle="primary", command=open_folder)
open_folder_btn.pack(side="left", padx=5)

progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=400)
progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
progress_bar.grid_remove()

columns = ("filename", "candidate_name", "keyword_counts")
treeview = tb.Treeview(frame, columns=columns, show="headings", height=18)
treeview.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(10,0))

treeview.heading("filename", text="File Name")
treeview.heading("candidate_name", text="Candidate Name")
treeview.heading("keyword_counts", text="Keyword Counts")

treeview.column("filename", width=250)
treeview.column("candidate_name", width=220)
treeview.column("keyword_counts", width=300)

treeview.tag_configure('oddrow', background='white')
treeview.tag_configure('evenrow', background='#cce6ff')  # light blue

frame.columnconfigure(1, weight=1)
frame.rowconfigure(3, weight=1)

root.mainloop()
