### Financial RAG System with Agent Capabilities

A focused RAG system that answers financial questions about Microsoft (MSFT), Alphabet (GOOGL), and NVIDIA (NVDA) using their recent 10-K filings. It supports simple questions, comparative queries, and complex multi-step questions via agent-style decomposition.

## Setup

- **Python**: 3.12 recommended
- Create and activate a virtual environment

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

- Install dependencies

```powershell
pip install -r requirements.txt
```

- Set your Groq API key (free at `https://console.groq.com`)

```powershell
$env:GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

## Run (Non-interactive demo)

Generates sample answers for 5 queries and writes them to `sample_results.json`.

```powershell
$env:NON_INTERACTIVE="1"
./venv/Scripts/python.exe ./main.py
```

Open `sample_results.json` to view results.

## Run (Interactive)

Ask your own questions after the sample run finishes.

```powershell
./venv/Scripts/python.exe ./main.py
```

Type `quit` to exit.

## Quick Demo Expectations

- **Simple queries**
- **Comparative queries**
- **Complex query with agent decomposition**

The script prints answers to the console and saves sample outputs to `sample_results.json`.

## Notes

- **Data**: If SEC endpoints fail (or to reduce load), the system uses realistic demo content written to `sec_data/`.
- **Embeddings**: `sentence-transformers` with FAISS for retrieval.
- **LLM**: Groq `llama-3.1-8b-instant`.
