import argparse
import json
import os
from ingestion.pdf_loader import load_pdfs
from ingestion.parser import parse_receipt
from models.embeddings import embed_texts
from analysis.trend_model import compute_trends
from analysis.forecasting import forecast_next_year, generate_historical_table

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdf_dir",
        type=str,
        required=True,
        default="data/receipts",
        help="Path to directory containing PDF receipts"
    )
    args = parser.parse_args()
    pdf_dir = args.pdf_dir

    print(f"[1] Loading PDFs from: {pdf_dir}")
    pdf_texts = load_pdfs(pdf_dir)

    # ------------------------------
    # Debug: Check for empty raw PDF text
    # ------------------------------
    for pdf in pdf_texts:
        if not pdf["text"].strip():
            print(f"⚠️ Empty PDF text detected: {pdf['filename']}")

    print("[2] Parsing structured fields...")
    parsed = [parse_receipt(pdf) for pdf in pdf_texts]

    # ------------------------------
    # Debug: Check for empty notes after parsing
    # ------------------------------
    for p in parsed:
        if not p["notes"].strip():
            print(f"⚠️ Empty notes after parsing: {p['filename']}")
        if p["volume"] == 0.0:
            print(f"⚠️ No volume captured in {p['filename']}")
        if not p["products"]:
            print(f"⚠️ No products captured in {p['filename']}")
        if p["date"] is None:
            print(f"⚠️ No date captured in {p['filename']}")

    # Ensure directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Save parsed receipts
    with open("data/processed.json", "w") as f:
        json.dump(parsed, f, indent=2)

    print(f"[3] Generating embeddings (Ollama)...")
    notes_to_embed = [p["notes"] for p in parsed if p["notes"].strip()]
    embeddings = embed_texts(notes_to_embed)

    # Attach embeddings to parsed entries
    emb_index = 0
    for p in parsed:
        if p["notes"].strip():
            p["embedding"] = embeddings[emb_index]
            emb_index += 1
        else:
            p["embedding"] = []

    # Save with embeddings
    with open("processed.json", "w") as f:
        json.dump(parsed, f, indent=2)

    print("[4] Computing trends...")
    trends = compute_trends(parsed, embeddings)

    print("[5] Forecasting next year...")
    forecast = forecast_next_year(parsed, trends)
    
    # Save forecast
    with open("output/forecast.json", "w") as f:
        json.dump(forecast, f, indent=2)

    # Generate historical data table
    print("[6] Generating historical data table...")
    historical_table = generate_historical_table(parsed, embeddings)
    
    # Save historical data
    with open("output/historical_data.json", "w") as f:
        json.dump(historical_table, f, indent=2)
    
    # Also save as CSV for Excel
    import csv
    if historical_table["table"]:
        csv_file = "output/historical_data.csv"
        fieldnames = historical_table["table"][0].keys()
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(historical_table["table"])
        print(f"   Saved CSV to {csv_file}")

    print("\nDone! Check output/forecast.json and output/historical_data.json")

if __name__ == "__main__":
    main()
