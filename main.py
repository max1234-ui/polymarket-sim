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

TAB_X, TAB_Y, TAB_GAP, MAX_TABS = 10, 6, 2, 6
tab_dim = tab.copy()
tab_dim.set_alpha(150)

browser_open = False
tabs = []
current = 0

####main loop #####
while True:
    clock.tick(60)
    tab_rects = []
    cross_rects = []
    for i in range(len(tabs)):
        r = tab.get_rect(topleft=(TAB_X + i * (tab.get_width() + TAB_GAP), TAB_Y))
        tab_rects.append(r)
        cross_rects.append(cross.get_rect(midright=(r.right - 6, r.centery)))
    plus_X = TAB_X + len(tabs) * (tab.get_width() + TAB_GAP) + 4
    plus_rect = plus.get_rect(midleft=(plus_X, TAB_Y + tab.get_height() // 2))
    
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
            elif len(tabs) < MAX_TABS and plus_rect.collidepoint(e.pos):
                tabs.append(newpage)
                current = len(tabs) - 1
            else:
                for i in range(len(tabs)):
                    if cross_rects[i].collidepoint(e.pos):
                        tabs.pop(i)
                        if not tabs:
                            browser_open = False
                        elif i < current:
                            current -= 1
                        else:
                            current = min(current, len(tabs) - 1)
                        break
                    if tab_rects[i].collidepoint(e.pos):
                        current = i
                        break

    tab_rects = []
    cross_rects = []
    for i in range(len(tabs)):
        r = tab.get_rect(topleft=(TAB_X + i * (tab.get_width() + TAB_GAP), TAB_Y))
        tab_rects.append(r)
        cross_rects.append(cross.get_rect(midright=(r.right - 6, r.centery)))
    plus_X = TAB_X + len(tabs) * (tab.get_width() + TAB_GAP) + 4
    plus_rect = plus.get_rect(midleft=(plus_X, TAB_Y + tab.get_height() // 2))
    
    screen.blit(background, (0, 0))
    screen.blit(ie, ie_rect)
    if browser_open:
        screen.blit(tabs[current], (0, 0))
        for i in range (len(tabs)):
            screen.blit(tab if i == current else tab_dim, tab_rects[i])
            screen.blit(cross, cross_rects[i])
        if len(tabs) < MAX_TABS:
            screen.blit(plus, plus_rect)

    pygame.display.flip()