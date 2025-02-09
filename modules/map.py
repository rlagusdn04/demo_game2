import pygame
import random
import json

seed_path = "data/ditto.png"
shop_path = "data/shop.jpg"

####################################
# 타일 클래스
####################################
class Tile:
    def __init__(self, x, y, tile_type, tile_size):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.tile_size = tile_size
        self.walkable = tile_type not in ['water']  # 장애물 판정 (water는 걸을 수 없음)
        self.rect = pygame.Rect(x, y, tile_size, tile_size)  # 충돌 판정을 위한 rect 생성
        self.planted_time = 0  # 작물이 심어진 시간
        self.growth_stage = 0  # 작물의 성장 단계 (0: 심어진 직후, 1: 성장 중, 2: 완전히 성장)
        self.crop_type = 1     # 작물의 종류 (예: "carrot", "potato", 등)
        print("타일 생성")

    def draw(self, screen, tile_size, camera_x, camera_y):
        types = {
            'grass': (34, 139, 34),
            'stone': (169, 169, 169),
            'water': (0, 0, 255),
            'soil': (139, 69, 19),
            'planted soil': (139, 69, 19),
        }
        color = types.get(self.tile_type, (255, 255, 255))
        pygame.draw.rect(
            screen,
            color,
            (self.x - camera_x, self.y - camera_y, tile_size, tile_size)
        )

        # 작물이 심어진 경우
        if self.tile_type == 'planted soil' and self.crop_type:
            crop_color = (0, 255, 0) if self.growth_stage == 2 else (255, 165, 0)
            pygame.draw.circle(
                screen,
                crop_color,
                (self.x - camera_x + tile_size // 2, self.y - camera_y + tile_size // 2),
                tile_size // 4
            )

    def update_growth(self, dt):
        if self.tile_type == 'planted soil' and self.crop_type:
            self.planted_time += dt
            if self.planted_time >= 10000:
                self.growth_stage = 2
            elif self.planted_time >= 5000:
                self.growth_stage = 1

    def harvest(self):
        if self.tile_type == 'planted soil' and self.growth_stage == 2:
            self.tile_type = 'soil'
            self.planted_time = 0
            self.growth_stage = 0
            self.crop_type = None
            return True
        return False
    
    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.rect.topleft = (new_x, new_y)

####################################
# 타일맵 클래스
####################################
class TileMap:
    def __init__(self, map_width, map_height, tile_size=50):
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.tiles = []
        self.obstacles = []

    def generate(self, data):
        for row_idx, row in enumerate(data):
            for col_idx, tile_type in enumerate(row):
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size
                tile = Tile(x, y, tile_type, self.tile_size)
                self.tiles.append(tile)
                if not tile.walkable:
                    self.obstacles.append(tile.rect)

    def draw(self, screen, camera_x, camera_y):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        visible_tiles = [
            tile for tile in self.tiles
            if (camera_x - screen_width * 0.25 <= tile.rect.x < camera_x + screen_width * 1.25 and
                camera_y - screen_height * 0.25 <= tile.rect.y < camera_y + screen_height * 1.25)
        ]
        for tile in visible_tiles:
            tile.draw(screen, self.tile_size, camera_x, camera_y)

    def update_tile_position(self, old_x, old_y, new_x, new_y):
        for tile in self.tiles:
            if tile.x == old_x and tile.y == old_y:
                tile.update_position(new_x, new_y)
                break

    def update_tile_type(self, x, y, new_type, tile_map, game_map):
        current_map = game_map.get_current_map()
        for row_idx, row in enumerate(tile_map):
            for col_idx, tile_type in enumerate(row):
                if col_idx * self.tile_size == x and row_idx * self.tile_size == y:
                    tile_map[row_idx][col_idx] = new_type
                    current_map["tilemap"][row_idx][col_idx] = new_type
                    break

####################################
# 맵 클래스 (배경 이미지 처리 포함)
####################################
class Map:
    def __init__(self, json_file="maps_data.json"):
        self.json_file = json_file
        self.maps = []
        self.current_map_index = 0
        self.tile_size = 50
        self.tile_map = None
        self.background_images = {}  # 캐싱용
        self.load_maps()

    def load_maps(self):
        try:
            with open(self.json_file, 'r') as file:
                data = json.load(file)
                self.maps = data["maps"]
                print("맵 데이터 로드 완료")
        except FileNotFoundError:
            print("맵 데이터 파일이 없으므로 새로 생성합니다.")
            self.initialize_maps()
            self.save_maps()

        current_map = self.get_current_map()
        if current_map["tilemap"]:
            self.tile_map = TileMap(len(current_map["tilemap"][0]), len(current_map["tilemap"]))
            self.tile_map.generate(current_map["tilemap"])

    def initialize_maps(self):
        # 예시로 세 개의 맵 데이터를 정의합니다.
        map0_data = [
            ["grass"] * 9,
            ["grass"] * 9,
            ["grass"] * 9,
            ["grass", "planted soil", "planted soil", "planted soil", "planted soil", "planted soil", "planted soil", "grass", "grass"],
            ["grass", "planted soil", "soil", "soil", "soil", "planted soil", "planted soil", "grass", "grass"],
            ["grass"] * 9
        ]
        map1_data = []  # seed map은 tilemap 없이 배경 없이 관리 (아이템 중심)
        map2_data = []  # shop map도 tilemap 없이 단순 배경 이미지로 처리

        self.maps = [
            {
                "type": "spawn map",
                "size": [2000, 2000],
                "background_path": None,  # spawn map은 tilemap을 사용
                "tilemap": map0_data,
                "obstacles": [
                    {"x": 400, "y": 400, "width": 100, "height": 100},
                    {"x": 800, "y": 600, "width": 150, "height": 150},
                ],
                "transition_zones": [
                    {"zone": {"x": 1950, "y": 950, "width": 50, "height": 100}, "target_map": 1, "start_pos": [80, 725]},
                    {"zone": {"x": 400, "y": 490, "width": 20, "height": 10}, "target_map": 2, "start_pos": [0, 450]}
                ],
                "map_index": 0,
                "items": []
            },
            {
                "type": "seed map",
                "size": [1000, 1000],
                "background_path": None,
                "tilemap": map1_data,
                "obstacles": [
                    {"x": 300, "y": 300, "width": 50, "height": 50},
                    {"x": 700, "y": 500, "width": 100, "height": 100},
                ],
                "transition_zones": [
                    {"zone": {"x": 0, "y": 700, "width": 50, "height": 100}, "target_map": 0, "start_pos": [1880, 975]}
                ],
                "map_index": 1,
                "items": [
                    {"map_index": 1, "position": [58, 869], "type": "seed", "id": 0},
                    {"map_index": 1, "position": [251, 225], "type": "seed", "id": 0},
                    {"map_index": 1, "position": [368, 234], "type": "seed", "id": 0},
                    {"map_index": 1, "position": [77, 999], "type": "seed", "id": 1},
                    {"map_index": 1, "position": [114, 677], "type": "seed", "id": 1}
                ]
            },
            {
                "type": "shop map",
                "size": [600, 600],
                "background_path": shop_path,  # shop map은 shop_path 배경 이미지를 사용
                "tilemap": map2_data,
                "obstacles": [
                    {"x": 0, "y": 500, "width": 800, "height": 100}
                ],
                "transition_zones": [
                    {"zone": {"x": 0, "y": 500, "width": 20, "height": 10}, "target_map": 0, "start_pos": [400, 530]}
                ],
                "map_index": 2,
                "items": []
            }
        ]

    def save_maps(self):
        self.sync_tilemap_data()
        data = {"maps": self.maps}
        with open(self.json_file, 'w') as file:
            json.dump(data, file, indent=4)
        print("맵 데이터 저장 완료")

    def sync_tilemap_data(self):
        current_map = self.get_current_map()
        num_rows = len(current_map["tilemap"])
        num_cols = len(current_map["tilemap"][0]) if num_rows > 0 else 0
        if self.tile_map is None:
            return
        for tile in self.tile_map.tiles:
            col_idx = tile.x // self.tile_map.tile_size
            row_idx = tile.y // self.tile_map.tile_size
            if 0 <= row_idx < num_rows and 0 <= col_idx < num_cols:
                current_map["tilemap"][row_idx][col_idx] = tile.tile_type

    def load_background_image(self, path, screen_size):
        if path in self.background_images:
            return self.background_images[path]
        try:
            image = pygame.image.load(path).convert()
            image = pygame.transform.scale(image, screen_size)
            self.background_images[path] = image
            print(f"배경 이미지 로드 완료: {path}")
            return image
        except Exception as e:
            print("배경 이미지 로드 실패:", path, e)
            return None

    def get_current_map(self):
        return self.maps[self.current_map_index]

    def change_map(self, target_map_index, start_pos, player):
        self.current_map_index = target_map_index
        player.set_position(*start_pos)
        current_map = self.get_current_map()
        if self.tile_map:
            self.tile_map.tiles.clear()
            self.tile_map.obstacles.clear()
        if current_map["tilemap"]:
            self.tile_map = TileMap(len(current_map["tilemap"][0]), len(current_map["tilemap"]))
            self.tile_map.generate(current_map["tilemap"])

    def add_item(self, item):
        self.get_current_map()["items"].append(item)

    def remove_item(self, item):
        self.get_current_map()["items"].remove(item)

    def draw(self, screen, camera, seed_manager):
        current_map = self.get_current_map()
        screen_size = (screen.get_width(), screen.get_height())
        
        # type 값을 확인하여 배경 이미지를 결정합니다.
        if current_map["type"] == "shop map":
            # shop map은 배경 이미지를 불러옴
            bg_image = self.load_background_image(shop_path, screen_size)
            if bg_image:
                screen.blit(bg_image, (0, 0))
        else:
            # 다른 맵은 tilemap이나 다른 배경 방식 적용 (예를 들어 spawn map은 tilemap)
            if self.tile_map:
                self.tile_map.draw(screen, camera.camera_x, camera.camera_y)
        
        # 장애물 그리기
        for obstacle in current_map["obstacles"]:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (obstacle["x"] - camera.camera_x, obstacle["y"] - camera.camera_y,
                 obstacle["width"], obstacle["height"])
            )
        
        # 전환 존 그리기
        for zone in current_map["transition_zones"]:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (zone["zone"]["x"] - camera.camera_x, zone["zone"]["y"] - camera.camera_y,
                 zone["zone"]["width"], zone["zone"]["height"])
            )
        
        # 아이템 (씨앗) 그리기
        for item in current_map["items"]:
            if item["type"] == "seed":
                frame = seed_manager.seed_frames[seed_manager.frame_index]
                screen.blit(
                    frame,
                    (item["position"][0] - camera.camera_x, item["position"][1] - camera.camera_y)
                )
        
        seed_manager.update(current_map)

    def plant_seed(self, player, x, y):
        tile_x = (x + 20) // self.tile_size
        tile_y = (y + 20) // self.tile_size
        if self.tile_map:
            for tile in self.tile_map.tiles:
                if tile.x // self.tile_size == tile_x and tile.y // self.tile_size == tile_y:
                    if tile.tile_type == "soil":
                        tile.tile_type = "planted soil"
                        tile.crop_type = player.inventory[0]["name"]
                        tile.planted_time = 0
                        tile.growth_stage = 0
                        return True
                    else:
                        print("흙이 아닙니다.")
                        return False
        print("해당 위치에 타일이 없습니다.")
        return False
    
    def update_crop(self, dt):
        if self.tile_map:
            for tile in self.tile_map.tiles:
                tile.update_growth(dt)
                
    def harvest_crop(self, player, x, y):
        tile_x = (x + 20) // self.tile_size
        tile_y = (y + 20) // self.tile_size
        if self.tile_map:
            for tile in self.tile_map.tiles:
                if tile.x // self.tile_size == tile_x and tile.y // self.tile_size == tile_y:
                    if tile.harvest():
                        player.add_item({"type": "crop", "id": 3}, self)
                        return True
                    else:
                        print("수확할 작물이 없습니다.")
                        return False
        print("해당 위치에 타일이 없습니다.")
        return False

####################################
# SeedManager 및 Item_Sheet 클래스
####################################
class Item_Sheet:
    def __init__(self, file_path, scale_factor=0.2):
        self.sheet = pygame.image.load(file_path)
        self.scale_factor = scale_factor

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        if self.scale_factor != 1:
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image

    def get_animation_frames(self, start_x, start_y, frame_width, frame_height, num_frames):
        frames = []
        for i in range(num_frames):
            frame_x = start_x + i * frame_width
            frames.append(self.get_image(frame_x, start_y, frame_width, frame_height))
        return frames

class SeedManager:
    def __init__(self, game_map):
        self.global_timer = pygame.time.get_ticks()
        self.spawn_interval = 5000  # 5초 간격
        self.max_seeds = 5
        self.game_map = game_map
        self.sheet = Item_Sheet(seed_path)
        self.seed_frames = self.sheet.get_animation_frames(0, 128 * 13, 128, 128, 8)
        self.frame_index = 0
        self.animation_timer = pygame.time.get_ticks()
        self.animation_interval = 200

    def update(self, current_map):
        current_time = pygame.time.get_ticks()
        if current_map["type"] == "seed map":
            current_map_seeds = [
                seed for seed in current_map["items"] if seed["type"] == "seed"
            ]
            if len(current_map_seeds) == 0:
                print("맵에 씨앗이 없어 초기화 중...")
                for _ in range(self.max_seeds):
                    self.spawn_seed(current_map)
                self.global_timer = current_time
                return
            if len(current_map_seeds) < self.max_seeds and current_time - self.global_timer >= self.spawn_interval:
                self.spawn_seed(current_map)
                self.global_timer = current_time

        if current_time - self.animation_timer >= self.animation_interval:
            self.frame_index = (self.frame_index + 1) % len(self.seed_frames)
            self.animation_timer = current_time

    def spawn_seed(self, current_map):
        map_index = current_map["map_index"]
        map_size = current_map["size"]
        obstacles = current_map["obstacles"]
        transition_zones = current_map["transition_zones"]

        while True:
            seed_position = (
                random.randint(0, map_size[0]),
                random.randint(0, map_size[1]),
            )
            valid = True
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])
                if obstacle_rect.collidepoint(seed_position):
                    valid = False
                    break
            if not valid:
                continue
            for zone in transition_zones:
                zone_rect = pygame.Rect(zone["zone"]["x"], zone["zone"]["y"], zone["zone"]["width"], zone["zone"]["height"])
                if zone_rect.collidepoint(seed_position):
                    valid = False
                    break
            if not valid:
                continue
            if not (0 <= seed_position[0] <= map_size[0] and 0 <= seed_position[1] <= map_size[1]):
                continue
            break

        seed_id = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        seed_item = {
            "map_index": map_index,
            "position": seed_position,
            "type": "seed",
            "id": seed_id,
        }
        self.game_map.add_item(seed_item)
        print(f"씨앗 생성: {seed_position}")
