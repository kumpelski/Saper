import random
import numpy as np  # 1.26.4

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import compileProgram, compileShader


class GraphicsHandler:

    def __init__(self, game):
        self.game = game

        # pygame
        self.pygame = None
        self.config_pygame()

        # options
        self.music_lvl = 10
        self.sfx_lvl = 1
        self.mouse_trail = True

        # sounds
        self.lmb_sfx = None
        self.rmb_sfx = None
        self.you_win_sfx = None
        self.game_over_sfx = None
        self.played_already = False
        self.config_sounds()

        # font
        self.font = None
        self.char_width = None
        self.char_height = None
        self.config_font()

        # resolution
        self.grid_width = None
        self.grid_height = None
        self.window_width = None
        self.window_height = None
        self.config_resolution()

        # gl essentials
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.window_width, 0, self.window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # textures
        self.textures = None
        self.config_textures()

        # shaders
        self.curvature = 0.15
        self.shader_program = None
        self.fbo = None
        self.screen_texture = None
        self.config_shaders()

        # drawn chars log
        self.current = [['wk ' for _ in range(self.grid_height)] for _ in range(self.grid_width)]

        # background
        self.bg_bombs = []
        self.bg_interval_ms = 2000
        self.bg_last_execution_time = - self.bg_interval_ms
        self.shadow = self.generate_circular_gradient(1, 0.5)

        # gui
        self.state = 0
        self.trail = []

        # end screen
        self.you_win = [
            '▄' * self.grid_width + '█▄▄▄█▄████▄█▄▄█▄▄▄▄▄▄█▄█▄█▄███▄█▄▄▄█',
            '▄' * self.grid_width + '▄█▄█▄▄█▄▄█▄█▄▄█▄▄▄▄▄▄█▄█▄█▄▄█▄▄██▄▄█',
            '▄' * self.grid_width + '▄▄█▄▄▄█▄▄█▄█▄▄█▄▄▄▄▄▄█▄█▄█▄▄█▄▄█▄█▄█',
            '▄' * self.grid_width + '▄▄█▄▄▄█▄▄█▄█▄▄█▄▄▄▄▄▄█▄█▄█▄▄█▄▄█▄▄██',
            '▄' * self.grid_width + '▄▄█▄▄▄████▄████▄▄▄▄▄▄█████▄███▄█▄▄▄█'
        ]
        self.game_over = [
            '▄' * self.grid_width + '████▄████▄█████▄████▄▄▄▄▄▄████▄█▄▄▄█▄████▄████',
            '▄' * self.grid_width + '█▄▄▄▄█▄▄█▄█▄█▄█▄█▄▄▄▄▄▄▄▄▄█▄▄█▄█▄▄▄█▄█▄▄▄▄█▄▄█',
            '▄' * self.grid_width + '█▄██▄████▄█▄█▄█▄████▄▄▄▄▄▄█▄▄█▄▄█▄█▄▄████▄███▀',
            '▄' * self.grid_width + '█▄▄█▄█▄▄█▄█▄█▄█▄█▄▄▄▄▄▄▄▄▄█▄▄█▄▄█▄█▄▄█▄▄▄▄█▄▄█',
            '▄' * self.grid_width + '████▄█▄▄█▄█▄█▄█▄████▄▄▄▄▄▄████▄▄▄█▄▄▄████▄█▄▄█'
        ]
        self.es_t = 0
        self.es_interval_ms = 30
        self.es_last_execution_time = - self.es_interval_ms

        # play music
        self.pygame.mixer.music.play(loops=-1)

    def config_pygame(self):
        self.pygame = pygame
        self.pygame.init()
        self.pygame.mixer.init()
        self.pygame.mouse.set_visible(False)

    def config_sounds(self):
        self.pygame.mixer.music.load("sounds/menu.wav")
        self.lmb_sfx = self.pygame.mixer.Sound("sounds/button.mp3")
        self.lmb_sfx.set_volume(0.01)
        self.rmb_sfx = self.pygame.mixer.Sound("sounds/button2.mp3")
        self.rmb_sfx.set_volume(0.01)
        self.you_win_sfx = self.pygame.mixer.Sound("sounds/you_win.mp3")
        self.you_win_sfx.set_volume(0.01)
        self.game_over_sfx = self.pygame.mixer.Sound("sounds/game_over.mp3")
        self.game_over_sfx.set_volume(0.01)

    def config_font(self):
        font_name = 'Consolas'
        font_size = 40
        self.font = pygame.font.SysFont(font_name, font_size)
        w_surface = self.font.render('W', True, (255, 255, 255))
        self.char_width, self.char_height = w_surface.get_size()

    def config_resolution(self):
        self.grid_width, self.grid_height = 36, 20
        self.window_width = self.grid_width * self.char_width
        self.window_height = self.grid_height * self.char_height
        self.pygame.display.set_mode(
            (self.window_width, self.window_height),
            self.pygame.OPENGL | self.pygame.DOUBLEBUF
        )

    def config_textures(self):
        self.textures = {}
        supported_chars = (
            'abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '0123456789'
            ' .,!?\'\"/\\_+-|()[]$'
            '…°♠♥♣♦'
            '┌┐└┘─│┬┤┴├┼╔╗╚╝═║■░▒▓'
            '¤<>«←¶×•○◦☻☺☹'
        )
        extra = 1.5
        supported_colors = {
            'r': (255, 0, 0),  # red
            'g': (0, 255, 0),  # green
            'b': (0, 0, 255),  # blue
            'c': (0, 255, 255),  # cyan
            'y': (255, 255, 0),  # yellow
            'm': (128 * extra, 0, 128 * extra),  # magenta
            'w': (255, 255, 255),  # white
            '2': (0, 128 * extra, 0),
            '4': (0, 0, 128 * extra),
            '5': (128 * extra, 0, 0),
            '6': (0, 128 * extra, 128 * extra),
            '7': (64 * extra, 64 * extra, 64 * extra),
            '8': (128 * extra, 128 * extra, 128 * extra)
        }
        bg_color_key, bg_color = 'k', (0, 0, 0)
        custom_chars = '▄█▀'
        for color_key, color in supported_colors.items():
            for char in supported_chars:
                self.render_opengl_texture(color_key, color, bg_color_key, bg_color, char)
                self.render_opengl_texture(bg_color_key, bg_color, color_key, color, char)
            for char in custom_chars:
                self.render_opengl_texture(color_key, color, bg_color_key, bg_color, char, custom=True)
                self.render_opengl_texture(bg_color_key, bg_color, color_key, color, char, custom=True)

    def render_opengl_texture(self, color_key, color, bg_color_key, bg_color, char, custom=False):

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        surface = self.font.render(char, True, color, bg_color)

        if custom:
            array = self.pygame.surfarray.array3d(surface)
            middle_column_index = array.shape[0] // 2
            middle_column = array[middle_column_index, :, :]
            array[:, :, :] = np.tile(middle_column, (array.shape[0], 1, 1))
            surface = self.pygame.surfarray.make_surface(array)

        texture_bytes = self.pygame.image.tostring(surface, "RGBA", True)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.char_width, self.char_height, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                     texture_bytes)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        key = f'{color_key}{bg_color_key}{char}'
        self.textures[key] = texture_id

    def config_shaders(self):
        vertex_shader_code = """
        #version 330 core
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec2 texCoords;

        out vec2 TexCoords;

        void main()
        {
            gl_Position = vec4(position.xy, 0.0, 1.0);
            TexCoords = texCoords;
        }
        """

        fragment_shader_code = """
        #version 330 core

        in vec2 TexCoords;
        out vec4 FragColor;

        uniform sampler2D screenTexture;

        uniform float bloomStrength; // Jasność efektu bloom
        uniform int kernelSize; // Rozmiar kernela dla bloom

        const float curvature = 0.15; // Curvature strength
        const float scanlineIntensity = 0.3; // Intensity of scanlines

        vec2 barrelDistortion(vec2 coord) {
            coord = coord * 2.0 - 1.0; // Move to range [-1, 1]
            float r = dot(coord, coord);
            coord *= mix(1.0, 1.0 - curvature, r * 0.5); // Apply curvature
            return (coord + 1.0) * 0.5; // Move back to range [0, 1]
        }

        float scanlineEffect(vec2 coord) {
            return 1.0 - scanlineIntensity * sin(coord.y * 800.0); // Simulate scanlines based on y-coordinate
        }

        // Funkcja do rozmycia
        vec3 blur(vec2 texCoords) {
            vec3 result = vec3(0.0);
            float totalWeight = 1;

            // Kernel rozmycia
            for (int x = -kernelSize; x <= kernelSize; ++x) {
                for (int y = -kernelSize; y <= kernelSize; ++y) {
                    vec2 offset = vec2(float(x), float(y)) / 300.0; // Skala rozmycia
                    vec3 color = texture(screenTexture, texCoords + offset).rgb;
                    float weight = 1.0 - length(offset); // Waga na podstawie odległości
                    result += color * weight;
                    totalWeight += weight;
                }
            }

            return result / totalWeight; // Normalizacja
        }

        void main() {
            // Apply barrel distortion to texture coordinates
            vec2 distortedCoords = barrelDistortion(TexCoords);

            // If the distorted coordinates are outside of the texture bounds, return black
            if (distortedCoords.x < 0.0 || distortedCoords.x > 1.0 || distortedCoords.y < 0.0 || distortedCoords.y > 1.0) {
                FragColor = vec4(0.0, 0.0, 0.0, 1.0);
                return;
            }

            // Apply scanline effect
            vec3 color = texture(screenTexture, distortedCoords).rgb;
            color *= scanlineEffect(TexCoords);

            FragColor = vec4(color, 1.0);
        }
        """

        self.shader_program = compileProgram(
            compileShader(vertex_shader_code, GL_VERTEX_SHADER),
            compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
        )

        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        self.screen_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.screen_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.window_width, self.window_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.screen_texture, 0)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Framebuffer is not complete!")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def draw_char(self, at_x, at_y, key, alpha=1.0, record=True):

        if record:
            self.current[at_x][at_y] = key

        glBindTexture(GL_TEXTURE_2D, self.textures[key])
        glColor4f(1.0, 1.0, 1.0, alpha)

        x_pos = at_x * self.char_width
        y_pos = self.window_height - (at_y + 1) * self.char_height

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(x_pos, y_pos)
        glTexCoord2f(1, 0)
        glVertex2f(x_pos + self.char_width, y_pos)
        glTexCoord2f(1, 1)
        glVertex2f(x_pos + self.char_width, y_pos + self.char_height)
        glTexCoord2f(0, 1)
        glVertex2f(x_pos, y_pos + self.char_height)
        glEnd()

    def draw_string(self, at_x, at_y, color, string, alpha=1.0):
        char_x = at_x
        char_y = at_y
        for char in string:
            if char == '\n':
                char_x = at_x
                char_y += 1
            else:
                self.draw_char(char_x, char_y, f'{color}{char}', alpha)
                char_x += 1

    @staticmethod
    def generate_circular_gradient(arg0, arg1, rows=16, cols=30):
        x, y = np.ogrid[:rows, :cols]
        center_x, center_y = rows / 2, cols / 2
        distance_from_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
        normalized_distance = distance_from_center / max_distance
        gradient = arg1 - (arg1 - arg0) * normalized_distance
        return np.transpose(gradient ** 2 + 0.1)

    def draw_background(self, anchor_x=3, anchor_y=2, bg_w=30, bg_h=16, bg_b=99):

        current_time = self.pygame.time.get_ticks()

        if current_time - self.bg_last_execution_time >= self.bg_interval_ms:
            self.bg_last_execution_time = current_time
            self.bg_bombs = [[0 for _ in range(bg_h)] for _ in range(bg_w)]
            positions = random.sample(range(bg_w * bg_h), bg_b)
            for pos in positions:
                bomb_or_flag = 1 if random.randint(0, 1) == 0 else 2
                self.bg_bombs[pos % bg_w][pos // bg_w] = bomb_or_flag

        options = ['7k◦', 'bk1', '2k2', 'rk3', '4k4', '5k5', '6k6', '7k7', '8k8', 'wk░']

        for x in range(bg_w):
            for y in range(bg_h):
                bg_x, bg_y = anchor_x + x, anchor_y + y
                if self.bg_bombs[x][y] > 0:
                    key = '7k×' if self.bg_bombs[x][y] == 1 else 'mk¶'
                else:
                    bg_fv = self.game.count_around(x, y, self.bg_bombs)
                    key = options[bg_fv]
                self.draw_char(bg_x, bg_y, key, alpha=self.shadow[x][y])

    def get_mouse(self):
        wmx, wmy = self.pygame.mouse.get_pos()
        mx = (wmx / self.window_width) * 2.0 - 1.0
        my = (wmy / self.window_height) * 2.0 - 1.0

        r = mx * mx + my * my
        f = 1.0 - self.curvature * (r * 0.5)

        mx = (mx * f + 1.0) * 0.5 * self.window_width
        my = (my * f + 1.0) * 0.5 * self.window_height

        mx = int(mx // self.char_width)
        my = int(my // self.char_height)

        return mx, my

    def draw_gui(self, ax=8, ay=3):

        def draw_title():

            lines = (
                '███ ███ ███ ███ ███',
                '█   █ █ █ █ █   █ █',
                '███ ███ ███ ███ ██▀',
                '  █ █ █ █   █   █ █',
                '███ █ █ █   ███ █ █'
            )

            for y, line in enumerate(lines):
                for x, sign in enumerate(line):
                    if sign == ' ':
                        continue
                    self.draw_char(ax + x, ay + y, f'wk{sign}')
            self.draw_string(ax + 12, ay + 5, 'wk', 'by iski')

        def handle_button(bx, by, string):
            mx, my = self.get_mouse()
            on_button = bx <= mx <= bx + len(string) - 1 and my == by
            self.draw_string(bx, by, 'kw' if on_button else 'wk', string)

        def draw_welcome():
            handle_button(ax + 6, ay + 7, '(play)')
            handle_button(ax + 6, ay + 9, '(options)')
            handle_button(ax + 6, ay + 11, '(quit)')

        def draw_difficulty():
            handle_button(ax - 1, ay + 7, '(←)')
            handle_button(ax + 6, ay + 7, '(easy)')
            handle_button(ax + 6, ay + 9, '(medium)')
            handle_button(ax + 6, ay + 11, '(hard)')
            handle_button(ax + 6, ay + 13, '(custom)')

        def draw_custom():
            handle_button(ax - 1, ay + 7, '(←)')
            self.draw_string(ax + 3, ay + 7, 'wk', 'width')
            handle_button(ax + 10, ay + 7, '(-)')
            self.draw_string(ax + 14, ay + 7, 'wk', f'{self.game.w:02}')
            handle_button(ax + 17, ay + 7, '(+)')
            self.draw_string(ax + 3, ay + 9, 'wk', 'height')
            handle_button(ax + 10, ay + 9, '(-)')
            self.draw_string(ax + 14, ay + 9, 'wk', f'{self.game.h:02}')
            handle_button(ax + 17, ay + 9, '(+)')
            self.draw_string(ax + 3, ay + 11, 'wk', 'bombs')
            handle_button(ax + 10, ay + 11, '(-)')
            self.draw_string(ax + 14, ay + 11, 'wk', f'{self.game.b:02}')
            handle_button(ax + 17, ay + 11, '(+)')
            handle_button(ax + 3, ay + 13, '(play custom)')

        def draw_options():
            handle_button(ax - 1, ay + 7, '(←)')
            self.draw_string(ax + 3, ay + 7, 'wk', 'music')
            handle_button(ax + 10, ay + 7, '(-)')
            self.draw_string(ax + 14, ay + 7, 'wk', f'{self.music_lvl:02}')
            handle_button(ax + 17, ay + 7, '(+)')
            self.draw_string(ax + 3, ay + 9, 'wk', 'sfx')
            handle_button(ax + 10, ay + 9, '(-)')
            self.draw_string(ax + 14, ay + 9, 'wk', f'{self.sfx_lvl:02}')
            handle_button(ax + 17, ay + 9, '(+)')
            self.draw_string(ax + 3, ay + 11, 'wk', 'mouse trail')
            if self.mouse_trail:
                handle_button(ax + 15, ay + 11, '(off)')
            else:
                handle_button(ax + 16, ay + 11, '(on)')

        if self.state < 4:
            self.draw_background()
            draw_title()

        match self.state:
            case 0:
                draw_welcome()
            case 1:
                draw_difficulty()
            case 2:
                draw_custom()
            case 3:
                draw_options()
            case 4:  # game gui
                self.draw_string(8, 1, 'wk', 'BOMBS')
                self.draw_string(7 + len('BOMBS') + 1, 1, 'rk', f'{self.game.b - sum(sum(row) for row in self.game.is_flag)}')
                self.draw_char(17, 1, 'yk☺' if self.game.lost else 'yk☻')
                self.draw_string(20, 1, 'wk', 'TIME')
                self.draw_string(20 + len('TIME'), 1, 'rk', f'{min(int(self.game.get_time()), 999):03}')
                handle_button(12, 18, '(main menu)')

    def reset_current(self):
        self.current = [['wk ' for _ in range(22)] for _ in range(36)]

    def start(self, w, h, b):
        self.reset_current()
        self.game.start(w, h, b)
        self.state = 4

    def start_custom(self):
        self.reset_current()
        self.game.start_custom()
        self.state = 4

    def draw_end_screen(self, anchor_y=7, lost=False):

        text = self.game_over if lost else self.you_win
        color = 'r' if lost else 'g'

        current_time = self.pygame.time.get_ticks()
        if current_time - self.es_last_execution_time >= self.es_interval_ms:
            self.es_last_execution_time = current_time
            self.es_t = (self.es_t + 1) % len(text[0])

        for y, line in enumerate(text):
            to_display = line[self.es_t:self.grid_width + self.es_t]
            for x, sign in enumerate(to_display):
                if not sign == '▄':
                    self.draw_char(x, anchor_y + y, f'{color}k{sign}')

    def draw_game(self):

        char_keys = ['7k◦', 'bk1', '2k2', 'rk3', '4k4', '5k5', '6k6', '7k7', '8k8', '7k×']
        ax = (self.grid_width - self.game.w) // 2
        ay = (self.grid_height - self.game.h) // 2
        sx = (30 - self.game.w) // 2
        sy = (16 - self.game.h) // 2

        if not self.game.lost and not self.game.won:
            self.played_already = False
            self.es_t = 0
            for x in range(self.game.w):
                for y in range(self.game.h):
                    if self.game.is_flag[x][y]:
                        self.draw_char(ax + x, ay + y, 'mk¶')
                        continue
                    if not self.game.is_checked[x][y]:
                        self.draw_char(ax + x, ay + y, '8k•')
                        continue
                    ck = char_keys[self.game.field_value[x][y]]
                    self.draw_char(ax + x, ay + y, ck)

        if self.game.won or self.game.lost:
            for x in range(self.game.w):
                for y in range(self.game.h):
                    ck = None
                    if self.game.is_flag[x][y] and self.game.is_bomb[x][y]:
                        ck = 'gk¶'
                    if self.game.is_flag[x][y] and not self.game.is_bomb[x][y]:
                        ck = 'rk¶'
                    if not self.game.is_flag[x][y] and self.game.is_bomb[x][y]:
                        ck = 'rk×' if self.game.lost else 'gkx'
                    if not self.game.is_flag[x][y] and not self.game.is_bomb[x][y]:
                        ck = ('8' if self.game.is_checked[x][y] else '7') + char_keys[self.game.field_value[x][y]][1:]
                    self.draw_char(ax + x, ay + y, ck, alpha=self.shadow[sx + x][sy + y])
            self.draw_end_screen(lost=self.game.lost)
            if not self.played_already:
                self.played_already = True
                if self.game.lost:
                    self.game_over_sfx.play()
                else:
                    self.you_win_sfx.play()

    def draw_mouse(self):
        t_len = 30 if self.mouse_trail else 0
        mx, my = self.get_mouse()
        self.trail.append([mx, my])

        while len(self.trail) > t_len:
            self.trail.pop(0)

        for i, pos in enumerate(self.trail):
            if self.current[pos[0]][pos[1]][2] == '█':
                self.draw_char(pos[0], pos[1], 'yk█', alpha=(i + 1) / len(self.trail) / 2, record=False)
            else:
                self.draw_char(pos[0], pos[1], f'ky{self.current[pos[0]][pos[1]][2]}',
                               alpha=(i + 1) / len(self.trail) / 2,
                               record=False)

        if self.trail:
            if self.current[pos[0]][pos[1]][2] == '█':
                self.draw_char(pos[0], pos[1], 'yk█', alpha=1.0, record=False)
            else:
                self.draw_char(pos[0], pos[1], f'ky{self.current[pos[0]][pos[1]][2]}', alpha=1.0, record=False)
        else:
            if self.current[mx][my][2] == '█':
                self.draw_char(mx, my, 'yk█', alpha=1.0, record=False)
            else:
                self.draw_char(mx, my, f'ky{self.current[mx][my][2]}', alpha=1.0, record=False)

    def draw_frame(self):
        glClear(GL_COLOR_BUFFER_BIT)

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D)

        self.draw_gui(8, 3)
        if self.state == 4:
            self.draw_game()
        self.draw_mouse()

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        glUseProgram(self.shader_program)
        glBindTexture(GL_TEXTURE_2D, self.screen_texture)
        glUniform1i(glGetUniformLocation(self.shader_program, "screenTexture"), 0)
        vertices = [
            -1.0, 1.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ]
        indices = [0, 1, 2, 0, 2, 3]
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(ctypes.c_float * len(vertices)),
                     (ctypes.c_float * len(vertices))(*vertices), GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(ctypes.c_uint * len(indices)),
                     (ctypes.c_uint * len(indices))(*indices), GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * ctypes.sizeof(ctypes.c_float),
                              ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))
        glEnableVertexAttribArray(1)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glUseProgram(0)
        glBindVertexArray(0)
        glDeleteVertexArrays(1, [vao])
        glDeleteBuffers(1, [vbo])
        glDeleteBuffers(1, [ebo])

        glDisable(GL_TEXTURE_2D)
        self.pygame.display.flip()
