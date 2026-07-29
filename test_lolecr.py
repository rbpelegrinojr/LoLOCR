"""
Unit tests for LoLOCR
Tests core functionality of all modules
"""

import unittest
import tempfile
import json
from pathlib import Path
from config import Config
from output_manager import OutputManager
from game_state import GameStateManager


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / 'config.json'
    
    def test_config_creation(self):
        """Test configuration file creation."""
        config = Config(str(self.config_path))
        self.assertTrue(self.config_path.exists())
    
    def test_config_get_set(self):
        """Test configuration get/set operations."""
        config = Config(str(self.config_path))
        
        # Test getting default values
        self.assertEqual(config.get_capture_method(), 'ndi')
        self.assertEqual(config.get_update_interval_ms(), 500)
        
        # Test setting values
        config.set('capture.method', 'window')
        self.assertEqual(config.get_capture_method(), 'window')
    
    def test_config_ndi_methods(self):
        """Test NDI-specific configuration methods."""
        config = Config(str(self.config_path))
        
        # Test NDI source methods
        config.set_ndi_source('OBS (Main):Main Output')
        self.assertEqual(config.get_ndi_source(), 'OBS (Main):Main Output')


class TestGameState(unittest.TestCase):
    """Test game state management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameStateManager()
    
    def test_initial_state(self):
        """Test initial game state."""
        state = self.game_state.get_state()
        
        self.assertIn('gametime', state)
        self.assertIn('teams', state)
        self.assertIn('players', state)
        self.assertIn('objectives', state)
    
    def test_set_game_time(self):
        """Test setting game time."""
        self.game_state.set_game_time('10:30')
        state = self.game_state.get_state()
        self.assertEqual(state['gametime'], '10:30')
    
    def test_set_team_name(self):
        """Test setting team name."""
        self.game_state.set_team_name('left', 'Team A')
        state = self.game_state.get_state()
        self.assertEqual(state['teams']['left']['name'], 'Team A')
    
    def test_set_team_stat(self):
        """Test setting team statistics."""
        self.game_state.set_team_stat('left', 'gold', 5000)
        self.game_state.set_team_stat('left', 'kills', 10)
        
        state = self.game_state.get_state()
        self.assertEqual(state['teams']['left']['gold'], 5000)
        self.assertEqual(state['teams']['left']['kills'], 10)
    
    def test_set_player_stat(self):
        """Test setting player statistics."""
        self.game_state.set_player_stat('left', 0, 'name', 'Player 1')
        self.game_state.set_player_stat('left', 0, 'champion', 'Ahri')
        self.game_state.set_player_stat('left', 0, 'level', 18)
        
        state = self.game_state.get_state()
        player = state['players']['left'][0]
        self.assertEqual(player['name'], 'Player 1')
        self.assertEqual(player['champion'], 'Ahri')
        self.assertEqual(player['level'], 18)
    
    def test_invalid_team(self):
        """Test invalid team handling."""
        with self.assertRaises(ValueError):
            self.game_state.set_team_name('invalid', 'Test')
    
    def test_invalid_player_index(self):
        """Test invalid player index handling."""
        with self.assertRaises(ValueError):
            self.game_state.set_player_stat('left', 10, 'name', 'Invalid')


class TestOutputManager(unittest.TestCase):
    """Test output file management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_manager = OutputManager(self.temp_dir)
    
    def test_output_manager_creation(self):
        """Test output manager initialization."""
        # Check that output directories are created
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue((Path(self.temp_dir) / 'teams').exists())
        self.assertTrue((Path(self.temp_dir) / 'players').exists())
        self.assertTrue((Path(self.temp_dir) / 'objectives').exists())
        self.assertTrue((Path(self.temp_dir) / 'debug').exists())
    
    def test_write_files(self):
        """Test file writing."""
        # Set up game state
        self.output_manager.game_state['gametime'] = '10:00'
        self.output_manager.game_state['teams']['left']['name'] = 'Team Red'
        self.output_manager.game_state['teams']['right']['name'] = 'Team Blue'
        
        # Write files
        self.output_manager.write_outputs()
        
        # Check that files were created
        gametime_file = Path(self.temp_dir) / 'gametime.txt'
        self.assertTrue(gametime_file.exists())
        self.assertEqual(gametime_file.read_text(), '10:00')
        
        # Check team files
        left_team_file = Path(self.temp_dir) / 'teams' / 'left_team_name.txt'
        self.assertTrue(left_team_file.exists())
        self.assertEqual(left_team_file.read_text(), 'Team Red')
    
    def test_json_output(self):
        """Test JSON output generation."""
        # Set up game state
        self.output_manager.game_state['gametime'] = '15:30'
        
        # Write files
        self.output_manager.write_outputs()
        
        # Check JSON file
        json_file = Path(self.temp_dir) / 'game_state.json'
        self.assertTrue(json_file.exists())
        
        # Parse and verify JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['gametime'], '15:30')
        self.assertIn('teams', data)
        self.assertIn('players', data)
    
    def test_smart_writes(self):
        """Test that files are only written when content changes."""
        # First write
        self.output_manager.game_state['gametime'] = '10:00'
        self.output_manager.write_outputs()
        
        gametime_file = Path(self.temp_dir) / 'gametime.txt'
        first_mtime = gametime_file.stat().st_mtime
        
        # Wait a moment
        import time
        time.sleep(0.1)
        
        # Second write with same data (should not rewrite)
        self.output_manager.write_outputs()
        second_mtime = gametime_file.stat().st_mtime
        
        # Modification time should be the same
        self.assertEqual(first_mtime, second_mtime)
    
    def test_player_files_generation(self):
        """Test that all player files are generated."""
        # Write files
        self.output_manager.write_outputs()
        
        # Check that player files exist for all positions
        players_dir = Path(self.temp_dir) / 'players'
        
        for team in ['left', 'right']:
            for player_num in range(1, 6):
                for field in ['name', 'champion', 'level', 'kills', 'deaths', 'assists', 'cs', 'gold']:
                    filename = f'{team}_player{player_num}_{field}.txt'
                    filepath = players_dir / filename
                    self.assertTrue(filepath.exists(), f"Missing: {filename}")


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test full workflow from config to output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.json'
            output_dir = Path(temp_dir) / 'output'
            
            # Create config
            config = Config(str(config_path))
            self.assertTrue(config_path.exists())
            
            # Create output manager
            output_manager = OutputManager(str(output_dir))
            
            # Create game state
            game_state = GameStateManager()
            game_state.set_game_time('25:00')
            game_state.set_team_name('left', 'Vitality')
            game_state.set_team_name('right', 'G2')
            
            # Update and write
            output_manager.update_game_state(game_state.get_state())
            output_manager.write_outputs()
            
            # Verify
            gametime_file = output_dir / 'gametime.txt'
            self.assertTrue(gametime_file.exists())
            self.assertEqual(gametime_file.read_text(), '25:00')


if __name__ == '__main__':
    unittest.main()
