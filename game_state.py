"""
Game State Manager for LoLOCR
Manages game state and provides helper functions for updating game data
"""

from typing import Dict, Any, List


class GameStateManager:
    """Manages game state and provides interface for updating game data."""
    
    def __init__(self):
        """Initialize game state manager."""
        self.state = self._init_state()
    
    def _init_state(self) -> Dict[str, Any]:
        """Initialize empty game state."""
        return {
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
                'left': [self._init_player() for _ in range(5)],
                'right': [self._init_player() for _ in range(5)]
            },
            'objectives': {
                'dragon_timer': 0,
                'baron_timer': 0,
                'herald_timer': 0,
                'elder_timer': 0,
            }
        }
    
    @staticmethod
    def _init_player() -> Dict[str, Any]:
        """Initialize empty player state."""
        return {
            'name': '',
            'champion': '',
            'level': 0,
            'kills': 0,
            'deaths': 0,
            'assists': 0,
            'cs': 0,
            'gold': 0,
        }
    
    def set_game_time(self, game_time: str) -> None:
        """
        Set game time.
        
        Args:
            game_time: Time string in MM:SS format
        """
        self.state['gametime'] = game_time
    
    def set_team_name(self, team: str, name: str) -> None:
        """
        Set team name.
        
        Args:
            team: 'left' or 'right'
            name: Team name
        """
        if team not in ['left', 'right']:
            raise ValueError("Team must be 'left' or 'right'")
        self.state['teams'][team]['name'] = name
    
    def set_team_stat(self, team: str, stat: str, value: int) -> None:
        """
        Set team statistic.
        
        Args:
            team: 'left' or 'right'
            stat: Stat name (gold, kills, towers, dragons, heralds, barons)
            value: Stat value
        """
        if team not in ['left', 'right']:
            raise ValueError("Team must be 'left' or 'right'")
        if stat not in self.state['teams'][team]:
            raise ValueError(f"Unknown team stat: {stat}")
        self.state['teams'][team][stat] = value
    
    def set_player_stat(self, team: str, player_idx: int, stat: str, value: Any) -> None:
        """
        Set player statistic.
        
        Args:
            team: 'left' or 'right'
            player_idx: Player index (0-4)
            stat: Stat name
            value: Stat value
        """
        if team not in ['left', 'right']:
            raise ValueError("Team must be 'left' or 'right'")
        if player_idx < 0 or player_idx >= 5:
            raise ValueError("Player index must be 0-4")
        if stat not in self.state['players'][team][player_idx]:
            raise ValueError(f"Unknown player stat: {stat}")
        self.state['players'][team][player_idx][stat] = value
    
    def set_objective_timer(self, objective: str, timer: int) -> None:
        """
        Set objective respawn timer.
        
        Args:
            objective: Objective name (dragon, baron, herald, elder)
            timer: Timer in seconds
        """
        timer_key = f'{objective}_timer'
        if timer_key not in self.state['objectives']:
            raise ValueError(f"Unknown objective: {objective}")
        self.state['objectives'][timer_key] = timer
    
    def update_team_data(self, team: str, data: Dict[str, Any]) -> None:
        """
        Update multiple team stats at once.
        
        Args:
            team: 'left' or 'right'
            data: Dictionary with team stats
        """
        if team not in ['left', 'right']:
            raise ValueError("Team must be 'left' or 'right'")
        
        for key, value in data.items():
            if key in self.state['teams'][team]:
                self.state['teams'][team][key] = value
    
    def update_player_data(self, team: str, player_idx: int, data: Dict[str, Any]) -> None:
        """
        Update multiple player stats at once.
        
        Args:
            team: 'left' or 'right'
            player_idx: Player index (0-4)
            data: Dictionary with player stats
        """
        if team not in ['left', 'right']:
            raise ValueError("Team must be 'left' or 'right'")
        if player_idx < 0 or player_idx >= 5:
            raise ValueError("Player index must be 0-4")
        
        for key, value in data.items():
            if key in self.state['players'][team][player_idx]:
                self.state['players'][team][player_idx][key] = value
    
    def get_state(self) -> Dict[str, Any]:
        """Get current game state."""
        return self.state
    
    def reset_state(self) -> None:
        """Reset game state to initial empty state."""
        self.state = self._init_state()
