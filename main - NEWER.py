import pygame
import random

pygame.init()

# CONSTANTS AND HELPER FUNCTIONS
squareSize = 100
boardSize = 8
offset = (300, 100)

def ScreenToBoard(position, offset):
    boardX = (position[0] - offset[0]) // squareSize
    boardY = 7 - ((position[1] - offset[1]) // squareSize)
    return (boardX, boardY)

def BoardToScreen(position, offset):
    screenX = position[0] * squareSize + offset[0]
    screenY = offset[1] + (7 - position[1]) * squareSize
    return (screenX, screenY)

class Move:
    def __init__(self, startSquare, endSquare, board):
        self.startRow, self.startCol = startSquare
        self.endRow, self.endCol = endSquare
        self.pieceMoved = board.GetPieceAt(startSquare)
        self.pieceCaptured = board.GetPieceAt(endSquare)
        self.oldEnPassantTarget = board.enPassantTarget # save to restore later

        # need to determine captured piece for en passant (the captured pawn is NOT on the end square)
        self.isEnPassant = False
        if self.pieceMoved and self.pieceMoved.type == "p" and endSquare == board.enPassantTarget: # conditions for detecting en passant
            self.isEnPassant = True
            direction = 1 if self.pieceMoved.colour == "w" else -1 # inverse directions relative to colour
            capturedPosition = (endSquare[0], endSquare[1] - direction)
            self.pieceCaptured = board.GetPieceAt(capturedPosition)
        else: # if theres no en passant just log the enemy piece on the destination/end square
            self.pieceCaptured = board.GetPieceAt(endSquare)

        # check for castling
        self.isCastling = False
        self.rookStart = None # determines start pos of rook
        self.rookEnd = None # determines end pos of rook
        if self.pieceMoved and self.pieceMoved.type == "k" and abs(startSquare[0] - endSquare[0]) == 2: # conditions for detecting castling move
            self.isCastling = True
            # IF QUEENSIDE CASTLE
            if endSquare[0] < startSquare[0]: # consider x-axis to determine what rook should be moved
                self.rookStart = (0, startSquare[1]) # rook starts at x = 0 or x = 7
                self.rookEnd = (endSquare[0] + 1, startSquare[1])
            # IF KINGSIDE CASTLE
            else:
                self.rookStart = (7, startSquare[1])
                self.rookEnd = (endSquare[0] - 1, startSquare[1])

        # flag for pawn promotion
        self.promoted = False

class Timer:
    def __init__(self, timeSeconds):
        self.remaining = timeSeconds
        self.lastTick = pygame.time.get_ticks()

    def Update(self):
        now = pygame.time.get_ticks()
        delta = (now - self.lastTick) / 1000.0
        self.remaining -= delta
        self.lastTick = now

    def Reset(self, timeSeconds):
        self.remaining = timeSeconds
        self.lastTick = pygame.time.get_ticks()

    def GetTime(self):
        return max(0, self.remaining)
    
class Board:
    def __init__(self, screen, squareSize=squareSize):
        self.screen = screen
        self.squareSize = squareSize
        self.grid = {(x, y): None for x in range(boardSize) for y in range(boardSize)}
        self.enPassantTarget = None

    def Draw(self, offset=offset):
        offsetX, offsetY = offset
        for i in range(boardSize):
            for j in range(boardSize):
                colour = "#CDDBE1" if (i + j) % 2 == 0 else "#386F88"
                rect = (offsetX + i * self.squareSize,
                        offsetY + (boardSize - 1 - j) * self.squareSize,
                        self.squareSize, self.squareSize)
                pygame.draw.rect(self.screen, colour, rect)

    def PlacePiece(self, piece):
        self.grid[piece.position] = piece

    def MovePiece(self, piece, newPosition):
        oldPosition = piece.position
        
        # en passant
        if piece.type == "p" and newPosition == self.enPassantTarget:
            direction = 1 if piece.colour == "w" else -1
            captured_pos = (newPosition[0], newPosition[1] - direction)
            captured = self.GetPieceAt(captured_pos)
            if captured and captured.type == "p":
                self.RemovePiece(captured)
        self.grid[oldPosition] = None
        piece.position = newPosition
        self.grid[newPosition] = piece

        # reset en passant target then set it for double pawn moves
        self.enPassantTarget = None
        if piece.type == "p" and abs(newPosition[1] - oldPosition[1]) == 2:
            self.enPassantTarget = (newPosition[0], (newPosition[1] + oldPosition[1]) // 2)
    
    def RemovePiece(self, piece):
        self.grid[piece.position] = None

    def GetPieceAt(self, position):
        return self.grid.get(position)
    
    def GetPieces(self, colour):
        return [p for p in self.grid.values() if p is not None and p.colour == colour]
    
class Piece:
    def __init__(self, data, position, sprite):
        self.colour = data[0]
        self.type = data[1]
        self.position = position
        self.sprite = pygame.transform.scale(sprite, (squareSize, squareSize))
        self.moved = False
        self.castled = False

    def Render(self, screen, offset=offset):
        position = BoardToScreen(self.position, offset)
        screen.blit(self.sprite, position)

    def CalculatePseudoLegalMoves(self, board):
        x, y = self.position
        moves = []
        if self.type == "p":
            direction = 1 if self.colour == "w" else -1
            forward = (x, y + direction)
            if board.GetPieceAt(forward) is None:
                moves.append(forward)
                # double pawn move
                if not self.moved:
                    doubleForward = (x, y + 2 * direction)
                    if board.GetPieceAt(doubleForward) is None:
                        moves.append(doubleForward)

            enemyPiece = board.GetPieceAt((x - 1, y + direction)) # left
            capturePosition = (x - 1, y + direction)
            if (enemyPiece is not None and enemyPiece.colour != self.colour) or (capturePosition == board.enPassantTarget):
                moves.append((x - 1, y + direction))
            
            enemyPiece = board.GetPieceAt((x + 1, y + direction)) # right
            capturePosition = (x + 1, y + direction)
            if enemyPiece is not None and enemyPiece.colour != self.colour or (capturePosition == board.enPassantTarget):
                moves.append((x + 1, y + direction))

        if self.type == "k":
            directions = [(x, y + 1), (x + 1, y + 1), (x + 1, y), (x + 1, y - 1),
                    (x, y - 1), (x - 1, y - 1), (x - 1, y), (x - 1, y + 1)]

            for d in directions:
                if board.GetPieceAt(d) == None or board.GetPieceAt(d).colour != self.colour: # if square empty or has enemy piece
                    moves.append(d)

            # Castling logic
            if not self.moved: # if king hasnt moved
                # left
                left = []
                invalid = False
                for i in range(1, 5): # must start at 1
                    if i != 4 and board.GetPieceAt((x - i, y)) is not None: # check if we are on last increment - we want the rook to be there
                        invalid = True
                        break
                    left.append(board.GetPieceAt((x - i, y)))

                if not invalid and left[-1] is not None:
                    if left[-1].type == "r" and not left[-1].moved: # left[-1] is the rook; rook is always last
                        moves.append((x - 2, y))
                
                # right
                right = []
                invalid = False
                for i in range(1, 4):
                    if i != 3 and board.GetPieceAt((x + i, y)) is not None:
                        invalid = True
                        break
                    right.append(board.GetPieceAt((x + i, y)))
                if not invalid and right[-1] is not None:
                    if right[-1].type == "r" and not right[-1].moved: # right[-1] is the rook; rook is always last
                        moves.append((x + 2, y))

        if self.type == "n":
            directions = [(x - 1, y + 2), (x + 1, y + 2), (x - 1, y - 2), (x + 1, y - 2),
                (x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1)]

            for d in directions:
                if board.GetPieceAt(d) == None or board.GetPieceAt(d).colour != self.colour:
                    moves.append(d)

        if self.type == "r":
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            moves.extend(self.SlidingMoves(board, x, y, directions))

        if self.type == "b":
            directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
            
            moves.extend(self.SlidingMoves(board, x, y, directions))

        if self.type == "q":
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                          (1, 1), (-1, 1), (1, -1), (-1, -1)]

            moves.extend(self.SlidingMoves(board, x, y, directions))

        return [move for move in moves if 0 <= move[0] < 8 and 0 <= move[1] < 8] # filter valid board positions based on limited range

    def SlidingMoves(self, board, x, y, directions):
        moves = []
        for dx, dy in directions:
            for i in range(1, boardSize):
                newPos = (x + dx * i, y + dy * i)
                if not (0 <= newPos[0] < boardSize and 0 <= newPos[1] < boardSize):
                    break
                occupant = board.GetPieceAt(newPos)
                if occupant is None:
                    moves.append(newPos)
                elif occupant.colour != self.colour:
                    moves.append(newPos)
                    break
                else:
                    break
        return moves

    def Promote(self, board): # only limited to queen for simulation simplicity + cba
        self.type = "q" # change to queen
        sprite = pygame.image.load(f"Pieces/{self.colour}q.png").convert_alpha() # setup queen sprite
        self.sprite = pygame.transform.scale(sprite, (squareSize, squareSize))

class Engine:
    def __init__(self, board):
        self.board = board
    
    def FindKingPosition(self, colour, board):
        for position, piece in board.grid.items():
            if piece and piece.colour == colour and piece.type == "k":
                return position
        return None
    
    def IsAttacking(self, enemyPiece, kingPosition, board):
        return kingPosition in enemyPiece.CalculatePseudoLegalMoves(board)
    
    def GetAllPieces(self, board, colour):
        pieces = []
        for piece in board.grid.values():
            if piece is not None and piece.colour == colour:
                pieces.append(piece)
        return pieces

    def IsCheck(self, colour, board):
        enemyColour = "w" if colour == "b" else "b"
        kingPosition = self.FindKingPosition(colour, board)
        for piece in board.GetPieces(enemyColour):
            if kingPosition in piece.CalculatePseudoLegalMoves(board): # if king attacked by enemy
                return True
        return False
    
    def IsSquareAttacked(self, position, enemyColour, board): # different board state
        for piece in board.GetPieces(enemyColour):
            if position in piece.CalculatePseudoLegalMoves(board):
                return True
        return False

    def CalculateLegalMoves(self, piece, board):
        pseudoMoves = piece.CalculatePseudoLegalMoves(board)
        legalMoves = []
        savedEnPassant = board.enPassantTarget
        enemyColour = "w" if piece.colour == "b" else "b"

        for move in pseudoMoves:
            # extra check for castling moves - king moving 2 squares to the left/right
            # determine the square the king crosses (sequentially?)
            if piece.type == "k" and abs(piece.position[0] - move[0]) == 2: # only need to observe the x-axis, this could be -2, use abs()
                if self.IsCheck(piece.colour, board): # king cannot castle if in check
                    continue
                if move[0] > piece.position[0]:
                    intermediate = (piece.position[0] + 1, piece.position[1]) # intermediate square (in between) depending on the direction of the castle
                else:
                    intermediate = (piece.position[0] - 1, piece.position[1])
                if self.IsSquareAttacked(intermediate, enemyColour, board):
                    continue

            originalPosition = piece.position
            captured = board.GetPieceAt(move)
            capturedEnemyPiece = None

            if piece.type == "p" and move == board.enPassantTarget:
                direction = 1 if piece.colour == "w" else -1
                capturedPosition = (move[0], move[1] - direction)
                capturedEnemyPiece = board.GetPieceAt(capturedPosition)
            board.MovePiece(piece, move)
            if not self.IsCheck(piece.colour, board):
                legalMoves.append(move)

            # undo move
            board.MovePiece(piece, originalPosition)
            board.grid[move] = captured
            if capturedEnemyPiece: # if theres a captured enemy piece
                board.grid[capturedEnemyPiece.position] = capturedEnemyPiece
            board.enPassantTarget = savedEnPassant
        return legalMoves
    
    def IsCheckmate(self, colour, board):
        if not self.IsCheck(colour, board):
            return False
        for piece in self.GetAllPieces(board, colour):
            if self.CalculateLegalMoves(piece, board): # if theres a move
                return False
        return True

class Player:
    def __init__(self, colour):
        self.colour = colour

class Human(Player):
    def __init__(self, colour):
        super().__init__(colour)
    # human input handled by game loop

class AI(Player):
    def __init__(self, colour):
        super().__init__(colour)

    def ChooseMove(self, game):
        # basic AI
        moves = []
        for piece in game.board.GetPieces(self.colour):
            legalMoves = game.engine.CalculateLegalMoves(piece, game.board)
            for destination in legalMoves:
                moves.append((piece, destination))
        if moves:
            return random.choice(moves)
        return None
    
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board(screen, squareSize)
        self.engine = Engine(self.board)
        self.moveLog = []
        self.historyIndex = -1

        self.players = {"w": Human("w"), "b": AI("b")} # CHANGE FOR TESTING
        self.currentTurn = "w"
        self.selectedPiece = None
        self.validMoves = []
        self.offset = offset
        self.timers = {"w": Timer(300), "b": Timer(300)}
        self.running = True
        self.SetupPieces()

        self.disableAI = False
        self.gameOver = False

    def SetupPieces(self): # sets pieces positions up
        generalOrder = ["r", "n", "b", "q", "k", "b", "n", "r"]
        whitePositions = [(i, 0) for i in range(8)] + [(i, 1) for i in range(8)]
        blackPositions = [(i, 7) for i in range(8)] + [(i, 6) for i in range(8)]

        for position in whitePositions:
            if position[1] == 0:
                pieceType = generalOrder[position[0]]
            else:
                pieceType = "p"
            data = "w" + pieceType
            sprite = pygame.image.load(f'Pieces/{data}.png').convert_alpha() # images have transparency so converting to alpha is more optimal for blitting
            piece = Piece(data, position, sprite)
            self.board.PlacePiece(piece)

        # Place black pieces
        for position in blackPositions:
            if position[1] == 7:
                pieceType = generalOrder[position[0]]
            else:
                pieceType = "p"
            data = "b" + pieceType
            sprite = pygame.image.load(f'Pieces/{data}.png').convert_alpha()
            piece = Piece(data, position, sprite)
            self.board.PlacePiece(piece)

    def HandleEvents(self): # exit button, LMB, arrow keys pressed?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # only handle mouse clicks if it is a human player's turn
            if self.CurrentPlayerIsHuman():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    position = ScreenToBoard(event.pos, self.offset)
                    self.HandleHumanClick(position)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.UndoMove()
                if event.key == pygame.K_RIGHT:
                    self.RedoMove()
        
    def HandleHumanClick(self, position): # handles selecting/deselecting pieces
        piece = self.board.GetPieceAt(position)
        if self.selectedPiece is None:
            if piece and piece.colour == self.currentTurn:
                self.selectedPiece = piece
                self.validMoves = self.engine.CalculateLegalMoves(piece, self.board)
                self.disableAI = False

        else: # deselect after clicking
            if position in self.validMoves:
                self.MakeMove(self.selectedPiece, position)
            self.selectedPiece = None
            self.validMoves = []

    def MakeMove(self, piece, destination): # logs moves that are made
        # IF MOVES WERE UNDONE BEFORE, DISCARD THE "REDO" MOVES
        if self.historyIndex < len(self.moveLog) - 1:
            self.moveLog = self.moveLog[:self.historyIndex + 1]

        startSquare = piece.position
        # record move for history
        move = Move(startSquare, destination, self.board)
        self.moveLog.append(move)
        self.historyIndex += 1

        # execute the move
        self.board.MovePiece(piece, destination)
        piece.moved = True

        # check for castling
        if move.isCastling:
            rook = self.board.GetPieceAt(move.rookStart)
            if rook:
                self.board.MovePiece(rook, move.rookEnd)
                rook.moved = True

        # check for pawn promotion
        if piece.type == "p" and ((piece.colour == "w" and destination[1] == 7) or (piece.colour == "b" and destination[1] == 0)):
            piece.Promote(self.board)
            move.promoted = True

        self.currentTurn = "w" if self.currentTurn == "b" else "b"

    def UndoMove(self):
        if self.historyIndex >= 0: # if the move log is not empty, then theres no move to undo duhh
            move = self.moveLog[self.historyIndex]
            piece = move.pieceMoved

            # move the piece back
            self.board.grid[(move.endRow, move.endCol)] = None
            piece.position = (move.startRow, move.startCol)
            self.board.grid[(move.startRow, move.startCol)] = piece
            piece.moved = False

            if move.promoted:
                piece.type = "p"
                sprite = pygame.image.load(f"Pieces/{piece.colour}p.png").convert_alpha()
                piece.sprite = pygame.transform.scale(sprite, (squareSize, squareSize))

            # restore captured piece
            if move.pieceCaptured is not None:
                if move.isEnPassant:
                    direction = 1 if piece.colour == "w" else -1
                    capturedPosition = (move.endRow, move.endCol - direction)
                else:
                    capturedPosition = (move.endRow, move.endCol)
                move.pieceCaptured.position = capturedPosition
                self.board.grid[capturedPosition] = move.pieceCaptured

            # undo castling
            if move.isCastling:
                rook = self.board.GetPieceAt(move.rookEnd)
                if rook:
                    self.board.grid[move.rookEnd] = None
                    rook.position = move.rookStart
                    self.board.grid[move.rookStart] = rook
                    rook.moved = False

            # restore en passant target
            self.board.enPassantTarget = move.oldEnPassantTarget

            # revert the turn
            self.currentTurn = "w" if self.currentTurn == "b" else "b"
            self.historyIndex -= 1

            # clear selection
            self.selectedPiece = None
            self.validMoves = []

            # disable AI
            self.disableAI = True

    def RedoMove(self):
        if self.historyIndex < len(self.moveLog) - 1:
            self.historyIndex += 1
            move = self.moveLog[self.historyIndex]
            piece = move.pieceMoved

            if move.pieceCaptured is not None and move.isEnPassant:
                self.board.grid[(move.endRow, move.endCol)] = None

            # move capturing piece forward
            self.board.grid[(move.startRow, move.startCol)] = None
            piece.position = (move.endRow, move.endCol)
            self.board.grid[(move.endRow, move.endCol)] = piece
            piece.moved = True

            # for en passant, removed captured pawn
            if move.pieceCaptured is not None and move.isEnPassant:
                direction = 1 if piece.colour == "w" else -1
                capturedPosition = (move.endRow, move.endCol - direction)
                self.board.grid[capturedPosition] = None

            # redo castling - move rook
            if move.isCastling:
                rook = self.board.GetPieceAt(move.rookStart)
                if rook:
                    self.board.grid[move.rookStart] = None
                    rook.position = move.rookEnd
                    self.board.grid[move.rookEnd] = rook
                    rook.moved = True

            # redo pawn promotion
            if move.promoted:
                piece.Promote(self.board)

            # update en passant target if needed
            self.board.enPassantTarget = None
            if piece.type == "p" and abs(move.endRow - move.startRow) == 2:
                self.board.enPassantTarget = (move.endRow, (move.endRow + move.startRow) // 2)

            # update turn
            self.currentTurn = "w" if self.currentTurn == "b" else "b"

            # clear selection
            self.selectedPiece = None
            self.validMoves = []

            # disable AI
            self.disableAI = True

    def CurrentPlayerIsHuman(self):
        return isinstance(self.players[self.currentTurn], Human)
    
    def Update(self):
        # update timer for current player
        self.timers[self.currentTurn].Update()
        # if its an AI's turn, ask AI to choose an execute a move
        if self.engine.IsCheckmate(self.currentTurn, self.board):
            print("CHECKMATE DETECTED")
            self.gameOver = True # instead of self.running = False
        else:
            if not self.disableAI and not self.CurrentPlayerIsHuman():
                AIMove = self.players[self.currentTurn].ChooseMove(self)
                if AIMove:
                    piece, move = AIMove
                    self.MakeMove(piece, move)

    def Render(self):
        self.screen.fill("#04202F")
        self.board.Draw(self.offset)
        # render all pieces
        for piece in self.board.grid.values():
            if piece:
                piece.Render(self.screen, self.offset)
        # move highlighting
        if self.selectedPiece:
            position = BoardToScreen(self.selectedPiece.position, self.offset)
            pygame.draw.rect(self.screen, "red", (position[0], position[1], squareSize, squareSize), 2)
        
        for move in self.validMoves:
            position = BoardToScreen(move, self.offset)
            pygame.draw.rect(self.screen, "green", (position[0], position[1], squareSize, squareSize), 2)

        # game over rendering
        if self.gameOver: # temp message
            font = pygame.font.SysFont("Arial", 50)
            text = font.render("Checkmate!", True, (255, 255, 255))
            self.screen.blit(text, (self.offset[0], self.offset[1] - 60))

        ## ADD INTERFACE RENDERING HERE + TIMERS
        pygame.display.flip()

def main():
    screen = pygame.display.set_mode((1400, 1000))
    pygame.display.set_caption("notchess.com")
    clock = pygame.time.Clock()
    game = Game(screen)

    while game.running:
        game.HandleEvents()
        game.Update()
        game.Render()
        clock.tick(60)
    pygame.quit()

main()

## A-Level Data Stuctures
# USED:
# 1) Dictionaries (Hash Tables)
# the board is a dictionary
# 2) Lists (Dynamic Arrays)
# moveLog is a list that stores all moves
# validMoves and products of GetPieces() are also lists
# 3) Stacks
# Undo() and Redo() act as a stack
# 4) Linear Search
# iterating through lists (scanning move log amd valid moves)

# COULD BE USED:


# 1) Trees
# move/game tree, node - board state, branch - possible move
# minimax searched through this
# 2) Binary Search/Sorting
# sort a list of moves and even binary search when evaluating with piece values for the AI

## FLAWS
# no redo
# added Redo() and updated Move class, changing MakeMove() and Undo()
# when against AI, Undo() and Redo() are useless
# disableAI flag
# program is forced to close when checkmate occurs
# gameOver flag
# when undoing, human player can select a piece in the past then when redoing/undoing to another position, the valid moves from the initial selected piece
# are still applied, meaning illegal moves can be made
# fixed by clearing the selection at the end of Undo() and Redo()