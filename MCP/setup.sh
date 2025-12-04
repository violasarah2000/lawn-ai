#!/bin/bash
# Phase 1 Quick Setup Script

echo "🚀 Lawn-AI MCP Phase 1 Setup"
echo "================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Copy environment template
echo "✓ Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env file - UPDATE IT with your SERPER_API_KEY"
else
    echo "  .env already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo ""
echo "1. Get Serper API Key:"
echo "   - Visit https://serper.dev"
echo "   - Sign up (free tier)"
echo "   - Copy your API key"
echo ""
echo "2. Update .env file:"
echo "   - nano .env (or open in your editor)"
echo "   - Replace 'your_serper_api_key_here' with your actual key"
echo ""
echo "3. Run the server:"
echo "   - python server.py"
echo ""
echo "4. Study the code:"
echo "   - Read README.md for overview"
echo "   - Read SECURITY_CONCEPTS.md to understand why each pattern matters"
echo "   - Read server.py comments to see security implementation"
echo ""
