import pygame
import os

class Button:
    def __init__(self, name, pos, surface):
        self.name = name
        self.pos = pos
        self.screen = surface
        ##boolean attribute tells program if button is being hovered over
        self.hover = False
        ##load button asset
        self.image = pygame.image.load(os.path.join(f'Assets/{self.name}-Button.png'))
        ##load image of button when it is being hovered over
        self.hoverImage = pygame.image.load(os.path.join(f'Assets/{self.name}-Hover.png'))
    
    def is_hovering(self, event):
        hoverPos = event.pos
        self.hover = False
        ##Check if the mouse position is within the width of the button
        if hoverPos[0] in range(self.pos[0], self.pos[0] + 150):
            ##Check if the mouse position is within the height of the button
            if hoverPos[1] in range(self.pos[1], self.pos[1] + 75):
                self.hover = True

    def is_clicked(self, event):
        clickPos = event.pos
        ##Check if the mouse position is within the width of the button
        if clickPos[0] in range(self.pos[0], self.pos[0] + 150):
            ##Check if the mouse position is within the height of the button
            if clickPos[1] in range(self.pos[1], self.pos[1] + 75):
                return True

    ##DRAW METHODS
        
    def draw_button(self):
        ##draw a rectangle around the button
        pygame.draw.rect(self.screen, (137, 91, 64), pygame.Rect(self.pos[0]-5, self.pos[1]-5, 160, 85))
        ##draw the button
        self.screen.blit(self.image, self.pos)

    def draw_hover(self):
        ##draw a rectangle around the button
        pygame.draw.rect(self.screen, (137, 91, 64), pygame.Rect(self.pos[0]-5, self.pos[1]-5, 160, 85))
        ##draw the buttons hover asset
        self.screen.blit(self.hoverImage, self.pos)

    
            
