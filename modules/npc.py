import pygame
import time

npc1_path = "Leah.png" 

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
        self.dialogue = dialogue if dialogue else ["!!!", "nice to meet you!", "It's a nice day ;)"]
        self.show_dialogue = False
        self.current_dialogue_index = 0
        self.dialogue_timer = 0  # 대사 전환 타이머
        self.last_dialogue_end_time = 0  # 대화 종료 시간 기록
        self.dialogue_interval = 500  # 대화 간격 (밀리초)

    def interact(self):
        """플레이어와 상호작용 시 대화 상자를 활성화하고 대사를 순환"""
        current_time = pygame.time.get_ticks()

        # 대화 종료 후 일정 시간 동안 상호작용을 제한
        if current_time - self.last_dialogue_end_time < 1000:  # 1초 간격으로 제한
            return

        if not self.show_dialogue:  # 상호작용이 처음 시작되면
            self.show_dialogue = True
            self.current_dialogue_index = 0  # 대화 시작 시 첫 번째 대사로 초기화
            self.dialogue_timer = current_time
        else:
            if current_time - self.dialogue_timer >= self.dialogue_interval:  # 대사 전환 간격을 짧게 설정
                self.current_dialogue_index += 1
                self.dialogue_timer = current_time  # 대사 전환 시간 갱신

                if self.current_dialogue_index >= len(self.dialogue):
                    self.show_dialogue = False  # 대화 종료 후 상호작용 종료
                    self.current_dialogue_index = 0  # 초기화
                    self.last_dialogue_end_time = current_time  # 대화 종료 시간 기록
                    self.dialogue_timer = 0  # 대사 타이머 초기화

    def draw(self, screen, camera):
        draw_x = self.x - camera.camera_x
        draw_y = self.y - camera.camera_y

        pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y, self.width, self.height))
        screen.blit(self.image, (draw_x, draw_y - 30))

        if self.show_dialogue:
            self.draw_dialogue_box(screen, camera)

    def draw_dialogue_box(self, screen, camera):
        if not self.show_dialogue:
            return

        box_width = 200
        box_height = 50
        box_x = self.x - camera.camera_x + 50
        box_y = self.y - camera.camera_y - 70

        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

        font = pygame.font.Font(None, 24)
        current_text = self.dialogue[self.current_dialogue_index]
        text_surface = font.render(current_text, True, (255, 255, 255))
        screen.blit(text_surface, (box_x + 10, box_y + 10))

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
