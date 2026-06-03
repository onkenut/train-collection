import json

class AttributeCalculator:
    @staticmethod
    def exp_for_level(level: int) -> int:
        return int(50 * (1.5 ** (level - 1)))
    @staticmethod
    def level_up_stats(rng) -> dict:
        return {'hp': rng.randint(5, 15), 'mp': rng.randint(0, 8), 'attack': rng.randint(1, 3), 'defense': rng.randint(0, 2), 'speed': rng.randint(0, 1)}

class Player:
    def __init__(self, name: str = "冒险者", save_slot: int = 0):
        import random
        self.save_slot = save_slot
        self.name = name
        self.x = 0
        self.y = 0
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.base_attack = 10
        self.base_defense = 5
        self.speed = 5
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.current_floor = 1
        self.is_dead = False
        self.equipment = {'weapon': None, 'armor': None, 'accessory': None}
        self.skills = ['power_strike']
        self.flags = set()
        self.rng = random.Random()
        self.game_time = 0.0
        self.hardcore = False
        
    @property
    def attack(self):
        total = self.base_attack
        for slot, item in self.equipment.items():
            if item:
                total += item.stats.get('attack', 0)
        return total
        
    @property
    def defense(self):
        total = self.base_defense
        for slot, item in self.equipment.items():
            if item:
                total += item.stats.get('defense', 0)
        return total
        
    def gain_exp(self, amount: int) -> list[str]:
        messages = []
        self.exp += amount
        while self.exp >= AttributeCalculator.exp_for_level(self.level):
            self.exp -= AttributeCalculator.exp_for_level(self.level)
            self.level += 1
            stat_gain = AttributeCalculator.level_up_stats(self.rng)
            self.max_hp += stat_gain['hp']
            self.max_mp += stat_gain['mp']
            self.base_attack += stat_gain['attack']
            self.base_defense += stat_gain['defense']
            self.speed += stat_gain['speed']
            self.hp = self.max_hp
            self.mp = self.max_mp
            messages.append(f"升级了！你现在是 {self.level} 级！")
        return messages
        
    def take_damage(self, damage: int) -> int:
        actual = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual)
        if self.hp <= 0:
            self.is_dead = True
        return actual
        
    def heal(self, amount: int) -> int:
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old
        
    def restore_mp(self, amount: int) -> int:
        old = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old
        
    def to_dict(self) -> dict:
        return {
            'player_name': self.name, 'current_floor': self.current_floor,
            'x': self.x, 'y': self.y, 'hp': self.hp, 'max_hp': self.max_hp,
            'mp': self.mp, 'max_mp': self.max_mp, 'attack': self.base_attack,
            'defense': self.base_defense, 'speed': self.speed, 'level': self.level,
            'exp': self.exp, 'gold': self.gold, 'is_dead': int(self.is_dead),
            'game_time': self.game_time, 'hardcore': int(self.hardcore)
        }
        
    @classmethod
    def from_dict(cls, data: dict, save_slot: int) -> 'Player':
        p = cls(data.get('player_name', '冒险者'), save_slot)
        p.current_floor = data.get('current_floor', 1)
        p.x = data.get('x', 0); p.y = data.get('y', 0)
        p.max_hp = data.get('max_hp', 100); p.hp = data.get('hp', p.max_hp)
        p.max_mp = data.get('max_mp', 50); p.mp = data.get('mp', p.max_mp)
        p.base_attack = data.get('attack', 10)
        p.base_defense = data.get('defense', 5)
        p.speed = data.get('speed', 5)
        p.level = data.get('level', 1); p.exp = data.get('exp', 0)
        p.gold = data.get('gold', 0)
        p.is_dead = bool(data.get('is_dead', 0))
        p.game_time = data.get('game_time', 0.0)
        p.hardcore = bool(data.get('hardcore', 0))
        return p

class Monster:
    def __init__(self, monster_id: str, template: dict):
        self.monster_id = monster_id
        self.name = template.get('name', '怪物')
        self.symbol = template.get('symbol', 'M')
        self.max_hp = template.get('hp', 10)
        self.hp = self.max_hp
        self.max_mp = template.get('mp', 0)
        self.mp = self.max_mp
        self.attack = template.get('attack', 5)
        self.defense = template.get('defense', 0)
        self.speed = template.get('speed', 5)
        self.exp_reward = template.get('exp_reward', 10)
        self.ai_mode = template.get('ai_mode', 'random')
        loot_str = template.get('loot_table', '[]')
        if isinstance(loot_str, str):
            self.loot_table = json.loads(loot_str)
        else:
            self.loot_table = loot_str
        self.description = template.get('description', '')
        self.x = 0
        self.y = 0
        
    def take_damage(self, damage: int) -> int:
        actual = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual
        
    @property
    def is_dead(self) -> bool:
        return self.hp <= 0
