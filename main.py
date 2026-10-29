import pygame, json, math, os, sys
from pathlib import Path

WIDTH = 1280
HEIGHT = 720

BASE = os.path.dirname(os.path.abspath(__file__))

def load(img):
    path = os.path.join(BASE, "assets", img)
    if not os.path.exists(path):
        sys.exit("missing asset" + path)
    return pygame.image.load(path).convert_alpha()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("")
clock = pygame.time.Clock()

#######asset loading########

background = load("bg.png")
ie = load("ie.png")
page = load("page.png")
cross = load("cross.png")
plus = load("plus.png")

#######postiions#######

ie_rect = ie.get_rect(topleft=(30, 30))
page_rect = page.get_rect(topleft=(0, 0))
cross_rect = cross.get_rect(topright=(6, 6))
plus_rect = plus.get_rect(topleft=(400, 6))

browser_open = False

####main loop #####

while True:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if not browser_open and ie_rect.collidepoint(e.pos):
                browser_open = True
            elif browser_open and cross_rect.collidepoint(e.pos):
                browser_open = False

    screen.blit(background, (0, 0))
    screen.blit(ie, ie_rect)
    if browser_open:
        screen.blit(page, page_rect)
        screen.blit(cross, cross_rect)
        screen.blit(plus, plus_rect)

    pygame.display.flip()
