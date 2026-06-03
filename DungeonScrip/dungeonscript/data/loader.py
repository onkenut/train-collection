import yaml
import json
from pathlib import Path
from typing import Optional

from dungeonscript.data.database import Database

GAME_DATA_DIR = Path(__file__).parent.parent.parent / "game_data"


class DataLoader:
    def __init__(self, db: Database, data_dir: Optional[Path] = None):
        self.db = db
        self.data_dir = data_dir or GAME_DATA_DIR

    def load_all(self):
        self.load_items()
        self.load_monsters()
        self.load_dialogues()
        self.load_skills()
        self.load_crafting_recipes()

    def load_items(self):
        items = self._load_yaml("items.yaml")
        for item in items:
            stats = item.get("stats", {})
            self.db.cache_item_template(
                item_id=item["id"],
                name=item["name"],
                item_type=item["type"],
                rarity=item.get("rarity", "common"),
                description=item.get("description", ""),
                stats=json.dumps(stats) if isinstance(stats, dict) else stats,
                value=item.get("value", 0),
                stackable=item.get("stackable", 0),
            )

    def load_monsters(self):
        monsters = self._load_yaml("monsters.yaml")
        for monster in monsters:
            loot_table = monster.get("loot_table", [])
            self.db.cache_monster_template(
                monster_id=monster["id"],
                name=monster["name"],
                symbol=monster["symbol"],
                hp=monster["hp"],
                mp=monster.get("mp", 0),
                attack=monster["attack"],
                defense=monster["defense"],
                speed=monster.get("speed", 5),
                exp_reward=monster["exp_reward"],
                ai_mode=monster.get("ai_mode", "random"),
                loot_table=json.dumps(loot_table) if isinstance(loot_table, list) else loot_table,
                description=monster.get("description", ""),
            )

    def load_dialogues(self):
        dialogues = self._load_yaml("dialogues.yaml")
        for dialogue in dialogues:
            nodes = dialogue.get("nodes", [])
            self.db.cache_dialogue(
                dialogue_id=dialogue["id"],
                npc_name=dialogue["npc_name"],
                nodes=json.dumps(nodes) if isinstance(nodes, list) else nodes,
            )

    def load_skills(self):
        skills = self._load_yaml("skills.yaml")
        for skill in skills:
            self.db.cache_skill_template(
                skill_id=skill["id"],
                name=skill["name"],
                mp_cost=skill["mp_cost"],
                damage_multiplier=skill.get("damage_multiplier", 1.0),
                effect_type=skill.get("effect_type", "damage"),
                effect_value=skill.get("effect_value", 0),
                description=skill.get("description", ""),
                unlock_level=skill.get("unlock_level", 1),
            )

    def load_crafting_recipes(self):
        recipes = self._load_yaml("crafting.yaml")
        for recipe in recipes:
            self.db.cache_crafting_recipe(
                recipe_id=recipe["id"],
                ingredient_a=recipe["ingredient_a"],
                ingredient_b=recipe["ingredient_b"],
                result_item=recipe["result_item"],
                description=recipe.get("description", ""),
            )

    def load_events(self) -> list[dict]:
        return self._load_yaml("events.yaml")

    def _load_yaml(self, filename: str) -> list[dict]:
        filepath = self.data_dir / filename
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, list):
                return data
            return []
        except (OSError, yaml.YAMLError):
            return []
