"""
Capture System for LoLOCR
Handles capturing game frames from various sources (NDI, window, screen)
"""

from abc import ABC, abstractmethod
from typing import Optional

try:
    import numpy as np
except ImportError:
    np = None


class CaptureSource(ABC):
    """Abstract base class for capture sources."""
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the capture source.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the capture source."""
        pass
    
    @abstractmethod
    def capture_frame(self) -> Optional:
        """
        Capture a frame from the source.
        
        Returns:
            Frame as numpy array (BGR format) or None if capture failed
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if source is connected."""
        pass


class NDICapture(CaptureSource):
    """
    NDI capture source.
    
    Requires NDI Runtime to be installed:
    https://ndi.video/tools/
    """
    
    def __init__(self, source_name: str = None):
        """
        Initialize NDI capture.
        
        Args:
            source_name: NDI source name (e.g., "OBS (Main):Main Output")
                        If None, will use first available source
        """
        self.source_name = source_name
        self.ndi_find = None
        self.ndi_recv = None
        self.connected = False
        
        # Lazy load NDI SDK
        self._ndi_sdk = None
    
    def _load_ndi_sdk(self):
        """Load NDI SDK (lazy load)."""
        if self._ndi_sdk is not None:
            return True
        
        try:
            import ndi
            self._ndi_sdk = ndi
            return True
        except ImportError:
            print("[ERROR] NDI SDK not found. Please install: pip install pyndi")
            print("[INFO] Or download NDI Tools from https://ndi.video/tools/")
            return False
    
    def connect(self) -> bool:
        """Connect to NDI source."""
        if not self._load_ndi_sdk():
            return False
        
        try:
            ndi = self._ndi_sdk
            
            # Initialize finder
            ndi.find_create_default()
            self.ndi_find = ndi.find_create_default()
            
            if self.ndi_find is None:
                print("[ERROR] Failed to initialize NDI finder")
                return False
            
            # Find sources
            sources = ndi.find_get_sources(self.ndi_find, 1000)  # Wait up to 1 second
            
            if not sources:
                print("[ERROR] No NDI sources found")
                return False
            
            # Select source
            if self.source_name:
                # Find specific source by name
                selected_source = None
                for source in sources:
                    if self.source_name in str(source):
                        selected_source = source
                        break
                
                if not selected_source:
                    print(f"[ERROR] NDI source '{self.source_name}' not found")
                    print(f"[INFO] Available sources: {[str(s) for s in sources]}")
                    return False
            else:
                # Use first available source
                selected_source = sources[0]
                self.source_name = str(selected_source)
                print(f"[INFO] Auto-selected NDI source: {self.source_name}")
            
            # Create receiver
            self.ndi_recv = ndi.recv_create(selected_source, show_ui=False)
            
            if self.ndi_recv is None:
                print("[ERROR] Failed to create NDI receiver")
                return False
            
            self.connected = True
            print(f"[INFO] Connected to NDI source: {self.source_name}")
            return True
        
        except Exception as e:
            print(f"[ERROR] NDI connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from NDI source."""
        try:
            ndi = self._ndi_sdk
            if ndi is None:
                return
            
            if self.ndi_recv:
                ndi.recv_destroy(self.ndi_recv)
                self.ndi_recv = None
            
            if self.ndi_find:
                ndi.find_destroy(self.ndi_find)
                self.ndi_find = None
            
            self.connected = False
            print("[INFO] Disconnected from NDI source")
        except Exception as e:
            print(f"[WARNING] Error disconnecting NDI: {e}")
    
    def capture_frame(self) -> Optional:
        """Capture frame from NDI source."""
        if not self.connected or self.ndi_recv is None:
            return None
        
        try:
            ndi = self._ndi_sdk
            
            # Receive frame with timeout
            frame = ndi.recv_capture(self.ndi_recv, timeout_ms=1000)
            
            if frame is None:
                return None
            
            # Convert frame to numpy array
            # This is a placeholder - actual conversion depends on NDI SDK version
            # frame should be converted to BGR format for OpenCV compatibility
            return np.array(frame, dtype=np.uint8)
        
        except Exception as e:
            print(f"[ERROR] Failed to capture NDI frame: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if NDI source is connected."""
        return self.connected


class WindowCapture(CaptureSource):
    """
    Windows window capture source.
    Requires pyautogui and PIL/Pillow
    """
    
    def __init__(self, window_title: str = 'League of Legends'):
        """
        Initialize window capture.
        
        Args:
            window_title: Title of window to capture
        """
        self.window_title = window_title
        self.hwnd = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to window."""
        try:
            import pygetwindow
            
            # Find window by title
            windows = pygetwindow.getWindowsWithTitle(self.window_title)
            
            if not windows:
                print(f"[ERROR] Window '{self.window_title}' not found")
                return False
            
            self.hwnd = windows[0]
            self.connected = True
            print(f"[INFO] Connected to window: {self.window_title}")
            return True
        
        except ImportError:
            print("[ERROR] pygetwindow not found. Please install: pip install pygetwindow")
            return False
        except Exception as e:
            print(f"[ERROR] Window connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from window."""
        self.hwnd = None
        self.connected = False
        print("[INFO] Disconnected from window")
    
    def capture_frame(self) -> Optional:
        """Capture frame from window."""
        if not self.connected or self.hwnd is None:
            return None
        
        try:
            from PIL import ImageGrab
            import cv2
            
            # Get window bounds
            x1, y1, x2, y2 = self.hwnd.left, self.hwnd.top, self.hwnd.right, self.hwnd.bottom
            
            # Capture screen region
            frame = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # Convert to numpy array and BGR format
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            return frame
        
        except Exception as e:
            print(f"[ERROR] Failed to capture window frame: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if window capture is connected."""
        return self.connected


class ScreenCapture(CaptureSource):
    """
    Full screen capture source.
    Requires PIL/Pillow
    """
    
    def __init__(self, monitor_index: int = 0):
        """
        Initialize screen capture.
        
        Args:
            monitor_index: Monitor index (0 for primary)
        """
        self.monitor_index = monitor_index
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to screen capture."""
        try:
            from PIL import ImageGrab
            
            # Check if monitor index is valid
            try:
                # Try to get screen size for the monitor
                screen = ImageGrab.grab(all_screens=False) if self.monitor_index == 0 else None
                if screen is None and self.monitor_index > 0:
                    print(f"[ERROR] Monitor index {self.monitor_index} not found")
                    return False
            except Exception:
                pass
            
            self.connected = True
            print(f"[INFO] Connected to screen (monitor {self.monitor_index})")
            return True
        
        except ImportError:
            print("[ERROR] PIL/Pillow not found. Please install: pip install pillow")
            return False
        except Exception as e:
            print(f"[ERROR] Screen connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from screen capture."""
        self.connected = False
        print("[INFO] Disconnected from screen")
    
    def capture_frame(self) -> Optional:
        """Capture frame from screen."""
        if not self.connected:
            return None
        
        try:
            from PIL import ImageGrab
            import cv2
            
            # Capture screen
            screen = ImageGrab.grab(all_screens=False)
            
            # Convert to numpy array and BGR format
            frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            return frame
        
        except Exception as e:
            print(f"[ERROR] Failed to capture screen frame: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if screen capture is connected."""
        return self.connected


def create_capture_source(method: str, **kwargs) -> Optional[CaptureSource]:
    """
    Factory function to create capture source.
    
    Args:
        method: Capture method ('ndi', 'window', 'screen')
        **kwargs: Method-specific parameters
        
    Returns:
        CaptureSource instance or None if method unknown
    """
    if method == 'ndi':
        return NDICapture(source_name=kwargs.get('source_name'))
    elif method == 'window':
        return WindowCapture(window_title=kwargs.get('window_title', 'League of Legends'))
    elif method == 'screen':
        return ScreenCapture(monitor_index=kwargs.get('monitor_index', 0))
    else:
        print(f"[ERROR] Unknown capture method: {method}")
        return None
