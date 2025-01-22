import pygame

class NPC:
    def __init__(self, id, name, type, map_index, x, y):
        self.id = id
        self.name = name
        self.type = type
        self.map_index = map_index
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32  # 높이 추가 (사각형 형태로 그릴 경우 필요)

    def draw(self, screen, camera):
        draw_x = self.x - camera.camera_x
        draw_y = self.y - camera.camera_y

        pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y, self.width, self.height))

    def update(self):
        pass


class NPCManager:
    def __init__(self):
        self.npcs = []
        self.updated_npcs = []  # 업데이트된 NPC들을 따로 저장

    def add_npc(self, npc):
        self.npcs.append(npc)

    def update(self, game_map):
        current_map = game_map.get_current_map()["map_index"]  # 현재 맵을 가져옵니다
        self.updated_npcs.clear() 

        for npc in self.npcs:
            # NPC의 map_index와 현재 맵을 비교하여 일치할 때만 업데이트
            if npc.map_index == current_map:
                npc.update()  # NPC 업데이트
                self.updated_npcs.append(npc)  # 업데이트된 NPC를 저장

    def draw(self, screen, camera):
        for npc in self.updated_npcs:  # 업데이트된 NPC만 그려짐
            npc.draw(screen, camera)  # 각 NPC의 draw 메서드를 호출
