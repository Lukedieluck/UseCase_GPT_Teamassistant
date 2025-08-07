# 🧠 Team Assistant (Proof of Concept)

This project is a **proof of concept (POC)** to demonstrate a lightweight AI-based assistant for analyzing and managing team sentiment using an LLM (OpenAI API), a simple Flask GUI, and a vector database (Chroma + HuggingFace Embeddings).

The main goal was to test how user input can be stored, analyzed, requested and visualized to gain insights into team mood and dynamics.

This POC is an ongoing project. Updates will follow.


## 🔧 Features

### 1. 🗨️ Chat GUI (`chat_gui_flask.py`)
- Simple user interface for entering team-related text
- Visual sentiment barometer updated in real-time
- Data storage in Chroma vector database for later retrieval

### 2. 🛠️ Admin Tool (`entry_deletion_admin.py`)
- Command-line interface (CLI) to manage vector DB entries:
  - `list`: Display all entries (ID, timestamp, preview)
  - `find`: Search IDs by text substring
  - `delete-id`: Delete a single entry by ID (with `--yes` confirmation)
  - `delete-entry-id`: Delete all chunks of one entry (requires `entry_id`)
  - `delete-before`: Delete all entries before a given ISO timestamp
- Built-in safety: deletion actions require `--yes` confirmation

---
### 3. 🧪 Tech Stack
Python 3.10+

Flask

OpenAI API

LangChain

ChromaDB (local vector store)

HuggingFace Embeddings (MiniLM-L6-v2)

---
### 4. Screenshot (POC)

<img width="709" height="1113" alt="image" src="https://github.com/user-attachments/assets/aa3f82af-9317-40a5-9f47-9b534efc5442" />


### 5. Prompting
Already implement:

chain-of-thougts, temperature = 0.3, neutralisation


### 6. 🔭 Outlook / Future Ideas
🛡️ Migrate deprecated LangChain components to langchain-chroma and langchain-huggingface

💾 Add automatic backup/export function before deletion

🖼️ Enhance the UI with better design (charts, emojis, etc.)

📬 Add email or Slack notifications for sentiment alerts

📚 Enhance the Vector DB entries to analyze patterns and insights into the team mood

📈 Store long-term sentiment trends and visualize them

📦 Try other GPT-Models

---

## 🧪 Disclaimer

⚠️ This project is a **POC only** – not designed for production use.

- No authentication or authorization
- No logging or auditing
- No unit tests
- Basic styling and limited error handling

---

## ▶️ Setup & Usage

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME

2. Create & activate a virtual environment
bash

python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

3. Install dependencies
bash
pip install -r requirements.txt

4. Create a .env file (not included in the repo)
env
OPENAI_API_KEY=your-openai-api-key

5. Run the chat GUI
bash
python chat_gui_flask.py

6. Use the admin CLI for Vector-deletions
bash
python entry_deletion_admin.py list
python entry_deletion_admin.py delete-id --id <your-id> --yes

📦 Project Structure
bash

📁 UseCase_Teamassistant/
├── chat_gui_flask.py           # Chat UI with mood analysis
├── sentiment_dashboard.py      # Sentiment logic and barometer
├── vdb_helper.py               # Vector DB helper functions
├── entry_deletion_admin.py     # CLI admin tool for entry deletion
├── requirements.txt
├── .gitignore
├── README.md
🔮 Outlook

To set your personally API-Key:
# config_sample.env
OPENAI_API_KEY=sk-...
CHROMA_COLLECTION_NAME=team_mood
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2


Add authentication and access control

Export/backup vector database entries

Improve styling and mobile support

Migrate deprecated imports to langchain_chroma and langchain_huggingface

👨‍💻 Author
Luke
