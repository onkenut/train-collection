import yaml
import json
from pathlib import Path
from typing import Optional
from dungeonscript.data.loader import DataLoader

class EventResult:
    def __init__(self):
        self.messages = []
        self.changes = {}
        self.give_items = []
        self.spawn_monster = None
        self.teleport_dest = None
        self.open_dialogue = None
        self.open_shop = None
        self.game_over = False
        self.triggered = False

class EventManager:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.events = data_loader.load_events()
        
    def check_trigger(self, trigger_type: str, player, dungeon, x: Optional[int] = None, y: Optional[int] = None) -> list[EventResult]:
        results = []
        for event in self.events:
            if self._matches_trigger(event, trigger_type, player, dungeon, x, y):
                if self._check_conditions(event.get('conditions', []), player):
                    result = self._execute_actions(event.get('actions', []), player)
                    result.triggered = True
                    results.append(result)
        return results
        
    def _matches_trigger(self, event: dict, trigger_type: str, player, dungeon, x: Optional[int], y: Optional[int]) -> bool:
        trigger = event.get('trigger', {})
        if trigger.get('type') != trigger_type:
            return False
        floor_req = trigger.get('floor')
        if floor_req is not None:
            if isinstance(floor_req, int) and player.current_floor != floor_req:
                return False
            if isinstance(floor_req, list) and not (floor_req[0] <= player.current_floor <= floor_req[1]):
                return False
        tx, ty = trigger.get('x'), trigger.get('y')
        if tx is not None and x is not None and tx != x:
            return False
        if ty is not None and y is not None and ty != y:
            return False
        event_id = event.get('id', '')
        if event_id and f"event_{event_id}" in player.flags:
            return False
        return True
        
    def _check_conditions(self, conditions: list, player) -> bool:
        for cond in conditions:
            ctype = cond.get('type')
            if ctype == 'has_item':
                if not self._check_has_item(player, cond):
                    return False
            elif ctype == 'attribute':
                if not self._check_attribute(player, cond):
                    return False
            elif ctype == 'flag':
                if not self._check_flag(player, cond):
                    return False
        return True
        
    def _check_has_item(self, player, cond: dict) -> bool:
        item_id = cond.get('target', '')
        return player.inventory.has_item(item_id, cond.get('value', 1))
        
    def _check_attribute(self, player, cond: dict) -> bool:
        attr = cond.get('target', '')
        val = cond.get('value', 0)
        actual = getattr(player, attr, 0)
        op = cond.get('operator', '>=')
        if op == '>=': return actual >= val
        if op == '<=': return actual <= val
        if op == '>': return actual > val
        if op == '<': return actual < val
        if op == '==': return actual == val
        return True
        
    def _check_flag(self, player, cond: dict) -> bool:
        flag = cond.get('target', '')
        return flag in player.flags
        
    def _execute_actions(self, actions: list, player) -> EventResult:
        result = EventResult()
        for action in actions:
            atype = action.get('type')
            if atype == 'message':
                result.messages.append(action.get('text', ''))
            elif atype == 'give_item':
                item_id = action.get('item_id', '')
                qty = action.get('quantity', 1)
                if player.inventory.add_item(item_id, qty):
                    result.give_items.append((item_id, qty))
                    result.messages.append(f"获得了 {item_id} x{qty}！")
            elif atype == 'change_attribute':
                attr = action.get('target', '')
                val = action.get('value', 0)
                if hasattr(player, attr):
                    old = getattr(player, attr)
                    setattr(player, attr, old + val)
                    result.changes[attr] = (old, old + val)
                    if attr == 'hp':
                        player.hp = min(player.max_hp, max(0, player.hp))
                    if attr == 'mp':
                        player.mp = min(player.max_mp, max(0, player.mp))
            elif atype == 'spawn_monster':
                result.spawn_monster = action.get('monster_id', '')
            elif atype == 'teleport':
                result.teleport_dest = (action.get('floor', 1), action.get('x', 0), action.get('y', 0))
            elif atype == 'open_dialogue':
                result.open_dialogue = action.get('dialogue_id', '')
            elif atype == 'open_shop':
                result.open_shop = action.get('category', '')
            elif atype == 'set_flag':
                player.flags.add(action.get('flag', ''))
            elif atype == 'game_over':
                result.game_over = True
                result.messages.append(action.get('text', '游戏结束'))
        return result
