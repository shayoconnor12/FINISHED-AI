import pygame
import sys
import os
from Source.const import *
from Source.button import *
import Source.gamePlay as gamePlay
import Source.analysis as analysis

class Main:
    def __init__(self):
        ##initialise pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Main Menu!")
        ##load background image
        self.background = pygame.image.load(os.path.join('Assets/Background.png')) 
    
    def quit(self):
        pygame.quit()
        ##closes window
        sys.exit()

    def mainMenu(self):
        pvpButton = Button('PVP', (75,115), self.screen)
        aiButton = Button('Vs-AI', (75,205), self.screen)
        analysisButton = Button('Analysis', (75,295), self.screen)
        buttons = [pvpButton, aiButton, analysisButton]
        while True:
            ##iterates through all events
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    ##if escape pressed, then program is quit
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                if event.type == pygame.MOUSEMOTION:
                    for button in buttons:
                        button.is_hovering(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button.is_clicked(event):
                            ##if any button is clicked, then it selects the buttons name using a match case
                            match button.name:
                                case 'PVP':
                                    ##calls pvp main method
                                    gamePlay.main('')
                                    # after pvp.main() has stopped, it reconstructs the Main method
                                    # this clears the screen, effectively returning to the main menu
                                    self.__init__()
                                
                                ##repeated for other modules
                                case 'Vs-AI':
                                    gamePlay.main('AI')
                                    self.__init__()
                                case 'Analysis':
                                    analysis.main()
                                    self.__init__()
            
            ##CODE TO DRAW SCREEN

            ##blit background onto screens
            self.screen.blit(self.background, (0,0))
            ##blit main menu text onto screen
            self.screen.blit(pygame.image.load(os.path.join('Assets/Main-Menu-Text.png')), (61, 0))
            for button in buttons:
                if button.hover:
                    button.draw_hover()
                else:
                    button.draw_button()
            pygame.display.update()

def main():
    menu = Main()
    menu.mainMenu()
