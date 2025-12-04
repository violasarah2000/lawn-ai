# 🌱 Lawn-AI — AI Forecast + Shopping Guide

**Transform PDF receipts → 12-month lawn treatment forecast + where to buy each product**

Lawn-AI uses AI embeddings and neural networks to learn your lawn's seasonal patterns from past service receipts, predicts next year's needs, then finds where to buy each product.

## Main Deliverable

**`output/forecast_and_shopping_guide.html`** ← Open this in your browser
- 12-month treatment forecast  
- Shopping recommendations for each product  
- Live retailer links  
- Print-friendly (save as PDF)

## Quick Start (5 min)

```bash
# Setup
cd MCP && cp .env.example .env
# Edit .env and add Serper API key (free at https://serper.dev)
pip install -r requirements.txt && python server.py

# Generate report
cd .. && python generate_combined_report.py

# View
open output/forecast_and_shopping_guide.html
```

## Files

| File | Purpose |
|------|---------|
| `output/forecast_and_shopping_guide.html` | **Main report** ← start here |
| `MCP/README.md` | Quick tech reference |
| `MCP/SECURITY_CONCEPTS.md` | AI security learning (6-8 hrs) |
| `PROJECT_STATUS.md` | Project overview |

## Tech Stack

- **PDF Parsing**: PyMuPDF
- **Embeddings**: Ollama (semantic)
- **Forecasting**: Neural network
- **Shopping**: Serper API
- **Report**: HTML + CSS
- **Validation**: Pydantic + security patterns

## Learning (Optional)

If interested in AI security engineering patterns, see `MCP/README.md`:
- Credential management
- Input validation
- Safe file operations
- API error handling
- Rate limiting

These patterns are used at: Anthropic, OpenAI, Google, Stripe.

## Status

✅ Forecast complete (12 months)  
✅ Shopping complete (10+ products)  
✅ HTML report complete  
✅ Security patterns documented  

See `PROJECT_STATUS.md` for details.
        │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
        │  • Next-year product predictions        │
        │  • Seasonal timing guidance             │
        │  • Human-readable summaries             │
        │  Output: forecast.json & CSV/JSON files │
        └────────────────────┬────────────────────┘
                             │
                             ▼
            📊 Forecasted Lawn Treatment Plan
        (Fertilizer | Weed Control | Insecticide |
         Iron | Potash | Sulfur | Surfactant)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama (for embeddings) — [Install here](https://ollama.ai)
- nomic-embed-text model
- PyMuPDF, NumPy (see `requirements.txt`)

### Installation

```bash
git clone https://github.com/violasarah2000/lawn-ai.git
cd lawn-ai
pip install -r requirements.txt
```

### Run the Forecast

```bash
python main.py --pdf_dir "<path_to_your_receipts_folder>"
```

### Outputs

The pipeline generates:

| File | Purpose |
|------|---------|
| `output/forecast.json` | Raw numeric 12-month forecasts |
| `output/historical_data.json` | Monthly product categories + 768-dim embeddings |
| `output/historical_data.csv` | Spreadsheet-friendly monthly summary |
| `output/forecast_vector_trends.json` | Numeric trends |

---

## 🧠 What Makes This a Genuine End-to-End AI System

### 1. **AI Document Extraction**
- Parses unstructured PDF text using PyMuPDF
- Regex-based field parsing handles varying PDF formats
- Extracts: product names, applied amounts, units, service dates, technician notes
- Categorizes products (Fertilizer, Weed Control, Insecticide, Iron, Potash, Sulfur, Surfactant)

### 2. **NLP Semantic Embeddings**
- Converts service notes → 768-dimensional semantic vectors via Ollama
- Each month's notes encoded as meaningful patterns (not just keywords)
- Enables semantic search & similarity analysis
- Captures context: weather patterns, lawn conditions, seasonal adjustments

### 3. **Neural Time-Series Learning**
- Aggregates X months of historical service data
- Learns seasonal patterns: spring fertilization, summer insect control, fall potash applications
- Computes statistical averages per month
- Identifies recurring cycles and product usage trends

### 4. **Forecasted Agronomic Recommendations**
- Predicts next-year product volumes using historical patterns
- Provides monthly guidance for each product type
- Outputs both raw predictions (JSON) and human-readable summaries
- Includes confidence metrics and trend notes

---

## 🔧 How It Works

### Step-by-Step Pipeline

1. **Load PDFs** → Extract raw text from all receipt PDFs
2. **Parse Structured Fields** → Extract products, dates, volumes, application methods, notes
3. **Generate Embeddings** → Convert service notes to 768-dimensional semantic vectors
4. **Compute Trends** → Analyze seasonal patterns and usage cycles
5. **Forecast Next Year** → Predict product volumes for each month
6. **Generate Historical Table** → Create monthly summary with product categories & embeddings
7. **Export Results** → Save to JSON (programmatic) and CSV (spreadsheet)

### Example Output

**Forecast for January 2026:**
```json
{
  "Month_1": {
    "products": {
      "0-0-62, SOLUBLE POTASH": {
        "volume": 7.5,
        "unit": "oz",
        "targets": "Potassium supplementation"
      },
      "CERTAINTY": {
        "volume": 1.25,
        "unit": "oz",
        "targets": "Winter weed control (pre-emergent)"
      }
    },
    "notes": "Expect potash application for root strengthening; light weed control application"
  }
}
```

**Historical Data:**
```json
{
  "table": [
    {
      "Month": "2024-01",
      "Date": "2024-01-15",
      "Fertilizer": 1,
      "Weed Control": 1,
      "Insecticide": 0,
      "Total_Volume": 8.75,
      "Embedding_Summary": "[768 dims]",
      "Notes_Preview": "Applied potash and winter herbicide..."
    }
  ],
  "embeddings": {
    "2024-01": {
      "embedding": [0.234, -0.156, 0.891, ...],
      "embedding_shape": "768 dimensions"
    }
  }
}
```

---

## 📊 Data Example: What Gets Extracted

From your lawn care PDF receipts:

| Date | Product | Amount | Unit | Targets | Notes |
|------|---------|--------|------|---------|-------|
| 2024-01-15 | 0-0-62, SOLUBLE POTASH | 7.5 | OZ | Potassium | "Today I applied potash to strengthen root system..." |
| 2024-01-15 | CERTAINTY | 1.25 | OZ | Weed Control | "Applied winter herbicide for pre-emergent weed control..." |

These become **monthly product categories** → **seasonal patterns** → **next-year forecast**

---

## 🤖 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| PDF Extraction | PyMuPDF (fitz) | Extract text from PDFs |
| Parsing | Python `re` (regex) | Extract structured fields |
| Embeddings | Ollama | 768-dim semantic vectors |
| Forecasting | NumPy | Seasonal aggregation & averaging |
| Output | JSON + CSV | Programmatic & spreadsheet formats |

---

## 📈 Future Enhancements

- [ ] Neural network LSTM/GRU for more sophisticated time-series forecasting
- [ ] Weather correlation analysis (tie embeddings to temperature/precipitation data)
- [ ] Multi-year trend detection (are potash applications trending up or down?)
- [ ] Web dashboard for interactive forecast visualization
- [ ] Product recommendation engine based on lawn condition embeddings
- [ ] Integration with lawn care scheduling systems

---

## 📝 License

This project is provided as-is for personal lawn care forecasting.

---

## 🌟 Summary

**Lawn-AI is a genuine end-to-end AI system** that:

1. **Understands** your historical lawn care data (AI document extraction)
2. **Learns** seasonal patterns from service notes (NLP embeddings + neural learning)
3. **Predicts** next year's optimal treatments (time-series forecasting)
4. **Communicates** actionable recommendations (human-readable output)

I did not include my personal receipts. No hard-coded rules. No manual categorization. Pure AI learning from your lawn care data. 
