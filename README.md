# NL Data Analyst

Ask questions about any CSV or Excel file in plain English. Powered by LangChain + GPT-4o.

## What it does

- Upload any CSV or Excel file
- Ask questions in plain English: *"What was our best month for revenue?"*
- Get real answers computed from your actual data — not guesses
- Follow-up questions work naturally thanks to conversation memory
- Charts are generated automatically when relevant

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/nl-data-analyst.git
cd nl-data-analyst
```

### 2. Create a virtual environment
```bash
python -m venv venv
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

## Project structure

```
nl_data_analyst/
├── app.py                  # Streamlit UI
├── utils/
│   ├── agent.py            # LangChain agent + memory
│   ├── data_loader.py      # CSV/Excel loading + dataframe description
│   └── chart_detector.py   # Parses agent output and renders Plotly charts
├── requirements.txt
└── .env.example
```

## Tech stack

| Layer      | Tool                  |
|------------|-----------------------|
| Frontend   | Streamlit             |
| Agent      | LangChain             |
| LLM        | OpenAI GPT-4o         |
| Data       | Pandas                |
| Charts     | Plotly                |

## Coming soon (Phase 2)

- One-click full report generation
- Narrative insights, anomaly detection, recommendations
- PDF export
