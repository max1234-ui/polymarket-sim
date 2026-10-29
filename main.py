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
tab = load("tab.png")
newpage = load("newpage.png")

#######postiions#######

ie_rect = ie.get_rect(topleft=(30, 30))

TAB_X, TAB_Y, TAB_GAP, MAX_TABS = 10, 6, 2, 15
tab_dim = tab.copy()
tab_dim.set_alpha(150)

plus_rect = plus.get_rect(topleft=(10, 50))
cross_rect = cross.get_rect(topleft=(plus_rect.right + 6, 50))

browser_open = False
tabs = []
current = 0
dragging = None
grab_dx = 0
drag_x = 0
STEP = tab.get_width() + TAB_GAP

####main loop #####
while True:
    clock.tick(60)
    tab_rects = [tab.get_rect(topleft=(TAB_X + i * STEP, TAB_Y)) for i in range (len(tabs))]
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if not browser_open:
                if ie_rect.collidepoint(e.pos):
                    browser_open = True
                    tabs = [page]
                    current = 0
            elif plus_rect.collidepoint(e.pos):
                if len(tabs) < MAX_TABS:
                    tabs.append(newpage)
                    current = len(tabs) - 1
            elif cross_rect.collidepoint(e.pos):
                tabs.pop(current)
                if not tabs:
                    browser_open = False
                else:
                    current = min(current, len(tabs) - 1)
            else:
                for i in range(len(tabs)):
                    if tab_rects[i].collidepoint(e.pos):
                        current = i
                        dragging = i
                        grab_dx = e.pos[0] - tab_rects[i].x
                        drag_x = tab_rects[i].x
                        break
        if e.type == pygame.MOUSEMOTION and dragging is not None:
            drag_x = e.pos[0] - grab_dx
            drag_x = max(TAB_X, min(drag_x, TAB_X + (len(tabs) - 1) * STEP))
            target = round((drag_x - TAB_X) / STEP)
            if target != dragging:
                tabs.insert(target, tabs.pop(dragging))
                dragging = target
                current = target
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            dragging = None
    tab_rects = [tab.get_rect(topleft=(TAB_X + i * STEP, TAB_Y)) for i in range(len(tabs))]

    if dragging is not None:
        tab_rects[dragging].x = drag_x
        

    screen.blit(background, (0, 0))
    screen.blit(ie, ie_rect)
    if browser_open:
        screen.blit(tabs[current], (0, 0))
        order = [i for i in range(len(tabs)) if i != dragging]
        if dragging is not None:
            order.append(dragging)
        for i in order:
            screen.blit(tab if i == current else tab_dim, tab_rects[i])
        

        screen.blit(plus, plus_rect)
        screen.blit(cross, cross_rect)

    pygame.display.flip()