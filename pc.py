import os, pygame, sys

WIDTH, HEIGHT = 1280, 720
ART_W, ART_H = 1920, 1080
SCREEN_POS =(333, 116)
BASE = os.path.dirname(os.path.abspath(__file__))

def load(img):
    path = os.path.join(BASE, "assets", "pc",img)
    if not os.path.exists(path):
        sys.exit("missing asset" + path)
    return pygame.image.load(path).convert_alpha()


#######asset loading########
class Button:
    def __init__(self, name, topleft):
        self.img = load(name)
        self.bright = self.img.copy()
        self.bright.fill((80, 80, 80), special_flags=pygame.BLEND_RGB_ADD)
        self.rect = self.img.get_rect(topleft=topleft)
        self.mask = pygame.mask.from_surface(self.img)

    def hit(self, pos):
        x, y = pos[0] - self.rect.x, pos[1] - self.rect.y
        return 0 <= x < self.rect.w and 0 <= y < self.rect.h and bool(self.mask.get_at((x, y)))

    def draw(self, canvas, mouse):
        canvas.blit(self.bright if self.hit(mouse) else self.img, self.rect)

class Bank:
    RATE, MAX_DEBT = 0.3, 2000
    LOANS = (("loan_100.png", 100), ("loan_500.png", 500), ("loan_1000.png", 1000))
    REPAY = (("repay_100.png", 100), ("repay_500.png", 500), ("repay_1000.png", 1000))

    def __init__(self, font):
        self.font = font
        self.loan_btns = [(Button(f, (90, 220 + i * 80)), a) for i, (f, a) in enumerate(self.LOANS)]
        self.repay_btns = [(Button(f, (500, 220 + i * 80)), a) for i, (f, a) in enumerate(self.REPAY)]

    def borrow(self, player, amount):
        if player.debt + amount <= self.MAX_DEBT:
            player.cash += amount
            player.debt += amount

    def repay(self, player, amount):
        amount = min(amount or player.debt, player.debt, player.cash)
        player.cash -= amount
        player.debt -= amount

    def end_day(self, player):
        player.debt = round(player.debt * (1 + self.RATE))

    def click(self, pos, player):
        for btn, amount in self.loan_btns:
            if btn.hit(pos):
                self.borrow(player, amount)
                return True
        for btn, amount in self.repay_btns:
            if btn.hit(pos):
                self.repay(player, amount)
                return True
        return False

    def text(self, canvas, s, pos):
        canvas.blit(self.font.render(s, True, (0, 0, 0)), pos)

    def draw(self, canvas, mouse, player):
        for btn, _ in self.loan_btns + self.repay_btns:
            btn.draw(canvas, mouse)
        self.text(canvas, f"{player.cash}",(90, 665))
        self.text(canvas, f"Debt: {player.debt}", (90, 150))
        self.text(canvas, f"REPAY        Interest: {int(self.RATE * 100)}% per day", (500, 150))

class Browser:
    TAB_X, TAB_Y, TAB_GAP, MAX_TABS = 10, 6, 2, 15

    def __init__(self):
        self.page = load("page.png")
        self.tab = load("tab.png")
        self.tab_dim = self.tab.copy()
        self.tab_dim.set_alpha(150)
        self.plus = Button("plus.png", (10, 50))
        self.cross = Button("cross.png", (self.plus.rect.right + 6, 50))
        self.back = Button("back.png", (10, 120))
        self.join = Button("join.png", (0, 0))
        self.join.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.cards = [Button(n, (40 + i * 380, 200)) for i, n in enumerate(("card_market.png", "card_wiki.png", "card_bank.png"))]
        self.sites = [load(n) for n in ("market.png", "wiki.png", "bank.png")]
        self.step = self.tab.get_width() + self.TAB_GAP
        self.player = None
        self.font = pygame.font.SysFont(None, 60, True)
        self.bank = Bank(self.font)

        self.open = False
        self.tabs = []
        self.current = 0
        self.dragging = None
        self.grab_dx = 0
        self.drag_x = 0

    def open_browser(self):
        self.open , self.tabs, self.current = True, [self.page], 0

    def is_site(self, surf):
        return any(surf is s for s in self.sites)
    
    def tab_rects(self):
        rects = [self.tab.get_rect(topleft=(self.TAB_X + i * self.step, self.TAB_Y)) for i in range(len(self.tabs))]
        if self.dragging is not None:
            rects[self.dragging].x = self.drag_x
        return rects

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.click(e.pos)
        elif e.type == pygame.MOUSEMOTION and self.dragging is not None:
            self.drag(e.pos[0])
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging = None

    def click(self, pos):
        cur = self.tabs[self.current]
        card = next((s for c, s in zip(self.cards, self.sites) if c.hit(pos)), None)

        if self.plus.hit(pos):
            if len(self.tabs) < self.MAX_TABS:
                self.tabs.append(self.page)
                self.current = len(self.tabs) - 1

        elif self.cross.hit(pos):
            self.tabs.pop(self.current)
            self.open = bool(self.tabs)

            self.current = min(self.current, len(self.tabs) - 1)
        elif cur is self.page and card is not None:
            self.tabs[self.current] = card

        elif cur in self.sites and self.back.hit(pos):
            self.tabs[self.current] = self.page

        elif cur is self.sites[2] and self.bank.click(pos, self.player):
            pass
        else:
            self.pick_tab(pos)

    def pick_tab(self, pos):
        for i, r in enumerate(self.tab_rects()):
            if r.collidepoint(pos):
                self.current = self.dragging = i
                self.grab_dx, self.drag_x = pos[0] - r.x, r.x
                return

    def drag(self, x):
        self.drag_x = max(self.TAB_X, min(x - self.grab_dx, self.TAB_X + (len(self.tabs) - 1) * self.step))
        target = round((self.drag_x - self.TAB_X) / self.step)
        if target != self.dragging:
            self.tabs.insert(target, self.tabs.pop(self.dragging))
            self.dragging = self.current = target

    def draw(self, canvas, mouse):
        cur = self.tabs[self.current]
        canvas.blit(cur, (0, 0))
        if cur is self.page:
            for c in self.cards:
                c.draw(canvas, mouse)
        elif cur in self.sites:
            self.back.draw(canvas, mouse)
            if cur is self.sites[0]:
                self.join.draw(canvas, mouse)
            if cur is self.sites[2]:
                self.bank.draw(canvas, mouse, self.player)
        rects = self.tab_rects()
        order = [i for i in range(len(self.tabs)) if i != self.dragging] + ([self.dragging] if self.dragging is not None else [])
        for i in order:
            canvas.blit(self.tab if i == self.current else self.tab_dim, rects[i])
        self.plus.draw(canvas, mouse)
        self.cross.draw(canvas, mouse)

class Desktop:
    def __init__(self):
        self.background, self.ie = load("bg.png"), Button("ie.png", (30, 30))
        self.browser, self.player = Browser(), None

    def handle(self, e):
        if self.browser.open:
            self.browser.handle(e)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.ie.hit(e.pos):
            self.browser.open_browser()
    def draw(self, canvas, mouse):
        canvas.blit(self.background, (0, 0))
        self.ie.draw(canvas, mouse)
        if self.browser.open:
            self.browser.draw(canvas, mouse)

class Monitor:
    def __init__(self, screen):
        self.coeff = screen.get_width() / ART_W
        self.frame = pygame.transform.scale(OUTSIDE, screen.get_size())
        self.pos = (int(SCREEN_POS[0] * self.coeff), int(SCREEN_POS[1] * self.coeff))
        self.size = (int(WIDTH * self.coeff), int(HEIGHT * self.coeff))

    def to_desktop(self, pos):
        return (int((pos[0] - self.pos[0]) / self.coeff), int((pos[1] - self.pos[1]) / self.coeff))

OUTSIDE = load("pc_bg.png")
clock, desktop = pygame.time.Clock(), Desktop()

def run(screen, player):
    pc_window = pygame.Surface((WIDTH, HEIGHT))
    monitor, desktop.player = Monitor(screen), player
    desktop.browser.player = player
    while True:
        player.debt = getattr(player, "debt", 0)
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                desktop.browser.dragging = None
                return
            if hasattr(e, "pos"):
                e.pos = monitor.to_desktop(e.pos)
            desktop.handle(e)

        desktop.draw(pc_window, monitor.to_desktop(pygame.mouse.get_pos()))  
        screen.fill((46, 140, 120))
        screen.blit(monitor.frame, (0, 0))
        screen.blit(pygame.transform.scale(pc_window, monitor.size), monitor.pos)
        pygame.display.flip()