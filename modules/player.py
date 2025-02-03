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

import pygame

class CollisionManager:
    def __init__(self, game_map):
        self.game_map = game_map

    def check_obstacle_collision(self, player_rect, obstacles):
        """플레이어와 장애물 충돌 판정"""
        for obstacle in obstacles:
            # 장애물의 위치와 크기를 이용하여 pygame.Rect 객체 생성
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["width"], obstacle["height"])
            if player_rect.colliderect(obstacle_rect):
                return True  # 충돌 발생
        return False  # 충돌 없음

    def check_item_collision(self, player_rect, items):
        """플레이어와 충돌한 아이템 반환"""
        for item in items:
            item_width = 40  # 기본 아이템 크기 (40x40 크기 아이템 가정)
            item_rect = pygame.Rect(
                item["position"][0] - 20,  # 아이템의 x 좌표
                item["position"][1],        # 아이템의 y 좌표
                item_width + 20,            # 아이템의 너비
                item_width                  # 아이템의 높이
            )
            if player_rect.colliderect(item_rect):
                return item  # 충돌한 아이템 반환
        return None  # 충돌한 아이템 없음

    def check_transition_zone(self, player_rect, transition_zones):
        """플레이어가 전환 존에 진입했는지 확인"""
        for zone in transition_zones:
            # 전환 존의 영역을 나타내는 사각형과 충돌 검사
            zone_rect = pygame.Rect(zone["zone"]["x"], zone["zone"]["y"], zone["zone"]["width"], zone["zone"]["height"])
            if player_rect.colliderect(zone_rect):
                return zone  # 충돌한 전환 존 반환
        return None  # 전환 존과 충돌 없음

    
    def check_npc_collision(self, player_rect, npcs):
        for npc in npcs:
            npc_rect = pygame.Rect(npc.x, npc.y, npc.width, npc.height)
            if player_rect.colliderect(npc_rect):
                return True
        return False

class Player:
    def __init__(self, x, y, size, speed, sprite_sheet):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.health = 100
        self.hp_MAX = 100
        self.level = 1
        self.experience = 0
        self.exp_MAX = 100
        self.money = 0
        self.inventory = []
        self.color = (0, 255, 0)
        self.current_animation = "stand"
        self.hand = None  # 손에 든 아이템

        # 상태 관리 초기화
        self.state = "idle"  # "idle", "moving", "picking_up"
        self.state_timer = 0
        self.pick_up_timer = 0
        self.level_up_timer = 0

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
            "pick_up_right": [
                sprite_sheet.get_image(0, 128, 128, 128),
                sprite_sheet.get_image(128, 128, 128, 128),
            ],
            "pick_up_left": [
                pygame.transform.flip(img, True, False)
                for img in [
                    sprite_sheet.get_image(0, 128, 128, 128),
                    sprite_sheet.get_image(128, 128, 128, 128),
                ]
            ],
            "level_up": [
                    sprite_sheet.get_image(128*0, 128*8, 128, 128),
                    pygame.transform.flip(sprite_sheet.get_image(128*0, 128*8, 128, 128), True, False),
                    sprite_sheet.get_image(128*1, 128*8, 128, 128),
                    pygame.transform.flip(sprite_sheet.get_image(128*1, 128*8, 128, 128), True, False),
                    sprite_sheet.get_image(128*2, 128*8, 128, 128),
                    pygame.transform.flip(sprite_sheet.get_image(128*2, 128*8, 128, 128), True, False),
                    sprite_sheet.get_image(128*3, 128*8, 128, 128),
                    pygame.transform.flip(sprite_sheet.get_image(128*3, 128*8, 128, 128), True, False),
                    sprite_sheet.get_image(128*4, 128*8, 128, 128),
                    pygame.transform.flip(sprite_sheet.get_image(128*4, 128*8, 128, 128), True, False),
    
            ],
        
        }
        self.animator = Animation(self.animations[self.current_animation], 100)

    def move(self, keys, game_map, collision_manager, dt, npc_manager,camera,event):
    
        current_map = game_map.get_current_map()
        map_width, map_height = current_map["size"]
        obstacles = current_map["obstacles"]
        transition_zones = current_map["transition_zones"]
        items = current_map["items"]

        new_x, new_y = self.x, self.y

            

        if not self.state == "talking" and not self.state == "selling":
            if keys[pygame.K_w]:
                new_y -= self.speed
                self.current_animation = "walk_up"
                self.state = "moving"
            if keys[pygame.K_s]:
                new_y += self.speed
                self.current_animation = "walk_down"
                self.state = "moving"
            if keys[pygame.K_a]:
                new_x -= self.speed
                self.current_animation = "walk_left"
                self.state = "moving"
            if keys[pygame.K_d]:
                new_x += self.speed
                self.current_animation = "walk_right"
                self.state = "moving"


        if self.state == "idle":
            self.current_animation = "stand"
            self.interaction = False

    
        if self.level_up_timer > 0:
            self.current_animation = "level_up"
            self.level_up_timer -= dt


    
        new_x = max(0, min(new_x, map_width - self.size))
        new_y = max(0, min(new_y, map_height - self.size))
        player_rect = pygame.Rect(
                    new_x,  # 가로 중심 조정
                    new_y,
                    self.size, # 오른쪽 크기 확대
                    self.size 
                    )

        if self.animator.images != self.animations[self.current_animation]:
            self.animator = Animation(self.animations[self.current_animation], 200)
        self.animator.update(dt)

        # 충돌 검사: 장애물 + NPC
        if not collision_manager.check_obstacle_collision(player_rect, obstacles) and \
            not collision_manager.check_npc_collision(player_rect, npc_manager.updated_npcs):
                self.x = new_x
                self.y = new_y


        transition_zone = collision_manager.check_transition_zone(player_rect, transition_zones)
        if transition_zone:
            collision_manager.game_map.change_map(
                transition_zone["target_map"],
                transition_zone["start_pos"],
                self
            )

        self.pick(keys,items,collision_manager,player_rect,dt,game_map)

 

    def pick(self,keys,items,collision_manager,player_rect,dt,game_map):
        collided_item = collision_manager.check_item_collision(player_rect, items)
        if collided_item:
            if keys[pygame.K_e]:

                item_x, item_y = collided_item["position"]
                if item_x >= self.x:
                    self.current_animation = "pick_up_right"
                else:
                    self.current_animation = "pick_up_left"
            
                self.pick_up_timer += dt
                if self.pick_up_timer >= 2000:  # 2초 이상 눌렀을 경우
                    self.add_item(collided_item, game_map)
                    self.state = "idle"
                    self.pick_up_timer = 0
            else:
                self.pick_up_timer = 0
    
    def plant(self,event,game_map):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:  # E키를 누르면 씨앗 심기
                if self.inventory[0]["quantity"] > 0:
                    if game_map.plant_seed(self, self.x, self.y,game_map):
                        self.current_animation = "pick_up_right"

    def interact_with_npcs(self, event, npc_manager,camera):
        """NPC와 상호작용을 처리"""
        
        for npc in npc_manager.updated_npcs:
            npc_rect = pygame.Rect(npc.x - 5 , npc.y - 5, npc.width + 10, npc.height + 10) #충돌 판정보다 크게
            player_rect = pygame.Rect(self.x, self.y, self.size, self.size)

            if player_rect.colliderect(npc_rect):  # 충돌 감지
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:  # 'E' 키를 눌렀을 때
                    if self.state == "idle" or self.state == "moving" or self.state == "talking":
                        self.state = "talking"
                        npc.interact(self,camera,event)  # 해당 NPC와 상호작용 호출
                        
                        break
            if self.state == "selling":
                npc.sell(self, camera, event)
                        

        
    def draw(self, screen, camera):
        # 현재 애니메이션 이미지 가져오기
        current_image = self.animator.get_current_image()
        screen.blit(current_image, (self.x - camera.camera_x - 16, self.y - camera.camera_y - 16))
        
        # # 줍는 범위 사각형 계산
        # pick_up_rect = pygame.Rect(
        #     self.x - camera.camera_x,  
        #     self.y - camera.camera_y,
        #     self.size,                # 가로 크기 확장
        #     self.size                      # 세로 크기
        # )
        
        # # 줍는 범위 표시 (반투명 녹색)
        # surface = pygame.Surface((pick_up_rect.width, pick_up_rect.height), pygame.SRCALPHA)
        # surface.fill((0, 255, 0, 100))  # RGBA 형식으로 알파값(투명도) 설정
        # screen.blit(surface, (pick_up_rect.x, pick_up_rect.y))

    def hand(self, item):
        self.hand = item

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def add_experience(self, exp):
        self.experience += exp
        if self.experience >= self.exp_MAX:
            self.add_level()
            self.experience = 0


    def add_level(self):
        self.level += 1
        self.state = "level_up"  # 상태 전환
        self.level_up_timer = 2000
        self.add_health(self.hp_MAX)

        self.exp_MAX = self.level * 10

    def add_money(self, money):
        self.money += money

    def add_health(self, health):
        self.health += health
        if self.health >= self.hp_MAX:
            self.health = self.hp_MAX

    def add_item(self, item, game_map):
        item_type = item.get("type")
        item_id = item.get("id")
        if item_type == "seed":
            self.add_experience(10)

        add_check = False

        for inventory_item in self.inventory:
            if inventory_item["id"] == item_id:
                inventory_item["quantity"] += 1
                add_check = True
                break
            
        # inventory에 아이템이 없으면 새로 추가
        if add_check == False:
            self.inventory.append({
                "id": item_id,
                "type": item_type,
                "quantity": 1
            })

        game_map.remove_item(item)