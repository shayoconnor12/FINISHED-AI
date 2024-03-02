from tkinter import Tk
import chess.pgn
import pygame
import sys
import os
from Source.gamePlay import Themes, main as gameMain
from Source.chessLogic import fenParse
from tkinter.filedialog import askopenfilename

class AnalysisBoard:
    def __init__(self, positionList):
        #takes the positionlist as input, and assigns it to an attribute
        self.positions = positionList
        #attribute holding the currently viewed board.
        self.positionIndex = 0
        self.viewedPosition = fenParse(positionList[self.positionIndex])
    
    def updatePos(self, direction):
        try:
            #tries to increment/decrement the board position, if out of range the function will do nothing.
            self.positionIndex = self.positionIndex+direction
            self.viewedPosition = fenParse(self.positions[self.positionIndex% len(self.positions)])
        except:
            pass

class AnalysisMain:
    def __init__(self):
        #I would like to not have any GUI output from TKInter, so I am withdrawing Tk
        Tk().withdraw()

        #Displaying file open box, and taking input
        filename = askopenfilename()

        #validates that the file is of the type .pgn
        Found = False
        while not Found:
                #validates the file extension
                if filename[len(filename)-4:] != '.pgn':
                    print('Invalid file, file extension must be .pgn')
                    #asks for the file again
                    filename = askopenfilename()
                else:
                    Found = True

        #opens the pgn of the game, giving it name 'gamePGN'
        gamePGN = open(filename)
        #using chess library to read the game
        game = chess.pgn.read_game(gamePGN)
        #initialising a board 
        board = game.board()
        #initialises the fen list
        fenList = []
        #iterates for each move in the games moves
        for move in game.mainline_moves():
            #gets the boards FEN
            boardFEN = board.fen()
            #splits the FEN, and separates into two variables 'boardPosition' and 'boardInfo
            splitFEN = boardFEN.split(' ', 2)
            boardPosition = splitFEN[0]
            #appends to the fen list
            fenList.append(boardPosition)
            #makes the move
            board.push(move)

        self.analysisBoard = AnalysisBoard(fenList)
        #theme of the board
        self.boardTheme = Themes()

        #pygame initialisation
        pygame.init()
        #defining the screen and the background
        self.screen = pygame.display.set_mode((1000, 800))
        self.background = pygame.image.load(os.path.join("Assets/PBackground.png"))
        self.controls = pygame.image.load(os.path.join("Assets/AControls.png"))

        pygame.display.set_caption("Analysis")

    def mainLoop(self):
        #main loop for pygame
        while True:
            #event loop gets user input
            for event in pygame.event.get():

                match event.type:
                    #if the user presses the X in top right
                    case pygame.QUIT:
                        #quits the program
                        sys.exit()
                    case pygame.KEYDOWN:
                        match event.key:
                            #if the user presses escape
                            case pygame.K_ESCAPE:
                                #returns to the main menu
                                return 0 
                            #'A' to play against the AI
                            case pygame.K_a:
                                colourToPlay = 'W' if self.analysisBoard.positionIndex % 2 == 0 else 'b'
                                gameMain('AI', self.analysisBoard.positions[self.analysisBoard.positionIndex%len(self.analysisBoard.positions)], colourToPlay)
                                return 0
                            #'S' to play against self
                            case pygame.K_s:
                                colourToPlay = 'W' if self.analysisBoard.positionIndex % 2 == 0 else 'b'
                                gameMain('', self.analysisBoard.positions[self.analysisBoard.positionIndex%len(self.analysisBoard.positions)], colourToPlay)
                                return 0
                            #lets the user pick another PGN when 'R' pressed
                            case pygame.K_r:
                                self.__init__()
                    case pygame.MOUSEWHEEL:
                        #event.y is the direction of scroll
                        match event.y:
                            #if positive (up)
                            case 1:
                                #progress board
                                self.analysisBoard.updatePos(1)
                            #if negative (down)
                            case -1:
                                #regress board
                                self.analysisBoard.updatePos(-1)       

            self.draw()

    def draw(self):
        ##draw background onto screen
        self.screen.blit(self.background, (0,0))

        #draws the board and the pieces
        self.drawBoard()
        self.drawPieces()

        #draws the controls
        self.screen.blit(self.controls, (785, 100))

        #updates the screen
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
                if self.analysisBoard.viewedPosition[r][c] != '':
                    pieceName = getFileName(self.analysisBoard.viewedPosition[r][c])
                    ##turns this into a file name using an f-string
                    pieceFileName = f'{pieceName}.png'
                    ##load the image from file and then draw it onto the square
                    piece = pygame.image.load(os.path.join(f'Assets/{pieceFileName}'))
                    self.screen.blit(piece, (topLeft[0]+(squareSize*c)+centreValue,topLeft[1]+(squareSize*r)+centreValue))                            

def main():
    main = AnalysisMain()
    main.mainLoop()
    return 0



