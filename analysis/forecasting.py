import numpy as np
from datetime import datetime

def forecast_next_year(records, trends):
    """
    Forecast product volume usage and notes for the next 12 months.
    
    Args:
        records: list of parsed receipt dicts with date, products, volume, and notes
        trends: dict of month -> embedding vector (not used for product forecasting)
    
    Returns:
        dict of month_name -> {
            "products": {product_name: {"volume": X, "unit": Y, "targets": Z}, ...},
            "notes": "latest note for that month"
        }
    """
    # Group records by month to get historical usage patterns
    monthly_data = {}
    
    # Sort records by date to easily find the latest note
    records.sort(key=lambda r: r.get("date", ""), reverse=True)

    for record in records:
        if not record.get("date"):
            continue
        
        date_obj = datetime.fromisoformat(record["date"])
        month_key = date_obj.strftime("%B")  # "January", "February", etc.
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {"products": {}, "notes": []}
        
        # Capture notes for the month
        if record.get("notes"):
            monthly_data[month_key]["notes"].append(record["notes"])
            
        # Accumulate product volumes and metadata by month
        if record.get("products"):
            for product in record["products"]:
                prod_name = product.get("name", "Unknown")
                applied_amt = product.get("applied_amt", 0.0)
                unit = product.get("unit", "")
                targets = product.get("targets", "")
                
                if prod_name not in monthly_data[month_key]["products"]:
                    monthly_data[month_key]["products"][prod_name] = {
                        "volumes": [],
                        "unit": unit,
                        "targets": targets
                    }
                
                monthly_data[month_key]["products"][prod_name]["volumes"].append(applied_amt)

    # Create forecast for next 12 months using historical averages
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    forecast = {}
    for i, month_name in enumerate(month_names, 1):
        month_key = f"Month_{i}"
        forecast[month_key] = {"products": {}, "notes": ""}
        
        if month_name in monthly_data:
            # Get the latest note for the month
            if monthly_data[month_name]["notes"]:
                forecast[month_key]["notes"] = monthly_data[month_name]["notes"][0]

            # Calculate average product usage
            for prod_name, prod_data in monthly_data[month_name]["products"].items():
                volumes = prod_data["volumes"]
                if volumes:
                    avg_volume = np.mean(volumes)
                    forecast[month_key]["products"][prod_name] = {
                        "volume": round(avg_volume, 4),
                        "unit": prod_data.get("unit", ""),
                        "targets": prod_data.get("targets", "")
                    }
    
    return forecast


def generate_historical_table(records, embeddings):
    """
    Generate a historical data table showing product categories used each month.
    
    Args:
        records: list of parsed receipt dicts with date, products, notes
        embeddings: list of embedding vectors corresponding to notes
    
    Returns:
        dict with historical data organized by month/date
    """
    from datetime import datetime
    
    # Categorize products by type
    def categorize_product(prod_name):
        """Categorize product by name."""
        prod_lower = prod_name.lower()
        
        if any(x in prod_lower for x in ['nitrogen', 'potash', 'phosphorus', 'sulfur', 'scu', 'ubm', 'iron']):
            return 'Fertilizer'
        elif any(x in prod_lower for x in ['weed', 'manor', 'atrazine', 'certainty', 'herbicide', 'dicamba', 'mcpa', 'mecoprop', 'sulfosulfuron', 'prodiamine', 'indaziflam', 'halosulfuron', 'celsius', 'change up', 'barricade', 'specticle']):
            return 'Weed Control'
        elif any(x in prod_lower for x in ['iron', 'spt iron']):
            return 'Iron/Micronutrient'
        elif any(x in prod_lower for x in ['sulfur', 'dispersable']):
            return 'Sulfur'
        elif any(x in prod_lower for x in ['insect', 'talstar', 'bifenthrin', 'acelepryn', 'thiamethoxam', 'chlorantraniliprole']):
            return 'Insecticide'
        elif any(x in prod_lower for x in ['surfactant', 'non-ionic']):
            return 'Surfactant'
        else:
            return 'Other'
    
    # Group by date
    historical = {}
    embedding_idx = 0
    
    for record in records:
        if not record.get("date"):
            continue
        
        date_str = record["date"]
        date_obj = datetime.fromisoformat(date_str)
        month_str = date_obj.strftime("%Y-%m")
        
        if month_str not in historical:
            # Get embedding for this month's notes if available
            embedding_vector = None
            if record.get("notes") and record.get("notes").strip() and embedding_idx < len(embeddings):
                embedding_vector = embeddings[embedding_idx]
                embedding_idx += 1
            
            historical[month_str] = {
                "date": date_str,
                "products": {},
                "product_categories": {},
                "notes": record.get("notes", ""),
                "embedding": embedding_vector,
                "embedding_summary": f"[{len(embedding_vector)} dims]" if embedding_vector else "N/A",
                "volume_total": 0.0
            }
        
        # Count product categories used
        for product in record.get("products", []):
            prod_name = product.get("name", "Unknown")
            category = categorize_product(prod_name)
            applied_amt = product.get("applied_amt", 0.0)
            
            if prod_name not in historical[month_str]["products"]:
                historical[month_str]["products"][prod_name] = {
                    "volume": applied_amt,
                    "unit": product.get("unit", ""),
                    "category": category
                }
            else:
                historical[month_str]["products"][prod_name]["volume"] += applied_amt
            
            if category not in historical[month_str]["product_categories"]:
                historical[month_str]["product_categories"][category] = 0
            
            historical[month_str]["product_categories"][category] += 1
            historical[month_str]["volume_total"] += applied_amt
    
    # Sort by date
    sorted_historical = dict(sorted(historical.items()))
    
    # Convert to table format
    table_data = []
    
    # Get all unique product categories
    all_categories = set()
    for month_data in sorted_historical.values():
        all_categories.update(month_data["product_categories"].keys())
    
    all_categories = sorted(list(all_categories))
    
    for month_key, month_data in sorted_historical.items():
        row = {
            "Month": month_key,
            "Date": month_data["date"]
        }
        
        # Add count for each category
        for category in all_categories:
            row[category] = month_data["product_categories"].get(category, 0)
        
        row["Total_Volume"] = round(month_data["volume_total"], 2)
        row["Embedding_Summary"] = month_data["embedding_summary"]
        
        # Truncate notes to first 100 chars for CSV
        notes_preview = month_data["notes"][:100].replace('\n', ' ').replace('  ', ' ')
        row["Notes_Preview"] = notes_preview
        
        table_data.append(row)
    
    # Also prepare full embedding data (without embedding vectors in CSV to avoid huge files)
    full_data = {
        "table": table_data,
        "product_categories": sorted(list(all_categories)),
        "embeddings": {
            month_key: {
                "embedding": month_data["embedding"],
                "embedding_shape": f"{len(month_data['embedding'])} dimensions" if month_data["embedding"] else "N/A"
            }
            for month_key, month_data in sorted_historical.items()
            if month_data["embedding"]
        },
        "summary": {
            "total_records": len(sorted_historical),
            "date_range": f"{min(sorted_historical.keys())} to {max(sorted_historical.keys())}",
            "embedding_dimension": len(embeddings[0]) if embeddings else 0
        }
    }
    
    return full_data
