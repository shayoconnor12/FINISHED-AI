from copy import deepcopy

def fenParse(FEN):
        ##split FEN into rows by using split function
        fenParts = FEN.split()
        boardLayout = fenParts[0]
        boardRows = boardLayout.split('/') 

        ##function to expand a fen row into a list representing the row
        def expand(row):
            expandedRow = []
            for char in row:
                if char.isdigit():
                    ##if the character is a digit, then that amount of empty squares is added to the board
                    expandedRow.extend([''] * int(char)) 
                else:
                    ##if its not a digit, then it can be added to the board as is
                    expandedRow.append(char) 
            return expandedRow

        ##call expand() on all rows
        board = [expand(row) for row in boardRows]
        return board

class Board:
    def __init__(self, startingFEN, colour='W'):
        self.fen = startingFEN
        self.startingPos = fenParse(startingFEN)
        self.currentPos = fenParse(startingFEN)
        self.positionLog = [self.fen]
        self.moveLog = []
        self.playerToMove = colour
    
    def makeFullMove(self, move):
        self.moveLog.append(move)

        def makeBasicMove():
            start = move.initial
            target = move.final
            ##moves the piece on the starting position to the target square
            self.currentPos[target[0]][target[1]] = self.currentPos[start[0]][start[1]]
            ##empties the square that the piece came from
            self.currentPos[start[0]][start[1]] = ''


        match move.moveType:
            #normal moves are just made on the board
            case "normal":
                makeBasicMove()

            #en passant moves should delete the pawn from behind the friendly pawn
            case "en passant":

                #The row relative to the player pawn in which the takenD pawn is
                if self.playerToMove == "W":
                    direction = 1
                else:
                    direction = -1

                makeBasicMove()
                targetRow, targetCol = move.final
                #removes the enemy pawn from the board
                self.currentPos[targetRow + direction][targetCol] = ''
            
            #promotion moves should give the user the option of pieces to promote to
            case "promotion":
                queenLetter = "Q" if self.playerToMove == "W" else "q"
                #makes the move on the board
                makeBasicMove()
                targetRow, targetCol = move.final
                #changes the piece at that position to be a queen.
                self.currentPos[targetRow][targetCol] = queenLetter

            #castling moves should move both the king and the rook
            case "castlingK":
                #get the kings coordinates
                kingInitial = move.initial
                #this allows me to find the rook coordinates
                rookInitial = (kingInitial[0], kingInitial[1]+3)
                #instantiate the rook move
                rookMove = Move(rookInitial, (rookInitial[0], rookInitial[1]-2))
                #make the rook move
                self.makeFullMove(rookMove)
                #make the king move
                makeBasicMove()
                self.playerToMove = 'W' if self.playerToMove == 'b' else 'b'
            case "castlingQ":
                #repeat the above, but with different offsets for the rook
                kingInitial = move.initial
                rookInitial = (kingInitial[0], kingInitial[1]-4)
                rookMove = Move(rookInitial, (rookInitial[0], rookInitial[1]+2))
                self.makeFullMove(rookMove)
                makeBasicMove()
                self.playerToMove = 'W' if self.playerToMove == 'b' else 'b'

        self.playerToMove = 'W' if self.playerToMove == 'b' else 'b'
        self.updateFEN()
        self.positionLog.append(self.fen)
    
    def undoMove(self):
        if len(self.positionLog) > 1:
            # Remove the current position from the log
            self.positionLog.pop()
            # Restore the previous position
            self.currentPos = fenParse(self.positionLog[-1])
            # Switch player after undoing a move
            self.playerToMove = 'W' if self.playerToMove == 'b' else 'b'

    def display(self):
        # Printing the column labels
        print("  a b c d e f g h")
        print(" +-----------------+")
        row_number = 8  # Starting from the top of the board which is 8 in chess
        for row in self.currentPos:
            # Creating a string for the row with each piece separated by a space for readability
            row_display = " ".join(piece if piece else '.' for piece in row)
            print(f"{row_number}| {row_display} |")
            row_number -= 1
        print(" +-----------------+")
    
    def isGameOver(self):
        moveGen = MoveGenerator(self)
        allLegalMoves = moveGen.getLegalMoves()
        if len(allLegalMoves) == 0:
            #it is checkmate if the player is in check
            if moveGen.isInCheck(self, self.playerToMove):
                return True, self.playerToMove
            #else it is a stalemate
            else:
                return True, ''
        return False, ''
    
    def updateFEN(self):
        fen = ''
        #converts the board to FEN notation row by row
        for row in self.currentPos:
            emptyCount = 0
            for square in row:
                if square == '':
                    emptyCount += 1
                else:
                    if emptyCount > 0:
                        #if a piece is discovered, a number is added to the FEN, and the empty count is reset.
                        fen += str(emptyCount)
                        emptyCount = 0
                    fen += square
            #for empty squares at end of rows.
            if emptyCount > 0:
                fen += str(emptyCount)
            fen += '/'
        
        #removes the '/' at the end of the FEN.
        fen = fen[:-1]
        self.fen = fen

class Move:
    def __init__(self, initial, final, type="normal"):
        self.initial = initial
        self.final = final
        self.moveType = type
    
def getAllLegalMoves(board):
    moveGen = MoveGenerator(board)
    return moveGen.getLegalMoves()

class MoveGenerator:
    def __init__(self, board):
        ##copies the position of the board into a temporary attribute
        self.board = board
        self.currentPos = board.currentPos
        self.player = board.playerToMove
        self.moveLog = board.moveLog
        self.moves = self.getLegalMoves()

    def isInCheck(self, board, colourToPlay):
        boardPos = board.currentPos
        def getKingPos(pos, colour):
            for row in range(0,8):
                for col in range(0,8):
                    pieceName = pos[row][col]
                    #type of piece irrespective of colour
                    pieceType = pieceName.lower()
                    #kings represented by letter k
                    if pieceType == "k":
                        if (pieceName.isupper() == colour.isupper()):
                            return (row,col)
            return 0
        
        kingPos = getKingPos(boardPos, colourToPlay)
        try:
            kingRow, kingCol = kingPos
        except:
            return False

        #--------------------------------------------------------------
                #CHECKING FOR KNIGHT MOVES
        
        knightOffsets = [
            ( 2, 1), ( 2, -1),
            (-2, 1), (-2, -1),
            ( 1, 2), ( 1, -2),
            (-1, 2), (-1, -2)
        ]
        for offset in knightOffsets:
            #if the square is on the board
            if kingRow+offset[0] in range(0,8) and kingCol+offset[1] in range(0,8):
                offsetSquare = boardPos[kingRow+offset[0]][kingCol+offset[1]]

                #if the square contains a knight of the opposite colour
                if offsetSquare.lower() == 'n':
                    if (offsetSquare.isupper() != colourToPlay.isupper()):
                        #then the king is in check
                        return True
        #--------------------------------------------------------------
                #CHECKING FOR KING MOVES
        
        kingOffsets = [
                ( 1, 1),  ( 1, 0),
                (-1, 1),  (-1, 0),
                ( 1,-1),  ( 0, 1),
                (-1,-1),  ( 0,-1)
        ]
        for offset in kingOffsets:
            #if the square is on the board
            if kingRow+offset[0] in range(0,8) and kingCol+offset[1] in range(0,8):
                offsetSquare = boardPos[kingRow+offset[0]][kingCol+offset[1]]

                #if the square contains a knight of the opposite colour
                if offsetSquare.lower() == 'k':
                    if (offsetSquare.isupper() != colourToPlay.isupper()):
                        #then the king is in check
                        return True
        #----------------------------------------------------------------
                #CHECKING FOR VERTICAL AND HORIZONTAL MOVES
        
        offsets = [(1,0),(0,1),(-1,0),(0,-1)]
        for offset in offsets:
            #define counters for iteration
            searchedRow = kingRow+offset[0]
            searchedCol = kingCol+offset[1]
            #ensures the search does not go off the board
            while searchedRow in range(0,8) and searchedCol in range(0,8):
                offsetSquare = boardPos[searchedRow][searchedCol]

                #if there is a rook or queen of the opposite colour
                
                if (offsetSquare.isupper() != colourToPlay.isupper()):
                    if offsetSquare.lower() == 'r' or offsetSquare.lower() == 'q':
                        #the kings in check
                        return True
                    elif offsetSquare.lower() != '':
                        break
                elif offsetSquare != '':
                    break
                
                #increments with offset
                searchedRow += offset[0]
                searchedCol += offset[1]
                

        
        #----------------------------------------------------------------
                #CHECKING FOR DIAGONAL MOVES
        
        offsets = [(1,1),(-1,1),(1,-1),(-1,-1)]
        for offset in offsets:
            searchedRow = kingRow+offset[0]
            searchedCol = kingCol+offset[1]
            while searchedRow in range(0,8) and searchedCol in range(0,8):
                offsetSquare = boardPos[searchedRow][searchedCol]
                
                if (offsetSquare.isupper() != colourToPlay.isupper()):
                    
                    if offsetSquare.lower() == 'b' or offsetSquare.lower() == 'q':

                        return True
                        
                    #searches for pawn attacks
                    elif offsetSquare.lower() == 'p':
                        #the row offset for an attacking pawn
                        pawnRowOffsets = {
                            'W' : -1,
                            'b' : 1
                        }
                        pawnOffset = pawnRowOffsets[colourToPlay]
                        #if the pawn is one row away in the right direction
                        if searchedRow-kingRow == pawnOffset:
                            #then the kings in check
                            return True
                    
                    elif offsetSquare != '':
                        break
                elif offsetSquare != '':
                    break
                
                searchedRow += offset[0]
                searchedCol += offset[1]

        return False

    def getLegalMoves(self):

        #function to make sure a move is fully legal
        def isLegal(move):
            tempBoard = Board(self.board.fen)
            tempBoard.makeFullMove(move)
            if self.isInCheck(tempBoard, self.player):
                return False
            else:
                return True
        
        #gets all pseudo legal moves
        #a pseudo legal move is one where the piece does not move outside of its range
        #pseudo legal moves allow the user to put their own king in check, so this must be filtered
        pseudoLegalMoves = self.getPseudoLegalMoves()
        legalMoves = []

        #filters all moves that put ones own king in check
        for move in pseudoLegalMoves:
            if isLegal(move):
                legalMoves.append(move)
        
        return legalMoves
    

    def getPseudoLegalMoves(self):

        def getPawnMoves():

            #defines key variables depending on the player colour
            if self.player == "W":
                #pawn moves in negative direction if white
                direction = -1
                enPassantRow = 3
                startingSquare = 6
                enemyPawn = "p"
            else:
                #positive direction if black
                direction = 1
                enPassantRow = 4
                startingSquare = 1
                enemyPawn = "P"


            #list of all pawn moves to be appended to
            pawnMoves = []
            #shortening the name of self.currentPos
            #this will make the code easier to write and read
            pos = self.currentPos

            #iterate through the board to look for pawns
            for row in range(0,8):
                for col in range(0,8):
                    piece = pos[row][col]
                    #the piece is a pawn
                    if piece.upper() == "P":
                        #if the piece is the same colour as the player
                        if (piece.isupper() == self.player.isupper()):
                            
                            newRow = row + direction
                            #handles promotion for all other moves.
                            if newRow in [0,7]:
                                moveType = "promotion"
                            else:
                                moveType = "normal"

                #--------------------------------------------------------
                            #FORWARD MOVES

                            if newRow in range(0,8):
                                #single moves
                                if pos[newRow][col] == '':
                                    pawnMoves.append(Move((row, col), (row + direction, col), moveType))
                                    #double move from starting position
                                    doubleRow = row + (2*direction)
                                    if doubleRow in range(0,8):
                                        #handles promotion for double moves
                                        if row == startingSquare and pos[doubleRow][col] == '':
                                            #appends the move to the move list
                                            pawnMoves.append(Move((row, col), (doubleRow, col), moveType))

                #--------------------------------------------------------
                #--------------------------------------------------------
                            #DIAGONAL MOVES
                                        
                            #makes sure the pawn can't go off the board
                            if newRow in range(0,8):
                                #checks diagonally right
                                if col != 7:
                                    diagonalSquare = pos[row + direction][col + 1]
                                    #if the square on the diagonal is not empty, and is of a different colour to the player
                                    if (diagonalSquare != '') and not (diagonalSquare.isupper() == self.player.isupper()):
                                        pawnMoves.append(Move((row, col), (row + direction, col + 1), moveType))
                                #checks diagonally left
                                if col != 0:
                                    diagonalSquare = pos[row + direction][col - 1]
                                    #if the square on the diagonal is not empty, and is of a different colour to the player
                                    if (diagonalSquare != '') and not (diagonalSquare.isupper() == self.player.isupper()):
                                        pawnMoves.append(Move((row, col), (row + direction, col - 1), moveType))
                #--------------------------------------------------------
                #--------------------------------------------------------
                            #EN PASSANT MOVES
                                        
                            if row == enPassantRow:
                                #gets the previous move
                                if len(self.moveLog) >= 1:
                                    previousMove = self.moveLog[-1]
                                    previousTargetCol = previousMove.final[1]
                                    if abs(previousTargetCol - col) == 1:
                                        #if the piece moved 2 squares
                                        if abs(previousMove.final[0] - previousMove.initial[0]) == 2:
                                            #and the piece is a pawn
                                            if pos[previousMove.final[0]][previousTargetCol] == enemyPawn:
                                                #appends an en passant move
                                                pawnMoves.append(Move((row, col), (newRow, previousTargetCol), "en passant"))
                #--------------------------------------------------------          
            
            return pawnMoves
                        
            

        
        def getSlidingMoves():

            slidingMoves = []
            #the current board position
            pos = self.currentPos
            slidingPieces = ["b", "r", "q"]

            #stores the pieceOffsets for rooks, bishops and queens
            pieceOffsets = {
                #rook offsets 
                'r' : [(1,0),(0,1),(-1,0),(0,-1)],

                #bishop offsets
                'b' : [(1,1),(-1,1),(1,-1),(-1,-1)],

                #queen offsets 
                #these are identical to the rook offsets + bishop offsets
                'q' : [(1,0),(0,1),(-1,0),(0,-1),
                      (1,1),(-1,1),(1,-1),(-1,-1)]
            }
            #iterate through the board
            for row in range(0,8):
                for col in range(0,8):
                    #if the piece in the position is a sliding piece
                    pieceName = pos[row][col]
                    #type of piece irrespective of colour
                    pieceType = pieceName.lower()
                    if pieceType in slidingPieces:
                        #and is of the same colour as the player
                        if (pieceName.isupper() == self.player.isupper()):
                            ##GENERATE MOVES

                            #gets all of the increment directions for a piece
                            pieceIncrements = pieceOffsets[pieceType]
                            #iterates through these offsets
                            for incr in pieceIncrements:
                                #splits an increment into its row and column increment
                                rowIncr = incr[0]
                                colIncr = incr[1]

                                #defines a possible move row and column
                                possibleMoveRow = row + rowIncr
                                possibleMoveCol = col + colIncr

                                #boolean describes if the square is on the board
                                pieceOnBoard = True
                                while pieceOnBoard:
                                    #if else validates that the piece is on the board, before making a move
                                    if possibleMoveRow in range(0,8) and possibleMoveCol in range(0,8):
                                        #gets the initial and final square for a possible move
                                        initialSquare = (row, col)
                                        finalSquare = (possibleMoveRow, possibleMoveCol)

                                        #the move type for a sliding move is always normal.
                                        #castling will be done using the king
                                        possibleMove = Move(initialSquare, finalSquare, "normal")
                                        targetSquare = pos[possibleMoveRow][possibleMoveCol]

                                        #if a square is empty, a move is made and the loop continues
                                        if targetSquare == '':
                                            slidingMoves.append(possibleMove)

                                        #if a square has an enemy piece, the move is made and the loop is broken
                                        elif (targetSquare.isupper() != self.player.isupper()):
                                            slidingMoves.append(possibleMove)
                                            break

                                        #if a square has a friendly piece, the move is not made, and the loop is broken
                                        elif (targetSquare.isupper() == self.player.isupper()):
                                            break

                                        possibleMoveRow += rowIncr
                                        possibleMoveCol += colIncr


                                    else:
                                        pieceOnBoard = False

            return slidingMoves

        def getKnightMoves():
            #list of all knight moves
            knightMoves = []
            #renaming the current pos
            pos = self.currentPos
            
            #knight move offsets:
            offsets = [
                ( 2, 1), ( 2, -1),
                (-2, 1), (-2, -1),
                ( 1, 2), ( 1, -2),
                (-1, 2), (-1, -2)
            ]

            #iterate through the board
            for row in range(0,8):
                for col in range(0,8):
                    pieceName = pos[row][col]
                    #type of piece irrespective of colour
                    pieceType = pieceName.lower()
                    #knights represented by letter n
                    if pieceType == "n":
                        #if the knight is the same colour as the player
                        if (pieceName.isupper() == self.player.isupper()):
                            #loop through 8 squares
                            for offset in offsets:
                                #define potential coordinates
                                potentialMoveRow = row + offset[0]
                                potentialMoveCol = col + offset[1]

                                initial = (row, col)
                                target = (potentialMoveRow, potentialMoveCol)
                                #validation for move
                                if potentialMoveRow in range(0,8) and potentialMoveCol in range(0,8):
                                    targetPiece = pos[potentialMoveRow][potentialMoveCol]
                                    if (targetPiece.isupper() != self.player.isupper()) or targetPiece == '':
                                        #add the move
                                        move = Move(initial, target, "normal")
                                        knightMoves.append(move)
            
            return knightMoves

        def getKingMoves():

            def getCastleMoves(pos):
                #will return all castle moves
                castleMoves = []
                isWhite = self.player.isupper()

                kingSideCastle = False
                queenSideCastle = False

                if isWhite:
                    #get the coordinates for the white king
                    kingCoords = (7,4)
                    #white kings rook
                    kingRookCoords = (7,7)
                    #white queens rook
                    queenRookCoords = (7,0) 
                else:
                    #repeat for black
                    kingCoords = (0,4)
                    kingRookCoords = (0,7)
                    queenRookCoords = (0,0)

                #determine if castling is legal
                if pos[kingCoords[0]][kingCoords[1]] == "K":
                        #king side
                        if pos[kingRookCoords[0]][kingRookCoords[1]] == "R":
                            kingSideCastle = True
                        #queen side
                        if pos[queenRookCoords[0]][queenRookCoords[1]] == "R":
                            queenSideCastle = True

                if kingSideCastle:
                    #searches the squares between the king and rook
                    for col in range(kingCoords[1]+1, kingRookCoords[1]):
                        if pos[kingCoords[0]][col] != '':
                            #if there is an unempty square, then castling is unallowed.
                            kingSideCastle = False
                    
                    if kingSideCastle:
                        #defines the move as a king side castle
                        move = Move(kingCoords, (kingRookCoords[0],kingRookCoords[1]-1), "castlingK")
                        #appends the move
                        castleMoves.append(move)
                    
                if queenSideCastle:
                    #searches the squares between the king and rook
                    for col in range(queenRookCoords[1]+1, kingCoords[1]):
                        if pos[kingCoords[0]][col] != '':
                            #if there is an unempty square, then castling is unallowed.
                            queenSideCastle = False
                    
                    if queenSideCastle:
                        #defines the move as a queen side castle
                        move = Move(kingCoords, (queenRookCoords[0],queenRookCoords[1]+1), "castlingQ")
                        #appends the move
                        castleMoves.append(move)
                
                return castleMoves


            #list of all king moves
            kingMoves = []
            #renaming the current pos
            pos = self.currentPos
            
            #king move offsets:
            offsets = [
                ( 1, 1),  ( 1, 0),
                (-1, 1),  (-1, 0),
                ( 1,-1),  ( 0, 1),
                (-1,-1),  ( 0,-1)
            ]

            #iterate through the board
            for row in range(0,8):
                for col in range(0,8):
                    pieceName = pos[row][col]
                    #type of piece irrespective of colour
                    pieceType = pieceName.lower()
                    #kings represented by letter k
                    if pieceType == "k":
                        #if the kings is the same colour as the player
                        if (pieceName.isupper() == self.player.isupper()):
                            #loop through 8 squares
                            for offset in offsets:
                                #define potential coordinates
                                potentialMoveRow = row + offset[0]
                                potentialMoveCol = col + offset[1]

                                initial = (row, col)
                                target = (potentialMoveRow, potentialMoveCol)
                                #validation for move
                                if potentialMoveRow in range(0,8) and potentialMoveCol in range(0,8):
                                    targetPiece = pos[potentialMoveRow][potentialMoveCol]
                                    if (targetPiece.isupper() != self.player.isupper()) or targetPiece == '':
                                        #add the move
                                        move = Move(initial, target, "normal")
                                        kingMoves.append(move)
            
            return kingMoves + getCastleMoves(pos)
        
        pseudoLegalMoves = getPawnMoves() + getSlidingMoves() + getKnightMoves() + getKingMoves()
        return pseudoLegalMoves
        




        