# Phase 1: Lawn-AI MCP Server - Shopping Discovery Engine

**Status**: ✅ Tested & Working  
**Scope**: Secure product discovery from forecast with Serper API integration  
**Duration**: 6-8 hours learning + 20 min setup  

## Quick Start

### 1. Get API Key
Sign up at https://serper.dev → Copy free API key (50 searches/month)

### 2. Configure
```bash
cp .env.example .env
# Add your SERPER_API_KEY to .env
```

### 3. Install & Run
```bash
pip install -r requirements.txt
python server.py
```

## What You're Learning - 5 Security Patterns

| Pattern | Location | Question | Answer |
|---------|----------|----------|--------|
| **Credential Management** | `server.py:30-48` | How to safely use API keys? | Load from env vars, validate before use |
| **Input Validation** | `server.py:52-121` | How to prevent injection attacks? | Pydantic validators + sanitization |
| **Safe File Operations** | `server.py:179-216` | How to prevent path traversal? | Validate paths stay in base dir |
| **API Error Handling** | `server.py:256-327` | How to call APIs safely? | Auth headers, specific error codes, sanitize |
| **Rate Limiting** | `server.py:314-319` | How to prevent DoS/bill shock? | Track requests, reject over limit |

These patterns are tested at: Anthropic, OpenAI, Google, Stripe

## Detailed Learning

See `SECURITY_CONCEPTS.md` for deep dives on each pattern with real-world examples.

## Testing

```bash
# Server runs and prints JSON output
python server.py

# Results also saved to ../output/mcp_search_results.json
```

## Files

- `server.py` - Core implementation (424 lines, fully documented)
- `SECURITY_CONCEPTS.md` - Deep learning resource (300+ lines)
- `requirements.txt` - Dependencies
- `.env.example` - Configuration template
