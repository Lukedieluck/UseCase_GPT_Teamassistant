from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datetime, os

# Initialisiere Embedding Modell (MiniLM ist schnell und gratis)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Ordner für VDB
VDB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION = "team_mood"

# Funktion: Eintrag speichern
def save_entry(event_type, text):
    # Chunking (zerlegt große Texte in 1000er Blöcke)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    metadatas = [{"timestamp": datetime.datetime.utcnow().isoformat(), "event_type": event_type}] * len(chunks)

    vectordb = Chroma(
        collection_name=COLLECTION,
        persist_directory=VDB_DIR,
        embedding_function=embeddings
    )
    vectordb.add_texts(chunks, metadatas=metadatas)
    vectordb.persist()

# Funktion: Einträge abrufen (z.B. letzte 5 für Team-Stimmung)
def get_last_entries(n=5):
    vectordb = Chroma(
        collection_name=COLLECTION,
        persist_directory=VDB_DIR,
        embedding_function=embeddings
    )
    # Hole alle Einträge inkl. Metadaten
    results = vectordb.get()
    docs = results['documents']
    metadatas = results['metadatas']
    # Sortiere nach Zeitstempel absteigend
    sorted_entries = sorted(
        zip(docs, metadatas),
        key=lambda x: x[1]['timestamp'],
        reverse=True
    )
    # Gib die letzten n zurück
    return [doc for doc, meta in sorted_entries[:n]]


# Funktion: Liefert die Collection aus der VDB (wird z. B. für Debugging benötigt)
def get_collection():
    vectordb = Chroma(
        collection_name=COLLECTION,
        persist_directory=VDB_DIR,
        embedding_function=embeddings
    )
    return vectordb


# Funktion: Alle Einträge ausgeben welche in der VDB gespeichert sind (für Debugging)
def print_all_entries():
    collection = get_collection()
    results = collection.get()
    print("\n📋 Aktuelle Einträge in der VDB:\n" + "-"*35)
    for i, doc in enumerate(results['documents']):
        print(f"{i+1}. {doc}")

