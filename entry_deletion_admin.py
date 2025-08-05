# entry_deletion_admin.py
import os
import argparse
from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ---- Pfade / Settings (ggf. anpassen) ----
VDB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION = "team_mood"
EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# ------------------------------------------

embeddings = HuggingFaceEmbeddings(model_name=EMB_MODEL)

def _db():
    return Chroma(collection_name=COLLECTION, persist_directory=VDB_DIR, embedding_function=embeddings)

def list_entries(limit=200):
    db = _db()
    res = db.get()
    docs, metas, ids = res["documents"], res["metadatas"], res["ids"]
    print(f"\n📋 Einträge (max. {limit}):\n" + "-"*35)
    for i, (doc, meta, _id) in enumerate(zip(docs, metas, ids), start=1):
        if i > limit:
            print("... (gekürzt)")
            break
        ts = meta.get("timestamp")
        eid = meta.get("entry_id")
        preview = (doc or "").replace("\n", " ")[:80]
        print(f"{i}. id={_id}  entry_id={eid}  ts={ts}  text={preview}...")

def find_ids_by_text(substring: str, limit=200):
    db = _db()
    res = db.get()
    docs, ids = res["documents"], res["ids"]
    out = []
    sub = substring.lower()
    for doc, _id in zip(docs, ids):
        if doc and sub in doc.lower():
            out.append(_id)
            if len(out) >= limit:
                break
    return out

def delete_by_id(doc_id: str, yes: bool = False):
    db = _db()
    if not yes:
        print(f"Sicher löschen? id={doc_id}  (mit --yes bestätigen)")
        return
    db.delete(ids=[doc_id])
    print(f"✓ gelöscht: id={doc_id}")

def delete_by_ids(doc_ids, yes: bool = False):
    if not doc_ids:
        print("Keine IDs übergeben.")
        return
    if not yes:
        print(f"Sicher löschen? {len(doc_ids)} Dokument(e)  (mit --yes bestätigen)")
        return
    db = _db()
    db.delete(ids=doc_ids)
    print(f"✓ gelöscht: {len(doc_ids)} Dokument(e)")

def delete_by_entry_id(entry_id: str, yes: bool = False):
    db = _db()
    try:
        res = db.get(where={"entry_id": entry_id})
    except TypeError:
        res = db.get(filter={"entry_id": entry_id})
    ids = res.get("ids", [])
    if not ids:
        print(f"Keine Dokumente zu entry_id={entry_id} gefunden.")
        return
    delete_by_ids(ids, yes=yes)

def delete_before(iso_ts: str, yes: bool = False):
    db = _db()
    res = db.get()
    metas, ids = res["metadatas"], res["ids"]
    try:
        cutoff = datetime.fromisoformat(iso_ts)
    except ValueError:
        print("Ungültiges ISO-Datum. Beispiel: 2025-08-01T00:00:00")
        return
    to_delete = []
    for meta, _id in zip(metas, ids):
        ts = meta.get("timestamp")
        if not ts:
            continue
        try:
            t = datetime.fromisoformat(ts)
            if t < cutoff:
                to_delete.append(_id)
        except Exception:
            continue
    delete_by_ids(to_delete, yes=yes)

def main():
    p = argparse.ArgumentParser(description="Chroma VDB Admin – Einträge listen/suchen/löschen")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_list = sub.add_parser("list", help="Einträge anzeigen")
    s_list.add_argument("--limit", type=int, default=200)

    s_find = sub.add_parser("find", help="IDs per Textsuche finden")
    s_find.add_argument("--text", required=True)
    s_find.add_argument("--limit", type=int, default=200)

    s_del_id = sub.add_parser("delete-id", help="Einzelne ID löschen")
    s_del_id.add_argument("--id", required=True)
    s_del_id.add_argument("--yes", action="store_true", help="Sicherheitsabfrage überspringen")

    s_del_eid = sub.add_parser("delete-entry-id", help="Alle Chunks eines Eintrags löschen (NEUE Einträge)")
    s_del_eid.add_argument("--entry-id", required=True)
    s_del_eid.add_argument("--yes", action="store_true")

    s_del_before = sub.add_parser("delete-before", help="Alles vor Zeitpunkt löschen (ISO)")
    s_del_before.add_argument("--ts", required=True, help="z. B. 2025-08-01T00:00:00")
    s_del_before.add_argument("--yes", action="store_true")

    args = p.parse_args()

    if args.cmd == "list":
        list_entries(limit=args.limit)
    elif args.cmd == "find":
        ids = find_ids_by_text(args.text, limit=args.limit)
        print("Gefundene IDs:", ids if ids else "—")
    elif args.cmd == "delete-id":
        delete_by_id(args.id, yes=args.yes)
    elif args.cmd == "delete-entry-id":
        delete_by_entry_id(args.entry_id, yes=args.yes)
    elif args.cmd == "delete-before":
        delete_before(args.ts, yes=args.yes)

if __name__ == "__main__":
    main()
