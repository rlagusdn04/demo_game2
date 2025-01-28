import pygame
import random
import time

seed_path = "data/seed.jpg"

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
                    {"zone": pygame.Rect(1950, 950, 50, 100), "target_map": 1, "start_pos": (80, 725)},
                    {"zone": pygame.Rect(400, 490, 20, 10), "target_map": 2, "start_pos": (0, 450)}
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
            {
                "type": "house map",
                "size": (600, 600),
                "obstacles": [
                    pygame.Rect(0, 500, 10000, 100),
                    #pygame.Rect(500, 500, 100, 100)
                ],
                "transition_zones": [
                    {"zone": pygame.Rect(0, 500, 20, 10), "target_map": 0, "start_pos": (400, 530)}
                ],
                "map_index": 2,
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

          # Draw items with animation
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
        self.global_timer = time.time()
        self.spawn_interval = 5
        self.max_seeds = 5
        self.game_map = game_map
        self.sheet = Item_Sheet(seed_path)
        self.seed_frames = self.sheet.get_animation_frames(0, 0, 500, 500, 4)  # 프레임 4개 가져오기
        self.frame_index = 0
        self.animation_timer = time.time()
        self.animation_interval = 0.2  # 프레임 전환 속도

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

        # 애니메이션 프레임 업데이트
        if time.time() - self.animation_timer >= self.animation_interval:
            self.frame_index = (self.frame_index + 1) % len(self.seed_frames)
            self.animation_timer = time.time()

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
            if any(obstacle.collidepoint(seed_position) for obstacle in obstacles):
                continue  # 충돌 발생 시 새로운 위치를 찾음

            # 전환 구역과 충돌 확인
            if any(zone["zone"].collidepoint(seed_position) for zone in transition_zones):
                continue 

            break

        seed_id = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0] # 확률 조정
        seed_item = {
            "map_index": map_index,
            "position": seed_position,
            "type": "seed",
            "id": seed_id,
        }

        # Map 클래스에 씨앗 추가
        self.game_map.add_item(seed_item)
        print(f"씨앗 생성: {seed_position}")


class Item_Sheet:
    def __init__(self, file_path, scale_factor=0.05):
        self.sheet = pygame.image.load(file_path)
        self.scale_factor = scale_factor

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))

        # 축소된 이미지 반환
        if self.scale_factor != 1:
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image

    def get_animation_frames(self, start_x, start_y, frame_width, frame_height, num_frames):
        frames = []
        for i in range(num_frames):
            frame_x = start_x + i * frame_width
            frame_y = start_y
            frames.append(self.get_image(frame_x, frame_y, frame_width, frame_height))
        return frames

