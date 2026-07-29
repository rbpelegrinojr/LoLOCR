# LoLOCR - League of Legends OCR for Broadcasting

LoLOCR is an automated League of Legends game state extraction tool that uses OCR to capture game information and output it to individual text files and JSON format. It's designed to integrate seamlessly with OBS Studio and other broadcasting software for live esports streaming overlays.

## Table of Contents

1. [Features](#features)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
   - [NDI Installation (Mandatory for NDI Capture)](#ndi-installation-mandatory-for-ndi-capture)
   - [Python Setup](#python-setup)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Output Files](#output-files)
   - [Output Directory Structure](#output-directory-structure)
   - [Output Files Reference](#output-files-reference)
7. [OBS Integration](#obs-integration)
8. [Troubleshooting](#troubleshooting)

---

## Features

- **Automatic Game State Extraction**: Uses OCR to extract game information from League of Legends client
- **Multiple Capture Methods**: Supports NDI, window capture, and screen capture
- **Real-time Output**: Updates output files every 500ms
- **OBS-Ready Format**: Generates individual text files and JSON for easy OBS integration
- **Comprehensive Game Data**: Captures team stats, player stats, and objective timers
- **Debug Mode**: Saves latest captures and OCR results for troubleshooting

---

## System Requirements

- **OS**: Windows 10/11 or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum
- **Network**: For NDI sources (if using NDI capture)

---

## Installation

### NDI Installation (Mandatory for NDI Capture)

If you plan to use NDI as your capture method, follow these steps to install the NDI Runtime.

#### Step 1: Download NDI Tools

1. Visit the official NDI download page: https://ndi.video/tools/
2. Look for **NDI Tools** (the main package)
3. Download the latest version for your operating system
4. Accept the licensing agreement

#### Step 2: Run the Installer

1. Locate the downloaded installer file
2. Run the installer (Administrator privileges may be required)
3. Follow the installation wizard

#### Step 3: Install the NDI Runtime

During the installation process, ensure that **NDI Runtime** is selected for installation. This is the core component required for NDI functionality. The installer should include:

- NDI Runtime (required)
- NDI Tools (optional, but recommended for testing)
- Additional utilities (optional)

#### Step 4: Restart Your Computer

After installation completes, you may be prompted to restart your computer. It's recommended to do so to ensure the NDI Runtime is properly initialized.

#### Step 5: Verify NDI Runtime Installation

To verify the NDI Runtime is installed correctly:

**On Windows:**
- Open Device Manager
- Look for NDI Virtual Network Driver under Network adapters
- You should see "NDI Virtual Network" or similar device

**Alternative verification:**
- Run `ndi-auditioner.exe` (included in NDI Tools) to scan for available NDI sources on your network
- If NDI tools run without errors, the runtime is properly installed

#### Step 6: OBS NDI Plugin (If Using OBS as Capture Source)

**Important**: Recent versions of OBS Studio (21.0+) no longer include built-in NDI support.

If you need to output NDI from OBS:

1. **Install OBS NDI Plugin**:
   - Visit: https://github.com/Palakis/obs-ndi/releases
   - Download the latest release for your OS (Windows installer or Linux build)
   - Run the installer and follow the setup wizard
   - Restart OBS Studio

2. **Enable NDI Output in OBS**:
   - Open OBS Studio
   - Go to **Tools** → **NDI Output Settings**
   - Enable "Main Output" or your desired output
   - Give your NDI source a memorable name (e.g., "OBS (Main)")
   - Click **Apply**

3. **Configure LoLOCR to Use OBS NDI**:
   - Edit `config.json`
   - Set `capture.method` to `"ndi"`
   - Set `capture.ndi.source_name` to your OBS output name (e.g., `"OBS (Main):Main Output"`)
   - Save and restart LoLOCR

#### Step 7: Create an NDI Output from OBS (If Applicable)

If you're using OBS as your League of Legends capture source and want to output it via NDI:

1. In OBS, configure your League of Legends window/game capture source
2. Enable NDI output (see Step 6 above)
3. Other applications on your network can now discover and capture from your OBS instance via NDI
4. Use the NDI source name from OBS in LoLOCR's configuration

#### Step 8: How LoLOCR Discovers Available NDI Sources

LoLOCR automatically scans your network for available NDI sources when it starts:

1. The application queries the NDI Runtime for available sources
2. It builds a list of all NDI devices/applications currently broadcasting
3. Sources are displayed in the application's source selection interface
4. The application can also auto-detect the first available NDI source

**To manually list available NDI sources:**
- Run `ndi-auditioner.exe` from the NDI Tools installation
- This shows all NDI sources visible on your network

#### Step 9: Select an NDI Source in config.json

To configure which NDI source to use:

1. Open `config.json` in a text editor
2. Locate the `capture` section:
   ```json
   "capture": {
       "method": "ndi",
       "ndi": {
           "source_name": "OBS (Main):Main Output",
           "enabled": true
       }
   }
   ```
3. Set `source_name` to your desired NDI source (e.g., `"OBS (Main):Main Output"`)
4. Set `enabled` to `true`
5. Save the file

**Common NDI source names:**
- `OBS (Main):Main Output` - OBS Studio main output
- `OBS (Studio):Studio Output` - OBS Studio scene output
- Device names from OBS/NDI-enabled applications
- `Magewell Capture` - For Magewell NDI capture devices

#### Step 10: Troubleshooting NDI Issues

**No NDI Source Found**

1. Verify NDI Runtime is installed (see Step 5)
2. Check that your NDI source (e.g., OBS) is running and NDI output is enabled
3. Run `ndi-auditioner.exe` to confirm sources are visible
4. Ensure the source name in `config.json` matches exactly (case-sensitive)
5. Check Windows Firewall settings (see below)
6. Verify all devices are on the same network

**Firewall Blocking NDI**

NDI requires specific ports to be open:

1. **Windows Firewall**:
   - Open Windows Defender Firewall with Advanced Security
   - Click "Inbound Rules"
   - Create a new rule for ports 5960-5968 (UDP/TCP)
   - Allow NDI-related applications through the firewall
   - Restart your application

2. **Third-party Firewall**:
   - Add LoLOCR and your NDI source to firewall whitelist
   - Open ports 5960-5968 (UDP/TCP)
   - Consult your firewall's documentation

**NDI Runtime Missing**

- Reinstall NDI Runtime from https://ndi.video/tools/
- Restart your computer after installation
- Verify installation (Step 5)

**OBS Not Transmitting NDI**

1. Verify OBS NDI Plugin is installed (Step 6)
2. Check that NDI output is enabled in OBS Tools menu
3. Verify NDI output is active (not paused)
4. Check the source name matches your config exactly
5. Restart OBS and try again

**Black Screen**

1. Verify the NDI source is actively capturing/displaying content
2. Check OBS or your capture source is running and visible
3. Ensure the capture region in config.json is correct
4. Verify display settings haven't changed (resolution, refresh rate)
5. Check debug images in `output/debug/` folder

**High Latency**

1. Check network connectivity between devices
2. Reduce capture resolution in source settings
3. Increase update interval in config.json (`output.update_interval_ms`)
4. Disable unnecessary network traffic
5. Use wired connection instead of WiFi for better stability

---

## Configuration

### Initial Setup

When you first run LoLOCR, a default `config.json` file is created. Edit this file to customize:

```json
{
  "capture": {
    "method": "ndi",
    "ndi": {
      "source_name": "OBS (Main):Main Output",
      "enabled": true
    }
  },
  "ocr": {
    "enabled": true,
    "debug": false,
    "save_crops": true
  },
  "output": {
    "base_dir": "output",
    "update_interval_ms": 500,
    "generate_json": true,
    "generate_txt": true,
    "generate_debug": true
  }
}
```

---

## Usage

### Running LoLOCR

```bash
python main.py
```

The application will:
1. Load configuration from `config.json`
2. Connect to your NDI source
3. Start capturing and processing game data
4. Generate output files in the `output/` directory
5. Update files every 500ms

### Stopping LoLOCR

Press `Ctrl+C` to gracefully stop the application.

---

## Output Files

### Output Directory Structure

```
output/
├── game_state.json              # Complete game state in JSON format
├── gametime.txt                 # Current game time (MM:SS)
├── teams/
│   ├── left_team_name.txt
│   ├── right_team_name.txt
│   ├── left_team_gold.txt
│   ├── right_team_gold.txt
│   ├── left_team_kills.txt
│   ├── right_team_kills.txt
│   ├── left_team_towers.txt
│   ├── right_team_towers.txt
│   ├── left_team_dragons.txt
│   ├── right_team_dragons.txt
│   ├── left_team_heralds.txt
│   ├── right_team_heralds.txt
│   ├── left_team_barons.txt
│   └── right_team_barons.txt
├── players/
│   ├── left_player1_name.txt
│   ├── left_player1_champion.txt
│   ├── left_player1_level.txt
│   ├── left_player1_kills.txt
│   ├── left_player1_deaths.txt
│   ├── left_player1_assists.txt
│   ├── left_player1_cs.txt
│   ├── left_player1_gold.txt
│   ├── left_player2_name.txt
│   ... (repeat for players 2-5, then right team)
│   └── right_player5_gold.txt
├── objectives/
│   ├── dragon_timer.txt
│   ├── baron_timer.txt
│   ├── herald_timer.txt
│   └── elder_timer.txt
└── debug/
    ├── latest_capture.png
    ├── latest_scoreboard_crop.png
    └── latest_ocr.json
```

### Output Files Reference

| File | Location | Purpose | Type | Example |
|------|----------|---------|------|---------|
| gametime.txt | gametime.txt | Current game time | string | 25:30 |
| left_team_name.txt | teams/ | Left team name | string | Team Vitality |
| right_team_name.txt | teams/ | Right team name | string | G2 Esports |
| left_team_gold.txt | teams/ | Left team total gold | integer | 45230 |
| right_team_gold.txt | teams/ | Right team total gold | integer | 42150 |
| left_team_kills.txt | teams/ | Left team total kills | integer | 12 |
| right_team_kills.txt | teams/ | Right team total kills | integer | 10 |
| left_team_towers.txt | teams/ | Left team towers destroyed | integer | 3 |
| right_team_towers.txt | teams/ | Right team towers destroyed | integer | 2 |
| left_team_dragons.txt | teams/ | Left team dragons killed | integer | 2 |
| right_team_dragons.txt | teams/ | Right team dragons killed | integer | 1 |
| left_team_heralds.txt | teams/ | Left team heralds killed | integer | 1 |
| right_team_heralds.txt | teams/ | Right team heralds killed | integer | 0 |
| left_team_barons.txt | teams/ | Left team barons killed | integer | 0 |
| right_team_barons.txt | teams/ | Right team barons killed | integer | 1 |
| dragon_timer.txt | objectives/ | Dragon respawn timer | integer/timer | 120 |
| baron_timer.txt | objectives/ | Baron respawn timer | integer/timer | 180 |
| herald_timer.txt | objectives/ | Herald respawn timer | integer/timer | 60 |
| elder_timer.txt | objectives/ | Elder respawn timer | integer/timer | 300 |

#### Player Files (20 files per team, 40 total)

For each team (left/right) and player (1-5):

| File Pattern | Location | Purpose | Type | Example |
|--------------|----------|---------|------|---------|
| {team}_player{N}_name.txt | players/ | Player summoner name | string | Faker |
| {team}_player{N}_champion.txt | players/ | Player champion pick | string | Ahri |
| {team}_player{N}_level.txt | players/ | Player current level | integer | 18 |
| {team}_player{N}_kills.txt | players/ | Player total kills | integer | 7 |
| {team}_player{N}_deaths.txt | players/ | Player total deaths | integer | 2 |
| {team}_player{N}_assists.txt | players/ | Player total assists | integer | 15 |
| {team}_player{N}_cs.txt | players/ | Player creep score | integer | 287 |
| {team}_player{N}_gold.txt | players/ | Player total gold | integer | 12450 |

**Example player file list for left team:**
- left_player1_name.txt, left_player1_champion.txt, ... left_player1_gold.txt
- left_player2_name.txt, left_player2_champion.txt, ... left_player2_gold.txt
- left_player3_name.txt, left_player3_champion.txt, ... left_player3_gold.txt
- left_player4_name.txt, left_player4_champion.txt, ... left_player4_gold.txt
- left_player5_name.txt, left_player5_champion.txt, ... left_player5_gold.txt

*Same pattern for right_player1 through right_player5*

#### Debug Files

| File | Location | Purpose | Type |
|------|----------|---------|------|
| latest_capture.png | debug/ | Latest screenshot from capture source | PNG image |
| latest_scoreboard_crop.png | debug/ | Latest cropped scoreboard | PNG image |
| latest_ocr.json | debug/ | Latest OCR results | JSON |

### game_state.json

The consolidated JSON file contains all game state in a single file:

```json
{
  "gametime": "25:30",
  "teams": {
    "left": {
      "name": "Team Vitality",
      "gold": 45230,
      "kills": 12,
      "towers": 3,
      "dragons": 2,
      "heralds": 1,
      "barons": 0
    },
    "right": {
      "name": "G2 Esports",
      "gold": 42150,
      "kills": 10,
      "towers": 2,
      "dragons": 1,
      "heralds": 0,
      "barons": 1
    }
  },
  "players": {
    "left": [
      {
        "name": "Faker",
        "champion": "Ahri",
        "level": 18,
        "kills": 7,
        "deaths": 2,
        "assists": 15,
        "cs": 287,
        "gold": 12450
      },
      ...
    ],
    "right": [...]
  },
  "objectives": {
    "dragon_timer": 120,
    "baron_timer": 180,
    "herald_timer": 60,
    "elder_timer": 300
  }
}
```

---

## OBS Integration

### Using Text Files in OBS

1. **Add Text Source**:
   - In OBS, add a new **Text (GDI+)** source
   - Click "Text from file"
   - Browse to `output/teams/left_team_name.txt`
   - Click OK

2. **Repeat for Each Stat**:
   - Add multiple text sources for different game stats
   - Each can point to its corresponding TXT file
   - Position them on your broadcast overlay

3. **Example Overlay Setup**:
   - Top-left: Team names from `left_team_name.txt` and `right_team_name.txt`
   - Left side: Gold from `left_team_gold.txt`, kills from `left_team_kills.txt`
   - Right side: Same stats from right team files
   - Bottom center: Game time from `gametime.txt`

### Using JSON with Browser Source

1. **Create HTML File**:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <style>
       body { font-family: Arial; color: #fff; background: transparent; }
       .team { display: inline-block; margin: 20px; }
       .stat { font-size: 24px; padding: 5px; }
     </style>
   </head>
   <body>
     <div id="content"></div>
     <script>
       async function updateStats() {
         const response = await fetch('../output/game_state.json');
         const data = await response.json();
         document.getElementById('content').innerHTML = `
           <div class="team">
             <h2>${data.teams.left.name}</h2>
             <div class="stat">Gold: ${data.teams.left.gold}</div>
             <div class="stat">Kills: ${data.teams.left.kills}</div>
           </div>
           <div class="team">
             <h2>${data.teams.right.name}</h2>
             <div class="stat">Gold: ${data.teams.right.gold}</div>
             <div class="stat">Kills: ${data.teams.right.kills}</div>
           </div>
         `;
       }
       setInterval(updateStats, 500);
       updateStats();
     </script>
   </body>
   </html>
   ```

2. **Add Browser Source in OBS**:
   - Add new **Browser** source
   - Point to your HTML file
   - Set size to match your overlay needs

---

## Troubleshooting

### Application Issues

**Application won't start**
- Check Python version: `python --version` (requires 3.8+)
- Verify all dependencies are installed
- Check `config.json` for syntax errors

**No data being captured**
- Verify NDI source is running and visible
- Check `capture.method` in `config.json`
- Enable `debug` mode to see OCR results
- Check `output/debug/latest_ocr.json` for errors

**Output files not updating**
- Check `output.update_interval_ms` setting
- Verify write permissions to `output/` directory
- Check disk space availability
- Look at application logs for errors

### NDI Specific Issues

See [NDI Troubleshooting](#step-10-troubleshooting-ndi-issues) section above.

### Performance Issues

- Reduce capture resolution
- Disable debug mode
- Increase update interval
- Close unnecessary applications

---

## Development

### Project Structure

- `main.py` - Application entry point
- `output_manager.py` - Output file generation
- `game_state.py` - Game state management
- `config.py` - Configuration management
- `config.json` - Application configuration

### Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All features include documentation
- Changes are tested before submission

---

## License

[Add your license information here]

---

## Support

For issues and feature requests, please visit: [Your GitHub repository]