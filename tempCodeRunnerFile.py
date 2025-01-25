        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            camera.toggle_inventory(event)  # 인벤토리 토글
            player.interact_with_npcs(event, npc_manager,camera)