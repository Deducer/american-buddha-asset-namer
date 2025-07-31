# American Buddha Asset Namer

A powerful Mac application for bulk naming and renaming image and video files using AI-powered content recognition. Designed specifically for documentary teams to maintain organized asset libraries.

## Features

- 🖼️ **Content Recognition**: Automatically analyzes images and videos to generate descriptive names
- 📁 **Bulk Processing**: Process entire folders of media files at once
- 🏷️ **Custom Naming Conventions**: Define your own naming patterns and standards
- 🎥 **Multi-format Support**: Works with common image formats (JPEG, PNG, etc.) and video formats (MP4, MOV, etc.)
- 💻 **Native Mac App**: Built with Python and Tkinter for a smooth Mac experience
- 🤖 **AI-Powered**: Uses OpenAI's Vision API for intelligent content analysis

## Installation

### Prerequisites
- macOS 10.15 or later
- Python 3.8 or later
- OpenAI API key (for content recognition)

### Quick Install (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/american-buddha-asset-namer.git
cd american-buddha-asset-namer
```

2. Run the setup script:
```bash
./setup.sh
```

3. Add your OpenAI API key when prompted, or manually create a `.env` file:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Manual Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key

## Usage

### Running the App

```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
python src/main.py
```

### Quick Start

1. Launch the app
2. Select a folder containing your media files
3. Configure your naming convention (or use defaults)
4. Click "Process Files" to analyze and rename
5. Review the suggested names and apply changes

### Naming Convention Examples

- `YYYY-MM-DD_Description_SequenceNumber`
- `ProjectName_SceneType_Date_Number`
- `Location_Subject_Action_Counter`

## Team Setup

For team members to install:

1. Share the repository URL
2. Team members clone the repo
3. Run `./setup.sh`
4. Add their OpenAI API key
5. Ready to use!

## Configuration

Edit `config.json` to customize:
- Default naming patterns
- File type filters
- AI analysis settings
- Output preferences

## Support

For issues or questions, please create an issue in the repository.