import os
from data_manager import DataManager

SAMPLE_DATA_DIR = "./sample_data"

def extract_metadata_from_filename(filename):
    # Simple metadata extraction: you can improve this as needed
    name, _ = os.path.splitext(filename)
    return {
        "source_file": filename,
        "title": name.replace("_", " ").title()
    }

def main():
    persist_dir = "./chromadb_data"
    
    print(f"ChromaDB will persist data in: {os.path.abspath(persist_dir)}")

    dm = DataManager(persist_directory=persist_dir)
    dm.initialize_database()

    files = [f for f in os.listdir(SAMPLE_DATA_DIR) if f.lower().endswith(('.txt', '.md'))]

    print(files)

    print(f"Found {len(files)} files in {SAMPLE_DATA_DIR}")

    for fname in files:
        fpath = os.path.join(SAMPLE_DATA_DIR, fname)
        
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        metadata = extract_metadata_from_filename(fname)
        success = dm.store_proposal(text=text, metadata=metadata)
        
        print(f"{'Stored' if success else 'Failed'}: {fname}")

    # Check if the persist directory exists and print its contents
    if os.path.exists(persist_dir):
        print(f"Persist directory exists: {persist_dir}")
        print("Contents:", os.listdir(persist_dir))
    else:
        print(f"Persist directory NOT found: {persist_dir}")

    print("Vector store creation complete.")

if __name__ == "__main__":
    main()