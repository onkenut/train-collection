from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import BarColumn, Progress
from typing import Optional
from dungeonscript.engine.map_generator import DungeonMap, TILE_SYMBOLS, TILE_WALL, TILE_FLOOR, TILE_DOOR, TILE_TRAP, TILE_CHEST, TILE_EXIT
from dungeonscript.ui.theme import Themer

class GameRenderer:
    VIEW_RADIUS = 8
    
    def __init__(self, theme_name: str = 'classic'):
        self.theme = Themer.get(theme_name)
        self.console = Console(theme=self.theme)
        self.view_width = 50
        self.view_height = 18
        self._resize()
        
    def _resize(self):
        cols, rows = self.console.size
        self.view_width = min(80, max(40, cols - 28))
        self.view_height = min(25, max(15, rows - 10))
        
    def render_game(self, dungeon: DungeonMap, player, messages: list[str], combat_state=None):
        self._resize()
        layout = Layout()
        layout.split_column(
            Layout(self._render_status(player, dungeon.floor), name="status", size=3),
            Layout(name="main"),
            Layout(self._render_messages(messages), name="messages", size=7),
        )
        layout["main"].split_row(
            Layout(self._render_map(dungeon, player), name="map"),
            Layout(self._render_sidebar(player, combat_state), name="sidebar", size=22),
        )
        self.console.clear()
        self.console.print(layout)
        
    def _render_status(self, player, floor: int) -> Panel:
        hp_pct = player.hp / player.max_hp if player.max_hp > 0 else 0
        mp_pct = player.mp / player.max_mp if player.max_mp > 0 else 0
        
        t = Text()
        t.append(f" 层数: {floor}  ", style="highlight")
        t.append("HP: ", style="status_text")
        t.append(self._make_bar(hp_pct, 20, "bar_hp"))
        t.append(f" {player.hp}/{player.max_hp}  ", style="status_text")
        t.append("MP: ", style="status_text")
        t.append(self._make_bar(mp_pct, 15, "bar_mp"))
        t.append(f" {player.mp}/{player.max_mp}  ", style="status_text")
        t.append(f"金币: {player.gold}  ", style="gold")
        t.append(f"等级: {player.level}  ", style="highlight")
        return Panel(t, border_style="highlight")
        
    def _make_bar(self, pct: float, width: int, color: str) -> Text:
        filled = int(pct * width)
        t = Text()
        t.append("█" * filled, style=color)
        t.append("░" * (width - filled), style="bar_bg")
        return t
        
    def _render_map(self, dungeon: DungeonMap, player) -> Panel:
        dungeon.explored[player.x][player.y] = True
        for dx in range(-self.VIEW_RADIUS, self.VIEW_RADIUS + 1):
            for dy in range(-self.VIEW_RADIUS, self.VIEW_RADIUS + 1):
                nx, ny = player.x + dx, player.y + dy
                if 0 <= nx < dungeon.width and 0 <= ny < dungeon.height:
                    dungeon.explored[nx][ny] = True

        t = Text()
        view_x = max(0, min(dungeon.width - self.view_width, player.x - self.view_width // 2))
        view_y = max(0, min(dungeon.height - self.view_height, player.y - self.view_height // 2))
        
        for y in range(view_y, min(dungeon.height, view_y + self.view_height)):
            for x in range(view_x, min(dungeon.width, view_x + self.view_width)):
                dist = ((x - player.x)**2 + (y - player.y)**2) ** 0.5
                in_view = dist <= self.VIEW_RADIUS
                is_explored = dungeon.explored[x][y]
                
                if x == player.x and y == player.y:
                    t.append("@", style="map_player")
                    continue
                    
                monster_here = any(m['x'] == x and m['y'] == y for m in dungeon.monsters)
                if monster_here and in_view:
                    m_data = next(m for m in dungeon.monsters if m['x'] == x and m['y'] == y)
                    t.append(m_data.get('symbol', 'M'), style="map_monster")
                    continue
                    
                item_here = any(i['x'] == x and i['y'] == y for i in dungeon.items)
                if item_here and (in_view or is_explored):
                    t.append("!", style="map_item")
                    continue
                    
                tile = dungeon.tiles[x][y]
                if not is_explored and not in_view:
                    t.append("?", style="map_fog")
                    continue
                    
                if tile == TILE_WALL:
                    t.append(TILE_SYMBOLS.get(tile, '#'), style="map_wall")
                elif tile == TILE_DOOR:
                    t.append(TILE_SYMBOLS.get(tile, '+'), style="map_door")
                elif tile == TILE_EXIT:
                    t.append(TILE_SYMBOLS.get(tile, '>'), style="map_exit")
                elif tile == TILE_TRAP:
                    t.append(TILE_SYMBOLS.get(tile, '^'), style="map_trap")
                elif tile == TILE_CHEST:
                    t.append(TILE_SYMBOLS.get(tile, '*'), style="map_item")
                else:
                    t.append(TILE_SYMBOLS.get(tile, '.'), style="map_floor")
            t.append("\n")
                    
        return Panel(t, title=" 地图 ", border_style="highlight")
        
    def _render_sidebar(self, player, combat_state=None) -> Panel:
        t = Text()
        t.append(f" 攻击: {player.attack}\n", style="status_text")
        t.append(f" 防御: {player.defense}\n", style="status_text")
        t.append(f" 速度: {player.speed}\n", style="status_text")
        t.append(f" 经验: {player.exp}/{player.level * 50}\n", style="status_text")
        t.append(f" 背包: {len(player.inventory)} 格\n\n", style="status_text")
        
        if combat_state:
            t.append("═" * 20 + "\n", style="highlight")
            t.append(f" 战斗中: {combat_state.get('monster_name', '')}\n", style="map_monster")
            mhp = combat_state.get('monster_hp', 0)
            mmhp = combat_state.get('monster_max_hp', 0)
            t.append(f" 血量: {mhp}/{mmhp}\n", style="bar_hp")
            t.append(" [A]攻击 [S]技能 [I]物品 [R]逃跑\n", style="highlight")
        else:
            t.append("═" * 20 + "\n", style="highlight")
            t.append(" 移动: WASD/方向键\n", style="highlight")
            t.append(" [I]背包 [C]角色 [E]互动\n", style="highlight")
            t.append(" [ESC]菜单\n", style="highlight")
            
        return Panel(t, title=" 状态 ", border_style="highlight")
        
    def _render_messages(self, messages: list[str]) -> Panel:
        t = Text()
        for msg in messages[-6:]:
            t.append(f" » {msg}\n", style="log_text")
        return Panel(t, title=" 消息日志 ", border_style="highlight")
        
    def render_menu(self, title: str, options: list[str], selected: int = 0) -> Panel:
        t = Text()
        t.append(f"\n  {title}\n\n", style="title")
        for i, opt in enumerate(options):
            if i == selected:
                t.append(f"  > {opt}\n", style="menu_selected")
            else:
                t.append(f"    {opt}\n", style="menu_normal")
        return Panel(t, border_style="highlight")
        
    def print_center(self, content):
        self.console.clear()
        w, _ = self.console.size
        pad = max(0, (w - 50) // 2)
        self.console.print(" " * pad, content)
