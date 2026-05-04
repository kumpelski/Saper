from graphics import GraphicsHandler
from debug import DebugHandler
from game import GameHandler


def main_loop():

    def handle_music(lvl):
        value = lvl * 0.1
        gh.pygame.mixer.music.set_volume(value)

    def handle_sfx(lvl):
        value = 0 if lvl == 0 else (lvl - 1) * 0.02 + 0.01
        gh.lmb_sfx.set_volume(value)
        gh.rmb_sfx.set_volume(value)
        gh.you_win_sfx.set_volume(value)
        gh.game_over_sfx.set_volume(value)

    running = True
    lmb = False
    rmb = False

    while running:

        dh.debug_fps()

        for event in gh.pygame.event.get():
            if event.type == gh.pygame.QUIT:
                running = False
            if event.type == gh.pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    lmb = True
                    gh.lmb_sfx.play()
                if event.button == 3:
                    rmb = True
                    gh.rmb_sfx.play()
        mx, my = gh.get_mouse()
        if lmb:
            match gh.state:
                case 0:
                    if my == 10 and 14 <= mx <= 14 + len('(play)') - 1:
                        gh.state = 1
                    if my == 12 and 14 <= mx <= 14 + len('(options)') - 1:
                        gh.state = 3
                    if my == 14 and 14 <= mx <= 14 + len('(quit)') - 1:
                        running = False
                case 1:
                    if my == 10 and 7 <= mx <= 7 + len('(←)') - 1:
                        gh.state = 0
                    if my == 10 and 14 <= mx <= 14 + len('(easy)') - 1:
                        gh.start(9, 9, 10)
                    if my == 12 and 14 <= mx <= 14 + len('(medium)') - 1:
                        gh.start(16, 16, 40)
                    if my == 14 and 14 <= mx <= 14 + len('(hard)') - 1:
                        gh.start(30, 16, 99)
                    if my == 16 and 14 <= mx <= 14 + len('(custom)') - 1:
                        gh.state = 2
                case 2:
                    if 7 <= mx <= 7 + len('(←)') - 1 and my == 10:
                        gh.state = 1
                    if 18 <= mx <= 18 + len('(-)') - 1 and my == 10:
                        game.w = max(9, game.w - 1)
                        game.b = game.w * game.h // 5
                    if 25 <= mx <= 25 + len('(+)') - 1 and my == 10:
                        game.w = min(30, game.w + 1)
                        game.b = game.w * game.h // 5
                    if 18 <= mx <= 18 + len('(-)') - 1 and my == 12:
                        game.h = max(9, game.h - 1)
                        game.b = game.w * game.h // 5
                    if 25 <= mx <= 25 + len('(+)') - 1 and my == 12:
                        game.h = min(16, game.h + 1)
                        game.b = game.w * game.h // 5
                    if 18 <= mx <= 18 + len('(-)') - 1 and my == 14:
                        game.b = max(10, game.b - 1)
                    if 25 <= mx <= 25 + len('(+)') - 1 and my == 14:
                        game.b = min(99, game.b + 1)
                    if 11 <= mx <= 11 + len('(play custom)') - 1 and my == 16:
                        gh.start_custom()
                case 3:
                    if 7 <= mx <= 7 + len('(←)') - 1 and my == 10:
                        gh.state = 0
                    if 18 <= mx <= 18 + len('(-)') - 1 and my == 10:
                        gh.music_lvl = max(0, gh.music_lvl - 1)
                        handle_music(gh.music_lvl)
                    if 25 <= mx <= 25 + len('(+)') - 1 and my == 10:
                        gh.music_lvl = min(10, gh.music_lvl + 1)
                        handle_music(gh.music_lvl)
                    if 18 <= mx <= 18 + len('(-)') - 1 and my == 12:
                        gh.sfx_lvl = max(0, gh.sfx_lvl - 1)
                        handle_sfx(gh.sfx_lvl)
                    if 25 <= mx <= 25 + len('(+)') - 1 and my == 12:
                        gh.sfx_lvl = min(10, gh.sfx_lvl + 1)
                        handle_sfx(gh.sfx_lvl)
                    if gh.mouse_trail:
                        if 23 <= mx <= 23 + len('(off)') - 1 and my == 14:
                            gh.mouse_trail = False
                    else:
                        if 24 <= mx <= 24 + len('(on)') - 1 and my == 14:
                            gh.mouse_trail = True
                case 4:
                    game.handle_lmb(mx, my, gh)
                    if 17 <= mx <= 17 + len('☻') - 1 and my == 1:
                        gh.start(game.w, game.h, game.b)
                    if 12 <= mx <= 12 + len('(main menu)') - 1 and my == 18:
                        gh.state = 0
            lmb = False

        if rmb and gh.state == 4:
            game.handle_rmb(mx, my, gh)
            rmb = False

        gh.draw_frame()

    gh.pygame.quit()


gh = None
dh = None
game = None

if __name__ == "__main__":
    game = GameHandler()
    gh = GraphicsHandler(game)

    dh = DebugHandler(gh)
    dh.debug_lag(gh.draw_frame)

    main_loop()
