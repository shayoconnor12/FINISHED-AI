import pygame
import os
import sys
import Source.chessLogic as chessLogic
import Source.chessEngine as chessEngine
import time
from copy import deepcopy

class Gameplay:
    def __init__(self, opponent, fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', colour = 'W'):
        #initialises the Board. using a new chessLogic.Board class.
        self.fen = fen
        self.colour = colour
        self.gameBoard = chessLogic.Board(fen, colour)
        self.boardTheme = Themes()
        self.gameOver = False
        self.winner = ''
        #initialises pygame
        pygame.init()
        #draws the screen, and gets the background
        self.screen = pygame.display.set_mode((1200, 800))
        self.background = pygame.image.load(os.path.join("Assets/PBackground.png"))

        #load controls asset from file.
        self.controls = pygame.image.load(os.path.join("Assets/Controls.png"))
        enemyString = 'AI' if opponent == 'AI' else 'Self'
        pygame.display.set_caption(("Play vs " + enemyString))

        #black will be the AI if 'AI' button pressed
        self.blackPlayer = opponent

        self.hoverX,self.hoverY = 0,0

        self.clickedSquares = []

    def mainloop(self):
            ##indefinite game loop, will be broken out of by returning a value
            eventX, eventY = 0,0
            while True:
                for event in pygame.event.get():
                    ##if the "X" in the top right is pressed
                    match event.type:
                        case pygame.QUIT:
                            ##quit pygame
                            pygame.quit()
                            ##and then close the program
                            sys.exit()
                            
                        case pygame.KEYDOWN:
                            ##if escape is pressed, value 0 will be returned.
                            ##this effectively exits the mainloop, and will return to the main menu.
                            match event.key:
                                case pygame.K_ESCAPE:
                                    return 0
                                case pygame.K_r:
                                    #reinitialise the game, resetting all its attributes and methods.
                                    #this will reset the position of the board aswell.
                                    self.__init__(self.blackPlayer, self.fen, self.colour)
                                case pygame.K_t:
                                    ##system for switching the colour scheme
                                    if not self.gameOver:
                                        self.boardTheme.updateTheme()
                                case pygame.K_u:
                                    #remove last position
                                    if not self.gameOver and self.blackPlayer != 'AI':
                                        self.gameBoard.undoMove()

                        case pygame.MOUSEMOTION:
                            ##get the position of the event
                            self.hoverX, self.hoverY = event.pos

                        case pygame.MOUSEBUTTONDOWN:
                            match event.button:
                                case 1:
                                    ##update the clicked squares
                                    clickX, clickY = event.pos
                                    ##shorten names of attributes
                                    topLeft = (40,40)
                                    squareSize = 90

                                    ##get the row and column of the clicked square
                                    clickedRow = (clickY-topLeft[0])//squareSize
                                    clickedCol = (clickX-topLeft[1])//squareSize
                                    #validates that the click is on the board
                                    if clickedRow in range(0,8) and clickedCol in range(0,8):
                                        #appends to the clicked squares list
                                        self.clickedSquares.append((clickedRow, clickedCol))
                                case 3:
                                    self.clickedSquares = []

                ##draw all elements to the screen
                self.draw()  
                self.playMove()

    def aiMoveGetter(self, allLegalMoves):
        aiBoard = deepcopy(self.gameBoard)
        chessAI = chessEngine.ChessAI(aiBoard, self.gameBoard.playerToMove)
        move = chessAI.getBestMove(aiBoard, allLegalMoves)
        #AI move is played on the board
        self.gameBoard.makeFullMove(move)
        #clicked squares is emtied, as it is not the players turn.
        self.clickedSquares = []
    
    def playMove(self):
        gameOver = self.gameBoard.isGameOver()
        if gameOver[0]:
            self.gameOver = True
            self.winner = '' if gameOver[1] == '' else 'W' if gameOver[1] == 'b' else 'b'
        #generates all legal moves for the position
        allLegalMoves = chessLogic.getAllLegalMoves(self.gameBoard)
        #if the player is going against the AI, and it's the AIs turn
        if self.blackPlayer == 'AI' and self.gameBoard.playerToMove == 'b':
            t0 = time.time()
            self.aiMoveGetter(allLegalMoves)
            t1 = time.time()
            print(t1-t0)
        #if the opponent isnt the AI, or if its the players turn
        else:
            #if two squares have been clicked
            if len(self.clickedSquares) == 2:
                #initialises the move
                move = chessLogic.Move(self.clickedSquares[0], self.clickedSquares[1])
                #for loop checks if the move is in the legal moves
                for m in allLegalMoves:
                    if m.initial == move.initial and m.final == move.final:
                        #makes the move on the board
                        self.gameBoard.makeFullMove(m)
                #empties clickedSquares
                self.clickedSquares = []



    def gameEnd(self, winner):
        #gets the winner screen from file
        winnerScreen = pygame.image.load(os.path.join(f'Assets/{winner}win.png'))
        #draws to centre of screen
        self.screen.blit(winnerScreen, (423,310))
        #tells the main loop that the game is over
        self.gameOver = True
            
    def draw(self):
        ##draw background onto screen
        self.screen.blit(self.background, (0,0))
        

        ##draw board and pieces
        self.drawBoard()
        self.drawPieces()
        self.drawHover()

        
        #draws controls
        self.screen.blit(self.controls, (825,50))

        if self.gameOver:
            self.gameEnd(self.winner)

        ##update display
        pygame.display.update()

    def drawBoard(self):
        lightSquare = self.boardTheme.currentColour[0]
        darkSquare = self.boardTheme.currentColour[1]

        ##more compact variable names for existing attributes, make code less cluttered, as "self" isnt repeated constantly
        topLeft = (40,40)
        squareSize = 90

        for r in range(8):
            for c in range(8):
                ##this if statement will alternate light and dark squares
                if (r + c)%2 == 0:
                    ##draws a rectangle on the screen, with a dark colour. 
                    ##The coordinates are a function of the row and column
                    ##squares are of size 90*90
                    pygame.draw.rect(self.screen, darkSquare, pygame.Rect(topLeft[0]+(squareSize*c),topLeft[1]+(squareSize*r), squareSize, squareSize))
                else:
                    ##draws a rectangle with a light colour
                    pygame.draw.rect(self.screen, lightSquare, pygame.Rect(topLeft[0]+(squareSize*c),topLeft[1]+(squareSize*r), squareSize, squareSize))
    
    def drawPieces(self):

        ##more compact variable names for existing attributes, make code less cluttered, as "self" isnt repeated constantly
        topLeft = (40,40)
        squareSize = 90
        centreValue = (squareSize-80)//2

        def getFileName(pieceName):
            ##if pieceName.isupper(), then the piece is white
            if pieceName.isupper():
                return 'w' + pieceName.lower()
            ##else the piece is black and the file name is kept the same
            else:
                return pieceName

        ##iterate through all squares on the board.
        for r in range(8):
            for c in range(8):
                ##gets the piece's name, by indexing the currentPos attribute
                if self.gameBoard.currentPos[r][c] != '':
                    pieceName = getFileName(self.gameBoard.currentPos[r][c])
                    ##turns this into a file name using an f-string
                    pieceFileName = f'{pieceName}.png'
                    ##load the image from file and then draw it onto the square
                    piece = pygame.image.load(os.path.join(f'Assets/{pieceFileName}'))
                    self.screen.blit(piece, (topLeft[0]+(squareSize*c)+centreValue,topLeft[1]+(squareSize*r)+centreValue))

    def drawHover(self):

        ##more compact variable names for existing attributes, make code less cluttered, as "self" isnt repeated constantly
        topLeft = (40,40)
        squareSize = 90
        self.hoverY, self.hoverX

        ##locate the row and column being hovered over
        hoveredRow = (self.hoverY-topLeft[0])//squareSize
        hoveredCol = (self.hoverX-topLeft[1])//squareSize

        ##red colour for the highlighting
        hoverColour = (250, 55, 55)

        ##draws a hollow square
        ##final value in this function call is 5, this represents how many pixels wide the outline will be
        if hoveredRow in range(0,8) and hoveredCol in range(0,8):
            pygame.draw.rect(self.screen, hoverColour, (topLeft[0] + (hoveredCol*squareSize), topLeft[1] + (hoveredRow*squareSize), squareSize, squareSize), 5)

class Themes:

    def __init__(self):
        ##defining the colour schemes as tuples of colours
        ##[0] represents the light colour, [1] represents the dark colour
        self.green = ((234, 235, 200), (119, 154, 88))
        self.brown = ((235, 209, 166), (165, 117, 80))
        self.grey = ((160, 159, 158), (86, 85, 84))
        ##defining a list of colours, so that the current colour can be switched by pressing 'T'
        self.colours = [self.green, self.brown, self.grey]
        ##in the main game loop the input 'T' will increment colourIndex
        self.colourIndex = 0
        self.currentColour = self.colours[self.colourIndex]
    
    def updateTheme(self):
        self.colourIndex += 1
        self.currentColour = self.colours[self.colourIndex % 3]

def main(enemy, fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR', colour = 'W'):
    game = Gameplay(enemy, fen, colour)
    game.mainloop()
    return 0
