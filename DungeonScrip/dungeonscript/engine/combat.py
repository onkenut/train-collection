import random
from typing import Optional, Callable
from dungeonscript.engine.character import Player, Monster
from dungeonscript.data.database import Database

class CombatResult:
    def __init__(self):
        self.victory = False
        self.escape = False
        self.messages = []
        self.exp_gained = 0
        self.loot = []
        self.player_died = False

class CombatSystem:
    def __init__(self, player: Player, monster: Monster, db: Optional[Database] = None, save_slot: int = 0):
        self.player = player
        self.monster = monster
        self.db = db
        self.save_slot = save_slot
        self.rng = random.Random()
        self.turn = 0
        self.result = CombatResult()
        
    def _calc_damage(self, attacker_atk: int, defender_def: int, multiplier: float = 1.0) -> int:
        base = int(max(1, attacker_atk - defender_def) * multiplier)
        variance = self.rng.randint(-2, 2)
        return max(1, base + variance)
        
    def _roll_escape(self) -> bool:
        diff = self.player.speed - self.monster.speed
        chance = 0.3 + diff * 0.05
        return self.rng.random() < min(0.8, max(0.1, chance))
        
    def player_attack(self) -> str:
        is_crit = self.rng.random() < 0.1
        dmg = self._calc_damage(self.player.attack, self.monster.defense, 1.5 if is_crit else 1.0)
        actual = self.monster.take_damage(dmg)
        msg = f"你攻击了 {self.monster.name}，造成 {actual} 点伤害！"
        if is_crit:
            msg = "暴击！" + msg
        self.result.messages.append(msg)
        return msg
        
    def player_use_skill(self, skill_data: dict) -> str:
        if self.player.mp < skill_data.get('mp_cost', 0):
            return "魔法值不足！"
        self.player.mp -= skill_data.get('mp_cost', 0)
        effect_type = skill_data.get('effect_type', 'damage')
        multiplier = skill_data.get('damage_multiplier', 1.0)
        value = skill_data.get('effect_value', 0)
        
        if effect_type == 'damage':
            dmg = self._calc_damage(self.player.attack, self.monster.defense, multiplier)
            actual = self.monster.take_damage(dmg)
            msg = f"{skill_data.get('name', '技能')}！造成 {actual} 点伤害！"
        elif effect_type == 'heal':
            healed = self.player.heal(value)
            msg = f"{skill_data.get('name', '治疗')}！恢复了 {healed} 点生命！"
        elif effect_type == 'buff':
            self.player.base_attack += 2
            msg = f"{skill_data.get('name', '增益')}！攻击力提升了！"
        else:
            msg = f"{skill_data.get('name', '技能')}生效了！"
        self.result.messages.append(msg)
        return msg
        
    def monster_turn(self) -> str:
        if self.monster.is_dead:
            return ""
        ai = self.monster.ai_mode
        if ai == 'heal' and self.monster.hp < self.monster.max_hp * 0.3:
            healed = min(10, self.monster.max_hp - self.monster.hp)
            self.monster.hp += healed
            msg = f"{self.monster.name} 恢复了 {healed} 点生命！"
        else:
            dmg = self._calc_damage(self.monster.attack, self.player.defense)
            actual = self.player.take_damage(dmg)
            msg = f"{self.monster.name} 攻击了你，造成 {actual} 点伤害！"
        self.result.messages.append(msg)
        return msg
        
    def try_escape(self) -> str:
        if self._roll_escape():
            self.result.escape = True
            msg = "你成功逃跑了！"
            self.result.messages.append(msg)
            return msg
        msg = "逃跑失败！"
        self.result.messages.append(msg)
        return msg
        
    def check_victory(self) -> bool:
        if self.monster.is_dead:
            self.result.victory = True
            self.result.exp_gained = self.monster.exp_reward
            self.result.messages.append(f"你击败了 {self.monster.name}！获得 {self.monster.exp_reward} 经验值！")
            for drop in self.monster.loot_table:
                if self.rng.random() < drop.get('chance', 0.5):
                    if drop.get('item_id') == 'gold':
                        gold = self.rng.randint(drop.get('min', 1), drop.get('max', 10))
                        self.player.gold += gold
                        self.result.messages.append(f"获得 {gold} 金币！")
                        self.result.loot.append(('gold', gold))
                    else:
                        self.result.loot.append((drop.get('item_id'), drop.get('quantity', 1)))
                        self.result.messages.append(f"获得物品！")
            return True
        return False
        
    def check_defeat(self) -> bool:
        if self.player.is_dead:
            self.result.player_died = True
            self.result.messages.append("你被击败了...")
            return True
        return False
        
    def do_round(self, player_action: str, skill_data: Optional[dict] = None) -> CombatResult:
        self.turn += 1
        player_first = self.player.speed >= self.monster.speed
        if player_first:
            if player_action == 'attack':
                self.player_attack()
            elif player_action == 'skill' and skill_data:
                self.player_use_skill(skill_data)
            elif player_action == 'escape':
                self.try_escape()
            elif player_action == 'item':
                pass
            if not self.check_victory() and not self.result.escape:
                self.monster_turn()
                self.check_defeat()
        else:
            self.monster_turn()
            if not self.check_defeat():
                if player_action == 'attack':
                    self.player_attack()
                elif player_action == 'skill' and skill_data:
                    self.player_use_skill(skill_data)
                elif player_action == 'escape':
                    self.try_escape()
                elif player_action == 'item':
                    pass
                self.check_victory()
        return self.result
