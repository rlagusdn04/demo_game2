import pygame
import random

seed_path = "data/ditto.png"

# 타일 클래스
class Tile:
    def __init__(self, x, y, tile_type, tile_size):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.walkable = tile_type not in ['water']  # 장애물 판정
        self.rect = pygame.Rect(x, y, tile_size, tile_size)  # 충돌 판정을 위한 rect 생성

    def draw(self, screen, tile_size, camera_x, camera_y):
        colors = {
            'grass': (34, 139, 34),
            'stone': (169, 169, 169),  # stone 색상을 회색으로 설정
            'water': (0, 0, 255),
        }
        color = colors.get(self.tile_type, (255, 255, 255))
        pygame.draw.rect(
            screen,
            color,
            (self.x - camera_x, self.y - camera_y, tile_size, tile_size)
        )

class TileMap:
    def __init__(self, map_width, map_height, tile_size):
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.tiles = []
        self.obstacles = []  # 장애물 리스트

    def generate(self, data):
        for row_idx, row in enumerate(data):
            for col_idx, tile_type in enumerate(row):
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size
                tile = Tile(x, y, tile_type, self.tile_size)
                self.tiles.append(tile)

                # 장애물 타일을 obstacles에 추가
                if not tile.walkable:
                    self.obstacles.append(tile.rect)

    def draw(self, screen, camera_x, camera_y):
        for tile in self.tiles:
            tile.draw(screen, self.tile_size, camera_x, camera_y)

class Map:
    def __init__(self):
        self.maps = [
            {
                "type": "spawn map",
                "size": (2000, 2000),
                "tilemap": None,
                "obstacles": [  # 기존 장애물 정의
                    pygame.Rect(400, 400, 100, 100),
                    pygame.Rect(800, 600, 150, 150),
                    pygame.Rect(1200, 800, 200, 50),
                ],
                "transition_zones": [
                    {"zone": pygame.Rect(1950, 950, 50, 100), "target_map": 1, "start_pos": (80, 725)},
                    {"zone": pygame.Rect(400, 490, 20, 10), "target_map": 2, "start_pos": (0, 450)}
                ],
                "map_index": 0,
                "items": []
            },
            {
                "type": "seed map",
                "size": (1000, 1000),
                "tilemap": None,
                "obstacles": [
                    pygame.Rect(300, 300, 50, 50),
                    pygame.Rect(700, 500, 100, 100),
                ],
                "transition_zones": [
                    {"zone": pygame.Rect(0, 700, 50, 100), "target_map": 0, "start_pos": (1880, 975)}
                ],
                "map_index": 1,
                "items": []
            },
            {
                "type": "shop map",
                "size": (600, 600),
                "tilemap": None,
                "obstacles": [
                    pygame.Rect(0, 500, 10000, 100),
                ],
                "transition_zones": [
                    {"zone": pygame.Rect(0, 500, 20, 10), "target_map": 0, "start_pos": (400, 530)}
                ],
                "map_index": 2,
                "items": []
            },
        ]
        self.current_map_index = 0
        self.tile_size = 50  # 타일 크기

        # 각 맵에 타일맵 데이터 초기화
        self.initialize_tilemaps()

    def initialize_tilemaps(self):
        # 타일맵 데이터 정의
        spawn_map_data = [
            ['stone', 'stone', 'stone', 'stone', 'stone'],
            ['stone', 'stone', 'stone', 'stone', 'stone'],
            ['stone', 'stone', 'stone', 'stone', 'stone'],
            ['stone', 'stone', 'stone', 'stone', 'stone'],
            ['stone', 'stone', 'stone', 'stone', 'stone'],
        ]
        seed_map_data = [
            ['grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'water', 'water', 'grass', 'stone'],
            ['grass', 'water', 'water', 'grass', 'stone'],
            ['grass', 'grass', 'water', 'stone', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass'],
        ]

        # TileMap 초기화
        self.maps[0]["tilemap"] = TileMap(5, 3, self.tile_size)
        self.maps[0]["tilemap"].generate(spawn_map_data)
        self.maps[0]["obstacles"].extend(self.maps[0]["tilemap"].obstacles)

        self.maps[1]["tilemap"] = TileMap(5, 3, self.tile_size)
        self.maps[1]["tilemap"].generate(seed_map_data)
        self.maps[1]["obstacles"].extend(self.maps[1]["tilemap"].obstacles)

    def get_current_map(self):
        return self.maps[self.current_map_index]

    def change_map(self, target_map_index, start_pos, player):
        self.current_map_index = target_map_index
        player.set_position(*start_pos)

    def add_item(self, item):
        self.get_current_map()["items"].append(item)

    def remove_item(self, item):
        self.get_current_map()["items"].remove(item)

    def draw(self, screen, camera, seed_manager):
        current_map = self.get_current_map()

        # 타일맵 그리기
        if current_map["tilemap"]:
            current_map["tilemap"].draw(screen, camera.camera_x, camera.camera_y)

        # 장애물 그리기
        for obstacle in current_map["obstacles"]:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (obstacle.x - camera.camera_x, obstacle.y - camera.camera_y, obstacle.width, obstacle.height)
            )

        # 전환 존 그리기
        for zone in current_map["transition_zones"]:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (zone["zone"].x - camera.camera_x, zone["zone"].y - camera.camera_y, zone["zone"].width, zone["zone"].height)
            )

        # 아이템 그리기
        for item in current_map["items"]:
            if item["type"] == "seed":
                frame = seed_manager.seed_frames[seed_manager.frame_index]
                screen.blit(
                    frame,
                    (item["position"][0] - camera.camera_x, item["position"][1] - camera.camera_y)
                )

        seed_manager.update(current_map)

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

            # 초기 씨앗 생성: 맵에 씨앗이 없으면 5개 생성
            if len(current_map_seeds) == 0:
                print("맵에 씨앗이 없어 초기화 중...")
                for _ in range(self.max_seeds):
                    self.spawn_seed(current_map)
                self.global_timer = current_time  # 타이머 초기화
                return

            # 정기 씨앗 생성
            if len(current_map_seeds) < self.max_seeds and current_time - self.global_timer >= self.spawn_interval:
                self.spawn_seed(current_map)
                self.global_timer = current_time

        # 애니메이션 업데이트
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

            if any(obstacle.collidepoint(seed_position) for obstacle in obstacles):
                continue

            if any(zone["zone"].collidepoint(seed_position) for zone in transition_zones):
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
