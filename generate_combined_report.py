"""
Generate a combined forecast + shopping recommendation HTML report

This script integrates:
1. Lawn care forecast (what to apply when)
2. MCP shopping recommendations (where to buy each product)
3. Creates a single, clean HTML report for reference
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_forecast():
    """Load forecast.json"""
    with open("output/forecast.json", "r") as f:
        return json.load(f)

def load_mcp_results():
    """Load MCP search results"""
    try:
        with open("output/mcp_search_results.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"products": [], "errors": []}

def create_shopping_references(mcp_results):
    """Create a lookup dict of product name -> shopping options"""
    shopping = {}
    for product_info in mcp_results.get("products", []):
        product_name = product_info.get("product", "")
        search_results = product_info.get("search_results", [])
        shopping[product_name] = {
            "quantity": product_info.get("quantity", 0),
            "unit": product_info.get("unit", ""),
            "results": search_results
        }
    return shopping

def generate_html_report(forecast, shopping):
    """Generate comprehensive HTML report"""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lawn-AI Forecast & Shopping Guide</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c5f2d 0%, #1a3a1b 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .timestamp {
            text-align: center;
            padding: 15px 30px;
            background: #f0f0f0;
            color: #666;
            font-size: 0.9em;
            border-bottom: 1px solid #ddd;
        }
        
        .content {
            padding: 30px;
        }
        
        .month-section {
            margin-bottom: 40px;
            page-break-inside: avoid;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .month-header {
            background: linear-gradient(135deg, #4a7c4e 0%, #2c5f2d 100%);
            color: white;
            padding: 20px;
            font-size: 1.5em;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .month-header .month-number {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }
        
        .month-content {
            padding: 20px;
        }
        
        .products-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .products-table thead {
            background: #f5f5f5;
        }
        
        .products-table th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
            color: #333;
        }
        
        .products-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        .products-table tr:hover {
            background: #fafafa;
        }
        
        .product-name {
            font-weight: 600;
            color: #2c5f2d;
        }
        
        .shopping-section {
            background: #f9f9f9;
            border-left: 4px solid #4a7c4e;
            padding: 15px;
            margin-top: 15px;
            border-radius: 4px;
        }
        
        .shopping-section h4 {
            color: #2c5f2d;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .shopping-results {
            margin-left: 20px;
        }
        
        .shopping-option {
            background: white;
            border: 1px solid #ddd;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        .shopping-option:hover {
            border-color: #4a7c4e;
            box-shadow: 0 2px 8px rgba(74, 124, 78, 0.1);
        }
        
        .shopping-option-title {
            font-weight: 600;
            color: #2c5f2d;
            margin-bottom: 5px;
        }
        
        .shopping-option-snippet {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        .shopping-option-link {
            display: inline-block;
            background: #2c5f2d;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.85em;
            transition: background 0.3s;
        }
        
        .shopping-option-link:hover {
            background: #1a3a1b;
        }
        
        .notes {
            background: #fffacd;
            border-left: 4px solid #ffd700;
            padding: 15px;
            margin-top: 15px;
            border-radius: 4px;
            font-size: 0.95em;
            line-height: 1.6;
            color: #333;
        }
        
        .notes strong {
            color: #b8860b;
        }
        
        .no-shopping {
            color: #999;
            font-size: 0.9em;
            font-style: italic;
        }
        
        .footer {
            background: #f0f0f0;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
        }
        
        .summary-box {
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border: 2px solid #4a7c4e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .summary-box h3 {
            color: #2c5f2d;
            margin-bottom: 10px;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c5f2d;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
            }
            
            .month-section {
                page-break-inside: avoid;
            }
            
            .shopping-option-link {
                color: #2c5f2d;
                text-decoration: underline;
                background: none;
                border: 1px solid #2c5f2d;
            }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }
            
            .month-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .summary-stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 Lawn-AI Forecast & Shopping Guide</h1>
            <p>12-Month Lawn Treatment Plan with Product Recommendations</p>
        </div>
        
        <div class="timestamp">
            Generated on """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """
        </div>
"""
    
    # Add summary
    total_months = len(forecast)
    total_products = sum(len(month.get("products", [])) for month in forecast.values())
    total_shopping = len(shopping)
    
    html += f"""
        <div class="content">
            <div class="summary-box">
                <h3>📊 Overview</h3>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-number">{total_months}</div>
                        <div class="stat-label">Months of Treatments</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{total_products}</div>
                        <div class="stat-label">Total Products</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{total_shopping}</div>
                        <div class="stat-label">Products with Shopping Links</div>
                    </div>
                </div>
            </div>
"""
    
    # Month names
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Generate month sections
    for i, (month_key, month_data) in enumerate(forecast.items()):
        month_num = i + 1
        month_name = month_names[i] if i < 12 else f"Month {month_num}"
        
        html += f"""
        <div class="month-section">
            <div class="month-header">
                <span>{month_name}</span>
                <span class="month-number">Month {month_num}</span>
            </div>
            <div class="month-content">
                <table class="products-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Unit</th>
                            <th>Target</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        products = month_data.get("products", {})
        notes = month_data.get("notes", "")
        
        if not products:
            html += "<tr><td colspan='4' style='text-align:center; color:#999;'>No treatments scheduled</td></tr>"
        
        for product_name, product_info in products.items():
            volume = product_info.get("volume", 0)
            unit = product_info.get("unit", "")
            targets = product_info.get("targets", "")
            
            html += f"""
                        <tr>
                            <td class="product-name">{product_name}</td>
                            <td>{volume}</td>
                            <td>{unit}</td>
                            <td>{targets}</td>
                        </tr>
"""
            
            # Add shopping recommendations if available
            if product_name in shopping:
                shop_info = shopping[product_name]
                results = shop_info.get("results", [])
                
                html += f"""
                        <tr>
                            <td colspan="4">
                                <div class="shopping-section">
                                    <h4>🛒 Where to Buy</h4>
                                    <div class="shopping-results">
"""
                
                if results:
                    for result in results[:3]:  # Show top 3 results
                        title = result.get("title", "Unknown")
                        url = result.get("url", "#")
                        snippet = result.get("snippet", "")
                        
                        html += f"""
                                        <div class="shopping-option">
                                            <div class="shopping-option-title">{title}</div>
                                            <div class="shopping-option-snippet">{snippet}</div>
                                            <a href="{url}" target="_blank" class="shopping-option-link">View Product →</a>
                                        </div>
"""
                else:
                    html += """
                                        <div class="no-shopping">No shopping results found. Try searching manually.</div>
"""
                
                html += """
                                    </div>
                                </div>
                            </td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
"""
        
        if notes:
            html += f"""
                <div class="notes">
                    <strong>📝 Notes from Treatment History:</strong><br>
                    {notes[:500]}{'...' if len(notes) > 500 else ''}
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            <p>💡 <strong>Pro Tip:</strong> Save this page as PDF (Print → Save as PDF) for a portable reference guide.</p>
            <p>Last updated: """ + datetime.now().strftime("%B %d, %Y") + """</p>
            <p>Powered by Lawn-AI Forecasting + MCP Shopping Discovery</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("📊 Generating combined forecast & shopping report...")
    
    # Load data
    forecast = load_forecast()
    mcp_results = load_mcp_results()
    shopping = create_shopping_references(mcp_results)
    
    # Generate HTML
    html_content = generate_html_report(forecast, shopping)
    
    # Save report
    output_path = "output/forecast_and_shopping_guide.html"
    os.makedirs("output", exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"✓ Report saved to {output_path}")
    print(f"✓ Forecast months: {len(forecast)}")
    print(f"✓ Products with shopping info: {len(shopping)}")
    
    return output_path

if __name__ == "__main__":
    main()
