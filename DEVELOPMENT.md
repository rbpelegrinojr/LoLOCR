# Development Guide for LoLOCR

This guide explains how to set up a development environment and contribute to LoLOCR.

## Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv)

## Setting Up Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/rbpelegrinojr/LoLOCR.git
cd LoLOCR
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Core dependencies (none for basic functionality)
pip install -e .

# For development and testing
pip install -r requirements-dev.txt
```

## Running Tests

### Run All Tests

```bash
python -m unittest test_lolecr -v
```

### Run Specific Test Class

```bash
python -m unittest test_lolecr.TestConfig -v
```

### Run Specific Test Method

```bash
python -m unittest test_lolecr.TestConfig.test_config_creation -v
```

## Running the Application

### Basic Usage (Demo Mode)

```bash
python main.py
```

This will run the application in demo mode, generating output files with placeholder data.

### Running with NDI Capture

1. Install NDI Runtime:
   ```bash
   # Follow instructions at https://ndi.video/tools/
   ```

2. Install NDI Python bindings:
   ```bash
   pip install pyndi
   ```

3. Run with NDI:
   ```bash
   python main.py
   ```
   
   The application will automatically detect available NDI sources.

### Running with Window Capture

```bash
pip install pyautogui pygetwindow pillow opencv-python
python main.py
```

Then edit `config.json` and set:
```json
{
  "capture": {
    "method": "window",
    "window": {
      "window_title": "League of Legends",
      "enabled": true
    }
  }
}
```

### Running with Screen Capture

```bash
pip install pillow opencv-python
python main.py
```

Then edit `config.json` and set:
```json
{
  "capture": {
    "method": "screen",
    "screen": {
      "monitor_index": 0,
      "enabled": true
    }
  }
}
```

## Code Structure

### Core Modules

- **config.py** - Configuration management
  - `Config` class handles loading/saving configuration
  - Supports dot notation for accessing nested settings
  - Provides helper methods for common configurations

- **game_state.py** - Game state management
  - `GameStateManager` class manages game data
  - Provides methods to update team and player statistics
  - Thread-safe state management

- **output_manager.py** - Output file generation
  - `OutputManager` class handles file I/O
  - Implements smart writes (only write if content changed)
  - Generates individual TXT files and JSON output
  - 500ms update cycle

- **capture.py** - Capture sources
  - `CaptureSource` abstract base class
  - `NDICapture` for NDI sources
  - `WindowCapture` for window capture
  - `ScreenCapture` for full screen capture
  - Factory function for creating sources

- **ocr.py** - OCR processing
  - `OCRProcessor` class for text recognition
  - Support for EasyOCR, PaddleOCR, pytesseract
  - Lazy loading of OCR engines
  - Debug mode with image/JSON saving

- **main.py** - Application entry point
  - `LoLOCRApplication` class manages the app lifecycle
  - Runs capture and output loops in separate threads
  - Handles graceful shutdown
  - Provides statistics tracking

### Test Module

- **test_lolecr.py** - Unit tests
  - `TestConfig` tests configuration management
  - `TestGameState` tests game state handling
  - `TestOutputManager` tests file output
  - `TestIntegration` tests full workflow

## Adding OCR Support

To add OCR processing capabilities:

1. Install an OCR backend:
   ```bash
   pip install easyocr
   # or
   pip install paddleocr
   # or
   pip install pytesseract
   ```

2. Enable OCR in `config.json`:
   ```json
   {
     "ocr": {
       "enabled": true,
       "debug": true,
       "save_crops": true
     }
   }
   ```

3. Implement the `_extract_game_data` method in `ocr.py` to parse OCR results

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and returns
- Add docstrings to all classes and methods
- Use meaningful variable names

## Adding New Features

### Adding a New Capture Method

1. Create a new class in `capture.py` that extends `CaptureSource`
2. Implement required abstract methods
3. Update `create_capture_source` factory function
4. Add tests in `test_lolecr.py`

### Adding a New Output Format

1. Extend `OutputManager.write_outputs()` method
2. Add configuration options to `config.py`
3. Add tests for the new format

### Adding New Game State Fields

1. Update `GameStateManager._init_state()` method
2. Add helper methods if needed
3. Update `OutputManager` to generate corresponding files
4. Update README with new fields
5. Add tests

## Debugging

### Enable Debug Mode

Edit `config.json`:
```json
{
  "ocr": {
    "debug": true,
    "save_crops": true
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

### Check Output Files

Generated files are in `output/` directory:
- Text files in `output/teams/`, `output/players/`, `output/objectives/`
- JSON in `output/game_state.json`
- Debug images in `output/debug/`

### Examine Logs

- Check console output for errors
- Look for `.log` files in `logs/` directory

## Performance Tips

- Use NDI capture when possible (faster than window/screen capture)
- Disable debug mode in production
- Increase update interval if CPU usage is high
- Use appropriate OCR backend (EasyOCR is recommended)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python -m unittest test_lolecr -v`
6. Submit a pull request

## Troubleshooting

### No NDI Sources Found

- Verify NDI Runtime is installed: https://ndi.video/tools/
- Run `ndi-auditioner.exe` to see available sources
- Check firewall settings (ports 5960-5968)

### Import Errors

- Make sure you're using the virtual environment
- Check that all dependencies are installed: `pip list`
- Verify Python version: `python --version`

### File Permission Errors

- Ensure write permissions on `output/` directory
- Check disk space availability

## Release Checklist

- [ ] Update version number
- [ ] Update CHANGELOG
- [ ] Run all tests
- [ ] Update README if needed
- [ ] Create release notes
- [ ] Tag release in git
- [ ] Build distribution package

## Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [NDI Documentation](https://ndi.video/)
- [OpenCV Documentation](https://docs.opencv.org/)

## License

[Add license information]

## Support

For issues and questions:
- Check existing issues on GitHub
- Create a new issue with detailed information
- Include steps to reproduce
- Attach relevant logs or screenshots
