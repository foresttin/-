import pygame as pg
import random
import os 
from setting import *
from sprite import *
from os import path

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')

        # Check if the directory exists and print its contents for debugging
        print(f"Loading images from {img_dir}")
        if not path.exists(img_dir):
            print("Image directory does not exist.")
        else:
            print("Image directory exists.")
            print("Contents of the image directory:", os.listdir(img_dir))

        # Load player image
        player_img_path = path.join(img_dir, PLAYER_IMG)
        if path.exists(player_img_path):
            self.player_img = pg.image.load(player_img_path).convert_alpha()
        else:
            print(f"Player image not found at {player_img_path}")

        # Load platform images
        self.platform_imgs = []
        for img_file in PLATFORM_IMGS:
            img_path = path.join(img_dir, img_file)
            if path.exists(img_path):
                self.platform_imgs.append(pg.image.load(img_path).convert_alpha())
            else:
                print(f"Platform image not found at {img_path}")

    def new(self):
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        for plat in PLATFORM_LIST:
            p = Platform(*plat, self)
            self.all_sprites.add(p)
            self.platforms.add(p)

        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()

        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.rect.bottom < lowest.rect.centery + 10:  # Adjust the threshold value as needed
                    self.player.pos.y = lowest.rect.top + 0.1
                    self.player.vel.y = 0
                    self.player.jumping = False

        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
            self.playing = False
            self.show_end_message()  # Show game over screen if player falls

        if self.score >= 100:
            self.playing = False
            self.show_end_message(arrival=True)  # Show arrival message

        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            p = Platform(random.randrange(0, WIDTH - width),
                         random.randrange(-75, -30),
                         width, 20, self)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def show_end_message(self, arrival=False):
        self.screen.fill(BGCOLOR)
        if arrival:
        # Arrival 이미지를 화면에 표시합니다.
            arrival_img_path = path.join(path.dirname(__file__), 'img', 'clear.jpg')
            if path.exists(arrival_img_path):
                arrival_img = pg.image.load(arrival_img_path).convert_alpha()
                arrival_img = pg.transform.scale(arrival_img, (WIDTH, HEIGHT))  # 이미지 크기 조정
                self.screen.blit(arrival_img, (0, 0))
            else:
                print(f"Arrival image not found at {arrival_img_path}")

        else:
        # 게임 오버 이미지를 화면에 표시합니다.
            game_over_img_path = path.join(path.dirname(__file__), 'img', 'gameover.png')
            if path.exists(game_over_img_path):
                game_over_img = pg.image.load(game_over_img_path).convert_alpha()
            # 이미지 비율을 유지하면서 화면에 꽉 차게 표시하기 위해 먼저 이미지의 사이즈를 가져옵니다.
                img_rect = game_over_img.get_rect()
                img_ratio = img_rect.width / img_rect.height
            
            # 화면의 가로세로 비율에 맞게 이미지의 크기를 조정합니다.
                if img_ratio > WIDTH / HEIGHT:
                    game_over_img = pg.transform.scale(game_over_img, (int(HEIGHT * img_ratio), HEIGHT))
                else:
                    game_over_img = pg.transform.scale(game_over_img, (WIDTH, int(WIDTH / img_ratio)))
            
            # 이미지를 화면 가운데에 표시합니다.
                img_rect = game_over_img.get_rect(center=(WIDTH / 2, HEIGHT / 2))
                self.screen.blit(game_over_img, img_rect)
            else:
                print(f"Game over image not found at {game_over_img_path}")

        self.draw_text("Score : " + str(self.score), 28, PARANG, WIDTH * 3 / 4, HEIGHT - 60)  # 점수 텍스트 위치 조정 및 색상 변경
        self.draw_text("Press ENTER to play again", 22, PARANG, WIDTH * 3 / 4, HEIGHT - 30)
        pg.display.flip()
        self.wait_for_enter()
        self.new()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()

    
    def show_start_screen(self):
    # Step 1: Display background color and text
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
    
    # Wait for key press
        self.wait_for_key()
    
    # List of image file names to display sequentially
        img_files = ['start.png', 'start_second.png', 'third.png']
    
        for img_file in img_files:
            img_path = path.join(path.dirname(__file__), 'img', img_file)
            if path.exists(img_path):
                img = pg.image.load(img_path).convert_alpha()
                img_rect = img.get_rect()
                img_rect.center = (WIDTH / 2, HEIGHT / 2)
                self.screen.fill(BGCOLOR)  # Clear the screen
                self.screen.blit(img, img_rect)
                # '엔터키를 누르세요' 텍스트를 화면 하단 오른쪽에 정렬하여 표시합니다.
                self.draw_text("Press ENTER to continue", 28, WHITE, WIDTH * 3 / 4, HEIGHT * 15 / 16)
                pg.display.flip()
                self.wait_for_enter()
            else:
                print(f"Image not found at {img_path}")

    def wait_for_enter(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    waiting = False


    def wait_for_enter(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        waiting = False

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:
    g.new()

pg.quit()
