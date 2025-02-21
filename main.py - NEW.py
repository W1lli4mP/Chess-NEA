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
    def __init__(self, piece, start, end, captured=None, enPassantTarget=None, special=None):
        self.piece = piece
        self.start = start
        self.end = end
        self.captured = captured
        self.enPassantTarget = enPassantTarget
        self.special = special

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

    def Promote(self, board):
        sprite = pygame.image.load(f"Pieces/{self.colour}q.png")
        sprite = pygame.transform.scale(sprite, (squareSize, squareSize))
        newPiece = Piece(f"{self.colour}q", self.position, sprite)
        board.PlacePiece(newPiece)

class Engine:
    def __init__(self, board):
        self.board = board
    
    def FindKingPosition(self, colour):
        for position, piece in self.board.grid.items():
            if piece and piece.colour == colour and piece.type == "k":
                return position
        return None
    
    def IsAttacking(self, enemyPiece, kingPosition, board):
        return kingPosition in enemyPiece.CalculatePseudoLegalMoves(board)
    
    def IsCheck(self, colour, board):
        enemyColour = "w" if colour == "b" else "b"
        kingPosition = self.FindKingPosition(colour)
        for piece in board.GetPieces(enemyColour):
            if self.IsAttacking(piece, kingPosition, board):
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
            if capturedEnemyPiece:
                board.grid[capturedEnemyPiece.position] = capturedEnemyPiece
            board.enPassantTarget = savedEnPassant
        return legalMoves
    
    def IsCheckmate(self, colour, board):
        if not self.IsCheck(colour, board):
            return False
        for piece in board.GetPieces(colour):
            if self.CalculateLegalMoves(piece, board):
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
        self.moveHistory = []
        self.historyIndex = -1

        self.players = {"w": Human("w"), "b": Human("b")} # CHANGE FOR TESTING
        self.currentTurn = "w"
        self.selectedPiece = None
        self.validMoves = []
        self.offset = offset
        self.timers = {"w": Timer(300), "b": Timer(300)}
        self.running = True
        self.SetupPieces()

    def SetupPieces(self): # sets pieces positions up
        generalOrder = ["r", "n", "b", "q", "k", "b", "n", "r"]
        whitePositions = [(i, 0) for i in range(8)] + [(i, 1) for i in range(8)]

        blackPositions = [(i, 7) for i in range(8)] + [(i, 6) for i in range(8)]

        for position in whitePositions:
            if position[1] == 0:
                piece_type = generalOrder[position[0]]
            else:
                piece_type = "p"
            data = "w" + piece_type
            sprite = pygame.image.load(f'Pieces/{data}.png')
            piece = Piece(data, position, sprite)
            self.board.PlacePiece(piece)

        # Place black pieces
        for position in blackPositions:
            if position[1] == 7:
                piece_type = generalOrder[position[0]]
            else:
                piece_type = "p"
            data = "b" + piece_type
            sprite = pygame.image.load(f'Pieces/{data}.png')
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
        
    def HandleHumanClick(self, position):
        piece = self.board.GetPieceAt(position)
        if self.selectedPiece is None:
            if piece and piece.colour == self.currentTurn:
                self.selectedPiece = piece
                self.validMoves = self.engine.CalculateLegalMoves(piece, self.board)

        else: # deselect after clicking
            if position in self.validMoves:
                self.MakeMove(self.selectedPiece, position)
            self.selectedPiece = None
            self.validMoves = []

    def MakeMove(self, piece, destination):
        start = piece.position
        captured = self.board.GetPieceAt(destination)
        # record move for history
        move = Move(piece, start, destination, captured=captured, enPassantTarget=self.board.enPassantTarget)
        self.moveHistory.append(move)
        self.historyIndex += 1

        # execute the move
        self.board.MovePiece(piece, destination)
        piece.moved = True

        # check for pawn promotion
        if piece.type == "p" and ((piece.colour == "w" and destination[1] == 7) or (piece.colour == "b" and destination[1] == 0)):
            piece.Promote(self.board)

        if piece.type == "k" and abs(start[0] - destination[0]) == 2:
            if destination[0] < start[0]:
                rook = self.board.GetPieceAt((0, start[1]))
                if rook:
                    self.board.MovePiece(rook, (destination[0] + 1, start[1]))
            else:
                rook = self.board.GetPieceAt((7, start[1]))
                if rook:
                    self.board.MovePiece(rook, (destination[0] - 1, start[1]))

        self.currentTurn = "w" if self.currentTurn == "b" else "b"

    def UndoMove(self):
        if self.moveHistory:
            lastMove = self.moveHistory.pop()
            self.historyIndex -= 1
            piece = lastMove.piece
            # undo move: move piece back, restore any captured piece and reset en passant
            self.board.MovePiece(piece, lastMove.start)
            if lastMove.captured:
                self.board.PlacePiece(lastMove.captured)
            self.board.enPassantTarget = lastMove.enPassantTarget
            self.currentTurn = piece.colour

    def RedoMove(self):
        # make a separate redo stack and maintain it
        pass

    def CurrentPlayerIsHuman(self):
        return isinstance(self.players[self.currentTurn], Human)
    
    def Update(self):
        # update timer for current player
        self.timers[self.currentTurn].Update()
        # if its an AI's turn, ask AI to choose an execute a move
        if not self.CurrentPlayerIsHuman():
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

## FLAWS
# king can still castle even when there is an enemy piece supposedly blocking the path