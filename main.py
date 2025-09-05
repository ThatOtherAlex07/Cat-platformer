import pygame
import json

pygame.init()
width = 800
height = 800
clock = pygame.time.Clock()
fps = 60
block_size = 40
dead = False
has_jumped = True
next_level = 0
score = 0
font = pygame.font.SysFont('Arial', 40)
with open('levels/level1.json', 'r') as file:
    world_data = json.load(file)

level = 1
max_level = 4

def reset_level():
    player.rect.x = 100
    player.rect.y = height - 130
    death_group.empty()
    door_group.empty()
    with open(f"levels/level{level}.json", "r") as file:
        world_data = json.load(file)
    world = World(world_data)
    return world

def draw_text(text, color, x, y):
    img = font.render(text, True, color)
    display.blit(img, (x, y))

class Player:
    def __init__(self):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        for num in range(1, 4):
            img_right = pygame.image.load(f"sprites/walker{num}.png")
            img_right = pygame.transform.scale(img_right, (block_size, block_size))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.index]

        self.image = pygame.image.load("sprites/walker1.png")
        self.image = pygame.transform.scale(self.image, (block_size, block_size))
        self.rect = self.image.get_rect()
        self.rect.x = int(width / 2) - 45
        self.rect.y = -1 * height
        self.gravity = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.has_jumped = True

    def update(self):
        x = 0
        y = 0
        global dead
        global next_level
        global key
        walk_speed = 6
        key = pygame.key.get_pressed()

        if dead is False:
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                x -= 1
                self.direction = -1
                self.counter += 1
            elif key[pygame.K_RIGHT] or key[pygame.K_d]:
                x += 1
                self.direction = 1
                self.counter += 1
            if self.has_jumped is False:
                if key[pygame.K_SPACE] or key[pygame.K_UP] or key[pygame.K_w]:
                    self.gravity -= 2.5
                self.has_jumped = True

            if self.gravity > 0.6:
                self.gravity = 0.6

            self.gravity += 0.01

            y += self.gravity
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.has_jumped = False

            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1

            if self.index >= len(self.images_right):
                self.index = 0

            if self.direction == 1:
                self.image = self.images_left[self.index]
            else:
                self.image = self.images_right[self.index]

            self.rect.x += x
            self.rect.y += y
            self.direction = 0

            if pygame.sprite.spritecollide(self, death_group, False):
                sound_dead.play()
                dead = True
            if pygame.sprite.spritecollide(self, door_group, False):
                next_level = 1

        display.blit(self.image, self.rect)


class World:
    def __init__(self, data):
        dirt_img = pygame.image.load("sprites/dirt.png")
        grass_img = pygame.image.load("sprites/grass.png")

        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = {1: dirt_img, 2: grass_img}
                    img = pygame.transform.scale(images[tile], (block_size, block_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * block_size
                    img_rect.y = row_count * block_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    death = Death(col_count * block_size, row_count * block_size + (block_size // 2))
                    death_group.add(death)
                elif tile == 4:
                    door = Door(col_count * block_size, row_count * block_size)
                    door_group.add(door)
                elif tile == 5:
                    coin = Coin(col_count * block_size, row_count * block_size)
                    coin_group.add(coin)


                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            display.blit(tile[0], tile[1])




class Death(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('sprites/death.png')
        self.image = pygame.transform.scale(img, (block_size, block_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('sprites/door.jpg')
        self.image = pygame.transform.scale(img, (block_size, block_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('sprites/coin.jpg')
        self.image = pygame.transform.scale(img, (block_size, block_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Button:
    def __init__(self, x, y, image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x,y))

    def draw(self):
        action = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        display.blit(self.image, self.rect)
        return action


death_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
player = Player()

Restart_button = Button(width // 2, height // 2, "sprites/restart.png")
Start_button = Button(width // 2 - 150, height // 2, "sprites/start.png")
Exit_button     = Button(width // 2 + 150, height // 2, "sprites/exit.png")

world           = World(world_data)

display         = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game")

bg_image        = pygame.image.load("sprites/backdrop.jpg")
bg_rect         = bg_image.get_rect()

sound_coin      = pygame.mixer.Sound('music/Sfx1.wav')
sound_dead      = pygame.mixer.Sound('music/Sfx2.wav')
sound_bg        = pygame.mixer.Sound('music/BgM.wav')

key = pygame.key.get_pressed()


run = True
main_menu = True
restart = False
while run:
    display.blit(bg_image, bg_rect)
    if main_menu:
        if Start_button.draw():
            main_menu = False
            level = 1
            world = reset_level()
            sound_bg.play()
        if Exit_button.draw():
            run = False
    else:
        player.update()
        world.draw()
        death_group.draw(display)
        door_group.draw(display)
        coin_group.draw(display)
        draw_text(str(score), (255, 255, 255), 10, 10)
        player.update()
        death_group.update()

        if pygame.sprite.spritecollide(player, coin_group, True):
            sound_coin.play()
            score += 1
            print(score)

        if dead:
            key = pygame.key.get_pressed()
            if Restart_button.draw() or key[pygame.K_SPACE]:
                player = Player()
                #world = World(world_data)
                world = reset_level()
                dead = False
        if next_level == 1:
            next_level = 0
            if level < max_level:
                level += 1
                world = reset_level()
            elif level == max_level:
                main_menu = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()
