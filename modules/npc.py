import pygame
import time

npc1_path = "data/Leah.png"

class NPC:
    def __init__(self, id, name, type, map_index, x, y, dialogue):
        self.id = id
        self.name = name
        self.type = type
        self.map_index = map_index
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.sprite_path = npc1_path
        self.image = self.load_sprite()
        self.dialogue = dialogue if dialogue else ["None"]  # 기본 대사
        self.show_dialogue = False
        self.current_dialogue_index = 0
        self.sell_check = False
        self.dialogue_timer = 0  # 대사 전환 타이머
        self.last_dialogue_end_time = 0  # 대화 종료 시간 기록
        self.dialogue_interval = 500  # 대화 간격 (밀리초)
        self.interaction = False

    def interact(self, player, camera, event):
        """플레이어와 상호작용 시 대화 상자를 활성화하고 대사를 순환"""
        if player.state == "selling":  # 거래 중이라면 대화 처리 중단
            return

        if not self.show_dialogue:  # 상호작용이 처음 시작되면
            self.show_dialogue = True
            self.current_dialogue_index = 0  # 대화 시작 시 첫 번째 대사로 초기화
            player.state = "talking"
            print(player.state)
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e and player.state == "talking":  # 'E' 키를 눌렀을 때
                if self.current_dialogue_index < len(self.dialogue) - 1:  # 인덱스가 범위를 초과하지 않을 때만
                    self.current_dialogue_index += 1  # 대사 전환
                else:  # 마지막 대사일 경우 대화 종료
                    self.show_dialogue = False
                    self.current_dialogue_index = 0  # 초기화
                    self.dialogue_timer = 0
                    player.state = "idle"
                    self.interaction = False
                    return
                
                if self.type == "shop" and self.sell_check == False and "sell" in self.dialogue[self.current_dialogue_index] :  # 거래 시작
                    self.sell_check = True  # 판매 상태 변경
                    self.sell(player, camera, event)

    def sell(self, player, camera, event):
        items = [0,1,2,3]  # 판매 가능한 품목 ID 리스트
        player.state = "selling"
   
        if self.sell_check:  # 거래 가능 상태인지 확인
            camera.show_inventory = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # ESC 키를 눌렀을 때
                self.sell_check = False  # 거래 상태 종료
                camera.show_inventory = False
                player.state = "talking"  # 다시 대화 상태로 전환
                self.current_dialogue_index += 1
                return

            selected_item_id = camera.select_item()  # 선택된 아이템의 ID를 반환
    
            if selected_item_id is not None:  # 선택된 아이템이 있는 경우
                selected_item = next((item for item in player.inventory if item["id"] == selected_item_id), None)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  #마우스 클릭 확인
                    if selected_item and selected_item["id"] in items:  # 판매 가능한 품목인지 확인
                        sell_price = selected_item.get("price", 0)  # 가격 정보 가져오기 (기본값 0)
                        if sell_price > 0 and selected_item["quantity"] > 0:
                            player.money += sell_price  # 플레이어 돈 증가
                            selected_item["quantity"] -= 1  # 아이템 개수 감소

                    


    def draw(self, screen, camera):
        draw_x = self.x - camera.camera_x
        draw_y = self.y - camera.camera_y

        #pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y, self.width, self.height))
        screen.blit(self.image, (draw_x, draw_y - 30))

        if self.show_dialogue:
            self.draw_dialogue_box(screen, camera)

    def draw_dialogue_box(self, screen, camera):
        if not self.show_dialogue:
            return
        
        

        box_width = 500
        box_height = 100
        box_x = 150
        box_y = 450

        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

        font = pygame.font.Font(None, 24)
        current_text = self.print_dialogue()

        text_surface = font.render(current_text, True, (255, 255, 255))
        screen.blit(text_surface, (box_x + 10, box_y + 10))

    def print_dialogue(self, text=None):
        if text:
            return text
        if self.current_dialogue_index >= len(self.dialogue):  # 범위 초과 방지
            return "...?"  # 기본값 설정
        return self.dialogue[self.current_dialogue_index]

    def update(self):
        pass

    def load_sprite(self):
        sprite_sheet = pygame.image.load(self.sprite_path).convert_alpha()
        frame_width = 16
        frame_height = 32
        idle_image = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        idle_image.blit(sprite_sheet, (0, 0), (0, 0, frame_width, frame_height))

        scale_factor = 2
        new_width = int(frame_width * scale_factor)
        new_height = int(frame_height * scale_factor)
        scaled_image = pygame.transform.scale(idle_image, (new_width, new_height))

        return scaled_image


class NPCManager:
    def __init__(self):
        self.npcs = []
        self.updated_npcs = []
        self.last_interact_time = 0
        self.interact_cooldown = 500  # 상호작용 쿨타임 (밀리초 단위, 500ms)
        self.interacting = False  # 상호작용 상태 변수 추가

    def add_npc(self, npc):
        self.npcs.append(npc)

    def update(self, game_map):
        current_map = game_map.get_current_map()["map_index"]
        self.updated_npcs.clear()

        for npc in self.npcs:
            if npc.map_index == current_map:
                npc.update()
                self.updated_npcs.append(npc)

    def draw(self, screen, camera):
        for npc in self.updated_npcs:
            npc.draw(screen, camera)