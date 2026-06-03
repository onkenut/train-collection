"""DungeonScript - Main Entry Point."""

import sys
from pathlib import Path

def main():
    from dungeonscript.data.database import Database
    from dungeonscript.game.game import DungeonScriptGame
    
    db = Database()
    db.connect()
    db.initialize()
    
    from dungeonscript.data.loader import DataLoader
    loader = DataLoader(db)
    loader.load_all()
    
    game = DungeonScriptGame(db)
    game.main_menu()
    
    db.close()

if __name__ == "__main__":
    main()
