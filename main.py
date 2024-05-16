import pygame
from sys import exit
import random


# Pygame initialization
pygame.init()
clock = pygame.time.Clock()

# Skärm hur bred och hög den ska vara
win_height = 650
win_width = 541
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Floppy")

# Bilder för spelet (fågeln och pipes och backgrunden)
bird_frames = [pygame.image.load("assets/images/serbian-downflap.png"),
               pygame.image.load("assets/images/redbird-midflap.png"),
               pygame.image.load("assets/images/redbird-upflap.png")]
background_img = pygame.image.load("assets/images/background.png")
ground_img = pygame.image.load("assets/images/ground.png")
top_pipe_img = pygame.image.load("assets/images/pipe_top.png")
bottom_pipe_img = pygame.image.load("assets/images/pipe_bottom.png")
game_over_img = pygame.image.load("assets/images/game_over.png")
start_img = pygame.image.load("assets/images/start.png")

# Spelet, start position och hastighet för själva fågeln och backgrunden, font för score och om spelet är slut, variabel
scroll_speed = 2
initial_bird_pos = (100, 250)
current_score = 0
font = pygame.font.SysFont('Arial', 26)
top_scores = [0, 0, 0]
is_game_over = True
high_scores_file = 'high_scores.txt'


# klass för fågeln
class FlappyBird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = initial_bird_pos
        # variab för anmatiation rörrelse
        self.frame_index = 0
        self.velocity = 0
        self.flap = False
        self.is_alive = True

    def update(self, user_input):
        # Animera fågeln down / mid / up - flap
        if self.is_alive:
            self.frame_index += 1
        if self.frame_index >= 30:
            self.frame_index = 0
        self.image = bird_frames[self.frame_index // 10]

        # Gravititet och upp och ner
        self.velocity += 0.5
        if self.velocity > 7:
            self.velocity = 7
        if self.rect.y < 500:
            self.rect.y += int(self.velocity)
        if self.velocity == 0:
            self.flap = False

        # rotera skiten
        self.image = pygame.transform.rotate(self.image, self.velocity * -7)

        # input att skiten ska hoppa-flygga
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.is_alive:
            self.flap = True
            self.velocity = -7


# klass för pipes
class PipeObstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        # bild för rörena
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.entry, self.exit, self.crossed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        # flyttar på rörena
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()

        # Påengar om fågeln har passerat röret
        global current_score
        if self.pipe_type == 'bottom':
            if initial_bird_pos[0] > self.rect.topleft[0] and not self.crossed:
                self.entry = True
            if initial_bird_pos[0] > self.rect.topright[0] and not self.crossed:
                self.exit = True
            if self.entry and self.exit and not self.crossed:
                self.crossed = True
                current_score += 1


# klass så att marken rör sig
class GroundTerrain(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        # Flyttar marken
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()


def quit_game():
    # Stänger spelet
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


# funktion för att  updatera de högsta påengarna man får
def update_top_scores(score):
    global top_scores
    min_score = min(top_scores)
    if score > min_score:
        top_scores.remove(min_score)
        top_scores.append(score)
        top_scores.sort(reverse=True)
        save_high_scores()


# funktion för att spara högsta påeng till en fil
def save_high_scores():
    with open(high_scores_file, 'w') as file:
        for score in top_scores:
            file.write(str(score) + '\n')


# funktion för att ladda högsta påengarna från en fil
def load_high_scores():
    try:
        with open(high_scores_file, 'r') as file:
            return [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        return [0, 0, 0]


# Huvudspel
def play_game():
    global current_score

    # skapar fågeln
    flappy_bird = pygame.sprite.GroupSingle()
    flappy_bird.add(FlappyBird())

    # ställer in rörena
    pipe_timer = 0
    pipes = pygame.sprite.Group()

    # intialiserar marken
    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(GroundTerrain(x_pos_ground, y_pos_ground))

    run = True
    while run:
        # avslutar spelet
        quit_game()

        # restartar rutan
        window.fill((0, 0, 0))

        # input  spelarnen
        user_input = pygame.key.get_pressed()

        # ritar backgrunden
        window.blit(background_img, (0, 0))

        # skapar marken
        if len(ground) <= 2:
            ground.add(GroundTerrain(win_width, y_pos_ground))

        # ritar rören, marken och fågeln
        pipes.draw(window)
        ground.draw(window)
        flappy_bird.draw(window)

        # vissar score
        score_text = font.render('Score: ' + str(current_score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))

        # updaterar rören, marken och fågeln
        if flappy_bird.sprite.is_alive:
            pipes.update()
            ground.update()
        flappy_bird.update(user_input)

        # kollar om kollision med marken eller rören
        collision_pipes = pygame.sprite.spritecollide(flappy_bird.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(flappy_bird.sprites()[0], ground, False)
        if collision_pipes or collision_ground:
            flappy_bird.sprite.is_alive = False
            if collision_ground:
                window.blit(game_over_img, (win_width // 2 - game_over_img.get_width() // 2,
                                            win_height // 2 - game_over_img.get_height() // 2))
                if user_input[pygame.K_r]:
                    update_top_scores(current_score)
                    current_score = 0
                    break

        # skapar rören
        if pipe_timer <= 0 and flappy_bird.sprite.is_alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-600, -480)
            y_bottom = y_top + random.randint(90, 130) + bottom_pipe_img.get_height()
            pipes.add(PipeObstacle(x_top, y_top, top_pipe_img, 'top'))
            pipes.add(PipeObstacle(x_bottom, y_bottom, bottom_pipe_img, 'bottom'))
            pipe_timer = random.randint(180, 250)
        pipe_timer -= 1.7

        clock.tick(60)
        pygame.display.update()


# menyn
def main_menu():
    global is_game_over

    while is_game_over:
        quit_game()

        # ritar själva menyn
        window.fill((0, 0, 0))
        window.blit(background_img, (0, 0))
        window.blit(ground_img, GroundTerrain(0, 520))
        window.blit(bird_frames[0], (100, 250))
        window.blit(start_img, (win_width // 2 - start_img.get_width() // 2,
                                win_height // 2 - start_img.get_height() // 2))

        # inpiten
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            play_game()
        # ritar högsta påengarna på mitten av skärmen "top scores" och lägger in högsta påengarna där från filet
        top_scores_text = font.render('Top Scores: ' + ', '.join(map(str, top_scores)), True,
                                      pygame.Color(255, 255, 255))
        window.blit(top_scores_text, (180, 150))

        pygame.display.update()


main_menu()