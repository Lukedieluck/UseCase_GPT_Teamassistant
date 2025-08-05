# vdb_helper.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datetime, os
from uuid import uuid4

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
VDB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION = "team_mood"

def save_entry(event_type, text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    entry_id = str(uuid4())  # <-- NEU: übergreifende Entry-ID
    ts = datetime.datetime.utcnow().isoformat()
    metadatas = [{
        "timestamp": ts,
        "event_type": event_type,
        "entry_id": entry_id
    }] * len(chunks)

    vectordb = Chroma(
        collection_name=COLLECTION,
        persist_directory=VDB_DIR,
        embedding_function=embeddings
    )
    ids = vectordb.add_texts(chunks, metadatas=metadatas)
    vectordb.persist()
    return entry_id, ids  # darf vom Aufrufer ignoriert werden

def get_last_entries(n=5):
    vectordb = Chroma(
        collection_name=COLLECTION,
        persist_directory=VDB_DIR,
        embedding_function=embeddings
    )
    results = vectordb.get()
    docs = results['documents']
    metadatas = results['metadatas']
    # Chronologisch neueste zuerst
    sorted_entries = sorted(
        zip(docs, metadatas),
        key=lambda x: x[1].get('timestamp', ''),
        reverse=True
    )
    return [doc for doc, meta in sorted_entries[:n]]

def get_collection():
    vectordb = Chroma(
        collection_name=COLLECTION,
        persist_directory=VDB_DIR,
        embedding_function=embeddings
    )
    return vectordb

def print_all_entries():
    collection = get_collection()
    results = collection.get()
    print("\n📋 Aktuelle Einträge in der VDB:\n" + "-"*35)
    for i, (doc, meta, _id) in enumerate(zip(results['documents'], results['metadatas'], results['ids'])):
        print(f"{i+1}. id={_id}  entry_id={meta.get('entry_id')}  ts={meta.get('timestamp')}  text={doc[:80]}...")
