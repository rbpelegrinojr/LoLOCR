"""
LoLOCR - League of Legends OCR for Broadcasting
Main application entry point
"""

import time
import signal
import sys
from threading import Event, Thread
from config import Config
from output_manager import OutputManager
from game_state import GameStateManager


class LoLOCRApplication:
    """Main application controller."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.output_manager = OutputManager(self.config.get_output_dir())
        self.game_state = GameStateManager()
        
        # Application control
        self.shutdown_event = Event()
        self.update_thread = None
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        print("\n[INFO] Shutdown signal received, cleaning up...")
        self.shutdown_event.set()
    
    def _get_update_interval(self) -> float:
        """Get update interval in seconds from configuration."""
        interval_ms = self.config.get_update_interval_ms()
        return interval_ms / 1000.0
    
    def _update_loop(self):
        """Main update loop that runs in a separate thread."""
        interval = self._get_update_interval()
        
        print(f"[INFO] Starting output update loop (interval: {interval*1000:.0f}ms)")
        
        while not self.shutdown_event.is_set():
            try:
                # Get current game state and update output files
                self.output_manager.update_game_state(self.game_state.get_state())
                self.output_manager.write_outputs()
                
                # Sleep for the configured interval
                self.shutdown_event.wait(interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Error in update loop: {e}")
                break
    
    def run(self):
        """Run the application."""
        print("=" * 60)
        print("LoLOCR - League of Legends OCR for Broadcasting")
        print("=" * 60)
        
        # Log configuration
        print(f"\n[INFO] Configuration loaded from: {self.config.config_path}")
        print(f"[INFO] Capture method: {self.config.get_capture_method()}")
        print(f"[INFO] Output directory: {self.config.get_output_dir()}")
        
        # Start update thread
        self.update_thread = Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Example: Set some game state data
        print("\n[INFO] Initializing game state...")
        
        # Initialize example data
        self.game_state.set_game_time("00:00")
        self.game_state.set_team_name('left', 'Team Red')
        self.game_state.set_team_name('right', 'Team Blue')
        
        # Set team stats
        for team in ['left', 'right']:
            self.game_state.set_team_stat(team, 'gold', 0)
            self.game_state.set_team_stat(team, 'kills', 0)
            self.game_state.set_team_stat(team, 'towers', 0)
            self.game_state.set_team_stat(team, 'dragons', 0)
            self.game_state.set_team_stat(team, 'heralds', 0)
            self.game_state.set_team_stat(team, 'barons', 0)
        
        # Set player data (example)
        for team_idx, team in enumerate(['left', 'right']):
            for player_idx in range(5):
                player_num = player_idx + 1
                self.game_state.set_player_stat(team, player_idx, 'name', f'Player {team} {player_num}')
                self.game_state.set_player_stat(team, player_idx, 'champion', 'Champion')
                self.game_state.set_player_stat(team, player_idx, 'level', 1)
                self.game_state.set_player_stat(team, player_idx, 'kills', 0)
                self.game_state.set_player_stat(team, player_idx, 'deaths', 0)
                self.game_state.set_player_stat(team, player_idx, 'assists', 0)
                self.game_state.set_player_stat(team, player_idx, 'cs', 0)
                self.game_state.set_player_stat(team, player_idx, 'gold', 0)
        
        print("[INFO] Game state initialized")
        print(f"[INFO] Output files will be generated in: {self.config.get_output_dir()}/")
        print("\n[INFO] Application is running. Press Ctrl+C to stop.\n")
        
        # Wait for shutdown
        try:
            while not self.shutdown_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        # Wait for update thread to finish
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        
        print("[INFO] Application stopped.")
        print("[INFO] Output files are available at:")
        print(f"      {self.config.get_output_dir()}/")
        return 0


def main():
    """Application entry point."""
    try:
        app = LoLOCRApplication()
        return app.run()
    except Exception as e:
        print(f"[FATAL] Application error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
