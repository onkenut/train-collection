import sqlite3
import json
from pathlib import Path
from typing import Optional, Any

DB_NAME = "dungeonscript.db"


class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".dungeonscript" / DB_NAME)
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys=ON")
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error:
            self.conn = None

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
            self.conn = None

    def initialize(self):
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS saves (
                    slot INTEGER PRIMARY KEY,
                    player_name TEXT,
                    current_floor INT,
                    x INT,
                    y INT,
                    hp INT,
                    max_hp INT,
                    mp INT,
                    max_mp INT,
                    attack INT,
                    defense INT,
                    speed INT,
                    level INT,
                    exp INT,
                    gold INT,
                    game_time REAL DEFAULT 0,
                    is_dead INT DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT,
                    difficulty TEXT DEFAULT 'normal',
                    hardcore INT DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_slot INT REFERENCES saves(slot),
                    item_id TEXT,
                    quantity INT DEFAULT 1,
                    is_equipped INT DEFAULT 0,
                    slot_type TEXT DEFAULT NULL
                );

                CREATE TABLE IF NOT EXISTS map_state (
                    save_slot INT REFERENCES saves(slot),
                    floor INT,
                    map_seed INT,
                    explored TEXT DEFAULT '',
                    monster_positions TEXT DEFAULT '[]',
                    chest_opened TEXT DEFAULT '[]',
                    events_triggered TEXT DEFAULT '[]',
                    PRIMARY KEY (save_slot, floor)
                );

                CREATE TABLE IF NOT EXISTS game_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_slot INT REFERENCES saves(slot),
                    log_type TEXT,
                    message TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS item_templates (
                    item_id TEXT PRIMARY KEY,
                    name TEXT,
                    item_type TEXT,
                    rarity TEXT DEFAULT 'common',
                    description TEXT,
                    stats TEXT DEFAULT '{}',
                    value INT DEFAULT 0,
                    stackable INT DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS monster_templates (
                    monster_id TEXT PRIMARY KEY,
                    name TEXT,
                    symbol TEXT,
                    hp INT,
                    mp INT DEFAULT 0,
                    attack INT,
                    defense INT,
                    speed INT DEFAULT 5,
                    exp_reward INT,
                    ai_mode TEXT DEFAULT 'random',
                    loot_table TEXT DEFAULT '[]',
                    description TEXT
                );

                CREATE TABLE IF NOT EXISTS dialogue_data (
                    dialogue_id TEXT PRIMARY KEY,
                    npc_name TEXT,
                    nodes TEXT DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_slot INT REFERENCES saves(slot),
                    achievement_id TEXT,
                    unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(save_slot, achievement_id)
                );

                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    score INT,
                    floor_reached INT,
                    game_time REAL,
                    completed INT DEFAULT 0,
                    achieved_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS skill_templates (
                    skill_id TEXT PRIMARY KEY,
                    name TEXT,
                    mp_cost INT,
                    damage_multiplier REAL DEFAULT 1.0,
                    effect_type TEXT DEFAULT 'damage',
                    effect_value INT DEFAULT 0,
                    description TEXT,
                    unlock_level INT DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS crafting_recipes (
                    recipe_id TEXT PRIMARY KEY,
                    ingredient_a TEXT,
                    ingredient_b TEXT,
                    result_item TEXT,
                    description TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_saves_slot ON saves(slot);
                CREATE INDEX IF NOT EXISTS idx_inventory_save_slot ON inventory(save_slot);
                CREATE INDEX IF NOT EXISTS idx_map_state_save_slot_floor ON map_state(save_slot, floor);
                CREATE INDEX IF NOT EXISTS idx_game_log_save_slot ON game_log(save_slot);
                CREATE INDEX IF NOT EXISTS idx_achievements_save_slot ON achievements(save_slot);
            """)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def create_save(self, slot: int, player_name: str, **kwargs) -> bool:
        if not self.conn:
            return False
        try:
            columns = ["slot", "player_name", "created_at", "updated_at"]
            values: list[Any] = [slot, player_name, self._now(), self._now()]
            for key, value in kwargs.items():
                columns.append(key)
                values.append(value)
            placeholders = ", ".join("?" for _ in values)
            col_str = ", ".join(columns)
            sql = f"INSERT OR REPLACE INTO saves ({col_str}) VALUES ({placeholders})"
            self.conn.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def load_save(self, slot: int) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            cursor = self.conn.execute("SELECT * FROM saves WHERE slot=?", (slot,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def delete_save(self, slot: int) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute("DELETE FROM saves WHERE slot=?", (slot,))
            self.conn.execute("DELETE FROM inventory WHERE save_slot=?", (slot,))
            self.conn.execute("DELETE FROM map_state WHERE save_slot=?", (slot,))
            self.conn.execute("DELETE FROM game_log WHERE save_slot=?", (slot,))
            self.conn.execute("DELETE FROM achievements WHERE save_slot=?", (slot,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def list_saves(self) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute(
                "SELECT slot, player_name, current_floor, level, hp, max_hp, is_dead, game_time, hardcore FROM saves ORDER BY slot"
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def update_save(self, slot: int, **kwargs) -> bool:
        if not self.conn:
            return False
        if not kwargs:
            return False
        try:
            set_parts = []
            values: list[Any] = []
            for key, value in kwargs.items():
                set_parts.append(f"{key}=?")
                values.append(value)
            set_parts.append("updated_at=?")
            values.append(self._now())
            values.append(slot)
            sql = f"UPDATE saves SET {', '.join(set_parts)} WHERE slot=?"
            self.conn.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def add_inventory_item(self, save_slot: int, item_id: str, quantity: int = 1, is_equipped: int = 0, slot_type: Optional[str] = None) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT INTO inventory (save_slot, item_id, quantity, is_equipped, slot_type) VALUES (?, ?, ?, ?, ?)",
                (save_slot, item_id, quantity, is_equipped, slot_type),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def remove_inventory_item(self, save_slot: int, item_id: str, quantity: int = 1) -> bool:
        if not self.conn:
            return False
        try:
            cursor = self.conn.execute(
                "SELECT id, quantity FROM inventory WHERE save_slot=? AND item_id=?",
                (save_slot, item_id),
            )
            row = cursor.fetchone()
            if not row:
                return False
            if quantity >= row["quantity"]:
                self.conn.execute("DELETE FROM inventory WHERE id=?", (row["id"],))
            else:
                self.conn.execute(
                    "UPDATE inventory SET quantity=? WHERE id=?",
                    (row["quantity"] - quantity, row["id"]),
                )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_inventory(self, save_slot: int) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM inventory WHERE save_slot=?", (save_slot,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def update_inventory_item(self, save_slot: int, item_id: str, **kwargs) -> bool:
        if not self.conn:
            return False
        if not kwargs:
            return False
        try:
            set_parts = []
            values: list[Any] = []
            for key, value in kwargs.items():
                set_parts.append(f"{key}=?")
                values.append(value)
            values.append(save_slot)
            values.append(item_id)
            sql = f"UPDATE inventory SET {', '.join(set_parts)} WHERE save_slot=? AND item_id=?"
            self.conn.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def save_map_state(self, save_slot: int, floor: int, map_seed: int, explored: str, monster_positions: str, chest_opened: str, events_triggered: str) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO map_state (save_slot, floor, map_seed, explored, monster_positions, chest_opened, events_triggered) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (save_slot, floor, map_seed, explored, monster_positions, chest_opened, events_triggered),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def load_map_state(self, save_slot: int, floor: int) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            cursor = self.conn.execute(
                "SELECT * FROM map_state WHERE save_slot=? AND floor=?",
                (save_slot, floor),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def add_log(self, save_slot: int, log_type: str, message: str) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT INTO game_log (save_slot, log_type, message) VALUES (?, ?, ?)",
                (save_slot, log_type, message),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_logs(self, save_slot: int, limit: int = 50) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute(
                "SELECT * FROM game_log WHERE save_slot=? ORDER BY id DESC LIMIT ?",
                (save_slot, limit),
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def cache_item_template(self, item_id: str, name: str, item_type: str, **kwargs) -> bool:
        if not self.conn:
            return False
        try:
            columns = ["item_id", "name", "item_type"]
            values: list[Any] = [item_id, name, item_type]
            for key, value in kwargs.items():
                columns.append(key)
                values.append(value)
            placeholders = ", ".join("?" for _ in values)
            col_str = ", ".join(columns)
            sql = f"INSERT OR REPLACE INTO item_templates ({col_str}) VALUES ({placeholders})"
            self.conn.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_item_template(self, item_id: str) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            cursor = self.conn.execute("SELECT * FROM item_templates WHERE item_id=?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def get_all_item_templates(self) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM item_templates")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def cache_monster_template(self, monster_id: str, name: str, symbol: str, **kwargs) -> bool:
        if not self.conn:
            return False
        try:
            columns = ["monster_id", "name", "symbol"]
            values: list[Any] = [monster_id, name, symbol]
            for key, value in kwargs.items():
                columns.append(key)
                values.append(value)
            placeholders = ", ".join("?" for _ in values)
            col_str = ", ".join(columns)
            sql = f"INSERT OR REPLACE INTO monster_templates ({col_str}) VALUES ({placeholders})"
            self.conn.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_monster_template(self, monster_id: str) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            cursor = self.conn.execute("SELECT * FROM monster_templates WHERE monster_id=?", (monster_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def get_all_monster_templates(self) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM monster_templates")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def cache_dialogue(self, dialogue_id: str, npc_name: str, nodes: str) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO dialogue_data (dialogue_id, npc_name, nodes) VALUES (?, ?, ?)",
                (dialogue_id, npc_name, nodes),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_dialogue(self, dialogue_id: str) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            cursor = self.conn.execute("SELECT * FROM dialogue_data WHERE dialogue_id=?", (dialogue_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def unlock_achievement(self, save_slot: int, achievement_id: str) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO achievements (save_slot, achievement_id) VALUES (?, ?)",
                (save_slot, achievement_id),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_achievements(self, save_slot: int) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM achievements WHERE save_slot=?", (save_slot,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def add_leaderboard_entry(self, player_name: str, score: int, floor_reached: int, game_time: float, completed: int = 0) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT INTO leaderboard (player_name, score, floor_reached, game_time, completed) VALUES (?, ?, ?, ?, ?)",
                (player_name, score, floor_reached, game_time, completed),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM leaderboard ORDER BY score DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def cache_skill_template(self, skill_id: str, name: str, mp_cost: int, **kwargs) -> bool:
        if not self.conn:
            return False
        try:
            columns = ["skill_id", "name", "mp_cost"]
            values: list[Any] = [skill_id, name, mp_cost]
            for key, value in kwargs.items():
                columns.append(key)
                values.append(value)
            placeholders = ", ".join("?" for _ in values)
            col_str = ", ".join(columns)
            sql = f"INSERT OR REPLACE INTO skill_templates ({col_str}) VALUES ({placeholders})"
            self.conn.execute(sql, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_skill_template(self, skill_id: str) -> Optional[dict]:
        if not self.conn:
            return None
        try:
            cursor = self.conn.execute("SELECT * FROM skill_templates WHERE skill_id=?", (skill_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error:
            return None

    def get_all_skill_templates(self) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM skill_templates")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def cache_crafting_recipe(self, recipe_id: str, ingredient_a: str, ingredient_b: str, result_item: str, description: str = "") -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO crafting_recipes (recipe_id, ingredient_a, ingredient_b, result_item, description) VALUES (?, ?, ?, ?, ?)",
                (recipe_id, ingredient_a, ingredient_b, result_item, description),
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_all_crafting_recipes(self) -> list[dict]:
        if not self.conn:
            return []
        try:
            cursor = self.conn.execute("SELECT * FROM crafting_recipes")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    @staticmethod
    def _now() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
