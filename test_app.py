import os
from ocr_processor import OCRProcessor
from data_manager import DataManager
from ai_generator import AIGenerator
from document_parser import parse_proposal_sections, extract_metadata_from_text
from document_exporter import export_to_word

# 1. Test OCRProcessor (requires a sample image file, skipped if not present)
def test_ocr_processor():
    print("Testing OCRProcessor...")
    ocr = OCRProcessor()
    image_path = os.path.join("sample_data", "sample_image.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            class FileObj:
                def read(self): return f.read()
            try:
                text = ocr.extract_text_from_image(FileObj())
                print("Extracted text:", text[:200])
            except Exception as e:
                print("OCR error:", e)
    else:
        print("No sample image found, skipping OCR test.")

# 2. Test DataManager with sample proposal text
def test_data_manager():
    print("Testing DataManager...")
    dm = DataManager()
    dm.initialize_database()
    sample_text = "Executive Summary\nTest summary.\n\nScope of Work\nTest scope.\n\nPricing\nTest pricing."
    meta = {"client_name": "TestClient", "industry": "TestIndustry", "service_type": "TestService"}
    success = dm.store_proposal(sample_text, meta)
    print("Store proposal success:", success)
    results = dm.search_similar_proposals("Test summary")
    print("Search results:", results)
    all_props = dm.get_all_proposals()
    print("All proposals:", all_props)

# 3. Test AIGenerator with sample inputs (requires OpenAI API key)
def test_ai_generator():
    print("Testing AIGenerator...")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("No OpenAI API key set. Skipping AI generation test.")
        return
    ai = AIGenerator()
    similar = [{"text": "Sample similar proposal."}]
    proposal = ai.generate_full_proposal("TestClient", "TestIndustry", "TestService", similar)
    print("Generated proposal:", proposal)

# 4. Test document parser with sample text
def test_document_parser():
    print("Testing document parser...")
    sample_text = """Executive Summary\nThis is a summary.\n\nScope of Work\nWork details.\n\nPricing\nPrice info.\nIndustry: Tech\nService Type: Consulting\nClient: ExampleCo"""
    sections = parse_proposal_sections(sample_text)
    meta = extract_metadata_from_text(sample_text)
    print("Sections:", sections)
    print("Metadata:", meta)

# 5. Create sample proposal data for testing
def create_sample_data():
    print("Creating sample data...")
    os.makedirs("sample_data", exist_ok=True)
    samples = [
        ("proposal1.txt", "Executive Summary\nAcme Corp seeks to modernize its IT infrastructure.\n\nScope of Work\n- Assess current systems\n- Design new architecture\n\nPricing\nBased on project phases.\nIndustry: Technology\nService Type: Consulting\nClient: Acme Corp"),
        ("proposal2.txt", "Executive Summary\nMediHealth aims to enhance patient data analytics.\n\nScope of Work\n- Integrate EHR systems\n\nPricing\nFlexible pricing.\nIndustry: Healthcare\nService Type: Data Analytics\nClient: MediHealth"),
    ]
    for fname, content in samples:
        with open(os.path.join("sample_data", fname), "w", encoding="utf-8") as f:
            f.write(content)
    print("Sample data created.")

# 6. Populate database with sample data
def populate_db_with_samples():
    print("Populating DB with sample data...")
    dm = DataManager()
    dm.initialize_database()
    for fname in os.listdir("sample_data"):
        if fname.endswith(".txt"):
            with open(os.path.join("sample_data", fname), "r", encoding="utf-8") as f:
                text = f.read()
            meta = extract_metadata_from_text(text)
            dm.store_proposal(text, meta)
    print("Database populated.")

# 7. End-to-end workflow test
def test_end_to_end():
    print("Testing end-to-end workflow...")
    dm = DataManager()
    dm.initialize_database()
    # Use sample proposal
    with open(os.path.join("sample_data", "proposal1.txt"), "r", encoding="utf-8") as f:
        text = f.read()
    meta = extract_metadata_from_text(text)
    dm.store_proposal(text, meta)
    results = dm.search_similar_proposals("IT infrastructure")
    print("Similar proposals:", results)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        ai = AIGenerator()
        proposal = ai.generate_full_proposal(meta.get("client_name", "TestClient"), meta.get("industry", "TestIndustry"), meta.get("service_type", "TestService"), results)
        print("Generated proposal:", proposal)
        file_path = export_to_word(proposal, meta.get("client_name", "TestClient"))
        print("Exported Word file:", file_path)
    else:
        print("No OpenAI API key set. Skipping AI generation/export.")

if __name__ == "__main__":
    test_ocr_processor()
    test_data_manager()
    test_ai_generator()
    test_document_parser()
    create_sample_data()
    populate_db_with_samples()
    test_end_to_end()
