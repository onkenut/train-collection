import json
from typing import Optional, Any
from dungeonscript.data.database import Database

class Item:
    def __init__(self, item_id: str, template: dict):
        self.item_id = item_id
        self.name = template.get('name', '物品')
        self.type = template.get('item_type', template.get('type', 'consumable'))
        self.rarity = template.get('rarity', 'common')
        self.description = template.get('description', '')
        self.stats = json.loads(template.get('stats', '{}')) if isinstance(template.get('stats'), str) else template.get('stats', {})
        self.value = template.get('value', 0)
        self.stackable = bool(template.get('stackable', False))
        
    @property
    def slot_type(self) -> Optional[str]:
        if self.type == 'weapon': return 'weapon'
        if self.type == 'armor': return 'armor'
        return None

class Inventory:
    MAX_SLOTS = 20
    
    def __init__(self, save_slot: int, db: Database):
        self.save_slot = save_slot
        self.db = db
        self.items: list[tuple[Item, int]] = []
        self._load()
        
    def _load(self):
        rows = self.db.get_inventory(self.save_slot)
        for row in rows:
            tpl = self.db.get_item_template(row['item_id'])
            if tpl:
                item = Item(row['item_id'], tpl)
                self.items.append((item, row['quantity']))
                
    def _save(self):
        pass
        
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        tpl = self.db.get_item_template(item_id)
        if not tpl:
            return False
        item = Item(item_id, tpl)
        if item.stackable:
            for i, (existing, qty) in enumerate(self.items):
                if existing.item_id == item_id:
                    self.items[i] = (existing, qty + quantity)
                    self.db.update_inventory_item(self.save_slot, item_id, quantity=qty+quantity)
                    return True
        if len(self.items) >= self.MAX_SLOTS:
            return False
        self.items.append((item, quantity))
        self.db.add_inventory_item(self.save_slot, item_id, quantity)
        return True
        
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        for i, (item, qty) in enumerate(self.items):
            if item.item_id == item_id:
                if qty > quantity:
                    self.items[i] = (item, qty - quantity)
                    self.db.update_inventory_item(self.save_slot, item_id, quantity=qty-quantity)
                else:
                    self.items.pop(i)
                    self.db.remove_inventory_item(self.save_slot, item_id, quantity)
                return True
        return False
        
    def get_quantity(self, item_id: str) -> int:
        for item, qty in self.items:
            if item.item_id == item_id:
                return qty
        return 0
        
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        return self.get_quantity(item_id) >= quantity
        
    def use_item(self, item_id: str) -> Optional[dict]:
        for i, (item, qty) in enumerate(self.items):
            if item.item_id == item_id:
                if item.type == 'consumable':
                    effect = {'heal': item.stats.get('heal', 0), 'mp': item.stats.get('mp', 0), 'buff': item.stats.get('buff', {})}
                    if qty > 1:
                        self.items[i] = (item, qty - 1)
                        self.db.update_inventory_item(self.save_slot, item_id, quantity=qty-1)
                    else:
                        self.items.pop(i)
                        self.db.remove_inventory_item(self.save_slot, item_id, 1)
                    return effect
        return None
        
    def equip_item(self, item_id: str, equipment_slots: dict) -> bool:
        for item, qty in self.items:
            if item.item_id == item_id and qty > 0:
                slot = item.slot_type
                if slot:
                    old = equipment_slots.get(slot)
                    if old:
                        self.db.update_inventory_item(self.save_slot, old.item_id, is_equipped=0)
                    equipment_slots[slot] = item
                    self.db.update_inventory_item(self.save_slot, item_id, is_equipped=1, slot_type=slot)
                    return True
        return False
        
    def unequip_item(self, slot: str, equipment_slots: dict) -> Optional[Item]:
        item = equipment_slots.get(slot)
        if item:
            equipment_slots[slot] = None
            self.db.update_inventory_item(self.save_slot, item.item_id, is_equipped=0, slot_type=None)
            return item
        return None
        
    def craft(self, a_id: str, b_id: str) -> Optional[str]:
        if not (self.has_item(a_id) and self.has_item(b_id)):
            return None
        recipes = self.db.get_all_crafting_recipes()
        for r in recipes:
            if (r['ingredient_a'] == a_id and r['ingredient_b'] == b_id) or (r['ingredient_a'] == b_id and r['ingredient_b'] == a_id):
                self.remove_item(a_id, 1)
                self.remove_item(b_id, 1)
                self.add_item(r['result_item'], 1)
                return r['result_item']
        return None
        
    def __len__(self) -> int:
        return len(self.items)
        
    def __iter__(self):
        return iter(self.items)
