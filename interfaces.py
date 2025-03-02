import pygame

pygame.init()

## GLOBAL CONSTANTS
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

## Classes
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
    
class Board: # without deep copy
    def __init__(self, screen, squareSize=SQUARE_SIZE, boardSize = BOARD_SIZE):
        self.screen = screen
        self.squareSize = squareSize
        self.boardSize = boardSize
        self.grid = {(x, y): None for x in range(boardSize) for y in range(boardSize)}
        self.enPassantTarget = None

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

class Player:
    def __init__(self, colour):
        self.colour = colour

class Human(Player):
    pass # code in other file

class AI(Player):
    pass # code in other file

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

        for i in ALPHABET:
            i = Text((305 + 100 * ALPHABET.index(i), 900), TITLE_TEXT_COLOR, str(i), 25)
            self.coordText.append(i)

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

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board(screen, SQUARE_SIZE, BOARD_SIZE)

        self.mainMenu = Home(screen)
        self.gameSetupTime = TimeSetup(screen)
        self.gameSetupPlayer = PlayerSetup(screen)
        self.chessGameScreen = ChessGame(screen, self.board)
        self.gameSettings = Settings(screen)

        self.currentScreen = self.mainMenu # we want the program to start on the main menu

        self.players = {"w": Human("w"), "b": AI("b")} # CHANGE FOR TESTING
        self.currentTurn = "w"
        self.offsets = OFFSETS
        self.timers = {"w": Timer(60), "b": Timer(60)} # change later to respond to user input
        self.running = True

        self.inGame = False # there is no game currently
        self.gameOver = False

    def SetupPieces(self): # in other file
        pass

    def CurrentPlayerIsHuman(self): # processes huamn clicks IIF the current player is a human
        pass

    def HandleEvents(self): # LMB pressed?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # if LMB click
                clickPosition = event.pos
                # lets handle the screen anyways and handle the other human clicks if in game
                self.HandleScreen(clickPosition)
                if self.inGame and self.CurrentPlayerIsHuman():
                    self.HandleHumanClick(clickPosition)

    def HandleScreen(self, clickPosition): # matches clicked position to the buttons based on the current screen
        if self.currentScreen is self.mainMenu:
            # Play
            if self.mainMenu.playButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSetupTime
                return

            # Settings
            if self.mainMenu.settingsButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSettings
                return

        # setting up time controls
        if self.currentScreen is self.gameSetupTime:
            # Confirm
            if self.gameSetupTime.confirmButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSetupPlayer
                return

            # Back
            if self.gameSetupTime.backButton.IsClicked(clickPosition):
                self.currentScreen = self.mainMenu
                return

            # Time
            for button in self.gameSetupTime.timeButtons:
                if button.IsClicked(clickPosition):
                    if self.gameSetupTime.selectedTimeButton is not None: # checks if it has been selected before so it can revert colours
                        self.gameSetupTime.selectedTimeButton.colour = TIME_CONTROL_BUTTON_COLOR

                    self.gameSetupTime.selectedTimeButton = button
                    button.colour = SELECTED_TIME_CONTROL_BUTTON_COLOUR

                    newTime = self.gameSetupTime.timeValues[button]
                    self.timers["w"].Reset(newTime)
                    self.timers["b"].Reset(newTime)

        # setting up players
        if self.currentScreen is self.gameSetupPlayer:
            # Confirm
            if self.gameSetupPlayer.confirmButton.IsClicked(clickPosition):
                self.inGame = True
                self.SetupPieces()
                self.currentScreen = self.chessGameScreen
                return

            # Back
            if self.gameSetupPlayer.backButton.IsClicked(clickPosition):
                self.currentScreen = self.gameSetupTime
                return

            # MAKE THESE TOGGLE THE PLAYER TYPES - HUMAN OR AI
            if self.gameSetupPlayer.whitePlayerButton.IsClicked(clickPosition):
                return
            
            if self.gameSetupPlayer.blackPlayerButton.IsClicked(clickPosition):
                return

        if self.currentScreen is self.chessGameScreen:
            # Resign
            if self.chessGameScreen.resignButton.IsClicked(clickPosition):
                self.currentScreen = self.mainMenu
                self.inGame = False
                return

        if self.currentScreen is self.gameSettings:
            # Audio
            if self.gameSettings.audioButton.IsClicked(clickPosition):
                # toggle audio
                pass

            # Back
            if self.gameSettings.backButton.IsClicked(clickPosition):
                self.currentScreen = self.mainMenu
                return

            # Theme
            for button in self.gameSettings.themeButtons:
                if button.IsClicked(clickPosition):
                    # SET THEME
                    pass

    def HandleHumanClick(self, position): # handles selecting/deselecting squares and pieces
        pass
    
    def Update(self):
        if self.timers[self.currentTurn].GetTime() <= 0:
            self.gameOver = True
            self.gameOverMessage = "Time's up!"

        # pause timers when game is over
        if self.gameOver:
            self.timers["w"].running = False
            self.timers["b"].running = False
            return # skip further updates

        # checkmate and stalemate detection for checking if game over

        # update timer for active player
        self.timers[self.currentTurn].Update()

        # for inactive timer, refresh lastTick so they don't accidentally subtract time
        currentTime = pygame.time.get_ticks()

        for colour, timer in self.timers.items():
            if colour != self.currentTurn:
                timer.lastTick = currentTime

        # if its an AI's turn, ask AI to choose an execute a move

    def Render(self):
        # render screen
        self.currentScreen.Render()


        if self.inGame:
            # square highlighting, piece rendering, evaluation rendering, game over rendering...

            # render timers
            font = pygame.font.SysFont("Arial", 36)
            blackTime = int(self.timers["b"].GetTime())
            whiteTime = int(self.timers["w"].GetTime())
            blackText = font.render(f"Black: {blackTime}", True, (255, 255, 255))
            whiteText = font.render(f"White: {whiteTime}", True, (255, 255, 255))
            self.screen.blit(blackText, (20, 20))
            self.screen.blit(whiteText, (20, self.screen.get_height() - 40))

        pygame.display.flip()

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

## WHAT TO ADD
# 1) non-button objects:
#   logo? - 1
#   timers - 2
# 2) pop-ups (later):
#   win
#   loss
#   draw

## FLAWS
# the text labels are not aligned
# fixed by creating unique offsets for the x-axis
# buttons are being positioned wrongly (up to down THEN left to right) and not (left to right THEN up to down)
# fixed by flipping positions of column (i) and row (j)
# user MUST pick a time control, some may not want a timer at all
# fixed by adding infinite time button

# WHAT TO ADD
# audio
# audio settings
# theme button functionality
# time control buttons functionality

## CHANGELOG - interfaces.py V6
# made the interfaces inherit __init__ and Render() from Screen to reduce repetition (polymorphism)
# text labels made
# integrated new Board, Timer and Game classes from main - NEWER.py

## FLAWS 2
# need to detect what type of interface we are on
# added HandleScreen method that handles the activation of buttons for the screens

# the interfaces dont get rendered in the Game class
# set current screen to appropriate screens

# there are classes with the same name, causing conflicts
# changed the Game(Screen) class to ChessGame(Screen)

# the resign button does not work - the interfaces are not being handled any more when "in game"
# made the screens get handled regardless of the program being "in game" abd made human clicks only happen if "in game"

# the elements for the game are still being rendered in the main menu - e.g. timers
# made it so only certain objects get rendered when in game

# going to redesign the time control interface to have 1 min, 3 min, 5 min, 10 min and unlimited only for simplicity - increments may make the chess AI too strong

# new interface is not rendering - one click clicks through both interfaces at once - need to add a break somewhere
# fixed by using early returns in HandleScreens()

# need to add time functionality
# added a dictionary named pieceValues to map the buttons to their respective times