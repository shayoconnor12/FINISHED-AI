import Source.const as const
import Source.chessLogic as chessLogic
import time
from copy import deepcopy

class ChessAI:
    def __init__(self, board, colourToMove):
        #board position on which the move will be generated
        self.board = board
        #the player for which a move will be generated
        self.colourToMove = colourToMove
        self.CHECKMATE = 100000
        self.STALEMATE = 0
        self.DEPTH = 2
        self.evalValue = self.evaluationFunction(self.board)

    
    #heuristic that describes whos winning
    def evaluationFunction(self, board):
        boardStaticEval = 0
        boardPosition = board.currentPos

        def pieceValueTotal():
            #the total value of all white pieces + black pieces
            #default value is 0
            summedBoardValue = 0

            #the objective value of each piece, irrespective of position
            objectivePieceValues = {
                "K": 20000,
                "Q": 900, 
                "R": 500, 
                "B": 330, 
                "N": 320, 
                "P": 100
            }

            #iterate through the board
            for row in range(0,8):
                for col in range(0,8):
                    searchedSquare = boardPosition[row][col]
                    #if there is a piece
                    if searchedSquare != '':
                        #get the objective piece value by type
                        pieceType = searchedSquare.upper()
                        objPieceVal = objectivePieceValues[pieceType]
                        if searchedSquare.isupper():
                            #gets the piece square table bonus
                            piecePositionBonus = const.positionPieceValues[pieceType][row][col]
                            #adds to the summed board value
                            summedBoardValue += (objPieceVal+piecePositionBonus)
                        else:
                            #reverses the piece square table if the piece is black
                            piecePositionBonus = const.positionPieceValues[pieceType][::-1][row][col]
                            #subtracts from the summed board value
                            summedBoardValue -= (objPieceVal+piecePositionBonus)
                        

            return summedBoardValue
        
        def pawnStructureTotal():
            doubledPawnValue = 0
            emptyFileCount = 0
            #generator to rotate the board -90 degrees
            #done so I can iterate through each column
            rotatedBoard = list(zip(*boardPosition))
            
            #counts double pawns
            for col in rotatedBoard:
                #gets number of pawns of each colour for each row
                whitePawnCount = col.count('P')
                blackPawnCount = col.count('p')
                #white 
                match whitePawnCount:
                    case 0:
                        emptyFileCount -= 100
                    case _:
                        doubledPawnValue -= (whitePawnCount - 1)*100
                #black 
                match blackPawnCount:
                    case 0:
                        emptyFileCount += 100
                    case _:
                        doubledPawnValue += (blackPawnCount - 1)*100

            return doubledPawnValue + emptyFileCount
        
        def kingSafetyTotal():
            kingSafetyValue = 0
            #iterates through board
            for row in range(0,8):
                for col in range(0,8):
                    #checks if the searched square is any colour of king
                    searchedSquare = boardPosition[row][col]
                    if searchedSquare.lower() == 'k':
                        #iterates through 3 squares in front of kig
                        for square in range(-1,2):
                            #value sign will be negative for black, positive for white
                            front = 1 if searchedSquare.islower() else -1
                            valueSign = -1 if searchedSquare.islower() else 1
                            guardRow = row+front
                            guardCol = col+square
                            if guardRow in range(0,8) and guardCol in range(0,8):
                                guardingSquare = boardPosition[row+front][col+square]
                                if guardingSquare != '':
                                    if guardingSquare.isupper() == searchedSquare.isupper():
                                        #adds value if theres a friendly guarding piece
                                        kingSafetyValue += 100*valueSign
                                else:
                                    #deducts value if the square is empty
                                    kingSafetyValue -= 30*valueSign

            return kingSafetyValue
        #coefficients for the evaluation totals
        #pieceValues are given highest priority.
        a,b,c = 1,0.1,0.1

        #board eval is calculated and returned.
        boardStaticEval = 0.01*a*pieceValueTotal()
        isGameOver = board.isGameOver()
        
        if isGameOver[0]:
            #black wins
            match isGameOver[1]:
                case 'W':
                    return -self.CHECKMATE
                case 'b':
                    #white wins
                    return self.CHECKMATE
                case '':
                    return self.STALEMATE
        
        return boardStaticEval


    #searches at a depth, using minimax and alpha beta
    def search(self, board, depth, alpha, beta, colourMultiplier):
        #base case for recursive routine
        #if the depth has reached the end, or the game is over
        if depth == 0 or board.isGameOver()[0]:
            #returns the evaluation of the board 
            return colourMultiplier * self.evaluationFunction(board)

        #arbitrarily small number, will never be exceeded in magnitude by evaluation function
        maxScore = float("-inf")
        #gets all of the legal moves for the searched node
        legalMoves = chessLogic.getAllLegalMoves(board)

        #for each move in the legally generated moves
        for move in legalMoves:

            #makes a move, recurses, and then undoes the move
            board.makeFullMove(move)
            score = -self.search(board, depth - 1, -beta, -alpha, -colourMultiplier)
            board.undoMove()

            #updates max score
            maxScore = max(maxScore, score)
            #updates alpha, to cut off unnecessary nodes in the tree
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return maxScore

    def getBestMove(self, board, legalMoves):
        #initially the best move is None
        bestMove = None
        #arbitrarily large numbers 
        maxScore = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        #colour multiplier is 1 for white, and -1 for black. This is applied to the evaluation function
        colourMultiplier = 1 if board.playerToMove == 'W' else -1
        #for each legal move
        for move in legalMoves:
            #makes the move, then finds the max score in the position, and then undoes the move
            tempBoard = deepcopy(board)
            board.makeFullMove(move)
            score = -self.search(board, self.DEPTH - 1, -beta, -alpha, -colourMultiplier)
            board = deepcopy(tempBoard)
            #iteratively finds the best move, by comparing the actual scores to the max score.
            if score > maxScore:
                maxScore = score
                bestMove = move
            alpha = max(alpha, score)

        #returns the best move
        return bestMove
