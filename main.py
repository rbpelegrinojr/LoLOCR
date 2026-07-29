"""
LoLOCR - League of Legends OCR for Broadcasting
Main application entry point with full integration
"""

import time
import signal
import sys
from threading import Event, Thread
from typing import Optional
from config import Config
from output_manager import OutputManager
from game_state import GameStateManager
from capture import create_capture_source, CaptureSource
from ocr import OCRProcessor


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
        
        # Capture and OCR systems
        self.capture_source: Optional[CaptureSource] = None
        self.ocr_processor: Optional[OCRProcessor] = None
        
        # Application control
        self.shutdown_event = Event()
        self.update_thread = None
        self.capture_thread = None
        
        # Statistics
        self.frame_count = 0
        self.error_count = 0
        
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
    
    def _initialize_capture(self) -> bool:
        """Initialize capture source from configuration."""
        capture_method = self.config.get_capture_method()
        
        print(f"\n[INFO] Initializing {capture_method.upper()} capture...")
        
        try:
            if capture_method == 'ndi':
                self.capture_source = create_capture_source(
                    'ndi',
                    source_name=self.config.get_ndi_source()
                )
            elif capture_method == 'window':
                self.capture_source = create_capture_source(
                    'window',
                    window_title=self.config.get('capture.window.window_title', 'League of Legends')
                )
            elif capture_method == 'screen':
                self.capture_source = create_capture_source(
                    'screen',
                    monitor_index=self.config.get('capture.screen.monitor_index', 0)
                )
            else:
                print(f"[ERROR] Unknown capture method: {capture_method}")
                return False
            
            if self.capture_source is None:
                print("[ERROR] Failed to create capture source")
                return False
            
            if not self.capture_source.connect():
                print(f"[ERROR] Failed to connect to {capture_method} source")
                return False
            
            print(f"[INFO] Capture source connected successfully")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to initialize capture: {e}")
            return False
    
    def _initialize_ocr(self) -> bool:
        """Initialize OCR processor from configuration."""
        print("[INFO] Initializing OCR processor...")
        
        try:
            ocr_config = self.config.get('ocr', {})
            
            self.ocr_processor = OCRProcessor(
                debug=ocr_config.get('debug', False),
                save_crops=ocr_config.get('save_crops', True),
                output_dir=self.config.get_output_dir()
            )
            
            print("[INFO] OCR processor initialized")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to initialize OCR: {e}")
            return False
    
    def _capture_loop(self):
        """Main capture loop that runs in a separate thread."""
        print("[INFO] Starting capture loop...")
        
        while not self.shutdown_event.is_set():
            try:
                if self.capture_source is None or not self.capture_source.is_connected():
                    self.shutdown_event.wait(0.1)
                    continue
                
                # Capture frame
                frame = self.capture_source.capture_frame()
                
                if frame is None:
                    self.error_count += 1
                    if self.error_count > 10:
                        print("[WARNING] Multiple capture errors, reconnecting...")
                        self.capture_source.disconnect()
                        self.capture_source.connect()
                        self.error_count = 0
                    self.shutdown_event.wait(0.01)
                    continue
                
                # Reset error count on successful capture
                self.error_count = 0
                self.frame_count += 1
                
                # Process frame with OCR if enabled
                if self.config.get('ocr.enabled', True) and self.ocr_processor:
                    ocr_result = self.ocr_processor.process_frame(frame)
                    
                    if ocr_result:
                        # Update game state with OCR results
                        # This is where you would extract game data from OCR results
                        pass
                
                # Small sleep to avoid spinning
                self.shutdown_event.wait(0.01)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Error in capture loop: {e}")
                self.error_count += 1
                self.shutdown_event.wait(0.1)
    
    def _update_loop(self):
        """Main update loop for writing output files."""
        interval = self._get_update_interval()
        
        print(f"[INFO] Starting output update loop (interval: {interval*1000:.0f}ms)")
        
        while not self.shutdown_event.is_set():
            try:
                # Update output files based on current game state
                self.output_manager.update_game_state(self.game_state.get_state())
                self.output_manager.write_outputs()
                
                # Sleep for the configured interval
                self.shutdown_event.wait(interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Error in update loop: {e}")
                self.shutdown_event.wait(interval)
    
    def run(self):
        """Run the application."""
        print("=" * 70)
        print("LoLOCR - League of Legends OCR for Broadcasting")
        print("=" * 70)
        
        # Log configuration
        print(f"\n[INFO] Configuration loaded from: {self.config.config_path}")
        print(f"[INFO] Capture method: {self.config.get_capture_method()}")
        print(f"[INFO] Output directory: {self.config.get_output_dir()}")
        print(f"[INFO] Update interval: {self.config.get_update_interval_ms()}ms")
        
        # Initialize capture source
        capture_ok = self._initialize_capture()
        
        # Initialize OCR processor
        ocr_ok = self._initialize_ocr()
        
        if not capture_ok:
            print("[WARNING] Capture initialization failed, running in demo mode")
            print("[INFO] You can still use the application with placeholder data")
        
        # Initialize game state with example data
        print("\n[INFO] Initializing game state...")
        self._init_example_data()
        print("[INFO] Game state initialized")
        
        # Start capture thread (if capture source available)
        if capture_ok and self.capture_source:
            self.capture_thread = Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            print("[INFO] Capture thread started")
        
        # Start output update thread
        self.update_thread = Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        print(f"\n[INFO] Output files will be generated in: {self.config.get_output_dir()}/")
        print("[INFO] Application is running. Press Ctrl+C to stop.\n")
        
        # Print statistics periodically
        last_stats_time = time.time()
        
        # Wait for shutdown
        try:
            while not self.shutdown_event.is_set():
                current_time = time.time()
                
                # Print statistics every 10 seconds
                if current_time - last_stats_time >= 10:
                    if capture_ok and self.capture_source:
                        print(f"[STATS] Frames captured: {self.frame_count} | "
                              f"Capture errors: {self.error_count}")
                    else:
                        print("[STATS] Running in demo mode (no capture)")
                    last_stats_time = current_time
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            pass
        
        # Cleanup
        print("\n[INFO] Shutting down...")
        
        # Stop capture
        if self.capture_source:
            self.capture_source.disconnect()
        
        # Wait for threads to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        
        print("[INFO] Application stopped.")
        print(f"[INFO] Total frames processed: {self.frame_count}")
        print(f"[INFO] Output files available at: {self.config.get_output_dir()}/")
        return 0
    
    def _init_example_data(self):
        """Initialize example game state data."""
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
        
        # Set player data
        for team in ['left', 'right']:
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


def main():
    """Application entry point."""
    try:
        app = LoLOCRApplication()
        return app.run()
    except Exception as e:
        print(f"[FATAL] Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
