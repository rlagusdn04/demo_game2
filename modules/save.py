import json
from modules.npc import NPC

class SaveLoad:
    @staticmethod
    def save_game(player, map, npc_manager, file_path="game_save.json"):
        # 플레이어 상태와 NPC 정보를 JSON 형식으로 저장
        data = {
            "player": {
                "map": map.current_map_index,
                "x": player.x,
                "y": player.y,
                "level": getattr(player, "level", 1),
                "experience": getattr(player, "experience", 0),
                "health": getattr(player, "health", 100),
                "money": getattr(player, "money", 100),
                "inventory": getattr(player, "inventory", [])
            },
            "npcs": [
                {
                    "id": npc.id,
                    "name": npc.name,
                    "type": npc.type,
                    "map": npc.map_index,
                    "x": npc.x,
                    "y": npc.y,
                    "dialogue": npc.dialogue,  # 오타 수정
                }
                for npc in npc_manager.npcs
            ]
        }
        with open(file_path, "w", encoding="utf-8") as file: 
            json.dump(data, file, indent=4)
        print("게임과 NPC 정보가 저장되었습니다!")

    @staticmethod
    def load_game(player, map, npc_manager, file_path="game_save.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:  # UTF-8 인코딩 지정
                data = json.load(file)

            # 게임 상태 로드
            map.current_map_index = data["player"]["map"]
            player.x = data["player"]["x"]
            player.y = data["player"]["y"]
            player.level = data["player"].get("level", 1)
            player.experience = data["player"].get("experience", 0)
            player.health = data["player"].get("health", 100)
            player.money = data["player"].get("money", 100)
            player.inventory = data["player"].get("inventory", [])

            # NPC 로드
            npc_manager.npcs = []  # 기존 NPC 리스트 초기화
            for npc_data in data["npcs"]:
                # NPC 객체를 생성하고 리스트에 추가
                npc = NPC(
                    npc_data["id"], 
                    npc_data["name"], 
                    npc_data["type"], 
                    npc_data["map"], 
                    npc_data["x"], 
                    npc_data["y"],
                    npc_data.get("dialogue", ["..."])  # 올바른 키로 로드
                )
                npc_manager.add_npc(npc)  # NPC를 NPCManager에 추가

            print("게임과 NPC 정보가 로드되었습니다!")
        except FileNotFoundError:
            print("저장된 게임 파일이 없습니다.")
        except json.JSONDecodeError:
            print("저장 파일이 손상되었습니다.")
