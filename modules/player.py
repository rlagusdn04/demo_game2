import pygame

class SpriteSheet:
    def __init__(self, file_path, scale_factor=0.5):
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

class Animation:
    def __init__(self, images, frame_duration):
        self.images = images
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_counter = 0

    def update(self, dt):
        self.time_counter += dt
        if self.time_counter >= self.frame_duration:
            self.time_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.images)

    def get_current_image(self):
        return self.images[self.current_frame]


class CollisionManager:
    def __init__(self, game_map):
        self.game_map = game_map

    def check_obstacle_collision(self, player_rect, obstacles):
        for obstacle in obstacles:
            if player_rect.colliderect(obstacle):
                return True
        return False

    def check_item_collision(self, player_rect, items):
        """플레이어와 충돌한 아이템 반환"""
        for item in items:
            item_rect = pygame.Rect(item["position"][0], item["position"][1], 15, 15)  # 아이템 크기를 10x10으로 가정
            if player_rect.colliderect(item_rect):
                return item
        return None



    def check_transition_zone(self, player_rect, transition_zones):
        for zone in transition_zones:
            if player_rect.colliderect(zone["zone"]):
                return zone
        return None

class Player:
    def __init__(self, x, y, size, speed,sprite_sheet):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.health = 100
        self.level = 1
        self.experience = 0
        self.money = 0
        self.inventory = []
        self.color = (0, 255, 0)
        self.current_animation = "stand"
        

         # 애니메이션 초기화
        self.animations = {
            "stand": [
                sprite_sheet.get_image(0, 0, 128, 128),
                sprite_sheet.get_image(128, 0, 128, 128),
                sprite_sheet.get_image(128*2, 0, 128, 128),
            ],
            "walk_down": [
                sprite_sheet.get_image(0, 0, 128, 128),
                sprite_sheet.get_image(128, 0, 128, 128),
                sprite_sheet.get_image(128*2, 0, 128, 128),
            ],
            "walk_up": [
                sprite_sheet.get_image(0, 128*5, 128, 128),
                sprite_sheet.get_image(0, 128*6, 128, 128),
                sprite_sheet.get_image(128*3, 128*7, 128, 128),
                sprite_sheet.get_image(128*2, 128*7, 128, 128)
            ],
            "walk_left": [
                 pygame.transform.flip(img, True, False)
                for img in [
                    sprite_sheet.get_image(0, 0, 128, 128),
                    sprite_sheet.get_image(128, 0, 128, 128),
                    sprite_sheet.get_image(128*2, 0, 128, 128),
                ]
            ],
            "walk_right": [
                sprite_sheet.get_image(0, 0, 128, 128),
                sprite_sheet.get_image(128, 0, 128, 128),
                sprite_sheet.get_image(128*2, 0, 128, 128),
            ],
            "pick_up":[
                sprite_sheet.get_image(0, 128, 128, 128),
                sprite_sheet.get_image(128, 128, 128, 128),
            ],
        }
        self.animator = Animation(self.animations[self.current_animation], 100)
        

    def move(self, keys, game_map, collision_manager):
        current_map = game_map.get_current_map()
        map_width, map_height = current_map["size"]
        obstacles = current_map["obstacles"]
        transition_zones = current_map["transition_zones"]
        items = current_map["items"]
        

        new_x, new_y = self.x, self.y

        if keys[pygame.K_w]:
            new_y -= self.speed
            self.current_animation = "walk_up"
        if keys[pygame.K_s]:
            new_y += self.speed
            self.current_animation = "walk_down"
        if keys[pygame.K_a]:
            new_x -= self.speed
            self.current_animation = "walk_left"
        if keys[pygame.K_d]:
            new_x += self.speed
            self.current_animation = "walk_right"
        # else:
        #     self.current_animation = "stand"


        # Prevent player from moving outside the map boundaries
        new_x = max(0, min(new_x, map_width - self.size))
        new_y = max(0, min(new_y, map_height - self.size))

        player_rect = pygame.Rect(new_x, new_y, self.size, self.size)

        # 애니메이션 업데이트
        if self.animator.images != self.animations[self.current_animation]:
            self.animator = Animation(self.animations[self.current_animation], 200)
        self.animator.update(1000 / 60)



        # Obstacle collision
        if not collision_manager.check_obstacle_collision(player_rect, obstacles):
            self.x = new_x
            self.y = new_y
    

        # Item collision
        collided_item = collision_manager.check_item_collision(player_rect, items)
        if collided_item:
            if keys[pygame.K_e]:
                self.add_item(collided_item, game_map)
                self.current_animation = "pick_up"


        # Transition zone collision
        transition_zone = collision_manager.check_transition_zone(player_rect, transition_zones)
        if transition_zone:
            collision_manager.game_map.change_map(
                transition_zone["target_map"],
                transition_zone["start_pos"],
                self
            )


    def draw(self, screen, camera):
        pygame.draw.rect(
            screen,
            self.color,
            (self.x - camera.camera_x, self.y - camera.camera_y, self.size, self.size),
        )

        current_image = self.animator.get_current_image()
        screen.blit(current_image, (self.x - camera.camera_x - 16, self.y - camera.camera_y - 24))


    def set_position(self, x, y):
        self.x = x
        self.y = y

    def add_experience(self, exp):
        self.experience += exp
        if self.experience >= 100 and self.level < 10:
            self.level += 1
            self.experience = 0

    def add_money(self, money):
        self.money += money

    def add_health(self, health):
        self.health += health
    
    def add_item(self, item, game_map):

        # 아이템 분류
        item_type = item.get("type")
        if item_type == "seed":
            # 씨앗을 습득하면 경험치를 10 추가
            self.add_experience(10)

        # 인벤토리에 이미 존재하는 동일 아이템 확인
        for inventory_item in self.inventory:
            if inventory_item["type"] == item_type:
                inventory_item["quantity"] += 1
                break

        game_map.remove_item(item)