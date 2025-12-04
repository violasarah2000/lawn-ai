"""
Phase 1 Lawn-AI MCP Server
MVP for product discovery from lawn care forecasts

Learning focus:
- API authentication & credential management
- Input validation & sanitization
- Error handling
"""

import json
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables
load_dotenv()

# ============================================================================
# SECURITY: Credential Management
# ============================================================================
class APICredentials:
    """
    Learning Point: Secure credential management
    - Load from environment variables (never hardcode)
    - Validate credentials exist before using
    - Handle missing credentials gracefully
    """
    
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable not set")
    
    def get_serper_key(self) -> str:
        """Return API key for Serper service"""
        if not self.serper_api_key:
            raise RuntimeError("Serper API key not initialized")
        return self.serper_api_key


# ============================================================================
# DATA MODELS: Input Validation & Sanitization
# ============================================================================
class Product(BaseModel):
    """
    Learning Point: Pydantic for input validation
    - Type checking (name is string, volume is float)
    - Value constraints (volume > 0)
    - Custom validators for security
    """
    
    name: str = Field(..., min_length=1, max_length=500)
    volume: float = Field(..., gt=0, lt=1000)  # Must be positive, reasonable limit
    unit: str = Field(..., min_length=1, max_length=20)
    targets: str = Field(default="", max_length=500)
    month: str = Field(..., min_length=7, max_length=7)  # YYYY-MM format
    
    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """
        Learning Point: Input sanitization
        - Strip whitespace
        - Remove dangerous characters
        - Prevent prompt injection
        """
        v = v.strip()
        # Remove special characters that could cause injection
        dangerous_chars = ['$', '`', '$(', '{', '}', '|', '&', ';']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v
    
    @field_validator('month')
    @classmethod
    def validate_month_format(cls, v: str) -> str:
        """Validate month is in YYYY-MM format"""
        if len(v) != 7 or v[4] != '-':
            raise ValueError("Month must be in YYYY-MM format")
        try:
            year, month = v.split('-')
            int(year)
            int(month)
            if not (1 <= int(month) <= 12):
                raise ValueError("Month must be 01-12")
        except ValueError as e:
            raise ValueError(f"Invalid month format: {e}")
        return v


class ForecastRequest(BaseModel):
    """
    Learning Point: Request validation
    - Validate entire request structure before processing
    - Set reasonable limits to prevent DoS
    """
    
    forecast_file: str = Field(..., max_length=1000)  # Prevent path traversal
    limit_products: int = Field(default=10, ge=1, le=100)  # Rate limiting
    
    @field_validator('forecast_file')
    @classmethod
    def prevent_path_traversal(cls, v: str) -> str:
        """
        Learning Point: Security validation
        - Prevent directory traversal attacks
        - Only allow specific directory
        """
        # Remove any path traversal attempts
        v = v.replace('..', '').replace('//', '/')
        if v.startswith('/'):
            raise ValueError("Path must be relative")
        return v


class ProductSearchRequest(BaseModel):
    """Request for searching a product"""
    product_name: str = Field(..., min_length=1, max_length=500)
    quantity: float = Field(..., gt=0, lt=1000)
    unit: str = Field(..., min_length=1, max_length=20)
    
    @field_validator('product_name')
    @classmethod
    def sanitize_product_name(cls, v: str) -> str:
        """Sanitize product name to prevent API abuse"""
        v = v.strip()
        # Remove injection characters
        dangerous_chars = ['$', '`', '$(', '{', '}', '|', '&', ';', '<', '>']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v


# ============================================================================
# CORE LOGIC
# ============================================================================
class ForecastParser:
    """
    Learning Point: Reading and parsing external data
    - Validate file exists and is readable
    - Parse JSON safely
    - Handle malformed data gracefully
    """
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
    
    def read_forecast(self, forecast_file: str) -> dict:
        """
        Read and validate forecast file
        
        Learning: Safe file operations with error handling
        """
        try:
            file_path = self.base_dir / forecast_file
            
            # Resolve to absolute path
            resolved_file = file_path.resolve()
            resolved_base = self.base_dir.resolve()
            
            # Security: Check file exists first
            if not resolved_file.exists():
                raise FileNotFoundError(f"Forecast file not found: {file_path}")
            
            # Check if resolved file is under base directory (prevent traversal outside)
            try:
                resolved_file.relative_to(resolved_base)
            except ValueError:
                raise ValueError("Path traversal attempt detected")
            
            with open(resolved_file, 'r') as f:
                data = json.load(f)
            
            return data
        except FileNotFoundError as e:
            raise ValueError(f"Cannot read forecast: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in forecast file: {e}")
    
    def extract_products(self, forecast: dict, limit: int = 10) -> list[Product]:
        """
        Extract products from forecast
        
        Learning: Robust parsing with validation
        - Handle missing fields gracefully
        - Validate each product
        - Apply limits to prevent memory issues
        """
        products = []
        count = 0
        
        for month_key, month_data in forecast.items():
            if count >= limit:
                break
            
            # Extract month from key (e.g., "Month_1" -> "2025-01")
            try:
                month_num = int(month_key.split('_')[1])
                month_str = f"2025-{month_num:02d}"
            except (ValueError, IndexError):
                # Skip invalid month keys
                continue
            
            # Extract products from this month
            month_products = month_data.get('products', {})
            for product_name, product_data in month_products.items():
                if count >= limit:
                    break
                
                try:
                    # Validate and create product
                    product = Product(
                        name=product_name,
                        volume=float(product_data.get('volume', 0)),
                        unit=product_data.get('unit', 'oz'),
                        targets=product_data.get('targets', ''),
                        month=month_str
                    )
                    products.append(product)
                    count += 1
                except Exception as e:
                    # Log but don't crash on invalid product
                    print(f"Warning: Could not parse product '{product_name}': {e}")
                    continue
        
        return products


class ProductSearcher:
    """
    Learning Point: External API integration
    - Authenticate with API keys
    - Handle API errors gracefully
    - Rate limiting
    - Response validation
    """
    
    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self.client = httpx.AsyncClient(timeout=30.0)
        self.request_count = 0
        self.max_requests_per_minute = 60  # Rate limiting
    
    async def search_product(self, search_request: ProductSearchRequest) -> dict:
        """
        Search for product using Serper API
        
        Learning: API integration with error handling
        - Add authentication
        - Handle rate limiting
        - Validate responses
        - Graceful error handling
        """
        try:
            # Rate limiting check
            if self.request_count >= self.max_requests_per_minute:
                raise RuntimeError("Rate limit exceeded - too many requests")
            
            # Prepare request
            headers = {
                "X-API-KEY": self.credentials.get_serper_key(),
                "Content-Type": "application/json"
            }
            
            # Construct search query
            query = f"{search_request.product_name} {search_request.unit} lawn care"
            
            payload = {
                "q": query,
                "num": 5,  # Limit results
                "gl": "us"  # Geo-target
            }
            
            # Make API call
            response = await self.client.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers
            )
            
            # Increment counter for rate limiting
            self.request_count += 1
            
            # Validate response
            if response.status_code == 401:
                raise ValueError("Invalid Serper API key")
            elif response.status_code == 429:
                raise RuntimeError("API rate limit exceeded")
            elif response.status_code != 200:
                raise RuntimeError(f"API error: {response.status_code}")
            
            data = response.json()
            
            # Validate response structure
            if not isinstance(data, dict):
                raise ValueError("Invalid API response format")
            
            return self._format_results(data, search_request)
        
        except httpx.TimeoutException:
            raise RuntimeError("API request timeout")
        except httpx.RequestError as e:
            raise RuntimeError(f"API request failed: {e}")
    
    def _format_results(self, api_response: dict, request: ProductSearchRequest) -> dict:
        """
        Learning Point: Response validation & formatting
        - Extract relevant fields from API
        - Validate data types
        - Return consistent format
        """
        results = {
            "product": request.product_name,
            "quantity": request.quantity,
            "unit": request.unit,
            "search_results": []
        }
        
        # Extract results safely
        for result in api_response.get('organic', [])[:3]:  # Limit to 3
            if 'title' in result and 'link' in result:
                results['search_results'].append({
                    'title': result['title'][:200],  # Truncate
                    'url': result['link'][:500],
                    'snippet': result.get('snippet', '')[:300]
                })
        
        return results
    
    async def close(self):
        """Cleanup resources"""
        await self.client.aclose()


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================
class LawnAIMCPPhase1:
    """
    Phase 1 MCP Server
    
    Learning Points:
    - Orchestrating multiple components
    - Error handling at system level
    - Logging for audit trail
    """
    
    def __init__(self, forecast_path: str = "output/forecast.json"):
        self.forecast_path = forecast_path
        self.credentials = APICredentials()
        # base_dir is project root (parent of MCP directory)
        self.parser = ForecastParser("..")
        self.searcher = ProductSearcher(self.credentials)
    
    async def process_forecast(self) -> dict:
        """
        Main pipeline:
        1. Read forecast
        2. Extract products
        3. Search each product
        4. Return shopping recommendations
        """
        try:
            # Load and parse forecast
            forecast = self.parser.read_forecast(self.forecast_path)
            products = self.parser.extract_products(forecast)
            
            # Search each product
            shopping_list = {
                "products": [],
                "total_count": len(products),
                "errors": []
            }
            
            for product in products:
                try:
                    search_request = ProductSearchRequest(
                        product_name=product.name,
                        quantity=product.volume,
                        unit=product.unit
                    )
                    
                    result = await self.searcher.search_product(search_request)
                    shopping_list["products"].append(result)
                
                except Exception as e:
                    # Log error but continue processing
                    shopping_list["errors"].append({
                        "product": product.name,
                        "error": str(e)
                    })
            
            return shopping_list
        
        except Exception as e:
            raise RuntimeError(f"Error processing forecast: {e}")
    
    async def close(self):
        """Cleanup"""
        await self.searcher.close()


# ============================================================================
# QUICK TEST
# ============================================================================
if __name__ == "__main__":
    import asyncio
    
    async def test():
        try:
            server = LawnAIMCPPhase1()
            result = await server.process_forecast()
            
            # Print to stdout
            print(json.dumps(result, indent=2))
            
            # Also save to output file
            output_file = Path("../output/mcp_search_results.json")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n✓ Results saved to {output_file}", file=__import__('sys').stderr)
            
            await server.close()
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test())
