import pygame
import random

seed_path = "data/ditto.png"

# 타일 클래스
import pygame

class Tile:
    def __init__(self, x, y, tile_type, tile_size):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.tile_size = tile_size
        self.walkable = tile_type not in ['water']  # 장애물 판정 (water는 걸을 수 없음)
        self.rect = pygame.Rect(x, y, tile_size, tile_size)  # 충돌 판정을 위한 rect 생성

    def draw(self, screen, tile_size, camera_x, camera_y):
        """타일을 화면에 그리기"""
        types = {
            'grass': (34, 139, 34),  # 풀밭
            'stone': (169, 169, 169),  # 돌
            'water': (0, 0, 255),  # 물
            'soil': (139, 69, 19),  # 흙
            'planted soil': (255, 255, 0),  # 심은 흙
        }
        color = types.get(self.tile_type, (255, 255, 255))  # 기본은 흰색
        pygame.draw.rect(
            screen,
            color,
            (self.x - camera_x, self.y - camera_y, tile_size, tile_size)
        )

    def update_position(self, new_x, new_y):
        """타일의 위치를 업데이트"""
        self.x = new_x
        self.y = new_y
        self.rect.topleft = (new_x, new_y)  # rect의 위치 갱신

class TileMap:
    def __init__(self, map_width, map_height, tile_size = 50):
        self.map_width = map_width  # 맵의 가로 크기
        self.map_height = map_height  # 맵의 세로 크기
        self.tile_size = tile_size  # 타일 크기
        self.tiles = []  # 타일 리스트
        self.obstacles = []  # 장애물 리스트 (충돌이 있는 타일들)

    def generate(self, data):
        """맵 데이터에 따라 타일 생성"""
        for row_idx, row in enumerate(data):
            for col_idx, tile_type in enumerate(row):
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size
                tile = Tile(x, y, tile_type, self.tile_size)
                self.tiles.append(tile)

                # 장애물 타일을 obstacles 리스트에 추가
                if not tile.walkable:
                    self.obstacles.append(tile.rect)

    def draw(self, screen, camera_x, camera_y):
        """화면에 보이는 타일만 그리기"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 카메라와 화면 크기를 기준으로 보이는 타일만 필터링
        visible_tiles = [
            tile for tile in self.tiles
            if (camera_x - screen_width * 0.25 <= tile.rect.x < camera_x + screen_width * 1.25 and
                camera_y - screen_height * 0.25 <= tile.rect.y < camera_y + screen_height * 1.25)
        ]
        
        # 필터링된 타일을 화면에 그리기
        for tile in visible_tiles:
            tile.draw(screen, self.tile_size, camera_x, camera_y)

    def update_tile_position(self, old_x, old_y, new_x, new_y):
        """특정 위치에 있는 타일의 위치를 갱신"""
        for tile in self.tiles:
            if tile.x == old_x and tile.y == old_y:
                tile.update_position(new_x, new_y)
                break

    def update_tile_type(self, x, y, new_type, tile_map, game_map):
        """타일의 타입을 변경하고 tilemap 데이터도 갱신"""
        current_map = game_map.get_current_map()

        for row_idx, row in enumerate(tile_map):
            for col_idx, tile_type in enumerate(row):
                # 타일 위치를 계산하여 일치하는 경우 타입 변경
                if col_idx * self.tile_size == x and row_idx * self.tile_size == y:
                    tile_map[row_idx][col_idx] = new_type  # tile_map의 타입 갱신
                    current_map["tilemap"][row_idx][col_idx] = new_type  # 맵 데이터의 타입 갱신
                    break  # 타일을 찾으면 더 이상 반복할 필요 없음

        # # 타일 객체 리스트(self.tiles)에서 해당 타일을 찾아 타입 업데이트
        # for tile in self.tiles:
        #     if tile.x == x and tile.y == y:
        #         tile.tile_type = new_type  # 타일 객체의 타입 갱신
        #         current_map["tilemap"][row_idx][col_idx] = new_type
        #         break  # 타일을 찾으면 더 이상 반복할 필요 없음
        
        


import json

class Map:
    def __init__(self, json_file="maps_data.json"):
        self.json_file = json_file
        self.maps = []
        self.current_map_index = 0
        self.tile_size = 50  # 타일 크기

        # JSON 파일에서 맵 데이터를 로드하거나 초기화
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

    def initialize_maps(self):
        # 맵 초기화 (기본 맵 데이터 정의)
        map0_data = []
        map1_data = []
        
        self.maps = [
            {
                "type": "spawn map",
                "size": (2000, 2000),
                "tilemap": map0_data,
                "obstacles": [
                    {"x": 400, "y": 400, "width": 100, "height": 100},
                    {"x": 800, "y": 600, "width": 150, "height": 150},
                ],
                "transition_zones": [
                    {"zone": {"x": 1950, "y": 950, "width": 50, "height": 100}, "target_map": 1, "start_pos": (80, 725)},
                    {"zone": {"x": 400, "y": 490, "width": 20, "height": 10}, "target_map": 2, "start_pos": (0, 450)}
                ],
                "map_index": 0,
                "items": []
            },
            {
                "type": "seed map",
                "size": (1000, 1000),
                "tilemap": map1_data,
                "obstacles": [
                    {"x": 300, "y": 300, "width": 50, "height": 50},
                    {"x": 700, "y": 500, "width": 100, "height": 100},
                ],
                "transition_zones": [
                    {"zone": {"x": 0, "y": 700, "width": 50, "height": 100}, "target_map": 0, "start_pos": (1880, 975)}
                ],
                "map_index": 1,
                "items": []
            },
        ]

    def save_maps(self):
        # 맵 데이터를 JSON 파일로 저장
        data = {"maps": self.maps}
        with open(self.json_file, 'w') as file:
            json.dump(data, file, indent=4)
        print("맵 데이터 저장 완료")

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

        # 타일맵 그리기 (타일맵이 TileMap 인스턴스여야 함)
        if current_map["tilemap"]:
            # TileMap 객체로 초기화되어야 함
            tile_map = TileMap(len(current_map["tilemap"][0]), len(current_map["tilemap"]))
            tile_map.generate(current_map["tilemap"])  # 타일 생성
            tile_map.draw(screen, camera.camera_x, camera.camera_y)  # 타일 그리기

        # 장애물 그리기
        for obstacle in current_map["obstacles"]:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (obstacle["x"] - camera.camera_x, obstacle["y"] - camera.camera_y, obstacle["width"], obstacle["height"])
            )

        # 전환 존 그리기
        for zone in current_map["transition_zones"]:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (zone["zone"]["x"] - camera.camera_x, zone["zone"]["y"] - camera.camera_y, zone["zone"]["width"], zone["zone"]["height"])
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

    def plant_seed(self, player, x, y,game_map):
        """현재 위치(x, y)에 씨앗을 심는 함수"""
        tile_x = (x + 20) // self.tile_size  # 타일 인덱스 변환
        tile_y = (y + 20) // self.tile_size

        # TileMap 객체에서 타일을 확인
        current_map = self.get_current_map()
        tile_map = TileMap(len(current_map["tilemap"][0]), len(current_map["tilemap"]))
        tile_map.generate(current_map["tilemap"])

        for tile in tile_map.tiles:  # 타일 리스트에서 직접 확인
            if tile.x // self.tile_size == tile_x and tile.y // self.tile_size == tile_y:
                if tile.tile_type == "soil":  # 흙이면 씨앗 심기 가능
                    tile.tile_type = "planted_seed"  # 씨앗 심음
                    tile_map.update_tile_type(tile.x, tile.y, "planted soil", current_map["tilemap"],game_map)  # 타일맵 데이터 업데이트

                    # 플레이어의 인벤토리에서 씨앗 개수 감소
                    player.inventory[0]["quantity"] -= 1
                    return True
                else:
                    print("흙이 아닙니다.")
                    return False

        print("해당 위치에 타일이 없습니다.")
        return False



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
        
            for obstacle in obstacles:
                obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])
                if obstacle_rect.collidepoint(seed_position):
                    continue
    

            for zone in transition_zones:
                zone_rect = pygame.Rect(zone["zone"]["x"], zone["zone"]["y"], zone["zone"]["width"], zone["zone"]["height"])
                if zone_rect.collidepoint(seed_position):
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
