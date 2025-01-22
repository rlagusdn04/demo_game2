import pygame
import random
import time

class Map:
    def __init__(self):
        self.maps = [
            {
                "type": "spawn map",
                "size": (2000, 2000),
                "obstacles": [
                    pygame.Rect(400, 400, 100, 100),
                    pygame.Rect(800, 600, 150, 150),
                    pygame.Rect(1200, 800, 200, 50),
                ],
                "transition_zones": [
                    {"zone": pygame.Rect(1950, 950, 50, 100), "target_map": 1, "start_pos": (80, 725)}
                ],
                "map_index": 0,
                "items": [] # 아이템 정보 추가
            },
            {
                "type": "seed map",
                "size": (1000, 1000),
                "obstacles": [
                    pygame.Rect(300, 300, 50, 50),
                    pygame.Rect(700, 500, 100, 100),
                ],
                "transition_zones": [
                    {"zone": pygame.Rect(0, 700, 50, 100), "target_map": 0, "start_pos": (1880, 975)}
                ],
                "map_index": 1,
                "items": [] # 아이템 정보 추가
            },
        ]
        self.current_map_index = 0

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
        screen.fill((50, 50, 50))

        # Draw obstacles
        for obstacle in current_map["obstacles"]:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (obstacle.x - camera.camera_x, obstacle.y - camera.camera_y, obstacle.width, obstacle.height)
            )

        # Draw transition zones
        for zone in current_map["transition_zones"]:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (zone["zone"].x - camera.camera_x, zone["zone"].y - camera.camera_y, zone["zone"].width, zone["zone"].height)
            )

         # Draw items
        for item in current_map["items"]:
            pygame.draw.circle(
                screen,
                (255, 255, 0),  # Yellow for seeds
                (item["position"][0] - camera.camera_x, item["position"][1] - camera.camera_y),
                5,
            )

        
        seed_manager.update(current_map)


class SeedManager:
    def __init__(self, game_map):
        self.global_timer = time.time()
        self.spawn_interval = 5
        self.max_seeds = 5
        self.game_map = game_map

    def update(self, current_map):
        # 씨앗 생성
        if current_map["type"] == "seed map":
            current_map_seeds = [
                seed for seed in current_map["items"] if seed["type"] == "seed"
            ]
            if len(current_map_seeds) < self.max_seeds:
                current_time = time.time()
                if current_time - self.global_timer >= self.spawn_interval:
                    self.spawn_seed(current_map)
                    self.global_timer = current_time

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
            # 장애물과 충돌 확인
            if not any(obstacle.collidepoint(seed_position) for obstacle in obstacles):
                break

            # trans zone과 충돌 확인
            if not any(transition_zone.collidepoint(seed_position) for transition_zone in transition_zones):
                break

        seed_id = random.choice([1, 2, 3])
        seed_item = {
            "map_index": map_index,
            "position": seed_position,
            "type": "seed",
            "id": seed_id,

        }

        # Map 클래스에 씨앗 추가
        self.game_map.add_item(seed_item)
        print(f"씨앗 생성: {seed_position}")


