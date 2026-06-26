DataChat

> Ask questions about any CSV or Excel file in plain English — powered by LangChain and GPT-4o.

**[🚀 Live Demo](https://huggingface.co/spaces/pvk135/DataChat)** · **[GitHub](https://github.com/pvk135/DataChat)**

---

## What is DataChat?

DataChat lets anyone — with zero coding knowledge — talk to their data. Upload a spreadsheet, ask questions in plain English, and get real computed answers instantly. No SQL. No pandas. No Excel formulas.

It also generates a full professional business report from your data in one click, exported as a PDF.

---

## Features

- **Natural language Q&A** — ask any question about your data in plain English
- **Real computed answers** — generates and executes pandas code against your actual data, never guesses
- **Conversation memory** — follow-up questions work naturally ("now break that down by region")
- **Automatic chart rendering** — bar, line, and scatter charts generated when relevant
- **One-click report generation** — full narrative business report with insights, anomalies, and recommendations
- **PDF export** — download the report as a professional PDF

---

## Demo

Upload any CSV or Excel file and ask questions like:

- *"What was the best selling product by revenue?"*
- *"Which region had the most returns?"*
- *"Show me a line chart of monthly revenue"*
- *"What are the biggest anomalies in this dataset?"*

Then hit **Generate Full Report** for a complete AI-written business report on your data.

---

## How It Works

```
User asks a question in plain English
            ↓
LangChain agent receives the question + dataframe schema
            ↓
GPT-4o writes pandas code to answer it
            ↓
Code is executed against the real uploaded data
            ↓
Result is interpreted and returned as plain English
            ↓
Charts rendered automatically when relevant
```

For the report, three chained LLM calls run in sequence:
1. **Analyze** — extract key stats, trends, and anomalies
2. **Write** — produce a narrative business report
3. **Export** — format and render as a downloadable PDF

---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Agent orchestration | LangChain |
| LLM | OpenAI GPT-4o |
| Data processing | Pandas |
| Charts | Plotly |
| PDF generation | ReportLab |
| Hosting | Hugging Face Spaces |

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/pvk135/DataChat.git
cd DataChat
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key
```bash
cp .env.example .env
# Open .env and paste your OpenAI API key
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## Project Structure

```
DataChat/
├── app.py                    # Streamlit UI — file upload, chat, report button
├── utils/
│   ├── agent.py              # LangChain agent + GPT-4o + conversation memory
│   ├── data_loader.py        # CSV/Excel loading + dataframe description builder
│   ├── chart_detector.py     # Parses agent output and renders Plotly charts
│   └── report_generator.py   # Chained LLM calls — analyze, write, export PDF
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## Why I Built This

Most people at companies can't query their own data — they need to wait for a data analyst or learn SQL. DataChat removes that bottleneck entirely. Anyone can upload a spreadsheet and get real answers in seconds.

This project demonstrates end-to-end LLM application development: agent design, tool use, conversation memory, chained LLM calls, and production deployment.
