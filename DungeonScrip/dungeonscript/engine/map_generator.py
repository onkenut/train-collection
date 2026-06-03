TILE_WALL = 0
TILE_FLOOR = 1
TILE_DOOR = 2
TILE_TRAP = 3
TILE_CHEST = 4
TILE_EXIT = 5
TILE_UPSTAIRS = 6

TILE_SYMBOLS = {0: '#', 1: '.', 2: '+', 3: '^', 4: '*', 5: '>', 6: '<'}


class Room:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + w - 1, y + h - 1
    @property
    def center(self): return ((self.x1+self.x2)//2, (self.y1+self.y2)//2)
    def intersect(self, other) -> bool:
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1


class DungeonMap:
    def __init__(self, width: int = 40, height: int = 20, floor: int = 1, seed: int = None):
        import random
        self.width, self.height = width, height
        self.floor = floor
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.tiles = [[TILE_WALL]*height for _ in range(width)]
        self.rooms: list[Room] = []
        self.monsters = []
        self.items = []
        self.explored = [[False]*height for _ in range(width)]
        
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
        
    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y): return False
        return self.tiles[x][y] in (TILE_FLOOR, TILE_DOOR, TILE_CHEST, TILE_EXIT, TILE_UPSTAIRS)
        
    def carve_room(self, room: Room):
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                self.tiles[x][y] = TILE_FLOOR
                
    def carve_h_corridor(self, x1: int, x2: int, y: int):
        for x in range(min(x1,x2), max(x1,x2)+1):
            self.tiles[x][y] = TILE_FLOOR
            
    def carve_v_corridor(self, y1: int, y2: int, x: int):
        for y in range(min(y1,y2), max(y1,y2)+1):
            self.tiles[x][y] = TILE_FLOOR
            
    def get_random_floor_tile(self) -> tuple[int, int]:
        while True:
            x = self.rng.randint(1, self.width-2)
            y = self.rng.randint(1, self.height-2)
            if self.tiles[x][y] == TILE_FLOOR:
                return (x, y)


class BSPGenerator:
    @staticmethod
    def generate(width: int, height: int, floor: int, seed: int = None) -> DungeonMap:
        dungeon = DungeonMap(width, height, floor, seed)
        leaves = []
        max_leaf_size = 12
        min_room_size = 5
        
        class Leaf:
            def __init__(self, x, y, w, h):
                self.x, self.y, self.w, self.h = x, y, w, h
                self.child1 = self.child2 = None
                self.room = None
            def split(self, rng):
                if self.child1 or self.child2: return False
                split_h = rng.random() < 0.5
                max_size = self.h if split_h else self.w
                if max_size <= max_leaf_size: return False
                split = rng.randint(min_room_size, max_size - min_room_size)
                if split_h:
                    self.child1 = Leaf(self.x, self.y, self.w, split)
                    self.child2 = Leaf(self.x, self.y+split, self.w, self.h - split)
                else:
                    self.child1 = Leaf(self.x, self.y, split, self.h)
                    self.child2 = Leaf(self.x+split, self.y, self.w - split, self.h)
                return True
            def create_rooms(self, rng, dungeon):
                if self.child1 or self.child2:
                    if self.child1: self.child1.create_rooms(rng, dungeon)
                    if self.child2: self.child2.create_rooms(rng, dungeon)
                    if self.child1 and self.child2:
                        c1 = self.child1.get_room_center()
                        c2 = self.child2.get_room_center()
                        if rng.random() < 0.5:
                            dungeon.carve_h_corridor(c1[0], c2[0], c1[1])
                            dungeon.carve_v_corridor(c1[1], c2[1], c2[0])
                        else:
                            dungeon.carve_v_corridor(c1[1], c2[1], c1[0])
                            dungeon.carve_h_corridor(c1[0], c2[0], c2[1])
                else:
                    room_w = min_room_size
                    room_h = min_room_size
                    if self.w - 1 > min_room_size:
                        room_w = rng.randint(min_room_size, self.w - 1)
                    if self.h - 1 > min_room_size:
                        room_h = rng.randint(min_room_size, self.h - 1)
                    max_x = self.w - room_w
                    max_y = self.h - room_h
                    rx = self.x + (rng.randint(0, max_x) if max_x > 0 else 0)
                    ry = self.y + (rng.randint(0, max_y) if max_y > 0 else 0)
                    self.room = Room(rx, ry, room_w, room_h)
                    dungeon.carve_room(self.room)
                    dungeon.rooms.append(self.room)
            def get_room_center(self):
                if self.room: return self.room.center
                c1 = self.child1.get_room_center() if self.child1 else (0,0)
                c2 = self.child2.get_room_center() if self.child2 else (0,0)
                return ((c1[0]+c2[0])//2, (c1[1]+c2[1])//2)
        
        root = Leaf(0, 0, width, height)
        leaves.append(root)
        split = True
        while split:
            split = False
            for l in leaves[:]:
                if not l.child1 and not l.child2:
                    if l.split(dungeon.rng):
                        leaves.extend([l.child1, l.child2])
                        split = True
        root.create_rooms(dungeon.rng, dungeon)
        return dungeon


class CellularAutomataGenerator:
    @staticmethod
    def generate(width: int, height: int, floor: int, seed: int = None, fill_prob: float = 0.45, iterations: int = 5) -> DungeonMap:
        dungeon = DungeonMap(width, height, floor, seed)
        for x in range(width):
            for y in range(height):
                if x == 0 or y == 0 or x == width-1 or y == height-1:
                    dungeon.tiles[x][y] = TILE_WALL
                else:
                    dungeon.tiles[x][y] = TILE_FLOOR if dungeon.rng.random() < fill_prob else TILE_WALL
        for _ in range(iterations):
            new_tiles = [row[:] for row in dungeon.tiles]
            for x in range(1, width-1):
                for y in range(1, height-1):
                    walls = 0
                    for dx in (-1,0,1):
                        for dy in (-1,0,1):
                            if dungeon.tiles[x+dx][y+dy] == TILE_WALL:
                                walls += 1
                    new_tiles[x][y] = TILE_FLOOR if walls < 5 else TILE_WALL
            dungeon.tiles = new_tiles
        for x in range(1, width-1):
            for y in range(1, height-1):
                if dungeon.tiles[x][y] == TILE_FLOOR:
                    dungeon.rooms.append(Room(x, y, 3, 3))
                    break
            if dungeon.rooms:
                break
        return dungeon


class MapPopulator:
    monster_by_floor = {
        1: ['giant_rat', 'cave_bat'],
        3: ['goblin', 'giant_rat', 'cave_bat'],
        5: ['skeleton', 'zombie', 'goblin'],
        7: ['orc_warrior', 'skeleton', 'zombie'],
        10: ['dark_mage', 'orc_warrior', 'werewolf'],
        13: ['vampire_spawn', 'gargoyle', 'dark_mage'],
        15: ['shadow_assassin', 'hell_hound', 'vampire_spawn'],
        17: ['lich_minion', 'iron_golem', 'shadow_assassin'],
        19: ['dragon_whelp', 'banshee', 'lich_minion'],
        20: ['mind_flayer', 'beholder_eye', 'deep_horror', 'abyssal_librarian']
    }
    
    item_by_floor = {
        1: ['health_potion', 'rusty_dagger', 'leather_armor'],
        4: ['health_potion', 'mana_potion', 'iron_sword', 'chainmail'],
        7: ['great_health_potion', 'steel_longsword', 'plate_armor'],
        10: ['elixir_of_power', 'flame_blade', 'shadow_cloak'],
        13: ['phoenix_feather', 'holy_avenger', 'holy_armor'],
        16: ['staff_of_wisdom', 'dragon_scale_armor', 'book_of_spells'],
        20: ['dragon_slayer', 'ancient_scroll_7']
    }
    
    @staticmethod
    def get_monster_pool(floor: int) -> list[str]:
        pool = []
        for f, m in MapPopulator.monster_by_floor.items():
            if floor >= f:
                pool = m
        return pool
    
    @staticmethod
    def get_item_pool(floor: int) -> list[str]:
        pool = []
        for f, i in MapPopulator.item_by_floor.items():
            if floor >= f:
                pool = i
        return pool
    
    @staticmethod
    def populate(dungeon: DungeonMap):
        monster_count = 3 + dungeon.floor // 2
        item_count = 2 + dungeon.floor // 3
        
        monster_pool = MapPopulator.get_monster_pool(dungeon.floor)
        item_pool = MapPopulator.get_item_pool(dungeon.floor)
        
        for _ in range(monster_count):
            x, y = dungeon.get_random_floor_tile()
            monster_id = dungeon.rng.choice(monster_pool)
            dungeon.monsters.append({'monster_id': monster_id, 'x': x, 'y': y})
        
        for _ in range(item_count):
            x, y = dungeon.get_random_floor_tile()
            item_id = dungeon.rng.choice(item_pool)
            dungeon.items.append({'item_id': item_id, 'x': x, 'y': y})
        
        if dungeon.rooms:
            ex, ey = dungeon.rooms[-1].center
            dungeon.tiles[ex][ey] = TILE_EXIT
        
        if dungeon.floor >= 1:
            scroll_id = f"ancient_scroll_{min(dungeon.floor, 7)}"
            sx, sy = dungeon.get_random_floor_tile()
            dungeon.items.append({'item_id': scroll_id, 'x': sx, 'y': sy})
        
        return dungeon
