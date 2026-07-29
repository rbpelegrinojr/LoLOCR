# Quick Start Guide for LoLOCR

Get started with LoLOCR in 5 minutes!

## Installation

### 1. Download LoLOCR

```bash
git clone https://github.com/rbpelegrinojr/LoLOCR.git
cd LoLOCR
```

### 2. Verify Python Version

```bash
python --version
# Requires Python 3.8 or higher
```

### 3. Run Application

```bash
python main.py
```

That's it! The application will:
- Create a `config.json` file with default settings
- Create an `output/` directory with subdirectories
- Generate output files in demo mode

## Using with NDI

If you want to capture League of Legends via NDI:

### 1. Install NDI Runtime

Visit https://ndi.video/tools/ and download NDI Tools for your operating system. Follow the installation steps in the main [README.md](README.md#ndi-installation-mandatory-for-ndi-capture).

### 2. Set Up OBS (If Needed)

If using OBS as your capture source:
- Install the [OBS NDI Plugin](https://github.com/Palakis/obs-ndi/releases)
- Enable NDI output in OBS (Tools → NDI Output Settings)
- Create a game capture source pointing to your League of Legends window

### 3. Configure LoLOCR

Edit `config.json` and set your NDI source name:

```json
{
  "capture": {
    "method": "ndi",
    "ndi": {
      "source_name": "OBS (Main):Main Output",
      "enabled": true
    }
  }
}
```

### 4. Run Application

```bash
python main.py
```

The application will connect to your NDI source and generate output files.

## Viewing Output Files

Check the `output/` directory for generated files:

```
output/
├── game_state.json              # All data in JSON format
├── gametime.txt                 # Current game time
├── teams/                       # Team data
│   ├── left_team_name.txt
│   ├── right_team_name.txt
│   ├── left_team_gold.txt
│   └── ...
├── players/                     # Player data
│   ├── left_player1_name.txt
│   ├── left_player1_champion.txt
│   └── ...
├── objectives/                  # Objective timers
│   ├── dragon_timer.txt
│   ├── baron_timer.txt
│   └── ...
└── debug/                       # Debug images and OCR results
    ├── latest_capture.png
    └── latest_ocr.json
```

## Using with OBS Overlay

### Using Text Files

1. Open OBS Studio
2. Add a new **Text (GDI+)** source to your scene
3. Click "Text from file"
4. Browse to a TXT file (e.g., `output/teams/left_team_name.txt`)
5. Click OK
6. Position and style the text source
7. Repeat for each stat you want to display

### Using JSON with Browser Source

1. Create an HTML file with JavaScript to read and display data from `output/game_state.json`
2. Add a **Browser** source in OBS
3. Point it to your HTML file
4. The overlay will update automatically

## Configuration

All settings are stored in `config.json`. Key options:

- **capture.method**: `ndi`, `window`, or `screen`
- **capture.ndi.source_name**: NDI source to capture from
- **output.update_interval_ms**: How often to update files (default: 500ms)
- **ocr.enabled**: Enable/disable OCR processing
- **ocr.debug**: Save debug images

See [README.md](README.md#configuration) for complete configuration details.

## Troubleshooting

### No NDI sources found?
- Verify NDI Runtime is installed
- Run `ndi-auditioner.exe` from NDI Tools
- Check firewall settings (ports 5960-5968)
- See [NDI Troubleshooting](README.md#step-10-troubleshooting-ndi-issues)

### Files not updating?
- Check `output.update_interval_ms` in config
- Verify write permissions on `output/` directory
- Check disk space

### Application won't start?
- Verify Python 3.8+ is installed
- Check `config.json` for syntax errors (should be valid JSON)
- See [Troubleshooting](README.md#troubleshooting)

## Next Steps

- Read the [full README](README.md) for complete documentation
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
- Look at [config.example.json](config.example.json) for all configuration options

## Support

- 📖 See [README.md](README.md) for comprehensive documentation
- 🐛 Check [Troubleshooting](README.md#troubleshooting) section
- 💻 Review [DEVELOPMENT.md](DEVELOPMENT.md) for development guide
- 🔗 Visit NDI documentation: https://ndi.video/

## Tips

**Pro Tip 1**: Use NDI capture for best performance and reliability

**Pro Tip 2**: Enable debug mode in config.json to see OCR results in `output/debug/`

**Pro Tip 3**: Use the JSON file (`output/game_state.json`) for custom overlay solutions

**Pro Tip 4**: All output files are updated every 500ms by default

Good luck with your esports broadcast! 🎮📺
