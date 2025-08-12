# CV Keyword Analyzer

A simple Python GUI application to extract text from one or multiple PDF CVs, detect candidate names, and count occurrences of user-specified keywords.  
If any of the keywords appear in a CV, a green checkmark (✅) is displayed next to the candidate’s name.

---

## Features

- Extracts text from PDF resumes using `pdfplumber`
- Detects candidate names using SpaCy French NLP model (`fr_core_news_sm`)
- Counts occurrences of multiple keywords (case-insensitive)
- Supports processing a single PDF or all PDFs in a selected folder
- Displays results in a scrollable, user-friendly GUI with a progress bar
- Shows a green checkmark ✅ next to the name if any keyword is found

---

## Requirements

- Python 3.8+
- `pdfplumber`
- `spacy`
- SpaCy French model: `fr_core_news_sm`
- Tkinter (usually included with Python standard library)

---

## Installation

1. Clone this repository or download the Python script.

2. Install required Python packages:
   ```bash
   pip install pdfplumber spacy
  ```bash
   python -m spacy download fr_core_news_sm
