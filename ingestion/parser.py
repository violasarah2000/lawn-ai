import re
from datetime import datetime

def parse_receipt(pdf):
    text = pdf["text"]
    parsed = {
        "filename": pdf["filename"],
        "notes": "",
        "products": [],        # list of dicts: [{"name": ..., "volume": ..., "unit": ..., "rate": ..., "applied_amt": ...}]
        "volume": 0.0,         # total volume across all products
        "property_sqft": 0,
        "method": "",
        "areas": "",
        "date": None
    }

    # --------------------------
    # Extract notes
    # --------------------------
    notes_match = re.search(
        r"WHAT I DID AND WHAT TO EXPECT\s*(.*?)\n\s*PRODUCTS APPLIED", 
        text, re.DOTALL | re.IGNORECASE
    )
    if notes_match:
        parsed["notes"] = notes_match.group(1).strip()

    # --------------------------
    # Extract property SQFT
    # --------------------------
    sqft_match = re.search(r"(\d{3,5})\s*sqft", text, re.IGNORECASE)
    if sqft_match:
        parsed["property_sqft"] = int(sqft_match.group(1))

    # --------------------------
    # Extract method / areas
    # --------------------------
    method_match = re.search(r"METHOD:\s*(.*?)\n", text, re.IGNORECASE)
    if method_match:
        parsed["method"] = method_match.group(1).strip()

    areas_match = re.search(r"AREAS:\s*(.*?)\n", text, re.IGNORECASE)
    if areas_match:
        parsed["areas"] = areas_match.group(1).strip()

    # --------------------------
    # Extract service date
    # --------------------------
    date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", text)
    if date_match:
        try:
            parsed["date"] = datetime.strptime(date_match.group(1), "%m/%d/%Y").date().isoformat()
        except ValueError:
            parsed["date"] = None

    # --------------------------
    # Extract all products from all sections
    # --------------------------
    # Products can appear in multiple formats:
    # 1. After "PRODUCTS:" label with multiple products
    # 2. Standalone product names followed by EPA# (like SPT IRON)
    # We need to find ALL of them, including their targets/classification
    
    total_volume = 0.0
    
    # Find all "APPLIED AMT:" entries in the entire document
    # This is more robust than looking for PRODUCTS: sections
    applied_matches = list(re.finditer(
        r"APPLIED AMT:\s*\n?\s*([\d\.]+)\s+(FLOZ|OZ|GAL|LB)(?:\s|/)",
        text,
        re.IGNORECASE
    ))
    
    for i, applied_match in enumerate(applied_matches):
        amt_value = float(applied_match.group(1))
        amt_unit = applied_match.group(2).upper()
        
        # Normalize FLOZ to OZ for consistency
        if amt_unit == "FLOZ":
            amt_unit = "OZ"
        
        # Find the product name by looking backwards from this APPLIED AMT
        text_before = text[:applied_match.start()]
        
        # Find the last "RATE:" before this APPLIED AMT
        rate_pos = text_before.rfind("RATE:")
        if rate_pos == -1:
            continue
        
        # Get text between previous APPLIED AMT (if exists) and current RATE:
        if i > 0:
            prev_applied = applied_matches[i - 1]
            search_start = prev_applied.end()
        else:
            search_start = 0
        
        product_text = text[search_start:rate_pos].strip()
        
        # Extract product name from this text
        # It should be the last non-empty line
        lines = [line.strip() for line in product_text.split('\n') if line.strip()]
        if lines:
            prod_name = lines[-1]  # Last line is typically the product name
        else:
            continue
        
        # Extract targets/classification from the text after APPLIED AMT
        # Look for "TARGETS:" after this product's APPLIED AMT line
        text_after = text[applied_match.end():]
        targets_match = re.search(
            r"TARGETS:\s*(.*?)(?=RATE:|PRODUCTS:|METHOD:|WHAT I|APPLIED AMT:|$)",
            text_after,
            re.IGNORECASE | re.DOTALL
        )
        
        targets = ""
        if targets_match:
            targets_text = targets_match.group(1).strip()
            # Clean up the targets text - take first 100 chars or first item
            targets = targets_text.split('\n')[0][:100] if targets_text else ""
        
        prod = {
            "name": prod_name,
            "rate": 0.0,
            "applied_amt": amt_value,
            "unit": amt_unit,
            "targets": targets
        }
        
        total_volume += amt_value
        parsed["products"].append(prod)
    
    parsed["volume"] = total_volume

    return parsed
