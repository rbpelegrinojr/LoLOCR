"""
Output Manager for LoLOCR
Handles generation and management of output files (TXT and JSON)
"""

import os
import json
import threading
from pathlib import Path
from typing import Dict, Any, Optional


class OutputManager:
    """Manages output file generation and updates."""
    
    # Define all output files and their initial values
    OUTPUT_FILES = {
        # Game time
        'gametime.txt': '',
        
        # Team information
        'teams/left_team_name.txt': '',
        'teams/right_team_name.txt': '',
        'teams/left_team_gold.txt': '0',
        'teams/right_team_gold.txt': '0',
        'teams/left_team_kills.txt': '0',
        'teams/right_team_kills.txt': '0',
        'teams/left_team_towers.txt': '0',
        'teams/right_team_towers.txt': '0',
        'teams/left_team_dragons.txt': '0',
        'teams/right_team_dragons.txt': '0',
        'teams/left_team_heralds.txt': '0',
        'teams/right_team_heralds.txt': '0',
        'teams/left_team_barons.txt': '0',
        'teams/right_team_barons.txt': '0',
        
        # Objectives
        'objectives/dragon_timer.txt': '0',
        'objectives/baron_timer.txt': '0',
        'objectives/herald_timer.txt': '0',
        'objectives/elder_timer.txt': '0',
    }
    
    # Player stat files template (will be expanded for 5 players per team)
    PLAYER_STAT_FIELDS = [
        'name', 'champion', 'level', 'kills', 'deaths', 
        'assists', 'cs', 'gold'
    ]
    
    def __init__(self, output_dir: str = 'output'):
        """
        Initialize the output manager.
        
        Args:
            output_dir: Base directory for all output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / 'teams').mkdir(exist_ok=True)
        (self.output_dir / 'players').mkdir(exist_ok=True)
        (self.output_dir / 'objectives').mkdir(exist_ok=True)
        (self.output_dir / 'debug').mkdir(exist_ok=True)
        
        # Initialize file cache (for smart writes)
        self.file_cache: Dict[str, str] = {}
        
        # Current game state
        self.game_state: Dict[str, Any] = self._init_game_state()
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
    
    def _init_game_state(self) -> Dict[str, Any]:
        """Initialize game state structure."""
        state = {
            'gametime': '',
            'teams': {
                'left': {
                    'name': '',
                    'gold': 0,
                    'kills': 0,
                    'towers': 0,
                    'dragons': 0,
                    'heralds': 0,
                    'barons': 0,
                },
                'right': {
                    'name': '',
                    'gold': 0,
                    'kills': 0,
                    'towers': 0,
                    'dragons': 0,
                    'heralds': 0,
                    'barons': 0,
                }
            },
            'players': {
                'left': [],
                'right': []
            },
            'objectives': {
                'dragon_timer': 0,
                'baron_timer': 0,
                'herald_timer': 0,
                'elder_timer': 0,
            },
            'debug': {
                'latest_capture_path': '',
                'latest_scoreboard_crop_path': '',
                'latest_ocr_path': '',
            }
        }
        
        # Initialize 5 players per team
        for team_key in ['left', 'right']:
            for player_idx in range(1, 6):
                player = {
                    'name': '',
                    'champion': '',
                    'level': 0,
                    'kills': 0,
                    'deaths': 0,
                    'assists': 0,
                    'cs': 0,
                    'gold': 0,
                }
                state['players'][team_key].append(player)
        
        return state
    
    def _write_file_if_changed(self, filepath: str, content: str) -> bool:
        """
        Write file only if content has changed.
        
        Args:
            filepath: Relative path to output file
            content: Content to write
            
        Returns:
            True if file was written, False if unchanged
        """
        # Convert to string for comparison
        content_str = str(content)
        
        # Check if content has changed
        if self.file_cache.get(filepath) == content_str:
            return False
        
        # Write file
        full_path = self.output_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content_str)
        
        # Update cache
        self.file_cache[filepath] = content_str
        return True
    
    def update_game_state(self, updates: Dict[str, Any]) -> None:
        """
        Update game state with new values.
        
        Args:
            updates: Dictionary with updates to game state
        """
        with self.lock:
            self._deep_update(self.game_state, updates)
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """Deep merge updates into target dictionary."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def write_outputs(self) -> None:
        """Write all output files based on current game state."""
        with self.lock:
            # Write game time
            self._write_file_if_changed(
                'gametime.txt',
                self.game_state['gametime']
            )
            
            # Write team files
            for team_key, team_data in self.game_state['teams'].items():
                team_prefix = f'teams/{team_key}_team'
                self._write_file_if_changed(
                    f'{team_prefix}_name.txt',
                    team_data['name']
                )
                self._write_file_if_changed(
                    f'{team_prefix}_gold.txt',
                    str(team_data['gold'])
                )
                self._write_file_if_changed(
                    f'{team_prefix}_kills.txt',
                    str(team_data['kills'])
                )
                self._write_file_if_changed(
                    f'{team_prefix}_towers.txt',
                    str(team_data['towers'])
                )
                self._write_file_if_changed(
                    f'{team_prefix}_dragons.txt',
                    str(team_data['dragons'])
                )
                self._write_file_if_changed(
                    f'{team_prefix}_heralds.txt',
                    str(team_data['heralds'])
                )
                self._write_file_if_changed(
                    f'{team_prefix}_barons.txt',
                    str(team_data['barons'])
                )
            
            # Write player files
            for team_key, players in self.game_state['players'].items():
                for player_idx, player_data in enumerate(players, 1):
                    player_prefix = f'players/{team_key}_player{player_idx}'
                    for field in self.PLAYER_STAT_FIELDS:
                        value = player_data.get(field, '')
                        self._write_file_if_changed(
                            f'{player_prefix}_{field}.txt',
                            str(value)
                        )
            
            # Write objective timers
            for objective_key, timer_value in self.game_state['objectives'].items():
                self._write_file_if_changed(
                    f'objectives/{objective_key}.txt',
                    str(timer_value)
                )
            
            # Write JSON game state
            json_path = self.output_dir / 'game_state.json'
            json_str = json.dumps(self.game_state, indent=2)
            self._write_file_if_changed('game_state.json', json_str)
    
    def update_debug_file(self, debug_type: str, filepath: str) -> None:
        """
        Update debug file path (for latest captures/crops/OCR).
        
        Args:
            debug_type: Type of debug file ('capture', 'scoreboard_crop', 'ocr')
            filepath: Path to the debug file
        """
        debug_keys = {
            'capture': 'latest_capture_path',
            'scoreboard_crop': 'latest_scoreboard_crop_path',
            'ocr': 'latest_ocr_path',
        }
        
        if debug_type not in debug_keys:
            raise ValueError(f"Unknown debug type: {debug_type}")
        
        with self.lock:
            self.game_state['debug'][debug_keys[debug_type]] = str(filepath)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state (thread-safe copy)."""
        with self.lock:
            return json.loads(json.dumps(self.game_state))
    
    def generate_output_file_list(self) -> list:
        """
        Generate list of all output files with their metadata.
        
        Returns:
            List of dicts with file info
        """
        files = []
        
        # Game time
        files.append({
            'filename': 'gametime.txt',
            'path': 'gametime.txt',
            'purpose': 'Current game time in MM:SS format',
            'type': 'string',
            'example': '25:30'
        })
        
        # Team files
        for team in ['left', 'right']:
            team_label = 'Left' if team == 'left' else 'Right'
            files.extend([
                {
                    'filename': f'{team}_team_name.txt',
                    'path': f'teams/{team}_team_name.txt',
                    'purpose': f'{team_label} team name',
                    'type': 'string',
                    'example': 'Team Vitality'
                },
                {
                    'filename': f'{team}_team_gold.txt',
                    'path': f'teams/{team}_team_gold.txt',
                    'purpose': f'{team_label} team total gold',
                    'type': 'integer',
                    'example': '45230'
                },
                {
                    'filename': f'{team}_team_kills.txt',
                    'path': f'teams/{team}_team_kills.txt',
                    'purpose': f'{team_label} team total kills',
                    'type': 'integer',
                    'example': '12'
                },
                {
                    'filename': f'{team}_team_towers.txt',
                    'path': f'teams/{team}_team_towers.txt',
                    'purpose': f'{team_label} team towers destroyed',
                    'type': 'integer',
                    'example': '3'
                },
                {
                    'filename': f'{team}_team_dragons.txt',
                    'path': f'teams/{team}_team_dragons.txt',
                    'purpose': f'{team_label} team dragons killed',
                    'type': 'integer',
                    'example': '2'
                },
                {
                    'filename': f'{team}_team_heralds.txt',
                    'path': f'teams/{team}_team_heralds.txt',
                    'purpose': f'{team_label} team heralds killed',
                    'type': 'integer',
                    'example': '1'
                },
                {
                    'filename': f'{team}_team_barons.txt',
                    'path': f'teams/{team}_team_barons.txt',
                    'purpose': f'{team_label} team barons killed',
                    'type': 'integer',
                    'example': '0'
                },
            ])
        
        # Player files
        for team in ['left', 'right']:
            team_label = 'Left' if team == 'left' else 'Right'
            for player_num in range(1, 6):
                for field in self.PLAYER_STAT_FIELDS:
                    if field == 'name':
                        example = 'Faker'
                        value_type = 'string'
                    elif field == 'champion':
                        example = 'Ahri'
                        value_type = 'string'
                    elif field == 'level':
                        example = '18'
                        value_type = 'integer'
                    elif field in ['kills', 'deaths', 'assists']:
                        example = '5'
                        value_type = 'integer'
                    elif field == 'cs':
                        example = '287'
                        value_type = 'integer'
                    elif field == 'gold':
                        example = '12450'
                        value_type = 'integer'
                    else:
                        example = ''
                        value_type = 'string'
                    
                    files.append({
                        'filename': f'{team}_player{player_num}_{field}.txt',
                        'path': f'players/{team}_player{player_num}_{field}.txt',
                        'purpose': f'{team_label} team player {player_num} {field}',
                        'type': value_type,
                        'example': example
                    })
        
        # Objective timers
        for objective in ['dragon', 'baron', 'herald', 'elder']:
            files.append({
                'filename': f'{objective}_timer.txt',
                'path': f'objectives/{objective}_timer.txt',
                'purpose': f'{objective.capitalize()} respawn timer in seconds',
                'type': 'integer/timer',
                'example': '120'
            })
        
        # Debug files
        debug_files = [
            {
                'filename': 'latest_capture.png',
                'path': 'debug/latest_capture.png',
                'purpose': 'Latest screenshot from NDI source',
                'type': 'image',
                'example': 'PNG image file'
            },
            {
                'filename': 'latest_scoreboard_crop.png',
                'path': 'debug/latest_scoreboard_crop.png',
                'purpose': 'Latest cropped scoreboard image',
                'type': 'image',
                'example': 'PNG image file'
            },
            {
                'filename': 'latest_ocr.json',
                'path': 'debug/latest_ocr.json',
                'purpose': 'Latest OCR results in JSON format',
                'type': 'json',
                'example': '{"recognized_text": "..."}' 
            },
        ]
        files.extend(debug_files)
        
        return files
