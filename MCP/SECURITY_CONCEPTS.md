# Phase 1 Security Concepts Reference

## 1. Credential Management

### The Problem
```python
# ❌ INSECURE
SERPER_API_KEY = "abc123def456xyz"  # Committed to GitHub!
# Now everyone on GitHub has your key
```

### The Solution
```python
# ✅ SECURE
class APICredentials:
    def __init__(self):
        self.key = os.getenv("SERPER_API_KEY")  # Load from .env
        if not self.key:
            raise ValueError("SERPER_API_KEY not set")
```

### Why It Matters
- Your API key is like a password to your account
- If committed to GitHub, anyone can use it
- Costs YOU money if someone abuses it
- At companies: Getting fired if you commit secrets

### Real-World Example
- January 2023: GitHub scanning found 400,000+ API keys leaked
- Each key represents a potential $10,000+ bill if misused
- Companies now use secret vaults (HashiCorp Vault, AWS Secrets Manager, Google Secret Manager)

---

## 2. Input Validation & Sanitization

### The Problem: Prompt Injection
```python
# ❌ INSECURE
product_name = "potash; DROP TABLE products; --"
query = f"Find me {product_name}"
# Sends to LLM: "Find me potash; DROP TABLE products; --"
# LLM might interpret as: "DROP TABLE products"
```

### The Solution: Validation & Sanitization
```python
# ✅ SECURE with Pydantic
class Product(BaseModel):
    name: str = Field(..., max_length=500)
    
    @validator('name')
    def sanitize_name(cls, v):
        dangerous = ['$', '`', '$(' '{', '}', '|', '&', ';']
        for char in dangerous:
            v = v.replace(char, '')
        return v

# Now: "potash; DROP TABLE products; --"
# Becomes: "potash DROP TABLE products --" (safe)
```

### Why It Matters
- SQL Injection: Hackers could delete databases
- Prompt Injection: LLMs could be manipulated to do unexpected things
- Command Injection: System could execute malicious commands
- Path Traversal: Access files outside intended directory

### Real-World Example
- March 2023: OpenAI Plugin vulnerability allowed prompt injection
- November 2023: LLM injection attacks detected in the wild
- Now a top security concern in AI systems

---

## 3. Safe File Operations

### The Problem: Path Traversal
```python
# ❌ INSECURE
forecast_file = user_input  # User enters: "../../etc/passwd"
with open(forecast_file) as f:
    data = json.load(f)
# Now you've read the system password file!
```

### The Solution: Path Validation
```python
# ✅ SECURE
file_path = Path(user_input)
base_dir = Path(".")

if not str(file_path.resolve()).startswith(str(base_dir.resolve())):
    raise ValueError("Path traversal attempt!")

if not file_path.exists():
    raise FileNotFoundError("File not found")

with open(file_path) as f:
    data = json.load(f)
```

### Why It Matters
- Prevents reading sensitive files (/etc/passwd, ~/.ssh/id_rsa)
- Prevents reading other users' data
- At companies: GDPR/HIPAA violations if you read patient data by accident

---

## 4. API Error Handling

### The Problem: Leaking Secrets in Errors
```python
# ❌ INSECURE
try:
    response = requests.get(url)
except Exception as e:
    return str(e)  # Returns: "Connection to API_URL failed with key=abc123def"
    # Hacker sees your API key in error message!
```

### The Solution: Sanitized Error Messages
```python
# ✅ SECURE
try:
    response = requests.get(url, headers={"X-API-KEY": key})
except Exception as e:
    # Log full error internally
    logger.error(f"API error: {e}")
    # Return sanitized error to user
    raise RuntimeError("API request failed - please try again")
    # Hacker only sees: "API request failed"
```

### Why It Matters
- Error messages can leak credentials, versions, internal paths
- Hackers use verbose errors to find vulnerabilities
- At companies: Stack traces are classified information

---

## 5. Rate Limiting

### The Problem: DoS Attack
```python
# ❌ INSECURE - No rate limit
for i in range(1000000):
    result = searcher.search_product(...)
# Makes 1 million API calls in seconds
# Costs you $$$, API provider blocks you
```

### The Solution: Rate Limiting
```python
# ✅ SECURE
class ProductSearcher:
    def __init__(self):
        self.request_count = 0
        self.max_requests_per_minute = 60
    
    async def search_product(self, request):
        if self.request_count >= self.max_requests_per_minute:
            raise RuntimeError("Rate limit exceeded")
        # ... make API call ...
        self.request_count += 1
```

### Why It Matters
- Prevents API abuse
- Protects against Denial of Service attacks
- At companies: Required for security compliance (PCI-DSS, HIPAA)

---

## Learning Path

### Understanding the Attacks
1. Read OWASP Top 10: https://owasp.org/www-project-top-ten/
2. Understand: SQL Injection, Command Injection, Path Traversal
3. See how: Prompt Injection is similar to SQL Injection

### Implementing Defenses
1. Always validate input (type, length, format)
2. Always sanitize input (remove dangerous characters)
3. Never log secrets
4. Always handle errors gracefully
5. Always rate limit external API calls

### Testing Your Implementation
1. Try to break it (security testing)
2. Fuzz with unexpected input
3. Check error messages don't leak secrets
4. Verify rate limiting works

---

## Resources to Learn More

### Beginner
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- PortSwigger Web Security Academy: https://portswigger.net/web-security

### Intermediate
- SANS Institute: https://www.sans.org/reading-room/
- CWE (Common Weakness Enumeration): https://cwe.mitre.org/

### Advanced
- Prompt Injection: https://arxiv.org/abs/2304.14970
- API Security: https://www.owasp.org/index.php/API_Security

---

## Checklist for Your Code

Before deploying ANY code to production:

- [ ] No secrets in code or error messages
- [ ] All user input validated (type, length, format)
- [ ] All user input sanitized (dangerous chars removed)
- [ ] File operations check path doesn't escape base directory
- [ ] API errors don't leak sensitive information
- [ ] Rate limiting implemented
- [ ] Logging in place (who called what, when)
- [ ] Tests cover invalid input scenarios
- [ ] Security headers configured (if applicable)

---

## Why This Matters for Your Career

These concepts are:
✅ Tested in job interviews (Google, Amazon, etc.)
✅ Required for AI Security Engineer roles
✅ Directly applicable to production systems
✅ What distinguishes junior from senior engineers

Companies like Anthropic, OpenAI, Google hire specifically for:
- Understanding of API security
- Input validation rigor
- Error handling sophistication
- Rate limiting & cost control

Building this MCP server teaches exactly these skills.
