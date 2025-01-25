import pygame

# Camera Class
class Camera:
    def __init__(self, width, height, game_map, screen):
        self.width = width
        self.height = height
        self.camera_x = 0
        self.camera_y = 0
        self.game_map = game_map
        self.screen = screen  # Screen 객체 추가
        self.font = pygame.font.SysFont(None, 24)  # Font 초기화
        self.color = (0, 0, 0)
        self.show_inventory = False  # 인벤토리 표시 상태
        self.selected_item = None
        self.select_check = False

    def update(self, player):
        # Calculate the target position for the camera
        target_x = player.x - self.width // 2
        target_y = player.y - self.height // 2

        # Map boundaries
        current_map = self.game_map.get_current_map()
        map_width, map_height = current_map["size"]

        # Lerp for smooth movement
        lerp_factor = 1
        self.camera_x += (target_x - self.camera_x) * lerp_factor
        self.camera_y += (target_y - self.camera_y) * lerp_factor

        # Limit the camera speed
        max_speed = 25
        dx = target_x - self.camera_x
        dy = target_y - self.camera_y
        if abs(dx) > max_speed:
            self.camera_x += max_speed if dx > 0 else -max_speed
        if abs(dy) > max_speed:
            self.camera_y += max_speed if dy > 0 else -max_speed

        # Clamp camera within map boundaries
        self.camera_x = max(0, min(self.camera_x, map_width - self.width))
        self.camera_y = max(0, min(self.camera_y, map_height - self.height))

    def toggle_inventory(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            self.show_inventory = not self.show_inventory

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_inventory = False

    def draw_ui(self, player):
        health_text = self.font.render(f"Health: {player.health}", True, (0, 0, 0))
        exp_text = self.font.render(f"Experience: {player.experience}", True, (0, 0, 0))
        level_text = self.font.render(f"Level: {player.level}", True, (0, 0, 0))
        money_text = self.font.render(f"Money: {player.money}", True, (0, 0, 0))
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(level_text, (10, 25))
        self.screen.blit(exp_text, (10, 40))
        self.screen.blit(money_text, (10, 55))


    def draw_inventory(self, player):
        if self.show_inventory:
            padding = 10
            box_width = 400
            line_height = 40  # 라인 높이 늘리기
            inventory_height = len(player.inventory) * line_height + padding * 2
            box_x = 400
            box_y = 0

            # 배경 박스 그리기
            pygame.draw.rect(self.screen, (200, 200, 200), (box_x, box_y, box_width, inventory_height))
            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, inventory_height), 2)

            # 인벤토리 항목 렌더링
            for i, item in enumerate(player.inventory):
                item_name = item["name"]
                item_quantity = item["quantity"]

                # 아이템 항목 영역 계산
                item_rect = pygame.Rect(box_x + padding, box_y + padding + i * line_height, box_width - padding * 2, line_height)

                # 호버 효과 (마우스가 항목 위에 있을 때)
                if item_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (230, 230, 230), item_rect)  # 호버 색상
                    if pygame.mouse.get_pressed()[0] == 1:  # 클릭 시
                        self.selected_item = item["id"]  # 선택된 아이템 인덱스 추적
                        
                

                # 텍스트 렌더링
                inventory_text = self.font.render(f"{item_name}: {item_quantity}", True, (0, 0, 0))
                text_x = box_x + padding
                text_y = box_y + padding + i * line_height

                # 텍스트 그리기
                self.screen.blit(inventory_text, (text_x, text_y))

                
    def select_item(self):
        return self.selected_item



