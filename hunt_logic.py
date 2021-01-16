import numpy as np
from copy import copy, deepcopy

class Entit():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.initx = 0
        self.inity = 0

        self.icon = '??'
    def setinit(self):
        self.initx = self.x
        self.inity = self.y
        self.prev_x = self.x
        self.prev_y = self.y
    def revert(self):
        self.x = self.initx
        self.y = self.inity
        self.prev_x = self.x
        self.prev_y = self.y

class Basilesc():
    def __init__(self):

        # self.empty = '<:empty:737044654414889031>'
        self.emp = '  '
        self.wall = '██'



        #constants
        self.xbounds = 32
        self.ybounds = 16


        #variables
        self.levelnum = 1
        self.moves = 0
        self.lives = 3
        self.portalcount = 0

        self.screen = self.getnewmap()
        self.revertscreen = deepcopy(self.screen)
        # entities
        self.player = Entit()
        self.player.icon = '++'
        self.enemy = Entit()
        self.enemy.icon = '# '

        self.xit = Entit()
        self.xit.icon = '><'

        self.portal = Entit()
        self.portal.icon = '0 '
        self.placepeices()

        self.enemybrain = True

        self.victory = False
        self.gameover = False


    def getopenspot(self,ent):

        while(1):
            x = np.random.randint(self.xbounds - 1)
            y = np.random.randint(self.ybounds - 1)
            if self.screen[y][x] == self.emp:
                ent.x = x
                ent.y = y
                return ent

    def placepeices(self):
        if self.levelnum == 2:

            self.player.y = self.ybounds // 4
            self.player.x = self.xbounds // 4
            self.xit.y = (self.ybounds // 4) * 3
            self.xit.x = (self.xbounds // 4) * 3
            self.enemy.y = self.ybounds // 4
            self.enemy.x = (self.xbounds // 4) * 3

        elif self.levelnum == 10:
            self.player.y = self.ybounds // 2
            self.player.x = self.xbounds // 2
            self.enemy.y = self.ybounds - 2
            self.enemy.x = self.xbounds - 2
            self.xit = self.getopenspot(self.xit)


        else:
            self.player = self.getopenspot(self.player)
            self.screen[self.player.y][self.player.x] = self.player.icon
            self.enemy = self.getopenspot(self.enemy)
            self.screen[self.enemy.y][self.enemy.x] = self.enemy.icon
            self.xit = self.getopenspot(self.xit)
            self.screen[self.xit.y][self.xit.x] = self.xit.icon
        self.player.setinit()
        self.enemy.setinit()
        self.xit.setinit()

        x = np.random.randint(self.xbounds - 1)
        y = np.random.randint(self.ybounds - 1)
        if self.levelnum <= 2:
            self.portal.x = -1
            self.portal.y = -1
        elif self.screen[y][x] == self.emp:
            self.portal.x = x
            self.portal.y = y
            self.portal.setinit()

            self.screen[self.portal.y][self.portal.x] = self.portal.icon
        else:
            self.portal.x = -1
            self.portal.y = -1




    def getnewmap(self):
        screen = [[self.emp for i in range(self.xbounds)] for i in range(self.ybounds)]

        for y, i in enumerate(screen):
            for x, e in enumerate(i):
                if ((0 == x) or (0 == y) or ((self.xbounds - 1) == x) or ((self.ybounds - 1) == y)):
                    screen[y][x] = self.wall
                j = np.random.randint(self.xbounds)
                k = np.random.randint(self.ybounds)
                if self.levelnum != 2 and self.levelnum != 10 and (screen[y][x] == self.emp) and ((y * x % 40 //(self.levelnum)) == 0):
                    screen[k][j] = self.wall
                if self.levelnum == 2 and (x == self.xbounds//2 or y == self.ybounds//2):
                    screen[y][x] = self.wall
                if(self.levelnum % 5 == 0)and((x*y%8)==0):
                    screen[y][x] = self.wall



        return screen

    def checkplayerbounds(self):
        if self.player.x < 0:
            self.player.x = 0
        if self.player.y < 0:
            self.player.y = 0

        if self.player.y >= self.ybounds:
            self.player.y = self.ybounds-1
        if self.player.x >= self.xbounds:
            self.player.x = self.xbounds - 1





    def advanceframe(self,inp):

        self.player.prev_x = self.player.x
        self.player.prev_y = self.player.y

        self.moves +=1
        if inp.lower() == 'w':
            self.player.y -= 1
        elif inp.lower() == 's':
            self.player.y += 1
        elif inp.lower() == 'a':
            self.player.x -= 1
        elif inp.lower() == 'd':
            self.player.x += 1

        self.checkplayerbounds()
        #no phasing thru walls
        if self.screen[self.player.y][self.player.x] == self.wall:
            self.player.x = self.player.prev_x
            self.player.y = self.player.prev_y
        #portal get
        if self.screen[self.player.y][self.player.x] == self.portal.icon:
            self.portalcount += 1
        #portal use
        if self.portalcount > 0 :
            if inp.lower() == '0':
                self.portalcount -= 1
                self.player = self.getopenspot(self.player)
        #break wall mechanic
        if self.player.x == self.player.prev_x and self.player.y == self.player.prev_y:
            if inp.lower() == 'w':
                self.player.prev_x = self.player.x + 1
                self.player.prev_y = self.player.y - 1

            elif inp.lower() == 's':
                self.player.prev_x = self.player.x - 1
                self.player.prev_y = self.player.y + 1

            elif inp.lower() == 'a':
                self.player.prev_x = self.player.x - 1
                self.player.prev_y = self.player.y - 1

            elif inp.lower() == 'd':
                self.player.prev_x = self.player.x + 1
                self.player.prev_y = self.player.y + 1


        if inp.lower() == '~':
            self.enemybrain = False


        if self.enemybrain == True:
            if self.player.x > self.enemy.x:
                self.enemy.x += 1 + np.random.randint(2)*-1
            if self.player.y > self.enemy.y:
                self.enemy.y += 1 + np.random.randint(2)*-1
            if self.player.x <  self.enemy.x:
                self.enemy.x += -1 + np.random.randint(2)
            if self.player.y <  self.enemy.y:
                self.enemy.y += -1 + np.random.randint(2)
        if self.enemy.y == self.portal.y and self.enemy.x == self.portal.x:

            self.screen[self.portal.y][self.portal.x]= self.emp
            self.enemy = self.getopenspot(self.enemy)

        self.updateentities()

        if self.screen[self.player.y][self.player.x] == self.xit.icon:
            self.enemybrain = True
            if self.levelnum == 15:
                # GAME HAS BEEN WON
                self.victory = True
                pass
            else:
                self.levelnum += 1
                self.screen = self.getnewmap()
                self.revertscreen = deepcopy(self.screen)
                self.placepeices()
                self.updateentities()
        elif self.screen[self.player.y][self.player.x] == self.enemy.icon:
            if self.lives > 0:
                self.lives-=1
                self.screen = deepcopy(self.revertscreen)
                self.revertentities()
                self.updateentities()
            else:
                self.gameover = True
                # GAME OVER
                pass

    def updateentities(self):
        self.screen[self.player.prev_y][self.player.prev_x] = self.emp
        self.screen[self.player.y][self.player.x] = self.player.icon
        self.screen[self.enemy.y][self.enemy.x] = self.enemy.icon
        self.screen[self.xit.y][self.xit.x] = self.xit.icon
        # self.screen[self.portal.y][self.portal.x] = self.portal.icon


    def revertentities(self):
        self.player.revert()
        self.enemy.revert()
        self.portal.revert()


    def updategame(self,userinput): # assumes single character input
        num_frames_to_advance = len(userinput)
        for i in range(num_frames_to_advance):
            self.advanceframe(userinput[i])


    def getscreenstring(self):
        if self.victory == True:
            status = 'win'
            averagemoves = self.moves // self.levelnum
            grade = averagemoves - self.lives**2
            temp = '```\nSUCCESS!\n\n'
            temp += f'{self.levelnum} Levels Completed\nTotal Moves : {self.moves}\nAverage moves per level: {averagemoves}\nGrade: '
            if grade < 15:
                temp+=f"A#      you turned off the snake didn't you?\n"
            elif grade < 20:
                temp += "A++\n"
            elif grade < 26:
                temp += "A\n"
            elif grade < 33:
                temp += "B++\n"
            elif grade < 40:
                temp += "B\n"
            elif grade < 46:
                temp += "C#\n"
            elif grade < 53:
                temp += "C++\n"
            elif grade < 60:
                temp += "C\n"
            elif grade < 70:
                temp += "D\n"
            else:
                temp += "F+  You tried <3\n"
            temp += '```'

        elif self.gameover == True:
            status = 'lose'
            temp = '```\nGAME OVER\n'
            temp += f'On Level: {self.levelnum}\nTotal Moves before failure: {self.moves}\nGrade: F      \n```\n'
        else:
            status = 'run'
            temp = '```\n'

            temp += f'Level: {self.levelnum}    Lives: {self.lives}     Move Count: {self.moves}     \n'

            for j in self.screen:
                for k in j:
                    temp += k
                temp += '\n'

            temp += '\n'
            temp += f'                                          \n'
            temp += f'You:       {self.player.icon}                    \n'
            temp += f'Objective: {self.xit.icon}               \n'
            temp += f'Portal:    {self.portal.icon}                  \n'
            if self.portalcount == 0:
                temp += f'                                          \n'
            else:
                temp += f'Remaining Uses: {self.portalcount}    \n'

            temp += f'Enemy:     {self.enemy.icon}                   \n'
            temp += '```'
        return temp, status