import pygame as game
import random as r

global grid, level
grid, level = [], 1

class Tile:
    CLAIMED = 0
    UNCLAIMED = -1
    FILL = 1
    LIVE_CLAIM = 2

class Directions:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    NEXT = [RIGHT, DOWN, LEFT, UP]
    PREV = [LEFT, UP, RIGHT, DOWN]
    CLOCK = -1
    COUNTER_CLOCK = -2
    TO_CHECK = [[(-1,0),(0,-1),(0,1)], [(-1,0),(+1,0),(0,+1)], [(+1,0),(0,-1),(0,1)],  [(-1,0),(+1,0),(0,-1)] ]

class Colors:
    THEME = game.color.Color("#9a6b52")
    BLACK = game.color.Color("#1F2232")
    QIX = game.color.Color("#7aa1a4")
    PLAYER = game.color.Color("#8b4442")
    BACKGROUND = game.color.Color("#7aa1a4")
    GRID = game.color.Color("#000000")
    FILLED = game.color.Color("#809e4f")
    WALKABLE = game.color.Color("#f9e4af")
    WHITE = game.color.Color("#FFFFFF")
    RED = game.color.Color("#ff0000")
    LIVE = game.color.Color("#baaf94")
    LIGHTBLUE = game.color.Color("#56638A")
    QIX = game.color.Color("#B9E6FF")
    SPARX = game.color.Color("#0892A5")

class GameState:
    INTRO = 0
    SETUP = 1
    START = 2
    PLAYING = 3
    GAME_OVER = 4
    LEVELUP = 5

class MusicState:
    HIT = 0
    ONCLAIM = 1
    SELECT = 2
    GAMEOVER = 3
class ROOM:
    global level
    global state
    player = None
    sprites = None
    qix = None
    percent = 0
    percent_required = 0
    size = 300
    tiles_total = 0
    tiles_claimed = 0
    enemies = []
    sparx_Amount = 1
    def render():
        game.draw.rect(screen,Colors.BLACK,game.Rect(0,0,1400,1000))
        game.draw.rect(screen,Colors.THEME,game.Rect(300,300,825,450))
        createSpace()
        ROOM.sprites.update()
        ROOM.sprites.draw(screen)

    def resetLevel():
        global level
        level = 1
        ROOM.sparx_Amount = 1
        

    def EV():
        global level
        
        level += 1
        ROOM.sparx_Amount += level //2
        ROOM.percent = 0
        
    def addSparx():
        
        for i in range(ROOM.sparx_Amount): 
            xSpawn = r.randint(8,10)*100
            if xSpawn == 800: xSpawn +=10
            if xSpawn == 900: xSpawn +=15
            if xSpawn == 1000: xSpawn += 5
            multiplier = r.randint(0,6)
            
            if i % 2 == 0:
                
                ROOM.enemies.append(Spark(x=xSpawn+(15*multiplier),y=300))
            else:
                
                ROOM.enemies.append(Spark(x=xSpawn+(15*multiplier),y=735))
    def check_gamestate():
        global state
        if ROOM.percent >= ROOM.percent_required:
            ROOM.EV()
            state = GameState.LEVELUP

        if ROOM.player.getLives() == 0:
            state = GameState.GAME_OVER


    def partition():
        global grid
        def grid_replace(old, new):
            global grid
            grid = [[ (tile if tile!=old else new) for tile in row] for row in grid]
        partitions, count, min_value = 10, {}, 100
        for y,row in enumerate(grid):
            for x,tile in enumerate(row):
                if tile == Tile.UNCLAIMED:
                    if grid[y][x-1] >= 10: grid[y][x]=grid[y][x-1]
                    if grid[y-1][x] >= 10:
                        if grid[y][x] == Tile.UNCLAIMED: grid[y][x]=grid[y-1][x]
                        elif grid[y][x] == grid[y][x-1] and grid[y][x]!=grid[y-1][x]: grid_replace( grid[y][x], grid[y-1][x])
                    if grid[y][x] == Tile.UNCLAIMED: grid[y][x], partitions = partitions, partitions+1
        for row in grid:
            for tile in row:
                if tile>=10:
                    if tile not in count: count[tile] = 0
                    else: count[tile]+=1
        if(len(count)>=2): min_value = min(count, key=count.get)
        grid = [
                    [
                        (Tile.UNCLAIMED if tile!=min_value else Tile.FILL)
                    if tile>=10 else tile for tile in row]
                for row in grid ]
        ROOM.tiles_claimed = sum([sum([(0 if tile==Tile.UNCLAIMED else 1) for tile in row]) for row in grid])
        ROOM.check_sparx_stuck()

    def resetGrid():
        ROOM.percent = 0
        ROOM.tiles_claimed = 0
        for r in range(30):
            for c in range(55):
                if r == 0 or r == 29 or c == 0 or c == 54:
                    continue
                else:
                    grid[r][c] = -1

    def check_sparx_stuck():
        for enemy in ROOM.enemies:
            if enemy.checkStuck():
                enemy.state = Spark.State.RECALCULATING



class Character(game.sprite.Sprite):
    def __init__(self, x, y, sizex, sizey, colorSprite):
        game.sprite.Sprite.__init__(self)
        self.image = game.Surface((sizex,sizey))
        self.image.fill(colorSprite)
        self.rect = self.image.get_rect(center=(-sizex//2, -sizey//2))
        # only pass in speed value > 0 for non controlled user items
        self.x = x
        self.y = y
        self.life = 3

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def checkBlock(self): return grid[self.get_yGrid(0)][self.get_xGrid(0)]
    #checking the block ahead of the player
    def checkahead(self,x,y): return grid[y][x]

    def get_xGrid(self,g):
        return int(((self.x+g)-300)/15)
    def get_yGrid(self,g):
        return int(((self.y+g)-300)/15)

    # used to check for valid movement
    def get_x(self):
        return self.x

    # used to check for valid movement
    def get_y(self):
        return self.y

    # Used to decrament the number of lives the user has
    def loseLife(self):

        self.life -= 1

    def getLives(self):
        return self.life

    def resetlives(self):
        self.life = 3

class Spark (Character):
    class State:
        MOVING = 0
        RECALCULATING = 1
        LOOPBREAK = 2
        REVERSING = 3
        PERMALOOP = 4

    def __init__(self,x,y):
        super().__init__(x,y,15,15,Colors.SPARX)
        self.direction = Directions.UP
        self.state = Spark.State.MOVING
        self.dirnext, self.dirprev = Directions.NEXT, Directions.PREV

    def canMove(self,direction):
        row,col = self.get_xGrid(0), self.get_yGrid(0)
        if direction == Directions.UP: return (validatePos(col-1,row)==Tile.CLAIMED or validatePos(col-1,row)==Tile.FILL )
        if direction == Directions.DOWN: return (validatePos(col+1,row)==Tile.CLAIMED or validatePos(col+1,row)==Tile.FILL)
        if direction == Directions.LEFT: return (validatePos(col,row-1)==Tile.CLAIMED or validatePos(col,row-1)==Tile.FILL)
        if direction == Directions.RIGHT: return (validatePos(col,row+1)==Tile.CLAIMED or validatePos(col,row+1)==Tile.FILL)
        return False

    def reverse(self):
        (self.dirnext, self.dirprev) = (self.dirprev, self.dirnext)

    def dirMove(self):
        if self.direction == Directions.UP:      self.move(0,-15)
        if self.direction == Directions.DOWN:    self.move(0,15)
        if self.direction == Directions.LEFT:    self.move(-15,0)
        if self.direction == Directions.RIGHT:   self.move(15,0)

    def checkStuck(self):
        for i in range(4):
            if self.canMove(self.dirprev[self.direction]):
                self.direction=self.dirprev[self.direction]
                self.dirMove()
            else: return False
        return True

    def updateMove(self):
        if self.state==Spark.State.MOVING:
            if self.canMove(self.dirprev[self.direction]):  self.direction=self.dirprev[self.direction]
            elif not self.canMove(self.direction):          self.direction = self.dirnext[self.direction]
            self.dirMove()
        elif self.state==Spark.State.RECALCULATING: # LOOP BREAK CALCULATION
            def check_min(dir, current=(0,0)):
                result = validatePos(current[0]+dir[0],current[1]+dir[1])
                if result == None: return -1000
                if result == Tile.UNCLAIMED: return 0
                if result == Tile.CLAIMED or result == Tile.FILL: return 1+check_min(dir,(current[0]+dir[0],current[1]+dir[1]))
            directions = [ check_min(i,(self.get_yGrid(0), self.get_xGrid(0))) for i in [(-1,0),(1,0),(0,-1),(0,1)] ]# up down left right
            directions = list(map(lambda a,b: (a,b), directions, [Directions.UP, Directions.DOWN, Directions.LEFT, Directions.RIGHT]))
            directions = list(filter(lambda a: a[0]>=0, directions))
            if len(directions)==0:
                self.state = Spark.State.PERMALOOP
            else:
                self.direction = min(directions, key=lambda x:x[0])[1]
                self.state = Spark.State.LOOPBREAK
        elif self.state==Spark.State.LOOPBREAK:
            self.dirMove()
            if not self.canMove(self.direction):
                self.state = Spark.State.MOVING
                self.direction = self.dirnext[self.direction]
        elif self.state==Spark.State.PERMALOOP:
            self.dirMove()
            if not self.canMove(self.dirprev[self.direction]):
                self.state = Spark.State.MOVING

class Qix (Character):
    def __init__(self,x,y,sizex,sizey):
        super().__init__(x,y,sizex,sizey,Colors.QIX)
        self.direction = 0
        self.lastDirection = game.time.get_ticks()
        self.lastMove = game.time.get_ticks()
        self.cooldownDirection = r.randint(100,200)
        self.cooldownMove = 50

    def checkForPath(self):
        x,y = self.get_xGrid(0), self.get_yGrid(0)
        if (self.checkahead(x,y) == Tile.LIVE_CLAIM or self.checkahead(x+1,y) == Tile.LIVE_CLAIM or self.checkahead(x,y+1) == Tile.LIVE_CLAIM or self.checkahead(x+1,y+1) == Tile.LIVE_CLAIM):
            return True
        return False
        
    def canMove(self):
        row,col = self.get_xGrid(0), self.get_yGrid(0)
        if self.direction == Directions.UP and self.get_y() - 15 >= 315: # UP
            if grid[col-1][row] == Tile.UNCLAIMED or grid[col-1][row] == Tile.LIVE_CLAIM: return True # available to move on live path

        if self.direction == Directions.DOWN and self.get_y() + 15 <= 705: # DOWN
            if grid[col+2][row] == Tile.UNCLAIMED or grid[col+2][row] == Tile.LIVE_CLAIM: return True

        if self.direction == Directions.LEFT and self.get_x() - 15 >= 315: # LEFT
            if grid[col][row-1] == Tile.UNCLAIMED or grid[col][row-1] == Tile.LIVE_CLAIM: return True

        if self.direction == Directions.RIGHT and self.get_x() + 15 <= 1080: # RIGHT
            if grid[col][row+2] == Tile.UNCLAIMED or grid[col][row+2] == Tile.LIVE_CLAIM: return True

        return False

    def setDirection(self):

        
        if self.direction == Directions.UP:
            self.move(0,-15)
            self.update()
        if self.direction == Directions.DOWN:
            self.move(0,15)
            self.update()
        if self.direction == Directions.LEFT:
            self.move(-15,0)
            self.update()
        if self.direction == Directions.RIGHT:
            self.move(15,0)
            self.update()

    def updateMove(self):
        now = game.time.get_ticks()
        if (now - self.lastDirection) >= self.cooldownDirection: # get a new direction every
            self.lastDirection = now
            self.direction = r.randint(0,3) # 0:UP | 1:RIGHT | 2:DOWN | 3:LEFT
           
        # Check if in screen space
        # Still have to implement against claimed area **
        now = game.time.get_ticks()
        if (self.canMove() and (now - self.lastMove) >= self.cooldownMove):
            self.lastMove = now
            self.setDirection()

class Player(Character):
    def __init__(self,x,y,sizex,sizey,colorSprite):
        super().__init__(x,y,sizex,sizey,colorSprite)
        self.pushing = False
        self.path = set()
        self.last_DamageTime = game.time.get_ticks()
        self.cooldown_Damage = 1000
        self.lastSprite = game.time.get_ticks()
        self.cooldownSprite = 100
        self.pushStart = (0,0)
    def reset(self):
        self.x = (self.pushStart[0]*15) + 300
        self.y = (self.pushStart[1]*15) + 300

    def startDeath(self):
        self.reset()
        self.loseLife()
        self.removePath()
        self.handleSound(0)
    def handleSound(self, effect_ID):
        if effect_ID == MusicState.HIT:
            hitSound = game.mixer.Sound("Assets/Music/QixDamage.wav")
            game.mixer.Sound.set_volume(hitSound,0.1)
            hitSound.play()
        elif effect_ID == MusicState.ONCLAIM:
            claimSound = game.mixer.Sound("Assets/Music/QixOnClaim.wav")
            game.mixer.Sound.set_volume(claimSound,0.1)
            claimSound.play()
    def updatePushStart(self):
        self.pushStart = (self.get_xGrid(0),self.get_yGrid(0))

    def updateMove(self):
        x,y = self.get_xGrid(0),self.get_yGrid(0)
        keys = game.key.get_pressed()
        went = None

        # Run into your own line results in death
        if ROOM.player.checkBlock() == Tile.LIVE_CLAIM:
            self.startDeath()
            self.removePath()

        # Tracks starting block for push (used in sparx collide with push)
        if ROOM.player.checkBlock() == Tile.CLAIMED:
            self.updatePushStart()

        if keys:
            if keys[game.K_a] and self.get_x() - 15 >= 300:
                gx = ROOM.player.get_xGrid(-15)
                gy = ROOM.player.get_yGrid(0)

                if ROOM.player.checkahead(gx,gy) != Tile.FILL:
                    self.move(-15,0)
                    went = Directions.LEFT

            elif keys[game.K_d] and self.get_x() + 15 <= 1110:
                gx = ROOM.player.get_xGrid(15)
                gy = ROOM.player.get_yGrid(0)

                if ROOM.player.checkahead(gx,gy) != Tile.FILL:
                    self.move(15,0)
                    went = Directions.RIGHT

            elif keys[game.K_w] and self.get_y() - 15 >= 300:
                gx = ROOM.player.get_xGrid(0)
                gy = ROOM.player.get_yGrid(-15)

                if ROOM.player.checkahead(gx,gy) != Tile.FILL:
                    self.move(0,-15)
                    went = Directions.UP

            elif keys[game.K_s] and self.get_y() + 15 <= 735:
                gx = ROOM.player.get_xGrid(0)
                gy = ROOM.player.get_yGrid(15)

                if ROOM.player.checkahead(gx,gy) != Tile.FILL:
                    self.move(0,15)
                    went = Directions.DOWN

            # Finishing a push section
            if keys[game.K_a] or keys[game.K_d] or keys[game.K_w] or keys[game.K_s]:
                self.pushing = True if validatePos(y,x)==Tile.UNCLAIMED else False
                if validatePos(y,x)==Tile.UNCLAIMED: grid[y][x] = Tile.LIVE_CLAIM
                if self.pushing and went != None:
                    x,y,end = self.get_xGrid(0),self.get_yGrid(0),False
                    for to_check in Directions.TO_CHECK[went]:
                        place = validatePos(y+to_check[0], x+to_check[1])
                        if place != Tile.UNCLAIMED and place != Tile.LIVE_CLAIM:
                            grid[y][x] = Tile.CLAIMED
                            ROOM.partition()
                            self.updatePath()
                            self.handleSound(MusicState.ONCLAIM)
                            self.pushing = False
                            break

 
    def updatePath(self):
        for row in range(30):
            for col in range(55):
                if grid[row][col] == Tile.LIVE_CLAIM:
                    grid[row][col] = Tile.CLAIMED

    def removePath(self):
        for row in range(30):
            for col in range(55):
                if grid[row][col] == Tile.LIVE_CLAIM:
                    grid[row][col] = Tile.UNCLAIMED

    def imortalVisual(self,currentTime):
        
        if (currentTime - self.last_DamageTime) < self.cooldown_Damage:
            self.image.fill(Colors.RED)
        else:
            self.image.fill(Colors.PLAYER)

    def checkCollide(self, enemies, qix):
    

        for enemy in enemies:
            current_DeltaTime = game.time.get_ticks()
            x = enemy.get_xGrid(0)
            y = enemy.get_yGrid(0)
            if  ((self.get_x() in range (x, x+1) and self.get_y() in range (y, y+1)) or
                (self.pushStart[0] in range (x,x+1) and self.pushStart[1] in range (y,y+1) ) and
                (current_DeltaTime - self.last_DamageTime) >= self.cooldown_Damage):
                self.last_DamageTime = current_DeltaTime
                self.startDeath()
        
        self.imortalVisual(current_DeltaTime)
            
        xQix = qix.get_xGrid(0)
        yQix = qix.get_yGrid(0)
        current_DeltaTime = game.time.get_ticks()
        if ( ((self.get_xGrid(0) in range(xQix, xQix+1)) and (self.get_yGrid(0) in range(yQix, yQix+1))) or 
        (qix.checkForPath()) and ((current_DeltaTime - self.last_DamageTime) >= self.cooldown_Damage)):
           
            self.last_DamageTime = current_DeltaTime
            self.startDeath()


#----------------------------------Array Baked Grid----------------------------------
def initGrid():
    for row in range(30):
        grid.append([])
        for col in range(55):
            if row == 0 or row == 29 or col == 54 or col == 0:
                grid[row].append(Tile.CLAIMED)
            else:
                grid[row].append(Tile.UNCLAIMED)
initGrid()


def validatePos(col, row):
    if col<0 or row<0: return None
    try: return grid[col][row]
    except IndexError: return None


#--------------------------------------initiation--------------------------------------
def main():

    global screen
    global level
    global state
    game.mixer.pre_init(44100, -16, 2, 2048)
    game.mixer.init()
    game.init()
    clock = game.time.Clock()
    game.display.set_caption("Qix")
    screen = game.display.set_mode([1400, 1000])
    state = GameState.INTRO
    level = 1
    ROOM.sprites = game.sprite.Group()
 
    def getPercentReq(level_num):
        if level_num == 1: return r.randint(25,45)
        if level_num == 2: return r.randint(45,65)
        if level_num == 3: return r.randint(65,80)
        if level_num > 3: return (70 + (level_num)//2)
        return 100
    #-------------------------------------UI CLASS-----------------------------

    class UI:   # This has to be initialized after game.init()

        # -- Flipping visual effect -- #
        flip = False
        _flip = 30
        startWin = False
        # -- Image Loading -- #
        gamefont = game.font.Font("Assets/Font/goodbyeDespair.ttf", 40)
        headerfont = game.font.Font("Assets/Font/goodbyeDespair.ttf", 80)
        s_intro = game.image.load("Assets/Images/Qix Intro.jpg")
        s_end = game.image.load("Assets/Images/gameover.jpeg")
        s_win = game.image.load("Assets/Images/Win.jpg")

        # -- Hearts -- #
        heart_1 = game.image.load("Assets/Images/1heart.png")
        heart_2 = game.image.load("Assets/Images/2heart.png")
        heart_3 = game.image.load("Assets/Images/3heart.png")

        # -- Text -- #
        # Header
        t_head = headerfont.render("Qix",0,Colors.WALKABLE)

        # Intro
        c_header = headerfont.render("Controls",0,Colors.WALKABLE)
        c1 = gamefont.render("Use the WASD keys to move",0,Colors.THEME)
        c2 = gamefont.render("Claim land by splitting the map",0,Colors.THEME)
        # Game Over
        t_end = gamefont.render("You ran out of lives", 0, Colors.THEME)
        t_ready = gamefont.render("Press SPACE to start", 0, Colors.WHITE)
        r_start = gamefont.render("Press SPACE to restart", 0, Colors.THEME)

        r_startnxt = gamefont.render("Press SPACE to Continue", 0, Colors.THEME)
        r_endChoice = gamefont.render("Press SPACE to continue or Mouse 1 to Exit",0,"#06FB84")
        bg_black = game.Rect(0,0,1400,1000)
        
        # -- Sound Effects -- #
        #Sounds
        selectSound = game.mixer.Sound("Assets/Music/QixSelect.wav")
        gameOverMusic = game.mixer.Sound("Assets/Music/QixGameOver.wav")

        # Set Volume
        game.mixer.Sound.set_volume(selectSound,0.1)
        game.mixer.Sound.set_volume(gameOverMusic,0.04)


        ROOM.percent_required = getPercentReq(level)

        def updateFlip(quick=False):
            UI._flip+=1
            if UI._flip>= 300/(60 if quick else 1):
                UI._flip = 0
                UI.flip = not UI.flip

        def renderTitle(): screen.blit(UI.t_head,(650,120))

        def renderReady(): screen.blit(UI.t_ready,(450,620))

        def renderStartNext(): screen.blit(UI.r_startnxt, (300, 800))

        def renderGameOver():
            game.draw.rect(screen,Colors.BLACK,UI.bg_black)
            screen.blit(UI.s_end,(0,0))
            screen.blit(UI.t_end, (500 , 100))
            screen.blit(UI.r_start, (450, 850))
            if event.type == game.QUIT:
                game.quit()

        def soundHandler(sound_ID):
            if sound_ID == MusicState.SELECT:
                UI.selectSound.play(0)
            elif sound_ID == MusicState.GAMEOVER:
                UI.gameOverMusic.play(0)

        def renderNextLevel():
            global level
            if level <= 5:
                t_nextlvl = UI.gamefont.render("Level {} Completed!".format(level-1), 0, Colors.WALKABLE)
                screen.blit(t_nextlvl, (300 , 250))
            
            if level > 5:
                if not UI.startWin:
                    game.mixer.music.stop()
                    game.mixer.music.unload()
                    UI.startWin = True

                screen.blit(UI.s_win,(0,0))
                screen.blit(UI.r_endChoice,(200,850))
                if event.type == game.MOUSEBUTTONDOWN:
                    UI.startWin = False
                    game.quit()
            if event.type == game.QUIT:
                game.quit()


        def updateLife():
            lifeAmount = ROOM.player.getLives()

            if lifeAmount == 1:
                heart = game.transform.scale(UI.heart_1,(200,50))
                screen.blit(heart,(320,245))
            if lifeAmount == 2:
                heart = game.transform.scale(UI.heart_2,(200,50))
                screen.blit(heart,(320,245))
            if lifeAmount == 3:
                heart = game.transform.scale(UI.heart_3,(200,50))
                screen.blit(heart,(320,245))

        def renderIntro():
            #screen.blit(UI.s_intro,(0,0))
            UI.updateFlip(quick=True)
            if UI.flip: screen.blit(UI.t_ready,(475,850))
            screen.blit(UI.c1,(300,200))
            screen.blit(UI.c2,(300,250))

        def renderMain():
            global level
            gamefont = UI.gamefont
            percentage = int((ROOM.tiles_claimed/ROOM.tiles_total)*100)
            ROOM.percent = percentage
            
            if level < 5:
                level_number = gamefont.render("LEVEL {}".format(level), 0, Colors.WALKABLE)
            else:
                level_number = gamefont.render("LEVEL MUAHAHAHHAHAHAHAHA", 0, Colors.WALKABLE)
                
            t_score = gamefont.render("CLAIM: {0}/{1}%".format(ROOM.percent,ROOM.percent_required), 0, Colors.THEME)
            screen.blit(level_number,(950,250))
            screen.blit(t_score,(570,800))

        def setUp(levelValue):
            # character creation
            ROOM.level = levelValue
            ROOM.sprites = game.sprite.Group()
            ROOM.player = Player(x=300,y=300,sizex=15,sizey=15,colorSprite=Colors.PLAYER)
            ROOM.qix = Qix(x=600,y=465,sizex=30,sizey=30) # based off bottom left movement
            
            ROOM.sprites.add(ROOM.player)
            ROOM.sprites.add(ROOM.qix)
            ROOM.enemies = []
            #starting music
            game.mixer.music.stop()
            game.mixer.music.unload()
            game.mixer.music.load("Assets/Music/QixMusic.wav")
            game.mixer.music.play(-1)
            game.mixer.music.set_volume(0.04)
            
            ROOM.addSparx()
            for enemy in ROOM.enemies: ROOM.sprites.add(enemy)
            ahead = 0
            ROOM.tiles_total = sum([ (1 if tile==Tile.UNCLAIMED else 0) for row in grid for tile in row])

    ROOM.player = Player(x=300,y=300,sizex=15,sizey=15,colorSprite=Colors.PLAYER)
    ROOM.sprites.add(ROOM.player)
   
    while True:

        UI.renderTitle()
        #---------------------------------------End screen -----------------------------
        if state==GameState.GAME_OVER:
            UI.renderGameOver()
            if not UI.startWin:
                game.mixer.music.stop()
                UI.soundHandler(MusicState.GAMEOVER)
                UI.startWin = True
            
            game.display.flip()
            event = game.event.poll()
            if event.type == game.KEYDOWN:
                keys = game.key.get_pressed()
                if keys[game.K_SPACE]: 
                    UI.soundHandler(MusicState.SELECT)
                    ROOM.resetLevel()
                    state = GameState.INTRO
            if event.type == game.QUIT:
                    game.quit()
        #---------------------------------------Intro Screen-----------------------------
        if state==GameState.INTRO:
            event = game.event.get()
            for _event in event:
                if _event.type == game.KEYDOWN:
                    keys = game.key.get_pressed()
                    if keys[game.K_SPACE]: 
                        UI.soundHandler(MusicState.SELECT)
                        state = GameState.SETUP

            game.time.wait(65)
            # DELAY
            game.display.flip()
            ROOM.player.updateMove()

            # RENDER UI
            ROOM.render()
            UI.renderIntro()

        #--------------------------------------Round Setup (Go here before start of every round)--
        if state==GameState.SETUP:
            UI.setUp(level)
            ROOM.resetGrid()
            ROOM.percent_required = getPercentReq(level)
            ROOM.percent = 0
            ROOM.player.x = 300
            ROOM.player.y = 300
            state = GameState.START

        #---------------------------------------Level Up -----------------------------
        if state==GameState.LEVELUP:
            game.display.flip()
            ROOM.render()
            UI.updateFlip()
            UI.renderNextLevel()
            
            if UI.flip: UI.renderStartNext()
            event = game.event.poll()
            if event.type == game.KEYDOWN:
                keys = game.key.get_pressed()
                if keys[game.K_SPACE]: 
                    UI.soundHandler(MusicState.SELECT)
                    state = GameState.SETUP
            if event.type == game.QUIT:
                game.quit()

        if state==GameState.START:
            game.display.flip()
            ROOM.render()
            UI.renderMain()
            if UI.flip: UI.renderReady()
            UI.updateLife()
            UI.updateFlip()
            event = game.event.poll()
            
            if event.type == game.KEYDOWN:
                keys = game.key.get_pressed()
                if keys[game.K_SPACE]: 
                    UI.soundHandler(MusicState.SELECT)
                    state = GameState.PLAYING

        #-----------------------------Level 1(will be randomized square at some point)--------------
        if state==GameState.PLAYING:
            # DELAY
            game.time.delay(65)

            # RENDER UI
            UI.renderMain()
            UI.updateLife()
            # LET ALL OBJECTS MOVE
            for enemy in ROOM.enemies: enemy.updateMove()
            ROOM.player.updateMove()
            ROOM.qix.updateMove()
            ROOM.player.checkCollide(ROOM.enemies, ROOM.qix)

            # CHECK TO SEE IF LEVEL UP OR GAME OVER
            ROOM.check_gamestate()

            # QUIT
            for event in game.event.get():
                if event.type == game.QUIT:
                    game.quit()

            game.display.flip()
            ROOM.render()
        # end level

#Visual for grid based system. Allows movement in chunks.
def createSpace():

    # grid layout. X and Y coordinate based system
    cordX, cordY = 300,300
    for r in grid:
        for c in r:
            #pygame object for storing rectangular coordinates
            box = game.Rect(cordX,cordY,15,15)

            # Border conditional, if its on the edge vertically or horizontally draw a red box instead
            if c == Tile.CLAIMED:
                game.draw.rect(screen, Colors.WALKABLE, box)
            elif c == Tile.FILL:
                game.draw.rect(screen,Colors.FILLED if state!=GameState.LEVELUP else Colors.LIGHTBLUE,box)
            elif c == Tile.LIVE_CLAIM:
                game.draw.rect(screen,Colors.LIVE,box)
            #increment square based off size of visual (size 15 per square)
            cordX = 15 + cordX
        cordY = 15 + cordY # increment vertically
        cordX = 300 # reset for new row


main()
