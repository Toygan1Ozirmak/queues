import random
import sys
import time
from threading import Thread, Lock, current_thread
import pygame


class Chair(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        super().__init__()
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 4, self.image.get_height() * 4))
        self.rect = self.image.get_rect(center=location)


class BackgroundFurniture(pygame.sprite.Sprite):
    def __init__(self, image_file, location, scale_factor=1.0, horizontal_flip=False, vertical_flip=False):
        super().__init__()
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.flip(self.image, horizontal_flip, vertical_flip)
        self.image = pygame.transform.scale(
            self.image,
            (
                int(self.image.get_width() * scale_factor),
                int(self.image.get_height() * scale_factor)
            )
        )
        self.rect = self.image.get_rect(center=location)


class Meal(pygame.sprite.Sprite):
    def __init__(self, location, amount):
        super().__init__()
        self.amount = amount
        self.image = pygame.image.load("assets/spaghetti_full.png") if self.amount > 0 else pygame.image.load(
            "assets/spaghetti_empty.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 1, self.image.get_height() * 1))
        self.rect = self.image.get_rect(center=location)

    def eat(self):
        self.image = pygame.image.load("assets/spaghetti_full.png") if self.amount > 0 else pygame.image.load(
            "assets/spaghetti_empty.png")


class Character(pygame.sprite.Sprite):
    def __init__(self, character_id, state_id, location, i):
        super().__init__()
        self.index = i
        self.char_id = character_id
        self.image = pygame.image.load("assets/characters.png")
        self.rect = self.image.get_rect(center=location)
        self.image = self.image.subsurface(pygame.Rect(abs(state_id) * 16, character_id * 16, 16, 16))
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 4, self.image.get_height() * 4))
        # pygame.draw.rect(self.image, (255, 0, 0), self.image.get_rect(), 2)
        if state_id < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.direction = "right"
        self.moving = False
        self.speed = 5
        self.status = '  T  '
        self.hold = '     '


class Chopstick(pygame.sprite.Sprite):
    def __init__(self, angle, location, i):
        super().__init__()
        self.index = i
        self.location = location
        self.angle = angle
        self.image = pygame.image.load("assets/chopstick.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 0.3, self.image.get_height() * 0.3))
        self.image = pygame.transform.rotate(self.image, angle)
        self.copy_image = self.image
        self.rect = self.image.get_rect(center=location)
        self.rect_copy = self.rect
        self.lock = Lock()
        # pygame.draw.rect(self.image, (255, 0, 0), self.image.get_rect(), 2)  # draw border

    def update_rect(self, rect, angle):
        chopstick_obj = Chopstick(angle, self.location, self.index)
        if rect != self.rect_copy:
            # print("not mine")
            self.image = chopstick_obj.image
            self.rect = chopstick_obj.image.get_rect(topleft=rect.topleft)
        else:
            # print("mine")
            self.image = self.copy_image
            self.rect = self.image.get_rect(topleft=rect.topleft)
        time.sleep(1)


class Game_Parallel(pygame.sprite.Sprite):
    def __init__(self, chopstick_group, character_group, meal_group, number_of_philosophers):
        self.chopstick_sprites = chopstick_group
        self.character_sprites = character_group
        self.meal_sprites = meal_group
        self.character_list = list(character_group)
        self.chopstick_list = list(chopstick_group)
        self.meal_list = list(meal_group)
        self.meals = [meal for meal in self.meal_list]
        self.meals_sum = [meal.amount for meal in self.meal_list]
        self.chopsticks = [chopstick_lock.lock for chopstick_lock in self.chopstick_list]
        self.status = [character_status.status for character_status in self.character_list]
        self.chopstick_holders = ['     ' for _ in range(number_of_philosophers)]
        self.number_of_philosophers = number_of_philosophers
        # noinspection DuplicatedCode

    def get_meals_sum(self):
        self.meals_sum = [meal.amount for meal in self.meal_list]
        return self.meals_sum

    def draw(self, chopstick, player, chopstick2):
        if self.chopstick_holders[player.index] == ' /   ':
            # print(
            #     "=" * 25,
            #     f"Thread:{threading.current_thread()} , chopstick 1 : {chopstick.index} , player:{player.index} "
            #     f", status:{self.status[player.index]}, hold:{self.chopstick_holders[player.index]}")
            self.print_loop()
            chopstick.update_rect(player.rect, 15)
        elif self.chopstick_holders[player.index] == '     ':
            # print("=" * 25,
            #       f"Thread:{threading.current_thread()} , chopstick 1 : {chopstick.index} , player:{player.index}"
            #       f", status:{self.status[player.index]}, hold:{self.chopstick_holders[player.index]} ")
            self.print_loop()
            chopstick.update_rect(chopstick.rect_copy, 0)
            if self.status[player.index] == '  E  ':
                chopstick2.update_rect(chopstick2.rect_copy, 0)
        elif self.chopstick_holders[player.index] == ' / \\ ':
            # print("=" * 25,
            #       f"Thread:{threading.current_thread()} , chopstick 1 : {chopstick.index} , player:{player.index} , "
            #       f"chopstick 2:{chopstick2.index}"
            #       f", status:{self.status[player.index]},hold:{self.chopstick_holders[player.index]}")
            self.print_loop()
            chopstick.update_rect(player.rect, 15)
            chopstick2.update_rect(player.rect, 75)

        else:
            print("drawn nothing")

    def print_loop(self):
        print("=" * (self.number_of_philosophers * 5))
        print("".join(map(str, self.status)), " : ",
              str(self.status.count('  E  ')))
        print("".join(map(str, self.chopstick_holders)))
        print("".join("{:3d}  ".format(m.amount) for m in self.meals), " : ",
              str(sum(self.get_meals_sum())))

    def philosopher_queue(self, index):
        i = index
        j = (i + 1) % self.number_of_philosophers
        while sum(dining_philosophers.get_meals_sum()) > 0:
            keys = pygame.key.get_pressed()
            if self.meals[i].amount > 0 and keys[pygame.K_RIGHT]:
                self.status[i] = '  T  '
                time.sleep(random.random())
                self.status[i] = '  _  '
                if not self.chopsticks[i].locked():
                    self.chopsticks[i].acquire()
                    self.chopstick_holders[i] = ' /   '
                    self.draw(self.chopstick_list[i], self.character_list[i], self.chopstick_list[j])
                    time.sleep(random.random())
                    if not self.chopsticks[j].locked():
                        self.chopsticks[j].acquire()
                        self.chopstick_holders[i] = ' / \\ '
                        self.status[i] = '  E  '
                        self.draw(self.chopstick_list[i], self.character_list[i], self.chopstick_list[j])
                        time.sleep(random.random())
                        self.meals[i].amount -= 1
                        self.meals[i].eat()
                        self.chopsticks[j].release()
                        self.chopstick_holders[i] = '     '
                        self.draw(self.chopstick_list[i], self.character_list[i], self.chopstick_list[j])
                        self.chopsticks[i].release()
                        self.chopstick_holders[i] = '     '
                        self.status[i] = '  T  '
                    else:
                        self.chopstick_holders[i] = '     '
                        self.draw(self.chopstick_list[i], self.character_list[i], self.chopstick_list[j])
                        self.chopsticks[i].release()
                time.sleep(1)




WIDTH, HEIGHT = 800, 600
chopsticks_group = pygame.sprite.Group()
characters_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
meal_group = pygame.sprite.Group()
chairs_group_1 = pygame.sprite.Group()
chairs_group_2 = pygame.sprite.Group()

MEAL_AMOUNT = 3


def add_sprites():
    chair_0 = Chair("assets/chair_front_2.png", (WIDTH // 2 - 40, HEIGHT // 2 - 110))
    chair_1 = Chair("assets/chair_front_2.png", (WIDTH // 2 + 40, HEIGHT // 2 - 110))
    chair_2 = Chair("assets/chair_right_2.png", (WIDTH // 2 + 130, HEIGHT // 2 - 10))
    chair_3 = Chair("assets/chair_back_2.png", (WIDTH // 2, HEIGHT // 2 + 100))
    chair_4 = Chair("assets/chair_left_2.png", (WIDTH // 2 - 130, HEIGHT // 2 - 10))
    chairs_group_1.add([chair_0, chair_1, chair_2, chair_4, ])
    chairs_group_2.add([chair_3])
    background_group.add(
        [
            BackgroundFurniture("assets/floor.png", (x, y))
            for x in range(0, WIDTH + 100, 62) for y in range(0, HEIGHT + 100, 46)
        ]
    )
    background_group.add(BackgroundFurniture("assets/carpet.png", (WIDTH // 2, HEIGHT // 2), 12))
    background_group.add(BackgroundFurniture("assets/fireplace.png", (WIDTH // 2, 60), 4))
    background_group.add(BackgroundFurniture("assets/music_player.png", (720, 90), 4))
    background_group.add(BackgroundFurniture("assets/sofa_front.png", (560, 80), 4))
    background_group.add(BackgroundFurniture("assets/sofa_single_right.png", (740, 200), 4))
    background_group.add(BackgroundFurniture("assets/stairs.png", (700, 440), 4, True))
    background_group.add(BackgroundFurniture("assets/desk.png", (170, 120), 3))
    background_group.add(BackgroundFurniture("assets/table_horizontal.png", (WIDTH // 2, HEIGHT // 2), 4))

    chopstick_0 = Chopstick(225, (WIDTH // 2 + 0, HEIGHT // 2 - 60), 0)
    chopstick_1 = Chopstick(160, (WIDTH // 2 + 55, HEIGHT // 2 - 35), 1)
    chopstick_2 = Chopstick(75, (WIDTH // 2 + 40, HEIGHT // 2 + 10), 2)
    chopstick_3 = Chopstick(15, (WIDTH // 2 - 40, HEIGHT // 2 + 10), 3)
    chopstick_4 = Chopstick(290, (WIDTH // 2 - 55, HEIGHT // 2 - 35), 4)

    chopsticks_group.add([chopstick_0, chopstick_1, chopstick_2, chopstick_3, chopstick_4])

    philosopher_0 = Character(6, 0, (WIDTH // 2 + 10, HEIGHT // 2 + 30), 0)
    philosopher_1 = Character(0, 0, (WIDTH // 2 + 90, HEIGHT // 2 + 30), 1)
    philosopher_2 = Character(4, -2, (WIDTH // 2 + 160, HEIGHT // 2 + 100), 2)
    philosopher_3 = Character(10, 1, (WIDTH // 2 + 45, HEIGHT // 2 + 180), 3)
    philosopher_4 = Character(2, 2, (WIDTH // 2 - 65, HEIGHT // 2 + 100), 4)
    characters_group.add(
        [
            philosopher_0, philosopher_1, philosopher_2, philosopher_3, philosopher_4,
        ]
    )
    meal_0 = Meal((WIDTH // 2 - 40, HEIGHT // 2 - 50), MEAL_AMOUNT)
    meal_1 = Meal((WIDTH // 2 + 40, HEIGHT // 2 - 50), MEAL_AMOUNT)
    meal_2 = Meal((WIDTH // 2 + 60, HEIGHT // 2 - 15), MEAL_AMOUNT)
    meal_3 = Meal((WIDTH // 2 + 0, HEIGHT // 2 - 10), MEAL_AMOUNT)
    meal_4 = Meal((WIDTH // 2 - 60, HEIGHT // 2 - 15), MEAL_AMOUNT)
    meal_group.add([meal_0, meal_1, meal_2, meal_3, meal_4])


add_sprites()
pygame.init()
font = pygame.font.SysFont(None, 25)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
if __name__ == "__main__":
    run = True
    n = 5
    dining_philosophers = Game_Parallel(chopsticks_group, characters_group, meal_group, n)
    threads = [Thread(target=dining_philosophers.philosopher_queue, args=(i,)) for i in range(5)]
    for thread in threads:
        thread.daemon = True
        thread.start()

    while run or sum(dining_philosophers.get_meals_sum()) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit(0)

        screen.fill('black')
        background_group.draw(screen)
        chairs_group_1.draw(screen)
        dining_philosophers.character_sprites.draw(screen)
        chairs_group_2.draw(screen)

        dining_philosophers.meal_sprites.draw(screen)
        dining_philosophers.chopstick_sprites.draw(screen)
        dining_philosophers.chopstick_sprites.update()
        dining_philosophers.character_sprites.update()
        dining_philosophers.meal_sprites.update()

        pygame.display.update()
        clock.tick(60)
    print('end of line')
