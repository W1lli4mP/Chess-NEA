import pygame
import copy
import threading
import math
from heapq import heappush, heappop

pygame.init()

# region GLOBAL CONSTANTS
ALPHABET = "abcdefgh" # for board coord rendering
BACKGROUND_COLOUR = "#04202F"
SQUARE_SIZE = 100
BOARD_SIZE = 8
OFFSETS = (300, 100)
WIDTH, HEIGHT = 1400, 1000

# BUTTONS, TEXT, ETC
PLAY_BUTTON_COLOR         = "#0b5a84"       # Home screen Play button
SETTINGS_BUTTON_COLOR     = (50, 50, 50)    # Home screen settings button & confirm buttons in other screens
CONFIRM_BUTTON_COLOR      = (50, 50, 50)
BACK_BUTTON_COLOR         = (255, 255, 0)   # Used for back buttons in multiple screens
TIME_CONTROL_BUTTON_COLOR = (200, 200, 200) # All time control buttons in TimeSetup
SELECTED_TIME_CONTROL_BUTTON_COLOUR = (255, 165, 0) # Color for a selected time control button (e.g. orange)
WHITE_PLAYER_BUTTON_COLOR = (255, 255, 255)
BLACK_PLAYER_BUTTON_COLOR = (0, 0, 0)
THEME_BUTTON_COLOR        = (0, 255, 0)
AUDIO_BUTTON_COLOR        = (255, 0, 0)
RESIGN_BUTTON_COLOR       = (255, 0, 0)

# Text colors
PLAY_TEXT_COLOR      = "#FFFFFF"         # Home screen Play text
TITLE_TEXT_COLOR     = (255, 255, 255)     # For titles (e.g., in TimeSetup, PlayerSetup, Settings)
CONFIRM_TEXT_COLOR   = (255, 255, 255)     # For confirm button texts
TIME_LABEL_TEXT_COLOR = (0, 0, 0)          # For time control labels
WHITE_TEXT_COLOR     = (255, 255, 255)     # For 'White' text in PlayerSetup
BLACK_TEXT_COLOR     = (255, 255, 255)     # For 'Black' text in PlayerSetup
# endregion

# HELPER FUNCTIONS
def ScreenToBoard(position, offsets):
    boardX = (position[0] - offsets[0]) // SQUARE_SIZE
    boardY = 7 - ((position[1] - offsets[1]) // SQUARE_SIZE)
    return (boardX, boardY)

def BoardToScreen(position, offsets):
    screenX = position[0] * SQUARE_SIZE + offsets[0]
    screenY = offsets[1] + (7 - position[1]) * SQUARE_SIZE
    return (screenX, screenY)

# GUI CLASSES
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
        self.screen.fill(BACKGROUND_COLOUR)

class Home(Screen):
    def __init__(self, screen):
        super().__init__(screen)

    def InitialiseObjects(self):
        # Buttons
        self.playButton = Button(450, 500, 500, 300, PLAY_BUTTON_COLOR)
        self.settingsButton = Button(1100, 100, 200, 200, SETTINGS_BUTTON_COLOR)

        # Text
        self.text = Text((450, 450), PLAY_TEXT_COLOR, "Play", 300)

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

class TimeSetup(Screen):
    def __init__(self, screen):
        super().__init__(screen)

    def InitialiseObjects(self):
        self.title = Text((490, 25), TITLE_TEXT_COLOR, "Setup Time", 100)

        self.confirmButton = Button(525, 800, 350, 125, CONFIRM_BUTTON_COLOR)
        self.confirmText = Text((550, 805), CONFIRM_TEXT_COLOR, "Confirm", 100)

        self.backButton = Button(150, 800, 150, 150, BACK_BUTTON_COLOR)
        backSprite = pygame.image.load(f'Images/back.png')
        self.backIcon = Image((150, 800), (150, 150), backSprite)

        ## TIME
        self.timeControlButton1 = Button(100, 300, 350, 125, TIME_CONTROL_BUTTON_COLOR)
        self.timeControlButton2 = Button(525, 300, 350, 125, TIME_CONTROL_BUTTON_COLOR)
        self.timeControlButton3 = Button(950, 300, 350, 125, TIME_CONTROL_BUTTON_COLOR)
        self.timeControlButton4 = Button(310, 525, 350, 125, TIME_CONTROL_BUTTON_COLOR)
        self.timeControlButton5 = Button(740, 525, 350, 125, TIME_CONTROL_BUTTON_COLOR)

        self.timeLabel1 = Text((200, 320), TIME_LABEL_TEXT_COLOR, "1 min", 75)
        self.timeLabel2 = Text((625, 320), TIME_LABEL_TEXT_COLOR, "3 min", 75)
        self.timeLabel3 = Text((1050, 320), TIME_LABEL_TEXT_COLOR, "5 min", 75)
        self.timeLabel4 = Text((385, 545), TIME_LABEL_TEXT_COLOR, "10 min", 75)
        self.timeLabel5 = Text((790, 545), TIME_LABEL_TEXT_COLOR, "Unlimited", 75)

        self.timeButtons = [
            self.timeControlButton1,
            self.timeControlButton2,
            self.timeControlButton3,
            self.timeControlButton4,
            self.timeControlButton5
        ]

        self.timeValues = {
            self.timeControlButton1: 60,
            self.timeControlButton2: 180,
            self.timeControlButton3: 300,
            self.timeControlButton4: 600,
            self.timeControlButton5: 999999
        }

        self.selectedTimeButton = None

    def Render(self):
        super().Render()

        # Render title
        self.title.Draw(self.screen)

        # Render confirm button
        self.confirmButton.Draw(self.screen)
        self.confirmText.Draw(self.screen)

        # Render back button + icon
        self.backButton.Draw(self.screen)
        self.backIcon.Render(self.screen)

        self.timeControlButton1.Draw(self.screen)
        self.timeControlButton2.Draw(self.screen)
        self.timeControlButton3.Draw(self.screen)
        self.timeControlButton4.Draw(self.screen)
        self.timeControlButton5.Draw(self.screen)

        self.timeLabel1.Draw(self.screen)
        self.timeLabel2.Draw(self.screen)
        self.timeLabel3.Draw(self.screen)
        self.timeLabel4.Draw(self.screen)
        self.timeLabel5.Draw(self.screen)

class PlayerSetup(Screen):
    def __init__(self, screen):
        self.whiteIsHuman = True
        self.blackIsHuman = True
        super().__init__(screen)

    def InitialiseObjects(self):
        self.title = Text((450, 25), TITLE_TEXT_COLOR, "Setup Players", 100)

        self.confirmButton = Button(525, 800, 350, 125, CONFIRM_BUTTON_COLOR)
        self.confirmText = Text((550, 805), CONFIRM_TEXT_COLOR, "Confirm", 100)

        self.backButton = Button(150, 800, 150, 150, BACK_BUTTON_COLOR)
        backSprite = pygame.image.load(f'Images/back.png')
        self.backIcon = Image((150, 800), (150, 150), backSprite)

        ## PLAYERS
        self.whiteText = Text((400, 250), WHITE_TEXT_COLOR, "White", 80)
        self.blackText = Text((850, 250), BLACK_TEXT_COLOR, "Black", 80)

        self.whitePlayerButton = Button(350, 400, 250, 250, WHITE_PLAYER_BUTTON_COLOR)
        self.blackPlayerButton = Button(800, 400, 250, 250, BLACK_PLAYER_BUTTON_COLOR)

        self.whitePlayerText = Text((415, 500), (0, 0, 0), "Human", 50)
        self.blackPlayerText = Text((865, 500), (255, 255, 255), "Human", 50)

    def Render(self):
        super().Render()

        # Render title
        self.title.Draw(self.screen)

        # Render confirm button
        self.confirmButton.Draw(self.screen)
        self.confirmText.Draw(self.screen)

        # Render back button + icon
        self.backButton.Draw(self.screen)
        self.backIcon.Render(self.screen)

        self.whiteText.Draw(self.screen)
        self.blackText.Draw(self.screen)

        self.whitePlayerButton.Draw(self.screen)
        self.blackPlayerButton.Draw(self.screen)

        self.whitePlayerText.Draw(self.screen)
        self.blackPlayerText.Draw(self.screen)

class ChessGame(Screen):
    def __init__(self, screen, board): # this might not get updated
        self.board = board
        self.coordText = []
        super().__init__(screen)

    def InitialiseObjects(self):
        self.resignButton = Button(1175, 425, 150, 150, RESIGN_BUTTON_COLOR)

        # Coordinate text
        for i in range(1, 9):
            i = Text((280, 970 - (100 + (i - 1) * 100)), TITLE_TEXT_COLOR, str(i), 25)
            self.coordText.append(i)

        for letter in ALPHABET:
            letter = Text((305 + 100 * ALPHABET.index(letter), 900), TITLE_TEXT_COLOR, str(letter), 25)
            self.coordText.append(letter)

        sprite = pygame.image.load(f'Images/resign.png')
        self.resignIcon = Image((1200, 450), (100, 100), sprite)

    def Render(self):
        super().Render()

        # Render board
        self.board.Draw((300, 100))

        # Render resign button
        self.resignButton.Draw(self.screen)

        # Render resign icon
        self.resignIcon.Render(self.screen)

class Settings(Screen):
    def __init__(self, screen):
        self.themeButtons = []
        super().__init__(screen)

    def InitialiseObjects(self):
        for i in range(4):
            button = Button(175 + 300 * i, 175, 150, 150, THEME_BUTTON_COLOR)
            self.themeButtons.append(button)

        self.audioButton = Button(175, 475, 150, 150, AUDIO_BUTTON_COLOR)

        self.backButton = Button(175, 775, 150, 150, BACK_BUTTON_COLOR)

        self.title = Text((550, 25), TITLE_TEXT_COLOR, "Settings", 100)

        sprite = pygame.image.load(f'Images/back.png')
        self.backIcon = Image((175, 775), (150, 150), sprite)

    def Render(self):
        super().Render()
        # Render title
        self.title.Draw(self.screen)

        # Render audio button
        self.audioButton.Draw(self.screen)

        # Render back button
        self.backButton.Draw(self.screen)

        # Render back icon
        self.backIcon.Render(self.screen)

        # Render theme buttons
        for button in self.themeButtons:
            button.Draw(self.screen)

# LOGIC CLASSES
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
    def __init__(self, screen, squareSize=SQUARE_SIZE, boardSize = BOARD_SIZE):
        self.screen = screen
        self.squareSize = squareSize
        self.boardSize = boardSize
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

    def Draw(self, offsets=OFFSETS):
        offsetX, offsetY = offsets
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                colour = "#386F88" if (i + j) % 2 == 0 else "#CDDBE1"
                rect = (offsetX + i * self.squareSize,
                        offsetY + (self.boardSize - 1 - j) * self.squareSize,
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
        self.sprite = pygame.transform.scale(sprite, (SQUARE_SIZE, SQUARE_SIZE))
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

    def Render(self, screen, offsets=OFFSETS):
        position = BoardToScreen(self.position, offsets)
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

        return [move for move in moves if 0 <= move[0] < BOARD_SIZE and 0 <= move[1] < BOARD_SIZE] # filter valid board positions based on limited range

    def SlidingMoves(self, board, x, y, directions):
        moves = []
        for dx, dy in directions:
            for i in range(1, BOARD_SIZE):
                newPos = (x + dx * i, y + dy * i)
                if not (0 <= newPos[0] < BOARD_SIZE and 0 <= newPos[1] < BOARD_SIZE):
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
        self.sprite = pygame.transform.scale(sprite, (SQUARE_SIZE, SQUARE_SIZE))

class Engine:
    def __init__(self, board):
        self.board = board
        self.pieceValues = {"p": 1, "n": 3.2, "b": 3.3, "r": 5, "q": 9, "k": 20}
    
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
        bestCost = {start: 0}

        while heap:
            cost, position = heappop(heap)
            if position[1] == promotionRank:
                return cost
            
            forward = (position[0], position[1] + direction)
            if 0 <= forward[1] < BOARD_SIZE and board.GetPieceAt(forward) is None:
                newCost = cost + 1
                if forward not in bestCost or newCost < bestCost[forward]:
                    bestCost[forward] = newCost
                    heappush(heap, (newCost, forward))

            for dx in [-1, 1]:
                diagonal = (position[0] + dx, position[1] + direction)
                if 0 <= diagonal[0] < BOARD_SIZE and 0 <= diagonal[1] < BOARD_SIZE:
                    piece = board.GetPieceAt(diagonal)
                    if piece is not None and piece.colour != pawn.colour:
                        newCost = cost + 1
                        if diagonal not in bestCost or newCost < bestCost[diagonal]:
                            bestCost[diagonal] = newCost
                            heappush(heap, (newCost, diagonal))
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
                        bonus = 0.05 * math.log(max(8 - distance + 1, 1)) # diminishing bonus - punish pawn pushing to an extent
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
        self.maxDepth = 2
        self.transpositionTable = {} # board hash: (depth, eval)

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
        boardKey = engine.HashBoard(board)
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
        #self.transpositionTable.clear() - remove if good RAM - TEST
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
        return bestMove

# GAME CONTROLLER
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board(screen, SQUARE_SIZE, BOARD_SIZE)
        self.engine = Engine(self.board)
        self.moveLog = []
        self.historyIndex = -1
        self.selectedPiece = None
        self.validMoves = []
        self.highlightedSquares = []
        self.offsets = OFFSETS
        self.timers = {"w": Timer(300), "b": Timer(300)} # default value
        self.players = {"w": Human("w"), "b": AI("b")}
        self.currentTurn = "w"
        self.disableAI = False
        self.gameOver = False
        self.gameOverMessage = ""
        self.positionCount = {}

        # GUI Screens
        self.mainMenu = Home(screen)
        self.gameSetupTime = TimeSetup(screen)
        self.gameSetupPlayer = PlayerSetup(screen)
        self.chessGameScreen = ChessGame(screen, self.board)
        self.gameSettings = Settings(screen)
        self.currentScreen = self.mainMenu  # start at the main menu

        self.inGame = False  # not in an active game until setup is complete
        self.running = True

    def SetupPieces(self):
        generalOrder = ["r", "n", "b", "q", "k", "b", "n", "r"]
        whitePositions = [(i, 0) for i in range(8)] + [(i, 1) for i in range(8)]
        blackPositions = [(i, 7) for i in range(8)] + [(i, 6) for i in range(8)]

        for position in whitePositions:
            pieceType = generalOrder[position[0]] if position[1] == 0 else "p"
            data = "w" + pieceType
            sprite = pygame.image.load(f'Pieces/{data}.png').convert_alpha()
            piece = Piece(data, position, sprite)
            self.board.PlacePiece(piece)

        for position in blackPositions:
            pieceType = generalOrder[position[0]] if position[1] == 7 else "p"
            data = "b" + pieceType
            sprite = pygame.image.load(f'Pieces/{data}.png').convert_alpha()
            piece = Piece(data, position, sprite)
            self.board.PlacePiece(piece)

    def CurrentPlayerIsHuman(self):
        return isinstance(self.players[self.currentTurn], Human)

    def HandleHumanClick(self, position):
        piece = self.board.GetPieceAt(position)
        if self.selectedPiece is None:
            self.highlightedSquares = []
            if piece and piece.colour == self.currentTurn:
                self.selectedPiece = piece
                self.validMoves = self.engine.CalculateLegalMoves(piece, self.board)
                self.disableAI = False
        else:
            if position in self.validMoves:
                self.MakeMove(self.selectedPiece, position)
            self.selectedPiece = None
            self.validMoves = []
            self.highlightedSquares = []

    def MakeMove(self, piece, destination):
        # if moves were undone, discard "redo" moves.
        if self.historyIndex < len(self.moveLog) - 1:
            self.moveLog = self.moveLog[:self.historyIndex + 1]
        startSquare = piece.position
        move = Move(startSquare, destination, self.board)
        self.moveLog.append(move)
        self.historyIndex += 1

        # execute move
        self.board.MovePiece(piece, destination)
        piece.moved = True

        # handle castling
        if move.isCastling:
            rook = self.board.GetPieceAt(move.rookStart)
            if rook:
                self.board.MovePiece(rook, move.rookEnd)
                rook.moved = True

        # handle pawn promotion
        if piece.type == "p" and ((piece.colour == "w" and destination[1] == 7) or (piece.colour == "b" and destination[1] == 0)):
            piece.Promote(self.board)
            move.promoted = True

        # update the repetition counter
        boardStateHash = self.engine.HashBoard(self.board)
        self.positionCount[boardStateHash] = self.positionCount.get(boardStateHash, 0) + 1

        if self.positionCount[boardStateHash] >= 3:
            self.gameOver = True
            self.gameOverMessage = "Draw by threefold repetiion"

        # switch turn and timers
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
            piece.moved = move.pieceMovedWasMoved
            if move.promoted:
                piece.type = "p"
                sprite = pygame.image.load(f"Pieces/{piece.colour}p.png").convert_alpha()
                piece.sprite = pygame.transform.scale(sprite, (SQUARE_SIZE, SQUARE_SIZE))

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

            # revert turn
            self.currentTurn = "w" if self.currentTurn == "b" else "b"

            # decrement repetition count for the state after undoing
            boardStateHash = self.engine.HashBoard(self.board)
            if boardStateHash in self.positionCount:
                self.positionCount[boardStateHash] -= 1
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

            # for en passant, remove captured pawn
            if move.pieceCaptured is not None and move.isEnPassant:
                direction = 1 if piece.colour == "w" else -1
                capturedPosition = (move.endRow, move.endCol - direction)
                self.board.grid[capturedPosition] = None

            # redo castling - update rook
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

            # update en passant target
            self.board.enPassantTarget = None
            if piece.type == "p" and abs(move.endRow - move.startRow) == 2:
                self.board.enPassantTarget = (move.endRow, (move.endRow + move.startRow) // 2)

            # redo turn
            self.currentTurn = "w" if self.currentTurn == "b" else "b"

            # clear selection
            self.selectedPiece = None
            self.validMoves = []

            # disable AI
            self.disableAI = True

            # update repetition counter for redoing move
            boardStateHash = self.engine.HashBoard(self.board)
            self.positionCount[boardStateHash] = self.positionCount.get(boardStateHash, 0) + 1
            if self.positionCount[boardStateHash] >= 3:
                self.gameOver = True
                self.gameOverMessage = "Draw by threefold repetition!"

    def HandleScreen(self, clickPosition):
        # process GUI clicks
        if self.currentScreen is self.mainMenu:
            if self.mainMenu.playButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSetupTime
                return
            if self.mainMenu.settingsButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSettings
                return
        
        if self.currentScreen is self.gameSetupTime:
            if self.gameSetupTime.confirmButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSetupPlayer
                return
            if self.gameSetupTime.backButton.IsClicked(clickPosition):
                self.currentScreen = self.mainMenu
                return
            for button in self.gameSetupTime.timeButtons:
                if button.IsClicked(clickPosition):
                    if self.gameSetupTime.selectedTimeButton is not None:
                        self.gameSetupTime.selectedTimeButton.colour = TIME_CONTROL_BUTTON_COLOR
                    self.gameSetupTime.selectedTimeButton = button
                    button.colour = SELECTED_TIME_CONTROL_BUTTON_COLOUR
                    newTime = self.gameSetupTime.timeValues[button]
                    self.timers["w"].Reset(newTime)
                    self.timers["b"].Reset(newTime)
                    return
        
        if self.currentScreen is self.gameSetupPlayer:
            if self.gameSetupPlayer.confirmButton.IsClicked(clickPosition):
                if self.gameSetupPlayer.whiteIsHuman:
                    self.players["w"] = Human("w")
                else:
                    self.players["w"] = AI("w")
                if self.gameSetupPlayer.blackIsHuman:
                    self.players["b"] = Human("b")
                else:
                    self.players["b"] = AI("b")

                self.inGame = True
                self.SetupPieces()
                self.currentScreen = self.chessGameScreen
                return

            if self.gameSetupPlayer.backButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSetupTime
                return

            if self.gameSetupPlayer.whitePlayerButton.IsClicked(clickPosition):
                self.gameSetupPlayer.whiteIsHuman = not self.gameSetupPlayer.whiteIsHuman
                newText = "Human" if self.gameSetupPlayer.whiteIsHuman else "AI"
                newPosition = (415, 500) if self.gameSetupPlayer.whiteIsHuman else (455, 500)
                self.gameSetupPlayer.whitePlayerText = Text(newPosition, (0, 0, 0), newText, 50)

            if self.gameSetupPlayer.blackPlayerButton.IsClicked(clickPosition):
                self.gameSetupPlayer.blackIsHuman = not self.gameSetupPlayer.blackIsHuman
                newText = "Human" if self.gameSetupPlayer.blackIsHuman else "AI"
                newPosition = (865, 500) if self.gameSetupPlayer.blackIsHuman else (910, 500)
                self.gameSetupPlayer.blackPlayerText = Text(newPosition, (255, 255, 255), newText, 50)

        if self.currentScreen is self.gameSettings:
            if self.gameSettings.audioButton.IsClicked(clickPosition):
                pass  # Toggle audio

            if self.gameSettings.backButton.IsClicked(clickPosition):
                self.currentScreen = self.mainMenu
                return

            for button in self.gameSettings.themeButtons:
                if button.IsClicked(clickPosition):
                    pass  # Set theme
        
        if self.currentScreen is self.chessGameScreen:
            if self.chessGameScreen.resignButton.IsClicked(clickPosition):
                self.ResetGame()
                self.currentScreen = self.mainMenu
                self.inGame = False
                return

    def HandleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # process mouse events (for both GUI and board)
            if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3): # if LMB or RMB pressed
                clickPosition = event.pos
                if event.button == 1: # register LMB clicks only
                    self.HandleScreen(clickPosition)

                if self.inGame:
                    boardPosition = ScreenToBoard(clickPosition, self.offsets)
                    if event.button == 1:
                        self.highlightedSquares.clear() # gets rid of all highlighted squares
                        if not self.gameOver and self.CurrentPlayerIsHuman(): # prevent board interaction if game over but allow users to annotate squares for game analysis or something
                            self.HandleHumanClick(boardPosition)
                    
                    elif event.button == 3: # RMB
                        if boardPosition in self.highlightedSquares:
                            self.highlightedSquares.remove(boardPosition)
                        elif 0 <= boardPosition[0] < BOARD_SIZE and 0 <= boardPosition[1] < BOARD_SIZE: # make sure we can highlight the board's squares only
                            self.highlightedSquares.append(boardPosition)
                        self.selectedPiece = None
                        self.validMoves = []

            if self.inGame and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.UndoMove()
                if event.key == pygame.K_RIGHT:
                    self.RedoMove()

    def ComputeAIMove(self):
        AIMove = self.players[self.currentTurn].ChooseMove(self)
        if AIMove:
            piece, move = AIMove
            self.MakeMove(piece, move)
            self.disableAI = True

    def Update(self):
        if self.timers[self.currentTurn].GetTime() <= 0:
            self.gameOver = True
            self.gameOverMessage = "Time's up!"
        if self.gameOver:
            self.timers["w"].running = False
            self.timers["b"].running = False
            return

        if self.inGame:
            # check game termination conditions
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

        self.timers[self.currentTurn].Update()
        currentTime = pygame.time.get_ticks()
        for colour, timer in self.timers.items():
            if colour != self.currentTurn:
                timer.lastTick = currentTime

        if self.inGame and not self.disableAI and not self.CurrentPlayerIsHuman():
            self.disableAI = True
            threading.Thread(target=self.ComputeAIMove).start()

    def Render(self):
        self.currentScreen.Render()
        if self.inGame:
            # logic-based rendering of the chessboard and game state
            ColourScheme4 = ["red", "cyan", "purple", "purple"]
            spColour, vmColour, toColour, fmColour = ColourScheme4
            hlColour = "yellow"

            # highlight selected piece
            if self.selectedPiece:
                pos = BoardToScreen(self.selectedPiece.position, self.offsets)
                square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                square.set_alpha(100)
                square.fill(spColour)
                self.screen.blit(square, pos)

            # highlight valid moves
            for move in self.validMoves:
                pos = BoardToScreen(move, self.offsets)
                square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                square.set_alpha(50)
                square.fill(vmColour)
                self.screen.blit(square, pos)

            # highlight last move
            if self.historyIndex >= 0 and len(self.moveLog) > 0:
                lastMove = self.moveLog[self.historyIndex]
                fromSquare = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                fromSquare.set_alpha(100)
                fromSquare.fill(toColour)
                toSquare = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                toSquare.set_alpha(100)
                toSquare.fill(fmColour)
                fromPos = BoardToScreen((lastMove.startRow, lastMove.startCol), self.offsets)
                toPos = BoardToScreen((lastMove.endRow, lastMove.endCol), self.offsets)
                self.screen.blit(fromSquare, fromPos)
                self.screen.blit(toSquare, toPos)

            # highlight annotated squares
            for sq in self.highlightedSquares:
                position = BoardToScreen(sq, self.offsets)
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                highlight.set_alpha(100)
                highlight.fill(hlColour)
                self.screen.blit(highlight, position)

            # render all pieces
            for piece in self.board.grid.values():
                if piece:
                    piece.Render(self.screen, self.offsets)

            # render game over message if applicable
            if self.gameOver:
                font = pygame.font.SysFont("Arial", 50)
                msg = font.render(self.gameOverMessage, True, (255, 255, 255))
                self.screen.blit(msg, (self.offsets[0], self.offsets[1] - 60))

            # render timers
            font = pygame.font.SysFont("Arial", 36)
            blackTime = int(self.timers["b"].GetTime())
            whiteTime = int(self.timers["w"].GetTime())
            blackText = font.render(f"Black: {blackTime}", True, (255, 255, 255))
            whiteText = font.render(f"White: {whiteTime}", True, (255, 255, 255))
            self.screen.blit(blackText, (20, 20))
            self.screen.blit(whiteText, (20, self.screen.get_height() - 40))

            # render evaluation - FOR TESTING
            font = pygame.font.SysFont("Arial", 50)
            evalText = font.render(str(round(self.engine.Evaluate(self.board), 2)), True, (255, 255, 255))
            self.screen.blit(evalText, (self.offsets[0], self.offsets[1] + 800))
        pygame.display.flip()

    def ResetGame(self):
        # reinitialise the board and engine
        self.board = Board(self.screen, SQUARE_SIZE, BOARD_SIZE)
        self.engine = Engine(self.board)

        # reset move log and game state variables
        self.moveLog = []
        self.historyIndex = -1
        self.selectedPiece = None
        self.validMoves = []
        self.highlightedSquares = []
        self.currentTurn = "w"
        self.disableAI = False
        self.gameOver = False
        self.gameOverMessage = ""

        # reset timers back to default time
        self.timers["w"].Reset(300)
        self.timers["b"].Reset(300)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("notchess.com - now with interfaces")
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
# board does not get cleared after a game is complete
# fixed by adding the ResetGame() method in Game to be called in HandleScreen() so everything is cleared
# no sounds
# fixed by....
# pushes pawns too much
# fixed by making the bonus go through a logarithmic function - diminishing costs
# there is no draw by 3 move repetition
# fixed by using the HashBoard method to do this
# HashBoard method is in the AI class and not the engine class
# fixed by moving BoardHash method from AI to Engine
# players can still move when draw has occurred
# fixed by ignoring inputs if game is over
# players cannot undo and redo moves to check game history after a game has concluded
# fixed by tweaking HandleEvents()