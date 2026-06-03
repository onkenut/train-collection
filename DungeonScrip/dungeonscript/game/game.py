import time
import json
import random
from typing import Optional
from dungeonscript.data.database import Database
from dungeonscript.data.loader import DataLoader
from dungeonscript.engine.map_generator import BSPGenerator, CellularAutomataGenerator, MapPopulator, DungeonMap, TILE_EXIT
from dungeonscript.engine.character import Player, Monster
from dungeonscript.engine.combat import CombatSystem, CombatResult
from dungeonscript.engine.inventory import Inventory
from dungeonscript.engine.event_manager import EventManager
from dungeonscript.ui.renderer import GameRenderer
from dungeonscript.ui.console import InputReader, Terminal

class GameState:
    MENU = "menu"
    PLAYING = "playing"
    COMBAT = "combat"
    INVENTORY = "in_inventory"
    CHARACTER = "in_character"
    SHOP = "in_shop"
    DIALOGUE = "in_dialogue"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class DungeonScriptGame:
    def __init__(self, db: Database, theme: str = 'classic'):
        self.db = db
        self.loader = DataLoader(db)
        self.event_manager = EventManager(self.loader)
        self.renderer = GameRenderer(theme)
        self.state = GameState.MENU
        self.player: Optional[Player] = None
        self.inventory: Optional[Inventory] = None
        self.dungeon: Optional[DungeonMap] = None
        self.messages = ["欢迎来到 DungeonScript！"]
        self.current_combat: Optional[CombatSystem] = None
        self.combat_monster: Optional[Monster] = None
        self.menu_selected = 0
        self.menu_stack = []
        self.start_time = 0.0
        
    def main_menu(self):
        Terminal.clear()
        options = ["新游戏", "加载存档", "排行榜", "设置", "退出"]
        selected = 0
        with InputReader() as reader:
            while True:
                self.renderer.console.clear()
                self.renderer.console.print("\n" + "="*60, style="title")
                self.renderer.console.print("        ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗\n        ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║\n        ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║\n        ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║\n        ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║\n        ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝\n", style="title")
                self.renderer.console.print("="*60 + "\n", style="title")
                self.renderer.console.print(self.renderer.render_menu("主菜单", options, selected))
                
                key = reader.read_key()
                if key == 'up':
                    selected = (selected - 1) % len(options)
                elif key == 'down':
                    selected = (selected + 1) % len(options)
                elif key == 'enter':
                    if selected == 0:
                        self.new_game_menu()
                    elif selected == 1:
                        self.load_game_menu()
                    elif selected == 2:
                        self.show_leaderboard()
                    elif selected == 3:
                        self.settings_menu()
                    elif selected == 4:
                        return
                elif key == 'escape':
                    return
                    
    def new_game_menu(self):
        slots = self.db.list_saves()
        used = {s['slot'] for s in slots}
        options = [f"存档槽 {i+1}" + (f" - {slots[i]['player_name']}" if i < len(slots) else " (空)") for i in range(3)]
        selected = 0
        with InputReader() as reader:
            while True:
                self.renderer.console.clear()
                self.renderer.console.print(self.renderer.render_menu("选择存档槽", options, selected))
                self.renderer.console.print("\n  按 ENTER 确认，ESC 返回", style="log_text")
                
                key = reader.read_key()
                if key == 'up':
                    selected = (selected - 1) % len(options)
                elif key == 'down':
                    selected = (selected + 1) % len(options)
                elif key == 'enter':
                    self.start_new_game(selected)
                    return
                elif key == 'escape':
                    return
                    
    def load_game_menu(self):
        saves = self.db.list_saves()
        if not saves:
            with InputReader() as reader:
                self.renderer.console.clear()
                self.renderer.console.print(Panel(Text("\n  没有可用的存档。\n\n  按任意键返回...", style="status_text"), border_style="highlight"))
                reader.read_key()
            return
            
        options = [f"槽 {s['slot']} - {s['player_name']} Lv.{s['level']} (层{s['current_floor']})" for s in saves]
        options.append("删除存档...")
        options.append("返回")
        selected = 0
        with InputReader() as reader:
            while True:
                self.renderer.console.clear()
                self.renderer.console.print(self.renderer.render_menu("加载存档", options, selected))
                
                key = reader.read_key()
                if key == 'up':
                    selected = (selected - 1) % len(options)
                elif key == 'down':
                    selected = (selected + 1) % len(options)
                elif key == 'enter':
                    if selected == len(options) - 1:
                        return
                    elif selected == len(options) - 2:
                        self.delete_save_menu(saves)
                        return
                    else:
                        self.load_game(saves[selected]['slot'])
                        return
                elif key == 'escape':
                    return
                    
    def delete_save_menu(self, saves):
        options = [f"槽 {s['slot']} - {s['player_name']}" for s in saves]
        options.append("取消")
        selected = 0
        with InputReader() as reader:
            while True:
                self.renderer.console.clear()
                self.renderer.console.print(self.renderer.render_menu("删除存档", options, selected))
                self.renderer.console.print("\n  [警告] 删除后不可恢复！", style="bar_hp")
                
                key = reader.read_key()
                if key == 'up':
                    selected = (selected - 1) % len(options)
                elif key == 'down':
                    selected = (selected + 1) % len(options)
                elif key == 'enter':
                    if selected < len(saves):
                        self.db.delete_save(saves[selected]['slot'])
                    return
                elif key == 'escape':
                    return
                    
    def show_leaderboard(self):
        entries = self.db.get_leaderboard(10)
        lines = []
        for i, e in enumerate(entries, 1):
            status = "通关" if e['completed'] else "放弃"
            lines.append(f"  {i:2d}. {e['player_name']:12s} 分数:{e['score']:6d} 层数:{e['floor_reached']:3d}  {status}")
        if not lines:
            lines = ["  暂无记录"]
        text = Text("\n".join(lines), style="status_text")
        with InputReader() as reader:
            self.renderer.console.clear()
            self.renderer.console.print(Panel(text, title=" 排行榜 ", border_style="highlight"))
            self.renderer.console.print("\n  按任意键返回...", style="log_text")
            reader.read_key()
            
    def settings_menu(self):
        from dungeonscript.ui.theme import Themer
        themes = Themer.list()
        options = [f"主题: {t}" for t in themes]
        options.append("返回")
        selected = 0
        with InputReader() as reader:
            while True:
                self.renderer.console.clear()
                self.renderer.console.print(self.renderer.render_menu("设置", options, selected))
                
                key = reader.read_key()
                if key == 'up':
                    selected = (selected - 1) % len(options)
                elif key == 'down':
                    selected = (selected + 1) % len(options)
                elif key == 'enter':
                    if selected == len(options) - 1:
                        return
                    else:
                        self.renderer = GameRenderer(themes[selected])
                elif key == 'escape':
                    return
                    
    def start_new_game(self, slot: int):
        self.player = Player("无名冒险者", slot)
        self.player.hardcore = False
        self.inventory = Inventory(slot, self.db)
        self.player.inventory = self.inventory
        self.inventory.add_item('health_potion', 3)
        self.inventory.add_item('rusty_dagger', 1)
        self.inventory.equip_item('rusty_dagger', self.player.equipment)
        self.generate_floor(1)
        self.save_game()
        self.messages = ["你踏入了深渊图书馆...", "传说中失落的典籍就藏在深处..."]
        self.start_time = time.time()
        self.game_loop()
        
    def load_game(self, slot: int):
        data = self.db.load_save(slot)
        if not data:
            return
        self.player = Player.from_dict(data, slot)
        self.inventory = Inventory(slot, self.db)
        self.player.inventory = self.inventory
        self.load_floor(self.player.current_floor)
        self.messages = [f"欢迎回来，{self.player.name}！"]
        self.start_time = time.time()
        self.game_loop()
        
    def generate_floor(self, floor: int):
        self.player.current_floor = floor
        seed = random.randint(0, 999999)
        if floor % 3 == 0:
            self.dungeon = CellularAutomataGenerator.generate(50, 25, floor, seed)
        else:
            self.dungeon = BSPGenerator.generate(50, 25, floor, seed)
        MapPopulator.populate(self.dungeon)
        if self.dungeon.rooms:
            self.player.x, self.player.y = self.dungeon.rooms[0].center
        self.save_map_state()
        
    def load_floor(self, floor: int):
        state = self.db.load_map_state(self.player.save_slot, floor)
        if state:
            seed = state['map_seed']
            if floor % 3 == 0:
                self.dungeon = CellularAutomataGenerator.generate(50, 25, floor, seed)
            else:
                self.dungeon = BSPGenerator.generate(50, 25, floor, seed)
            MapPopulator.populate(self.dungeon)
            explored = json.loads(state['explored']) if state.get('explored') else [[False]*25 for _ in range(50)]
            self.dungeon.explored = explored
        else:
            self.generate_floor(floor)
            
    def save_map_state(self):
        explored = json.dumps(self.dungeon.explored)
        self.db.save_map_state(self.player.save_slot, self.player.current_floor,
                               self.dungeon.seed, explored, '[]', '[]', '[]')
                               
    def save_game(self):
        data = self.player.to_dict()
        self.db.create_save(self.player.save_slot, **data)
        self.save_map_state()
        
    def game_loop(self):
        self.state = GameState.PLAYING
        with InputReader() as reader:
            while self.state not in (GameState.GAME_OVER, GameState.VICTORY, GameState.MENU):
                if self.state == GameState.PLAYING:
                    self.render_game()
                    key = reader.read_key()
                    self.handle_movement(key)
                elif self.state == GameState.COMBAT:
                    self.render_combat()
                    key = reader.read_key()
                    self.handle_combat_input(key)
                elif self.state == GameState.INVENTORY:
                    self.render_inventory()
                    key = reader.read_key()
                    self.handle_inventory_input(key)
                elif self.state == GameState.CHARACTER:
                    self.render_character()
                    key = reader.read_key()
                    if key in ('escape', 'c', 'enter'):
                        self.state = GameState.PLAYING
                        
                if self.player and self.player.is_dead:
                    self.state = GameState.GAME_OVER
                    self.handle_death()
                    
        if self.state == GameState.GAME_OVER or self.state == GameState.VICTORY:
            self.show_end_screen()
            
    def render_game(self):
        self.renderer.render_game(self.dungeon, self.player, self.messages)
        
    def handle_movement(self, key: str):
        dx, dy = 0, 0
        if key in ('w', 'up'):
            dy = -1
        elif key in ('s', 'down'):
            dy = 1
        elif key in ('a', 'left'):
            dx = -1
        elif key in ('d', 'right'):
            dx = 1
        elif key == 'i':
            self.state = GameState.INVENTORY
            self.menu_selected = 0
            return
        elif key == 'c':
            self.state = GameState.CHARACTER
            return
        elif key == 'e':
            self.interact()
            return
        elif key == 'escape':
            if self.confirm_menu("确定要返回主菜单吗？"):
                self.state = GameState.MENU
            return
        else:
            return
            
        nx, ny = self.player.x + dx, self.player.y + dy
        if self.dungeon.is_walkable(nx, ny):
            monster = self.get_monster_at(nx, ny)
            if monster:
                self.start_combat(monster)
            else:
                self.player.x, self.player.y = nx, ny
                self.player.game_time += 0.1
                self.check_tile_events()
                self.save_game()
        else:
            pass
            
    def get_monster_at(self, x: int, y: int):
        for m in self.dungeon.monsters:
            if m['x'] == x and m['y'] == y:
                tpl = self.db.get_monster_template(m['monster_id'])
                if tpl:
                    monster = Monster(m['monster_id'], tpl)
                    monster.x, monster.y = x, y
                    return monster
        return None
        
    def check_tile_events(self):
        tile = self.dungeon.tiles[self.player.x][self.player.y]
        if tile == TILE_EXIT:
            self.messages.append("你找到了通往下一层的楼梯！")
            if self.confirm_menu("进入下一层？"):
                self.next_floor()
            return
            
        for i in self.dungeon.items[:]:
            if i['x'] == self.player.x and i['y'] == self.player.y:
                if self.inventory.add_item(i['item_id'], 1):
                    tpl = self.db.get_item_template(i['item_id'])
                    name = tpl.get('name', i['item_id']) if tpl else i['item_id']
                    self.messages.append(f"你捡到了 {name}！")
                    self.dungeon.items.remove(i)
                    
    def next_floor(self):
        new_floor = self.player.current_floor + 1
        if new_floor > 20:
            self.state = GameState.VICTORY
            return
        self.generate_floor(new_floor)
        self.messages = [f"你来到了第 {new_floor} 层..."]
        self.db.add_log(self.player.save_slot, 'floor', f"进入第 {new_floor} 层")
        self.save_game()
        
    def interact(self):
        events = self.event_manager.check_trigger('interact', self.player, self.dungeon, self.player.x, self.player.y)
        for ev in events:
            self.messages.extend(ev.messages)
        if not events:
            self.messages.append("这里没什么特别的...")
            
    def confirm_menu(self, question: str) -> bool:
        selected = 0
        options = ["是", "否"]
        with InputReader() as reader:
            while True:
                self.render_game()
                t = Text()
                t.append(f"\n  {question}\n\n", style="highlight")
                for i, opt in enumerate(options):
                    if i == selected:
                        t.append(f"    [{opt}]", style="menu_selected")
                    else:
                        t.append(f"     {opt} ", style="menu_normal")
                self.renderer.console.print(Panel(t, border_style="highlight"))
                
                key = reader.read_key()
                if key in ('left', 'a'):
                    selected = (selected - 1) % len(options)
                elif key in ('right', 'd'):
                    selected = (selected + 1) % len(options)
                elif key == 'enter':
                    return selected == 0
                elif key == 'escape':
                    return False
                    
    def start_combat(self, monster: Monster):
        self.combat_monster = monster
        self.current_combat = CombatSystem(self.player, monster, self.db, self.player.save_slot)
        self.state = GameState.COMBAT
        self.combat_skill_mode = False
        self.combat_item_mode = False
        self.messages = [f"遭遇了 {monster.name}！"]
        self.db.add_log(self.player.save_slot, 'combat', f"遭遇 {monster.name}")
        
    def render_combat(self):
        cs = {'monster_name': self.combat_monster.name,
              'monster_hp': self.combat_monster.hp,
              'monster_max_hp': self.combat_monster.max_hp} if self.combat_monster else None
        self.renderer.render_game(self.dungeon, self.player, self.messages, cs)
        
    def handle_combat_input(self, key: str):
        if self.combat_skill_mode:
            self._handle_skill_key(key)
            return
        if self.combat_item_mode:
            self._handle_combat_item_key(key)
            return
            
        if key == 'a':
            result = self.current_combat.do_round('attack')
            self.messages.extend(result.messages[-3:])
            self._check_combat_end()
        elif key == 's':
            self.combat_skill_mode = True
            self.messages.append("选择技能：1.强力一击  2.火球术  [ESC取消]")
        elif key == 'i':
            self.combat_item_mode = True
            self._show_combat_items()
        elif key == 'r':
            result = self.current_combat.do_round('escape')
            if result.escape:
                self.messages.append("成功逃跑！")
                self.state = GameState.PLAYING
                self.current_combat = None
                self.combat_monster = None
                return
            self.messages.extend(result.messages[-3:])
            self._check_combat_end()
        elif key == 'escape':
            return
            
    def _handle_skill_key(self, key: str):
        if key == 'escape':
            self.combat_skill_mode = False
            self.messages.pop()
            return
        skill_map = {'1': 'power_strike', '2': 'fireball'}
        if key in skill_map:
            skill_id = skill_map[key]
            skill_tpl = self.db.get_skill_template(skill_id)
            if skill_tpl:
                result = self.current_combat.do_round('skill', skill_tpl)
                self.messages.extend(result.messages[-3:])
                self.combat_skill_mode = False
                self._check_combat_end()
                
    def _show_combat_items(self):
        consumables = [(item, qty) for item, qty in self.inventory.items if item.type == 'consumable']
        if not consumables:
            self.messages.append("没有可用的消耗品！")
            self.combat_item_mode = False
            return
        msg = "选择物品："
        for i, (item, qty) in enumerate(consumables[:5], 1):
            msg += f" {i}.{item.name}x{qty} "
        msg += " [ESC取消]"
        self.messages.append(msg)
        self._combat_items = consumables[:5]
        
    def _handle_combat_item_key(self, key: str):
        if key == 'escape':
            self.combat_item_mode = False
            self.messages.pop()
            return
        try:
            idx = int(key) - 1
            if 0 <= idx < len(self._combat_items):
                item, qty = self._combat_items[idx]
                effect = self.inventory.use_item(item.item_id)
                if effect:
                    if effect.get('heal'):
                        self.player.heal(effect['heal'])
                        self.messages.append(f"使用了 {item.name}，恢复了 {effect['heal']} HP！")
                    if effect.get('mp'):
                        self.player.restore_mp(effect['mp'])
                        self.messages.append(f"使用了 {item.name}，恢复了 {effect['mp']} MP！")
                    self.combat_item_mode = False
                    result = self.current_combat.do_round('item')
                    self.messages.extend(result.messages[-2:])
                    self._check_combat_end()
        except ValueError:
            pass
            
    def _check_combat_end(self):
        if self.current_combat.result.victory:
            exp = self.current_combat.result.exp_gained
            level_msgs = self.player.gain_exp(exp)
            self.messages.extend(level_msgs)
            for item_id, qty in self.current_combat.result.loot:
                if item_id != 'gold':
                    self.inventory.add_item(item_id, qty)
            for i, m in enumerate(self.dungeon.monsters):
                if m['x'] == self.combat_monster.x and m['y'] == self.combat_monster.y:
                    self.dungeon.monsters.pop(i)
                    break
            self.state = GameState.PLAYING
            self.current_combat = None
            self.combat_monster = None
            self.save_game()
        elif self.current_combat.result.player_died:
            self.state = GameState.GAME_OVER
            
    def render_inventory(self):
        self.render_game()
        t = Text()
        t.append(f"\n  背包 ({len(self.inventory)}/{Inventory.MAX_SLOTS})\n\n", style="title")
        for i, (item, qty) in enumerate(self.inventory):
            prefix = ">" if i == self.menu_selected else " "
            rarity = ""
            if item.rarity == 'magic': rarity = "bright_blue"
            elif item.rarity == 'rare': rarity = "bright_magenta"
            elif item.rarity == 'legendary': rarity = "gold1"
            t.append(f"  {prefix}{i+1:2d}. ", style="status_text")
            t.append(f"{item.name}", style=rarity)
            if qty > 1:
                t.append(f" x{qty}", style="log_text")
            t.append(f" - {item.type}\n", style="log_text")
        t.append("\n  [ENTER]使用/装备  [U]卸下  [C]合成  [ESC]关闭", style="highlight")
        self.renderer.console.print(Panel(t, border_style="highlight"))
        
    def handle_inventory_input(self, key: str):
        n = len(self.inventory)
        if key == 'up':
            self.menu_selected = (self.menu_selected - 1) % max(1, n)
        elif key == 'down':
            self.menu_selected = (self.menu_selected + 1) % max(1, n)
        elif key == 'escape':
            self.state = GameState.PLAYING
        elif key == 'enter' and n > 0:
            item, qty = self.inventory.items[self.menu_selected]
            if item.type == 'consumable':
                effect = self.inventory.use_item(item.item_id)
                if effect:
                    if effect.get('heal'):
                        self.player.heal(effect['heal'])
                        self.messages.append(f"使用了 {item.name}，恢复了 {effect['heal']} HP！")
                    if effect.get('mp'):
                        self.player.restore_mp(effect['mp'])
                        self.messages.append(f"使用了 {item.name}，恢复了 {effect['mp']} MP！")
            elif item.slot_type:
                self.inventory.equip_item(item.item_id, self.player.equipment)
                self.messages.append(f"装备了 {item.name}！")
        elif key == 'u' and n > 0:
            item, qty = self.inventory.items[self.menu_selected]
            if item.slot_type and self.player.equipment.get(item.slot_type) == item:
                self.inventory.unequip_item(item.slot_type, self.player.equipment)
                self.messages.append(f"卸下了 {item.name}")
                
    def render_character(self):
        self.render_game()
        t = Text()
        t.append(f"\n  {self.player.name}\n\n", style="title")
        t.append(f"  等级: {self.player.level}\n", style="status_text")
        t.append(f"  经验: {self.player.exp} / {self.player.level * 50}\n\n", style="status_text")
        t.append(f"  HP: {self.player.hp}/{self.player.max_hp}\n", style="bar_hp")
        t.append(f"  MP: {self.player.mp}/{self.player.max_mp}\n\n", style="bar_mp")
        t.append(f"  攻击: {self.player.attack}  (基础 {self.player.base_attack})\n", style="status_text")
        t.append(f"  防御: {self.player.defense}  (基础 {self.player.base_defense})\n", style="status_text")
        t.append(f"  速度: {self.player.speed}\n\n", style="status_text")
        t.append("  装备:\n", style="highlight")
        for slot, item in self.player.equipment.items():
            if item:
                t.append(f"    {slot}: {item.name}\n", style="status_text")
            else:
                t.append(f"    {slot}: 无\n", style="log_text")
        t.append("\n  按任意键返回...", style="log_text")
        self.renderer.console.print(Panel(t, border_style="highlight"))
        
    def handle_death(self):
        self.db.add_log(self.player.save_slot, 'death', '角色死亡')
        score = self.player.level * 100 + self.player.current_floor * 50 + int(self.player.gold)
        self.db.add_leaderboard_entry(self.player.name, score, self.player.current_floor, self.player.game_time, 0)
        if self.player.hardcore:
            self.db.delete_save(self.player.save_slot)
            
    def show_end_screen(self):
        with InputReader() as reader:
            self.renderer.console.clear()
            t = Text()
            if self.state == GameState.VICTORY:
                t.append("\n\n" + "="*60 + "\n", style="gold")
                t.append("          ╔══════════════════════════════════════╗\n", style="gold")
                t.append("          ║            胜 利 ！                   ║\n", style="gold")
                t.append("          ╚══════════════════════════════════════╝\n", style="gold")
                t.append("="*60 + "\n\n", style="gold")
                t.append(f"  恭喜你，{self.player.name}！\n", style="status_text")
                t.append("  你击败了深渊图书馆的守护者，\n", style="status_text")
                t.append("  找回了所有失落的典籍！\n\n", style="status_text")
            else:
                t.append("\n\n" + "="*60 + "\n", style="bar_hp")
                t.append("          ╔══════════════════════════════════════╗\n", style="bar_hp")
                t.append("          ║            你 死 了                   ║\n", style="bar_hp")
                t.append("          ╚══════════════════════════════════════╝\n", style="bar_hp")
                t.append("="*60 + "\n\n", style="bar_hp")
                t.append(f"  你倒在了第 {self.player.current_floor} 层...\n\n", style="status_text")
                
            t.append(f"  等级: {self.player.level}\n", style="status_text")
            t.append(f"  层数: {self.player.current_floor}\n", style="status_text")
            t.append(f"  金币: {self.player.gold}\n", style="gold")
            t.append(f"  时间: {int(self.player.game_time)} 秒\n\n", style="status_text")
            t.append("  按任意键返回主菜单...", style="log_text")
            self.renderer.console.print(Panel(t, border_style="highlight"))
            reader.read_key()

from rich.panel import Panel
from rich.text import Text
