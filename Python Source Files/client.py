import pygame
from pygame import Color
from nnetwork import Network
import pickle
import glob
import time

# loading and intializing pygame shits
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
width = 700
height = 700
FPS = 1
empty = (0, 0, 0, 0)
numWins = 0
numTies = 0

# the one and only special surface limited by LSD
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

# loading images:
backgroundImg = pygame.image.load(
    "myfigure.png")

images_list = [pygame.image.load("anim1.png").convert_alpha(),
               pygame.image.load("anim2.png").convert_alpha(),
               pygame.image.load("anim3.png").convert_alpha()
               ]

display_index = 0


class Button:
    def __init__(self, text, code, x, y, color):
        self.text = text
        self.code = code
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, win):
        surf = pygame.Surface((162, 100), pygame.SRCALPHA)
        surf.fill((0, 100, 255, 155))
        pygame.draw.rect(surf, (0, 100, 255, 155), (self.x, self.y, self.width, self.height))
        text = images_list[self.code]
        text = pygame.transform.scale(text, (150, 150))

        win.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def redrawWindow(win, game, p):
    win.fill((128, 128, 128))
    win.blit(backgroundImg, (0, 0))

    # blitting the score fml :(
    # print(type(p))
    # print("the score i get for player " + str(p) + "  = " + game.getScore(p))

    if not (game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Waiting for Player...", 1, (255, 0, 0), True)
        win.blit(text, (100, 80))
    else:
        font = pygame.font.SysFont("comicsans", 50)
        text = font.render("Your Move", 1, (0, 255, 255))
        win.blit(text, (80, 80))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 80))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.bothWent():
            text1 = font.render(move1, 1, (255, 255, 255))
            text2 = font.render(move2, 1, (255, 255, 255))
        else:
            if game.p1Went and p == 0:
                text1 = font.render(move1, 1, (255, 255, 255))
            elif game.p1Went:
                text1 = font.render("Locked In", 1, (255, 255, 255))
            else:
                text1 = font.render("Waiting...", 1, (255, 255, 255))

            if game.p2Went and p == 1:
                text2 = font.render(move2, 1, (255, 255, 255))
            elif game.p2Went:
                text2 = font.render("Locked In", 1, (255, 255, 255))
            else:
                text2 = font.render("Waiting...", 1, (255, 255, 255))

        if p == 1:
            win.blit(text2, (100, 150))
            win.blit(text1, (430, 150))
        else:
            win.blit(text1, (100, 150))
            win.blit(text2, (430, 150))

        for btn in btns:
            btn.draw(win)

    textScore = "  Wins: " + str(
        numWins) + "                                                                                          Ties: " + str(
        numTies)
    font = pygame.font.SysFont("comicsans", 30)
    the_score = font.render(textScore, 1, (255, 0, 0), True)
    win.blit(the_score, (0, 0))
    pygame.display.update()


btns = [Button("Rock", 0, 50, 500, (0, 0, 0)), Button("Scissors", 1, 250, 500, (255, 0, 0)),
        Button("Paper", 2, 450, 500, (0, 255, 0))]


def drawLoading(win, game, p):
    # pygame.Surface.blit(your_image, the_screen, rect_or_coordinates)
    game.loading = True
    redrawWindow(win, game, p)
    global display_index
    clock.tick(FPS)
    if display_index > 2:
        display_index = 0
        # game.loading = False

    img_to_blit = pygame.transform.scale(images_list[display_index], (150, 150))
    recimg = images_list[display_index].get_rect()
    recimg.center = (width / 2), (height / 2)
    win.blit(img_to_blit, recimg)  # blit the image[index]
    display_index += 1
    pygame.display.update()
    pygame.time.delay(400)  # delay for 1 second


def main():
    global display_index
    global numWins
    global numTies
    run = True
    n = Network()
    player = int(n.getP())
    print("You are player", player)

    while run:
        clock.tick(60)
        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        if game.bothWent():
            for i in range(3):
                drawLoading(win, game, player)

            game.p1Went = True
            game.p2Went = True
            game.loading = False

            redrawWindow(win, game, player)

            pygame.time.delay(500)
            try:
                game = n.send("reset")
            except:
                run = False
                print("Couldn't get game")
                break

            font = pygame.font.SysFont("comicsans", 90)
            if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                text = font.render("You Won!", 1, (255, 0, 0))
                rect_text = text.get_rect()
                rect_text.center = (width / 2), (height / 2)
                # game.score[player] += 1
                numWins += 1

            elif game.winner() == -1:
                text = font.render("Tie Game!", 1, (255, 0, 0))
                rect_text = text.get_rect()
                rect_text.center = (width / 2), (height / 2)
                numTies += 1
            else:
                text = font.render("You Lost...", 1, (255, 0, 0))
                rect_text = text.get_rect()
                rect_text.center = (width / 2), (height / 2)

            win.blit(text, rect_text)
            pygame.display.update()
            pygame.time.delay(2000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Went:
                                n.send(btn.text)
                        else:
                            if not game.p2Went:
                                n.send(btn.text)

        redrawWindow(win, game, player)


def menu_screen():
    run = True

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        win.blit(backgroundImg, (0, 0))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255, 0, 0))
        win.blit(text, (200, 80))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()


while True:
    menu_screen()
