# 🎵 Meta-Googler

**Song Metadata Management System with AI-Powered Suggestions & Intelligent Cover Art Integration**

A comprehensive desktop application for managing music metadata, identifying songs using AI fingerprinting, and intelligently fetching cover artwork. Built with Python, featuring a modern GUI and multi-model LLM support.

## ✨ Features

### Core Capabilities
- 🎼 **Song Identification**: Automatically identify songs using audio fingerprinting (AudD API)
- 📝 **Metadata Management**: Edit and organize music tags (title, artist, album, genre, date, etc.)
- 🤖 **AI Suggestions**: Get intelligent metadata suggestions powered by LLMs (Ollama, GPT-4, Claude, etc.)
- 🖼️ **Cover Art**: Intelligent cover art fetching and embedding from multiple sources
- 📦 **Batch Processing**: Process multiple files at once
- 🎛️ **Modern GUI**: CustomTkinter-based interface with metadata sidebar and real-time editing

### Advanced Features
- **Multi-Model LLM Support**: Switch between 13+ LLM providers (Phase 1 complete)
- **Middle-of-Song Audio Sampling**: Optimized audio extraction for better identification accuracy
- **Auto-Rename**: Automatically rename files to "Artist - Title" format on save
- **Metadata Validation**: Comprehensive validation with issue reporting
- **Free APIs**: Uses free and affordable APIs (no expensive premium services required)

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/amir-seraj/MetaGoogler.git
cd MetaGoogler

# Install with dependencies
make install

# Or manually:
pip install -e .
```

### Running the Application

```bash
# Option 1: Using make
make run

# Option 2: Direct Python
python -m src.main

# Option 3: After package installation
meta-googler
```

## 📋 Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

For complete setup with all features:
- [Ollama](https://ollama.ai) (for local LLM - free and optional)
- Audio processing libraries (librosa, mutagen)

## 📚 Documentation

Complete documentation available in the `docs/` directory:

| Document | Purpose |
|----------|---------|
| [`docs/README.md`](docs/README.md) | Project overview |
| [`docs/MCP_LITELLM_GUIDE.md`](docs/MCP_LITELLM_GUIDE.md) | In-depth LiteLLM + MCP migration guide (Phases 1-3) |
| [`docs/MCP_LITELLM_QUICK_REF.md`](docs/MCP_LITELLM_QUICK_REF.md) | Quick reference for LiteLLM setup |
| [`docs/PHASE1_COMPLETE.md`](docs/PHASE1_COMPLETE.md) | Phase 1 completion summary |
| [`docs/SONG_IDENTIFICATION_GUIDE.md`](docs/SONG_IDENTIFICATION_GUIDE.md) | Song identification system details |
| [`docs/AI_FEATURE_GUIDE.md`](docs/AI_FEATURE_GUIDE.md) | AI features documentation |
| [`docs/COVER_ART_GUIDE.md`](docs/COVER_ART_GUIDE.md) | Cover art features guide |
| [`docs/SETUP_ACRCLOUD.md`](docs/SETUP_ACRCLOUD.md) | ACRCloud API setup |

## 🏗️ Project Structure

```
meta-googler/
├── src/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── app_gui.py                # GUI application
│   ├── song_identifier.py        # Song identification
│   ├── song_metadata_fixer_v2.py # Metadata management
│   ├── batch_process.py          # Batch processing
│   ├── ai_manager_v2.py          # LiteLLM AI manager
│   └── utils/                    # Supporting modules
│       ├── __init__.py
│       ├── cover_art_fetcher.py  # Cover art management
│       ├── suggestion_window.py  # UI suggestions
│       ├── config_manager.py     # Configuration
│       └── logger_setup.py       # Logging
├── docs/                         # Documentation
│   ├── MCP_LITELLM_GUIDE.md     # Complete upgrade guide
│   ├── PHASE1_COMPLETE.md       # Phase 1 summary
│   ├── SONG_IDENTIFICATION_GUIDE.md
│   ├── AI_FEATURE_GUIDE.md
│   └── ...
├── config/                       # Configuration files
├── tests/                        # Test suite
├── pyproject.toml               # Project configuration
├── setup.py                     # Setup script
├── requirements.txt             # Dependencies
├── Makefile                     # Development commands
└── README.md                    # This file
```

## 🛠️ Development

### Install Development Dependencies

```bash
make dev-install
```

### Running Tests

```bash
make test
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format
```

### Build Documentation

```bash
make docs
```

## 🎯 Current Status

### Phase 1: ✅ Complete
- Song identification system (AudD API)
- GUI with metadata sidebar and auto-rename
- LiteLLM multi-model AI support (13+ providers)
- Audio sampling optimization (middle-of-song)
- All tests passing

### Phase 2: 📋 Ready (Not Yet Implemented)
- MCP server for Spotify (real metadata + audio features)
- MCP server for MusicBrainz (comprehensive database)
- LLM tool-use integration for enhanced suggestions

### Phase 3: 🎯 Future
- Advanced MCP + LLM integration
- Real-time metadata enrichment
- Automated playlist generation

## 🔧 Configuration

### Environment Variables

```bash
# LLM Configuration
LLM_MODEL=ollama/mistral          # Default model
OLLAMA_BASE_URL=http://localhost:11434

# Cloud LLM APIs (optional)
OPENAI_API_KEY=sk-...            # For GPT-4
ANTHROPIC_API_KEY=sk-ant-...     # For Claude
GOOGLE_API_KEY=...               # For Gemini

# Music APIs
AUDD_API_TOKEN=...               # For song identification
ACRCLOUD_ACCESS_KEY=...          # Alternative identification API
```

### Configuration Files

See `config/` directory for template configuration files.

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

**Author**: Amir Seraj

For questions or issues, please open an issue on GitHub.

---

**Last Updated**: November 8, 2025  
**Current Version**: 1.0.0  
**Status**: Beta - Fully functional, ready for production use
