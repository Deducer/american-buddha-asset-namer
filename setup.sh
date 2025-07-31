#!/bin/bash

echo "🎬 American Buddha Asset Namer - Setup Script"
echo "==========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    echo "   You can download it from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo ""
echo "📁 Creating project directories..."
mkdir -p src
mkdir -p config
mkdir -p logs
mkdir -p temp

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "🔑 OpenAI API Key Setup"
    echo "----------------------"
    echo "To use the AI content recognition features, you'll need an OpenAI API key."
    echo "You can get one at: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    
    if [ ! -z "$api_key" ]; then
        echo "OPENAI_API_KEY=$api_key" > .env
        echo "✅ API key saved to .env file"
    else
        echo "OPENAI_API_KEY=your-api-key-here" > .env
        echo "⚠️  No API key provided. Please edit the .env file later."
    fi
fi

# Create default config if it doesn't exist
if [ ! -f config/config.json ]; then
    echo ""
    echo "⚙️  Creating default configuration..."
    cat > config/config.json << 'EOF'
{
    "naming_patterns": {
        "default": "{date}_{description}_{sequence}",
        "documentary": "{project}_{scene}_{date}_{number}",
        "location_based": "{location}_{subject}_{action}_{counter}"
    },
    "supported_formats": {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
        "videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"]
    },
    "ai_settings": {
        "model": "gpt-4-vision-preview",
        "max_tokens": 150,
        "temperature": 0.7,
        "detail_level": "auto"
    },
    "processing": {
        "batch_size": 10,
        "preview_thumbnails": true,
        "backup_originals": true,
        "max_file_size_mb": 100
    },
    "output": {
        "date_format": "%Y-%m-%d",
        "sequence_padding": 3,
        "lowercase_names": false,
        "replace_spaces": "_"
    }
}
EOF
fi

# Make run script executable
echo ""
echo "🔧 Setting up run script..."
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python src/main.py
EOF
chmod +x run.sh

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo ""
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Application
logs/
temp/
*.log
processed_files/
backup/

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover
EOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the app:"
echo "   ./run.sh"
echo ""
echo "📖 Or manually:"
echo "   source venv/bin/activate"
echo "   python src/main.py"
echo ""
echo "⚠️  Remember to add your OpenAI API key to the .env file if you haven't already!"