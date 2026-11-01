# -*- coding: utf-8 -*-


import pygame, random, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

def render_outlined_text(text:str, color:tuple, font, width:int):
    outline_color = (255 - color[0], 255 - color[1], 255 - color[2])
    base = font.render(text, True, color)
    edge = font.render(text, True, outline_color)
    surface = pygame.Surface((base.get_width() + width*2, base.get_height() + width*2), pygame.SRCALPHA)

    for x in range(-width, width + 1):
        for y in range(-width, width + 1):
            if x * x + y * y <= width * width:
                surface.blit(edge, (width + x, width + y))
    surface.blit(base, (width, width))
    return surface

def load_img(img):                                  #Good idea brother
    path = os.path.join(BASE, r"assets\images", img)
    if not os.path.exists(path):
        sys.exit("missing asset" + path)
    return pygame.image.load(path).convert_alpha()

def sort_news(tab): #[("text", int value)]
    length = len(tab)
    if length <= 1:
        return tab
    
    newest = tab.pop()

    for i in range(-2, -length-1, -1):
        if newest[1] < tab[i]:
            i = length - i + 2
            break
    j = 0
    found = 0
    new_tab = [None for i in range(length+1)]
    while j <= length:
        if i == j:
            new_tab[j] = newest
            found = 1
        else:
            new_tab[j] = tab[j - found]
        j += 1
    return new_tab





class Player:
    def __init__(self):
        self.luck = 0
        self.cash = 100 # Dollares
        self.predictions = {} # "name" : [percentage chance (float), reward]

    def roll_predictions(self):
        for key in self.predictions.keys():
            random_number = random.uniform(0,100)

            if random_number <= self.predictions[key][0]:
                self.predictions[key][0] = True
                cash += self.predictions[key][1]
            



class State:
    def __init__(self, resolution):
        self.state = "room"         # Possible states : "room", "Living_room", "sofa", "pc"
        self.pc_state = "main"      # Possible states : "main", "polski_tunes", "polski_market", "settings"
        self.bright_sprite = [None, None, None] #name:str, brighter_sprite, position:tuple
        self.resolution = resolution
        self.interactibles_per_location = {"room" : ["computer","room_door"] , "living_room": ["living_room_door", "sofa"]}
        self.masks = {"room" : {"computer" : None, "room_door" : None}, "living_room" : {"living_room_door" : None, "sofa" : None}}

        self.news_text = {  "polish_cow_dance_highway" : "For the third time this week, a neighboring cow has taken to the highway and started dancing", 
                            "tri_poloski_together" : "For an unknown reason three visibly polish men where spotted together, singing something indescribable"}
        
        self.miscellaneous_news = ( "Housing market in worse shape, pricing increasing at blistering speeds", 
                                    "Weather forecast states that there will be rain for the upcoming 24 years", 
                                    "Local man tries cookies, dies from the taste", 
                                    "Scientists create new cure for throat singing cats, causes dancing instead")


    def draw_screen(self, screen, image_dict):
        screen.blit(image_dict["background"][self.state], (0,0))

        if self.state == "pc":
            pass
        else:
            self.draw_interactible(screen, image_dict)

        

    def draw_interactible(self, screen, image_dict):
        for image in self.interactibles_per_location[self.state]:
            screen.blit(image_dict["interactible"][image],(0,0))

    def update_resolution(self, image_dict, original_image_dict):
        coef = self.resolution[0]/1920

        for key_1 in image_dict.keys():
            for key_2 in image_dict[key_1]:
                image_dict[key_1][key_2] = pygame.transform.scale(original_image_dict[key_1][key_2], self.resolution)

        for key_1 in self.masks.keys():
            for key_2 in self.masks[key_1].keys():
                try:
                    self.masks[key_1][key_2] = pygame.mask.from_surface(image_dict["interactible"][key_2])
                except:
                    print("missing image")

    def check_interact_collision(self, mouse_pos):
        for key, mask in self.masks[self.state].items():
            if mask.get_at(mouse_pos):
                return key
        return None

    def update_bright_sprite(self, selected, image_dict):
        self.bright_sprite[0] = selected
        if self.bright_sprite[0] is None:
            return
        brite = image_dict["interactible"][self.bright_sprite[0]].copy()
        brite.fill((80, 80, 80), special_flags=pygame.BLEND_RGB_ADD)
        self.bright_sprite[1] = brite
        self.bright_sprite[2] = {"computer" : (464, 317), "room_door" : (75, 432), "sofa" : (507, 403), "living_room_door" : (1124, 429)}[self.bright_sprite[0]]


    def draw_bright_sprite(self, screen, text_dict):
        screen.blit(self.bright_sprite[1], (0,0))
        screen.blit(text_dict[self.bright_sprite[0]], self.bright_sprite[2])


    def room_interactible_action(self, selected):
        if selected == "room_door":
            self.state = "living_room"
        elif selected == "living_room_door":
            self.state = "room"
        elif selected == "computer":
            self.state = "pc"
        else:
            self.state = "sofa"

    def draw_news(self, screen, player, font):
        player.roll_predictions()
        news = []
        for key in player.predictions.keys():
            if player.predictions[key][0] == True:
                if len(news) < 4:
                    news.append(key,player.predictions[key][1])
                elif news[3][1] < player.predictions[key][1]:
                    news[3] = player.predictions[key]
                sort_news(news)

        
        


pygame.init()
clock = pygame.time.Clock()

screen_resolutions = [(1920, 1080),(1280, 720), (854, 480), (640, 360)]

display_size = pygame.display.get_desktop_sizes()[0]

window_size = (1920, 1080)

for resolution in screen_resolutions:
    if display_size <= resolution:
        window_size = resolution
    else:
        break

size_coefficient = window_size[0]/1920

window = pygame.display.set_mode(window_size)

pc_window = pygame.Surface((1280*size_coefficient, 720*size_coefficient))

fonts = {"interact_font" : pygame.font.SysFont(None, 30, True), "sofa" : pygame.font.SysFont(None, 100, True)}
all_fancy_text = {  "room_door" : render_outlined_text("Enter living room", (255, 255, 255), fonts["interact_font"], 2), 
                    "living_room_door" : render_outlined_text("Enter room", (255, 255, 255), fonts["interact_font"], 2), 
                    "sofa" : render_outlined_text("End day", (255, 255, 255), fonts["sofa"], 5),
                    "computer" : render_outlined_text("Access computer", (255, 255, 255), fonts["interact_font"], 2)}

original_images = { "background" : {    "room" : load_img("room_bg.png"), 
                                        "living_room" : load_img("living_room_bg.png"),
                                        "pc" : load_img("pc_bg.png")}, 
                                   
                    "interactible" : {  "computer" : load_img("computer.png"), 
                                        "room_door" : load_img("room_door.png"), 
                                        "sofa" : load_img("sofa.png"),
                                        "living_room_door" : load_img("living_room_door.png")}}

images = {  "background" : {    "room" : None, 
                                "living_room" : None,
                                "pc" : None}, 
                                   
            "interactible" : {  "computer" : None, 
                                "room_door" : None, 
                                "sofa" : None,
                                "living_room_door" : None}}

import pc

player = Player()
current_state = State(window_size)

current_state.update_resolution(images, original_images)

running = True

while running:
    clock.tick(60)
    mx, my = pygame.mouse.get_pos()

    if current_state.state != "sofa":
        selected_interactible = current_state.check_interact_collision((mx, my))
        if selected_interactible != current_state.bright_sprite[0]:
            current_state.update_bright_sprite(selected_interactible, images) 
    else:
        current_state.bright_sprite[0] = None
        selected_interactible = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if selected_interactible is not None:
                    current_state.room_interactible_action(selected_interactible)
            if event.button == 3:
                print(mx, my)

    

    

    window.fill({"room" : (46, 140, 120), "living_room" : (78, 80, 116), "pc" : (46, 140, 120), "sofa" : (78, 80, 116)}[current_state.state])
    current_state.draw_screen(window, images)

    if current_state.state == "pc":
                pc_window.fill((255,255,255))
                window.blit(pc_window, (333*size_coefficient, 116*size_coefficient))
                
                pc.run(window, player)
                
                current_state.state = "room"
    
    

    if current_state.bright_sprite[0] is not None:
            current_state.draw_bright_sprite(window, all_fancy_text)

    pygame.display.flip()

pygame.quit()

pygame.quit()