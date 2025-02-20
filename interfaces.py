import pygame

pygame.init()

# For the board
global alphabet
alphabet = "abcdefgh"

# Screen
screen = pygame.display.set_mode((1400, 1000))
pygame.display.set_caption("Chess Interface")


## Classes
class Board:
    def __init__(self, screen, len=100): # len: sidelength
        self.screen = screen
        self.len = len
        self.board = [[None for _ in range(8)] for _ in range(8)] # List Comprehension

    def draw(self, pos): # pos = starting position
        x, y = pos
        for i in range(8):
            for j in range(8): # Nested Loop
                colour = "#CDDBE1" if (i + j) % 2 == 0 else "#386F88" # Ternary Operator
                pygame.draw.rect(self.screen, colour, (x + i * self.len, y + j * self.len, self.len, self.len))

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


class Home:
    def __init__(self, screen):
        self.screen = screen
        self.InitialiseObjects() # the buttons are initialised when the class is initialised - automatic and instant

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
        # Render background
        self.screen.fill("#04202F")

        # Render buttons
        self.playButton.Draw(self.screen)
        self.settingsButton.Draw(self.screen)

        # Render 'play' text
        self.text.Draw(self.screen)

        # Render settings icon
        self.settingsIcon.Render(self.screen)


class Setup:
    def __init__(self, screen):
        self.screen = screen
        self.timeButtons = [] # empty list for the buttons
        self.InitialiseObjects()

    def InitialiseObjects(self):
        self.confirmButton = Button(525, 800, 350, 125, (50, 50, 50))
        self.backButton = Button(150, 800, 150, 150, (255, 255, 0))

        self.bullet = Text((100, 65), (100, 100, 100), "Bullet", 50)
        self.blitz = Text((100, 290), (100, 100, 100), "Blitz", 50)
        self.rapid = Text((100, 515), (100, 100, 100), "Rapid", 50)
        self.confirm = Text((550, 805), (255, 255, 255), "Confirm", 100)

        for i in range(3): # 3 types of time control
            for j in range(3): # 3 buttons for each time control
                button = Button(100 + i * 425, 125 + j * 225, 350, 125, (200, 200, 200))
                self.timeButtons.append(button)

        sprite = pygame.image.load(f'Images/back.png')
        self.backIcon = Image((150, 800), (150, 150), sprite)

    def Render(self):
        # Render background
        self.screen.fill("#04202F")

        # Render confirm button
        self.confirmButton.Draw(self.screen)

        # Render back button
        self.backButton.Draw(self.screen)

        # Render time buttons
        for button in self.timeButtons:
            button.Draw(self.screen)

        # Render text
        self.bullet.Draw(self.screen)
        self.blitz.Draw(self.screen)
        self.rapid.Draw(self.screen)
        self.confirm.Draw(self.screen)

        # Render icon
        self.backIcon.Render(self.screen)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.coordText = []
        self.InitialiseObjects()

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
        # Render background
        self.screen.fill("#04202F")

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


class Settings:
    def __init__(self, screen):
        self.screen = screen
        self.themeButtons = []
        self.InitialiseObjects()

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
        # Render background
        self.screen.fill("#04202F")

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

# Instantiating classes
board = Board(screen, 100)
MainMenu = Home(screen)
GameSetup = Setup(screen)
ChessGameScreen = Game(screen)
GameSettings = Settings(screen)

# Default value for interface
interface = 0

def updateScreen(i):
    global interface
    interface = i

    if i == 0:
        MainMenu.Render()
    if i == 1:
        GameSetup.Render()
    if i == 2:
        ChessGameScreen.Render()
    if i == 3:
        GameSettings.Render()

updateScreen(0)
# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Getting coordinates
            clickPosition = pygame.mouse.get_pos()

            ### MAIN MENU
            if interface == 0:
                # Play
                if MainMenu.playButton.IsClicked(clickPosition):
                    updateScreen(1)
                    break

                # Settings
                if MainMenu.settingsButton.IsClicked(clickPosition):
                    updateScreen(3)

            ### GAME SETUP
            if interface == 1:
                # Confirm
                if GameSetup.confirmButton.IsClicked(clickPosition):
                    updateScreen(2)

                # Back
                if GameSetup.backButton.IsClicked(clickPosition):
                    updateScreen(0)

                # Time
                for button in GameSetup.timeButtons:
                    if button.IsClicked(clickPosition):
                        # SET TIMER TO A VALUE
                        pass

            ### CHESS GAME SCREEN
            if interface == 2:
                # Resign
                if ChessGameScreen.resignButton.IsClicked(clickPosition):
                    updateScreen(0)


            ### GAME SETTINGS
            if interface == 3:
                # Audio
                if GameSettings.audioButton.IsClicked(clickPosition):
                    pass
                # TOGGLE AUDIO

                # Back
                if GameSetup.backButton.IsClicked(clickPosition):
                    updateScreen(0)
                    break

                # Theme
                for button in GameSettings.themeButtons:
                    if button.IsClicked(clickPosition):
                        pass
                        # SET THEME



    pygame.display.flip()
pygame.quit()


## HOW A BUTTON WORKS
# 1) click
# 2) check if the clicked position lies on a button
# 3) activate that button based on the position clicked

## HOW A CHESS CLOCK WORKS
# 1) start clock
# 2) update ticks per second for the player in turn, alternate if needed
# 3) if the ticks go above the threshold, end the game


## ARCHIVED
# icons = []
        # icons.append(pygame.Rect(50, 25, 50, 50)) # bot_icon
        # icons.append(pygame.Rect(50, 925, 50, 50)) # player_icon
        # icons.append(pygame.Rect(1200, 25, 150, 50)) # timer1
        # icons.append(pygame.Rect(1200, 925, 150, 50)) # timer2

        # for i in icons:
        #     pygame.draw.rect(self.screen, (200, 200, 200), i)


## WHAT TO ADD
# 1) non-button objects:
#   player icons - 2
#   logo? - 1
#   timers - 2
#   time control text - 3 //
#   chess board coordinates - 16 //
#   player text - 2 //
#   play text - 1 //
#   settings text - 1 //
# 2) pop-ups (later):
#   win
#   loss
#   draw

## FLAWS
# looks ugly fr


## CHANGELOG - interfaces.py V5
# renamed InitialiseButtons() to InitialiseObjects()
# added Text class
# incorporated Text class into Home, Setup, Game and Settings class