import pygame
import random
import copy
from heapq import heappush, heappop

pygame.init()

# GLOBAL CONSTANTS AND HELPER FUNCTIONS
squareSize = 100
boardSize = 8
offset = (300, 100)
alphabet = "abcdefgh" # for board coord rendering
width, height = (1400, 1000)


def ScreenToBoard(position, offset):
    boardX = (position[0] - offset[0]) // squareSize
    boardY = 7 - ((position[1] - offset[1]) // squareSize)
    return (boardX, boardY)

def BoardToScreen(position, offset):
    screenX = position[0] * squareSize + offset[0]
    screenY = offset[1] + (7 - position[1]) * squareSize
    return (screenX, screenY)

class Button:
    def __init__(self, x, y, width, height, colour):
        self.rect = pygame.Rect(x, y, width, height)
        self.colour = colour
        self.clicked = False # default value for a button, prevents a button being clicked twice

    def Draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect, border_radius=40)

    def IsClicked(self, clickPosition):
        if self.rect.collidepoint(clickPosition): # returns True if in region, else False
            self.clicked = True
            return True
        return False

class Text:
    def __init__(self, position, colour, text, size):
        self.position = position
        self.font = pygame.font.SysFont("Arial", size) # fixed font
        self.text = self.font.render(text, False, colour) # anti aliasing set to False to reduce strain on computational power and memory
    
    def Draw(self, screen):
        screen.blit(self.text, self.position)

class Image:
    def __init__(self, position, dimensions, sprite):
        self.position = position
        self.sprite = pygame.transform.scale(sprite, dimensions)

    def Render(self, screen):
        screen.blit(self.sprite, self.position)

class Screen:
    def __init__(self, screen):
        self.screen = screen
        self.InitialiseObjects()

    def Render(self):
        # Render background
        self.screen.fill("#04202F")

class Home(Screen):
    def __init__(self, screen):
        super().__init__(screen)

    def InitialiseObjects(self):
        # Buttons
        self.playButton = Button(450, 500, 500, 300, "#0b5a84")
        self.settingsButton = Button(1100, 100, 200, 200, (50, 50, 50))

        # Text
        self.text = Text((450, 450), "#FFFFFF", "Play", 300)

        # Image
        sprite = pygame.image.load(f'Images/settings.png')
        self.settingsIcon = Image((1100, 100), (200, 200), sprite)

    def Render(self):
        super().Render()

        # Render buttons
        self.playButton.Draw(self.screen)
        self.settingsButton.Draw(self.screen)

        # Render 'play' text
        self.text.Draw(self.screen)

        # Render settings icon
        self.settingsIcon.Render(self.screen)

class Setup(Screen):
    def __init__(self, screen):
        self.timeButtons = []
        self.timeLabels = ["1 min", "1 | 1", "2 | 1", "3 min", "3 | 2", "5 min", "10 min", "15 | 10", "30 min"]
        self.timeLabelXOffsets = [75, 57, 50, 75, 55, 75, 95, 90, 87]
        super().__init__(screen)

    def InitialiseObjects(self):
        self.confirmButton = Button(525, 800, 350, 125, (50, 50, 50))
        self.backButton = Button(150, 800, 150, 150, (255, 255, 0))
        self.infiniteTimeButton = Button(1100, 800, 150, 150, (200, 200, 200))

        self.bullet = Text((100, 65), (100, 100, 100), "Bullet", 50)
        self.blitz = Text((100, 290), (100, 100, 100), "Blitz", 50)
        self.rapid = Text((100, 515), (100, 100, 100), "Rapid", 50)
        self.confirm = Text((550, 805), (255, 255, 255), "Confirm", 100)

        for row in range(3): # 3 types of time control
            for col in range(3): # 3 buttons for each time control
                button = Button(100 + col * 425, 125 + row * 225, 350, 125, (200, 200, 200))
                self.timeButtons.append(button)

        self.timeText = []
        i = 0
        for button, label in zip(self.timeButtons, self.timeLabels):
            position = (button.rect.center[0] - self.timeLabelXOffsets[i], button.rect.center[1] - 40)
            timeText = Text(position, (0, 0, 0), label, 75)
            self.timeText.append(timeText)
            i += 1

        sprite = pygame.image.load(f'Images/back.png')
        self.backIcon = Image((150, 800), (150, 150), sprite)

        sprite = pygame.image.load(f'Images/infinity.png')
        self.infinityIcon = Image((1113, 810), (125, 125), sprite)

    def Render(self):
        super().Render()

        # Render confirm button
        self.confirmButton.Draw(self.screen)

        # Render back button
        self.backButton.Draw(self.screen)

        # Render infinite time button
        self.infiniteTimeButton.Draw(self.screen)

        # Render time buttons and their respective text
        for button in self.timeButtons:
            button.Draw(self.screen)
        for timeText in self.timeText:
            timeText.Draw(self.screen)

        # Render text
        self.bullet.Draw(self.screen)
        self.blitz.Draw(self.screen)
        self.rapid.Draw(self.screen)
        self.confirm.Draw(self.screen)

        # Render icons
        self.backIcon.Render(self.screen)
        self.infinityIcon.Render(self.screen)

class Game(Screen):
    def __init__(self, screen):
        self.coordText = []
        super().__init__(screen)

    def InitialiseObjects(self):
        self.resignButton = Button(1175, 425, 150, 150, (255, 0, 0))

        self.player1 = Text((110, 25), (255, 255, 255), "Bot", 50)
        self.player2 = Text((110, 925), (255, 255, 255), "You", 50)

        # Coordinate text
        for i in range(1, 9):
            i = Text((280, 970 - (100 + (i - 1) * 100)), (255, 255, 255), str(i), 25)
            self.coordText.append(i)

        for i in alphabet:
            i = Text((305 + 100 * alphabet.index(i), 900), (255, 255, 255), str(i), 25)
            self.coordText.append(i)

        sprite = pygame.image.load(f'Images/resign.png')
        self.resignIcon = Image((1200, 450), (100, 100), sprite)

    def Render(self):
        super().Render()

        # Render board
        board.draw((300, 100))

        # Render resign button
        self.resignButton.Draw(self.screen)

        # Render text
        self.player1.Draw(self.screen)
        self.player2.Draw(self.screen)

        for Text in self.coordText:
            Text.Draw(self.screen)

        self.resignIcon.Render(self.screen)

class Settings(Screen):
    def __init__(self, screen):
        self.themeButtons = []
        super().__init__(screen)

    def InitialiseObjects(self):
        for i in range(4):
            button = Button(175 + 300 * i, 175, 150, 150, (0, 255, 0))
            self.themeButtons.append(button)

        self.audioButton = Button(175, 475, 150, 150, (255, 0, 0))

        self.backButton = Button(175, 775, 150, 150, (255, 255, 0))

        self.text = Text((550, 25), (255, 255, 255), "Settings", 100)

        sprite = pygame.image.load(f'Images/back.png')
        self.backIcon = Image((175, 775), (150, 150), sprite)

    def Render(self):
        super().Render()

        # Render audio button
        self.audioButton.Draw(self.screen)

        # Render back button
        self.backButton.Draw(self.screen)

        # Render theme buttons
        for button in self.themeButtons:
            button.Draw(self.screen)

        # Render text
        self.text.Draw(self.screen)

        # Render back icon
        self.backIcon.Render(self.screen)

class Move:
    def __init__(self, startSquare, endSquare, board):
        self.startRow, self.startCol = startSquare
        self.endRow, self.endCol = endSquare
        self.pieceMoved = board.GetPieceAt(startSquare)
        self.pieceCaptured = board.GetPieceAt(endSquare)
        # restore piece's moved state
        self.pieceMovedWasMoved = self.pieceMoved.moved if self.pieceMoved is not None else None # set it equal to move state if there a piece
        self.oldEnPassantTarget = board.enPassantTarget

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
        self.running = False

    def Update(self):
        if not self.running:
            self.lastTick = pygame.time.get_ticks() # refresh so not delta accumulates
            return
        now = pygame.time.get_ticks()
        delta = (now - self.lastTick) / 1000.0
        self.remaining -= delta
        self.lastTick = now

    def Reset(self, timeSeconds):
        self.remaining = timeSeconds
        self.lastTick = pygame.time.get_ticks()
        self.running = False # restart into pause mode

    def GetTime(self):
        return max(0, self.remaining)
    
class Board:
    def __init__(self, screen, squareSize=squareSize):
        self.screen = screen
        self.squareSize = squareSize
        self.grid = {(x, y): None for x in range(boardSize) for y in range(boardSize)}
        self.enPassantTarget = None

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        # Instead of copying the screen, we just assign the same reference.
        result.screen = self.screen  
        result.squareSize = self.squareSize
        # Deepcopy the grid manually so that each Piece is copied (using our overridden __deepcopy__)
        result.grid = {}
        for key, piece in self.grid.items():
            result.grid[key] = copy.deepcopy(piece, memo) if piece is not None else None
        result.enPassantTarget = self.enPassantTarget
        return result

    def Draw(self, offset=offset):
        offsetX, offsetY = offset
        for i in range(boardSize):
            for j in range(boardSize):
                colour = "#386F88" if (i + j) % 2 == 0 else "#CDDBE1"
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
            capturedPosition = (newPosition[0], newPosition[1] - direction)
            captured = self.GetPieceAt(capturedPosition)
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

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.colour = self.colour
        result.type = self.type
        result.position = self.position  # immutable tuple, so it's safe to share
        # Do not deepcopy the sprite; just share the reference
        result.sprite = self.sprite
        result.moved = self.moved
        result.castled = self.castled
        return result

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

        return [move for move in moves if 0 <= move[0] < boardSize and 0 <= move[1] < boardSize] # filter valid board positions based on limited range

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
        self.pieceValues = {"p": 1, "n": 3.2, "b": 3.3, "r": 5, "q": 9, "k": 20}
    
    def FindKingPosition(self, colour, board):
        for position, piece in board.grid.items():
            if piece and piece.colour == colour and piece.type == "k":
                return position
        return None
    
    def IsAttacking(self, enemyPiece, kingPosition, board):
        return kingPosition in enemyPiece.CalculatePseudoLegalMoves(board)

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
        for piece in board.GetPieces(colour):
            if self.CalculateLegalMoves(piece, board): # if theres a move
                return False
        return True

    def IsStalemate(self, colour, board):
        if self.IsCheck(colour, board):
            return False
        for piece in board.GetPieces(colour):
            if self.CalculateLegalMoves(piece, board):
                return False
        return True
        
    def IsDraw(self, board): # cba for other cases for now so its going to be draw IIF 2 kings on the board
        pieces = [piece for piece in board.grid.values() if piece is not None]
        # if there are exactly 2 pieces and both are kings, thats a draw.
        if len(pieces) == 2 and all(piece.type == "k" for piece in pieces):
            return True

    def PawnPromotionDistance(self, pawn, board):
        direction = 1 if pawn.colour == "w" else -1
        promotionRank = 7 if pawn.colour == "w" else 0
        start = pawn.position

        if start[1] == promotionRank:
            return 0

        heap = []
        heappush(heap, (0, start))
        visited = set()

        while heap:
            cost, position = heappop(heap)
            if position in visited:
                continue
            visited.add(position)
            if position[1] == promotionRank:
                return cost
            
            forward = (position[0], position[1] + direction)
            if 0 <= forward[1] < boardSize and board.GetPieceAt(forward) is None:
                heappush(heap, (cost + 1, forward))

            for dx in [-1, 1]:
                diagonal = (position[0] + dx, position[1] + direction)
                if 0 <= diagonal[0] < boardSize and 0 <= diagonal[1] < boardSize:
                    piece = board.GetPieceAt(diagonal)
                    if piece is not None and piece.colour != pawn.colour:
                        heappush(heap, (cost + 1, diagonal))
        return float("inf")

    def Evaluate(self, board):
        evaluation = 0
        for piece in board.grid.values():
            if piece is not None:
                if piece.colour == "w":
                    evaluation += self.pieceValues.get(piece.type, 0) # white maximises
                else:
                    evaluation -= self.pieceValues.get(piece.type, 0) # black minimises

                if piece.type == "p":
                    distance = self.PawnPromotionDistance(piece, board)
                    if distance < float("inf"):
                        bonus = (8 - distance) * 0.5
                        if piece.colour == "w":
                            evaluation += bonus
                        else:
                            evaluation -= bonus

        boardClone = copy.deepcopy(board)
        if self.IsCheckmate("w", boardClone):
            return -float("inf")
        if self.IsCheckmate("b", boardClone):
            return float("inf")

        return evaluation

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
        self.maxDepth = 3
        self.transpositionTable = {} # board hash: (depth, eval)

    def HashBoard(self, board):
        boardState = []
        for position in sorted(board.grid.keys()):
            piece = board.grid[position]
            if piece is not None:
                boardState.append((position, piece.colour, piece.type, piece.moved))
            else:
                boardState.append((None, position))
        boardState.append(("En Passant", board.enPassantTarget))
        return hash(tuple(boardState))

    def ChooseMove(self, game):
        timer = game.timers[self.colour]
        timeLimit = timer.GetTime() * 1000
        startTime = pygame.time.get_ticks()

        bestMove = None
        depth = 1
        while depth <= self.maxDepth:
            if pygame.time.get_ticks() - startTime > timeLimit: # if over time limit, stop
                break
            currentBest = self.GetBestMove(game.board, game.engine, depth)
            if currentBest is not None:
                bestMove = currentBest
            depth += 1
        return bestMove

    # generates all tuples in the form: (piece, legal move)
    def GetAllLegalMovePairs(self, board, engine, colour):
        legalMoves = []
        for piece in board.GetPieces(colour):
            moves = engine.CalculateLegalMoves(piece, board)
            for move in moves:
                legalMoves.append((piece, move))
        return legalMoves

    def FindPieceClone(self, boardClone, piece):
        for p in boardClone.grid.values():
            if p is not None and p.colour == piece.colour and p.type == piece.type and p.position == piece.position:
                return p
        return None

    def OrderMoves(self, moves, board, engine):
        scoredMoves = []
        for piece, move in moves:
            # check piece at the target square.
            capturedPiece = board.GetPieceAt(move)
            if capturedPiece is not None:
                attackerValue = engine.pieceValues.get(piece.type, 0)
                victimValue = engine.pieceValues.get(capturedPiece.type, 0)
                score = victimValue - attackerValue
            else:
                score = 0
            scoredMoves.append((score, (piece, move)))
        
        sortedMoves = self.MergeSort(scoredMoves)
        return [movePair for score, movePair in sortedMoves]
        
    def MergeSort(self, array):
        if len(array) <= 1:
            return array
        middle = len(array) // 2
        left = self.MergeSort(array[:middle])
        right = self.MergeSort(array[middle:])  # Corrected slice for the right half.
        return self.Merge(left, right)

    def Merge(self, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            # For descending order, compare scores.
            if left[i][0] >= right[j][0]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def Minimax(self, board, engine, depth, alpha, beta, isMaximising, colour):
        boardKey = self.HashBoard(board)
        if boardKey in self.transpositionTable:
            storedDepth, storedEvaluation = self.transpositionTable[boardKey]
            if storedDepth >= depth:
                return storedEvaluation

        if depth == 0:
            evaluation = engine.Evaluate(board)
            self.transpositionTable[boardKey] = (depth, evaluation)
            return engine.Evaluate(board)

        moves = self.OrderMoves(self.GetAllLegalMovePairs(board, engine, colour), board, engine)
        if not moves:
            return engine.Evaluate(board)

        if isMaximising:
            maxEval = -float("inf")
            for piece, move in moves:
                boardClone = copy.deepcopy(board)
                pieceClone = self.FindPieceClone(boardClone, piece)
                if pieceClone is None:
                    continue
                boardClone.MovePiece(pieceClone, move)
                nextColour = "w" if colour == "b" else "b"
                evaluation = self.Minimax(boardClone, engine, depth - 1, alpha, beta, False, nextColour)
                maxEval = max(maxEval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            self.transpositionTable[boardKey] = (depth, maxEval)
            return maxEval
        else:
            minEval = float("inf")
            for piece, move in moves:
                boardClone = copy.deepcopy(board)
                pieceClone = self.FindPieceClone(boardClone, piece)
                if pieceClone is None:
                    continue
                boardClone.MovePiece(pieceClone, move)
                nextColour = "w" if colour == "b" else "b"
                evaluation = self.Minimax(boardClone, engine, depth - 1, alpha, beta, True, nextColour)
                minEval = min(minEval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            self.transpositionTable[boardKey] = (depth, minEval)
            return minEval

    def GetBestMove(self, board, engine, depth):
        #self.transpositionTable.clear() - remove if good RAM
        moves = self.GetAllLegalMovePairs(board, engine, self.colour)
        if not moves:
            return None
        bestMove = None
        if self.colour == "w":
            bestEval = -float("inf")
            for piece, move in moves:
                boardClone = copy.deepcopy(board)
                pieceClone = self.FindPieceClone(boardClone, piece)
                if pieceClone is None:
                    continue
                boardClone.MovePiece(pieceClone, move)
                # blacks move next turn
                evaluation = self.Minimax(boardClone, engine, depth - 1, -float("inf"), float("inf"), False, "b") # minimising
                if evaluation > bestEval:
                    bestEval = evaluation
                    bestMove = (piece, move)
        else:
            bestEval = float("inf")
            for piece, move in moves:
                boardClone = copy.deepcopy(board)
                pieceClone = self.FindPieceClone(boardClone, piece)
                if pieceClone is None:
                    continue
                boardClone.MovePiece(pieceClone, move)
                # whites move next turn
                evaluation = self.Minimax(boardClone, engine, depth - 1, -float("inf"), float("inf"), True, "w") # maximising
                if evaluation < bestEval:
                    bestEval = evaluation
                    bestMove = (piece, move)
        # if bestMove is None:
        #     bestMove = random.choice(moves)
        #     print("cant think of a best move... random move made")
        return bestMove

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
        self.timers = {"w": Timer(100000), "b": Timer(10000)} # change later to respond to user input
        self.running = True

        self.disableAI = False
        self.gameOver = False
        self.highlightedSquares = []

        self.mainMenu = Home(self.screen)
        self.gameSetup = Setup(self.screen)
        self.chessGameScreen = Game(self.screen)
        self.gameSettings = Settings(self.screen)

        self.currentScreen = self.mainMenu

        self.inGame = True if self.currentScreen is self.chessGameScreen else False

    def ChangeScreen(self, newScreen):
        self.currentScreen = newScreen

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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.inGame:
                        position = ScreenToBoard(event.pos, self.offset) # convert screen pos to board pos
                        if event.button == 1: # LMB
                            if self.currentScreen is self.chessGameScreen:
                                self.HandleHumanClick(position)
                        elif event.button == 3 and self.currentScreen is self.chessGameScreen: # RMB
                            if position in self.highlightedSquares:
                                self.highlightedSquares.remove(position)
                            else:
                                self.highlightedSquares.append(position)
                            self.selectedPiece = None
                            self.validMoves = []

                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_LEFT:
                                self.UndoMove()
                            if event.key == pygame.K_RIGHT:
                                self.RedoMove()

                    else:
                        if event.button == 1:
                            self.HandleGUI(event.pos)
        
    def HandleHumanClick(self, position): # handles selecting/deselecting pieces
        piece = self.board.GetPieceAt(position)
        if self.selectedPiece is None:
            self.highlightedSquares = [] # unselect annotation squares
            if piece and piece.colour == self.currentTurn:
                self.selectedPiece = piece
                self.validMoves = self.engine.CalculateLegalMoves(piece, self.board)
                self.disableAI = False

        else: # deselect after clicking
            if position in self.validMoves:
                self.MakeMove(self.selectedPiece, position)
            self.selectedPiece = None
            self.validMoves = []
            self.highlightedSquares = []

    def HandleGUI(self, position): # handles clicking GUI buttons
        if self.currentScreen == self.mainMenu:
            # Play
            if self.mainMenu.playButton.IsClicked(position):
                self.ChangeScreen(self.gameSetup)

            # Settings
            if self.mainMenu.settingsButton.IsClicked(position):
                self.ChangeScreen(self.gameSettings)

        if self.currentScreen == self.gameSetup:
            # Confirm
            if self.gameSetup.confirmButton.IsClicked(position):
                self.ChangeScreen(self.chessGameScreen)

            # Back
            if self.gameSetup.backButton.IsClicked(position):
                self.ChangeScreen(self.mainMenu)

            # Time
            for button in self.gameSetup.timeButtons: # NEED TO UPDATE SOON
                if button.IsClicked(position):
                    # SET TIMER TO A VALUE
                    break

        if self.currentScreen == self.chessGameScreen:
            self.SetupPieces()

            # Resign
            if self.chessGameScreen.resignButton.IsClicked(position):
                self.ChangeScreen(self.mainMenu)

        if self.currentScreen == self.gameSettings:
            # Audio
            if self.gameSettings.audioButton.IsClicked(position):
                pass
            # TOGGLE AUDIO

            # Back
            if self.gameSettings.backButton.IsClicked(position):
                self.ChangeScreen(self.mainMenu)

            # Theme
            for button in self.gameSettings.themeButtons: # NEED TO UPDATE SOON
                if button.IsClicked(position):
                    break
                    # SET THEME

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

        # switching turns (now with timers)
        if self.currentTurn == "w":
            self.timers["w"].running = False
            self.currentTurn = "b"
            self.timers["b"].running = True
        else:
            self.timers["b"].running = False
            self.currentTurn = "w"
            self.timers["w"].running = True

    def UndoMove(self):
        if self.historyIndex >= 0: # if the move log is not empty, then theres no move to undo duhh
            move = self.moveLog[self.historyIndex]
            piece = move.pieceMoved # retrieve piece object

            # move the piece back
            self.board.grid[(move.endRow, move.endCol)] = None
            piece.position = (move.startRow, move.startCol)
            self.board.grid[(move.startRow, move.startCol)] = piece
            # restore original move state
            piece.moved = move.pieceMovedWasMoved

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
        if self.timers[self.currentTurn].GetTime() <= 0:
            self.gameOver = True
            self.gameOverMessage = "Time's up!"

        # pause timers when game is over
        if self.gameOver:
            self.timers["w"].running = False
            self.timers["b"].running = False
            return # skip further updates

        # checkmate + stalemate detection
        if self.engine.IsCheckmate(self.currentTurn, self.board):
            self.gameOver = True
            self.gameOverMessage = "Checkmate!"
            return
        elif self.engine.IsStalemate(self.currentTurn, self.board):
            self.gameOver = True
            self.gameOverMessage = "Stalemate!"
            return
        elif self.engine.IsDraw(self.board):
            self.gameOver = True
            self.gameOverMessage = "Draw!"
            return

        # update timer for active player
        self.timers[self.currentTurn].Update()

        # for inactive timer, refresh lastTick so they don't accidentally subtract time
        currentTime = pygame.time.get_ticks()

        for colour, timer in self.timers.items():
            if colour != self.currentTurn:
                timer.lastTick = currentTime

        # if its an AI's turn, ask AI to choose an execute a move
        if not self.disableAI and not self.CurrentPlayerIsHuman():
                AIMove = self.players[self.currentTurn].ChooseMove(self)
                if AIMove:
                    piece, move = AIMove
                    self.MakeMove(piece, move)

    def Render(self):
        ColourScheme0 = ["red", "green", "yellow", "yellow"]
        ColourScheme1 = ["#FFD700", "#32CD32", "#B22222", "#FFA500"]
        ColourScheme2 = ["#00FFFF", "#00FF00", "#FF00FF", "#FF1493"]
        ColourScheme3 = ["red", "green", "purple", "purple"]
        ColourScheme4 = ["red", "cyan", "purple", "purple"]

        spColour, vmColour, toColour, fmColour = ColourScheme4

        hlColour = "yellow"

        self.screen.fill("#04202F")
        self.board.Draw(self.offset)

        # move highlighting (must be first to go under pieces)
        if self.selectedPiece: # highlighting the selected piece
            position = BoardToScreen(self.selectedPiece.position, self.offset)
            square = pygame.Surface((squareSize, squareSize))
            square.set_alpha(100) # 100/255 opacity
            square.fill(spColour)
            self.screen.blit(square, (position[0], position[1]))
        
        for move in self.validMoves: # highlighting the selected piece's valid moves
            position = BoardToScreen(move, self.offset)
            square = pygame.Surface((squareSize, squareSize))
            square.set_alpha(50)
            square.fill(vmColour)
            self.screen.blit(square, (position[0], position[1]))

        # highlighting last move of a previously moved piece (indicates what moved and where)
        if self.historyIndex >= 0 and len(self.moveLog) > 0: # we are looking into the past moves so we need to use the move log
            lastMove = self.moveLog[self.historyIndex]

            fromSquare = pygame.Surface((squareSize, squareSize))
            fromSquare.set_alpha(100)
            fromSquare.fill(toColour)

            toSquare = pygame.Surface((squareSize, squareSize))
            toSquare.set_alpha(100)
            toSquare.fill(fmColour)

            fromPosition = BoardToScreen((lastMove.startRow, lastMove.startCol), self.offset)
            toPosition = BoardToScreen((lastMove.endRow, lastMove.endCol), self.offset)

            self.screen.blit(toSquare, toPosition)
            self.screen.blit(fromSquare, fromPosition)

        for square in self.highlightedSquares:
            position = BoardToScreen(square, self.offset)
            highlightSquare = pygame.Surface((squareSize, squareSize))
            highlightSquare.set_alpha(100)
            highlightSquare.fill(hlColour)
            self.screen.blit(highlightSquare, position)


        # render all pieces
        for piece in self.board.grid.values():
            if piece:
                piece.Render(self.screen, self.offset)
        
        # game over rendering
        if self.gameOver: # temp message
            font = pygame.font.SysFont("Arial", 50)
            text = font.render(self.gameOverMessage, True, (255, 255, 255))
            self.screen.blit(text, (self.offset[0], self.offset[1] - 60))

        # timer render
        font = pygame.font.SysFont("Arial", 36)
        blackTime = int(self.timers["b"].GetTime())
        whiteTime = int(self.timers["w"].GetTime())
        blackText = font.render(f"Black: {blackTime}", True, (255, 255, 255))
        whiteText = font.render(f"White: {whiteTime}", True, (255, 255, 255))
        self.screen.blit(blackText, (20, 20))
        self.screen.blit(whiteText, (20, self.screen.get_height() - 40))

        # evaluation render
        font = pygame.font.SysFont("Arial", 50)
        text = font.render(str(round(self.engine.Evaluate(self.board), 2)), True, (255, 255, 255))
        self.screen.blit(text, (self.offset[0], self.offset[1] + 800))

        ## ADD INTERFACE RENDERING HERE
        pygame.display.flip()

def main():
    screen = pygame.display.set_mode((width, height))
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
# transposition table
# 2) Lists (Dynamic Arrays)
# moveLog is a list that stores all moves
# validMoves and products of GetPieces() are also lists
# 3) Stacks
# Undo() and Redo() act as a stack
# 4) Linear Search
# iterating through lists (scanning move log amd valid moves)
# 5) Trees
# move/game tree, node - board state, branch - possible move
# minimax searched through this
# 6) Dijkstra's Algorithm
# for evaluating pawn's positions and how close they are to promoting
# 7) Merge Sort
# for ordering the best moves

## WHAT TO ADD
# Better evaluation function, consider: king safety, control of the center, etc

# FINALISING THE PROGRAM
# Integrate interfaces.py
# Create selection screen for assigning Human/AI to the colours - new interface NEEDED
# Replayability

# ADDED DIJKSTRA-INSPIRED ALGORITHM in Evaluate()
# how to improve its effectiveness?
# differentiate game phases
# endgames: pawn promotion and king activity
# middlegames: piece coordination and tactical possibilities
# opening: rapid development and central control