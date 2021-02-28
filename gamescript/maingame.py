"""
## Known problem
another rare bug where subunit easily get killed for some reason, can't seem to repricate it
autoplacement of 2 units somehow allow the other subunit that stop from retreat to auto place to the enemy side already occupied
Optimise list
melee combat need to be optimised more
change all percentage calculation to float instead of int/100 if possible. Especially number from csv file
remove index and change call to the sprite itself
"""

import datetime
import glob
import random
import numpy as np
import pygame
import sys
import pygame.freetype
from pygame.locals import *
from scipy.spatial import KDTree
from math import hypot

import main
from gamescript import gamesubunit, gameunit, gameui, gameleader, gamemap, gamecamera, rangeattack, gamepopup, gamedrama, gamemenu, gamelongscript, \
    gamelorebook, gameweather, gamefaction, gameunitstat

config = main.config
SoundVolume = main.Soundvolume
SCREENRECT = main.SCREENRECT
main_dir = main.main_dir

load_image = gamelongscript.load_image
load_images = gamelongscript.load_images
csv_read = gamelongscript.csv_read
load_sound = gamelongscript.load_sound

class Battle():
    splitunit = gamelongscript.splitunit
    losscal = gamelongscript.losscal
    traitskillblit = gamelongscript.traitskillblit
    effecticonblit = gamelongscript.effecticonblit
    countdownskillicon = gamelongscript.countdownskillicon

    def __init__(self, main, winstyle):
        # pygame.init()  # Initialize pygame

        # v Get game object/variable from main

        self.eventlog = main.eventlog
        self.battlecamera = main.battlecamera
        self.battleui = main.battleui

        self.unitupdater = main.unitupdater
        self.subunitupdater = main.subunitupdater
        self.leaderupdater = main.leaderupdater
        self.uiupdater = main.uiupdater
        self.weatherupdater = main.weatherupdater
        self.effectupdater = main.effectupdater

        self.battlemapbase = main.battlemapbase
        self.battlemapfeature = main.battlemapfeature
        self.battlemapheight = main.battlemapheight
        self.showmap = main.showmap

        self.team0army = main.team0army
        self.team1army = main.team1army
        self.team2army = main.team2army
        self.team0subunit = main.team0subunit
        self.team1subunit = main.team1subunit
        self.team2subunit = main.team2subunit
        self.subunit = main.subunit
        self.armyleader = main.armyleader

        self.arrows = main.arrows
        self.directionarrows = main.directionarrows
        self.troopnumbersprite = main.troopnumbersprite

        self.gameui = main.gameui
        self.inspectuipos = main.inspectuipos
        self.inspectsubunit = main.inspectsubunit
        self.popgameui = main.gameui  # saving list of gameui that will pop out when parentunit is selected

        self.battlemapbase = main.battlemapbase
        self.battlemapfeature = main.battlemapfeature
        self.battlemapheight = main.battlemapheight
        self.showmap = main.showmap

        self.minimap = main.minimap
        self.eventlog = main.eventlog
        self.logscroll = main.logscroll
        self.buttonui = main.buttonui
        self.subunitselectedborder = main.inspectselectedborder
        self.switchbuttonui = main.switchbuttonui

        self.fpscount = main.fpscount

        self.terraincheck = main.terraincheck
        self.buttonnamepopup = main.buttonnamepopup
        self.leaderpopup = main.leaderpopup
        self.effectpopup = main.effectpopup
        self.textdrama = main.textdrama

        self.skillicon = main.skillicon
        self.effecticon = main.effecticon

        self.battlemenu = main.battlemenu
        self.battlemenubutton = main.battlemenubutton
        self.escoptionmenubutton = main.escoptionmenubutton

        self.armyselector = main.armyselector
        self.armyicon = main.armyicon
        self.selectscroll = main.selectscroll

        self.timeui = main.timeui
        self.timenumber = main.timenumber

        self.scaleui = main.scaleui

        self.speednumber = main.speednumber

        self.weathermatter = main.weathermatter
        self.weathereffect = main.weathereffect

        self.lorebook = main.lorebook
        self.lorenamelist = main.lorenamelist
        self.lorebuttonui = main.lorebuttonui
        self.lorescroll = main.lorescroll
        self.subsectionname = main.subsectionname
        self.pagebutton = main.pagebutton

        self.allweather = main.allweather
        self.weathermatterimgs = main.weathermatterimgs
        self.weathereffectimgs = main.weathereffectimgs

        self.featuremod = main.featuremod

        self.allfaction = main.allfaction
        self.coa = main.coa
        self.teamcolour = main.teamcolour

        self.allweapon = main.allweapon
        self.allarmour = main.allarmour

        self.statusimgs = main.statusimgs
        self.roleimgs = main.roleimgs
        self.traitimgs = main.traitimgs
        self.skillimgs = main.skillimgs

        self.gameunitstat = main.gameunitstat
        self.leaderstat = main.leaderstat

        self.statetext = main.statetext

        self.squadwidth = main.squadwidth
        self.squadheight = main.squadheight
        self.collidedistance = self.squadheight / 5 # distance to check collision

        self.escslidermenu = main.escslidermenu
        self.escvaluebox = main.escvaluebox

        self.screenbuttonlist = main.screenbuttonlist
        self.unitcardbutton = main.unitcardbutton
        self.inspectbutton = main.inspectbutton
        self.colsplitbutton = main.colsplitbutton
        self.rowsplitbutton = main.rowsplitbutton

        self.leaderposname = main.leaderposname
        # ^ End load from main

        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth)  # set up game screen

        #v Assign default variable to some class
        gameunit.Unitarmy.maingame = self
        gamesubunit.Subunit.maingame = self
        gameleader.Leader.maingame = self
        #^ End assign default

        self.background = pygame.Surface(SCREENRECT.size) # Create background image
        self.background.fill((255, 255, 255)) # fill background image with black colour

    def preparenew(self, ruleset, rulesetfolder, teamselected, enactment, mapselected, source, unitscale):

        self.ruleset = ruleset # current ruleset used
        self.rulesetfolder = rulesetfolder # the folder of rulseset used
        self.mapselected = mapselected # map folder name
        self.source = str(source)
        self.unitscale = unitscale
        self.playerteam = teamselected # player selected team

        #v load the sound effects
        # boom_sound = load_sound('boom.wav')
        # shoot_sound = load_sound('car_door.wav')
        #^ End load sound effect

        #v Random music played from list
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, 'data/sound/')
            self.musiclist = glob.glob(main_dir + '/data/sound/music/*.mp3')
            self.pickmusic = random.randint(1, 1)
            pygame.mixer.music.set_endevent(self.SONG_END)
            pygame.mixer.music.load(self.musiclist[self.pickmusic])
            pygame.mixer.music.play(0)
        #^ End music play

        #v Load weather schedule
        try:
            self.weatherevent = csv_read('weather.csv', ["data", 'ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], 1)
            self.weatherevent = self.weatherevent[1:]
            gamelongscript.convertweathertime(self.weatherevent)
        except:  # If no weather found use default light sunny weather start at 9.00
            newtime = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
            self.weatherevent = [[4, newtime, 0]] # default weather light sunny all day
        self.weatherschedule = self.weatherevent[0][1]
        #^ End weather schedule

        try:  # get new map event for event log
            mapevent = csv_read('eventlog.csv', ["data", 'ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], 0)
            gameui.Eventlog.mapevent = mapevent
        except:  # can't find any event file
            mapevent = {}  # create empty list

        self.eventlog.makenew() # reset old event log

        self.eventlog.addeventlog(mapevent)

        self.eventschedule = None
        self.eventlist = []
        for index, event in enumerate(self.eventlog.mapevent):
            if self.eventlog.mapevent[event][3] is not None:
                if index == 0:
                    self.eventmapid = event
                    self.eventschedule = self.eventlog.mapevent[event][3]
                self.eventlist.append(event)

        self.timenumber.startsetup(self.weatherschedule)

        #v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1  # Camera zoom
        gamecamera.Camera.SCREENRECT = SCREENRECT
        self.camera = gamecamera.Camera(self.camerapos, self.camerascale)

        imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], loadorder=False)
        self.battlemapbase.drawimage(imgs[0])
        self.battlemapfeature.drawimage(imgs[1])
        self.battlemapheight.drawimage(imgs[2])
        self.showmap.drawimage(self.battlemapbase, self.battlemapfeature, self.battlemapheight, imgs[3])
        #^ End create battle map

        self.minimap.drawimage(self.showmap.trueimage, self.camera)

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.enactment = enactment  # enactment mod, control both team
        self.mapshown = self.showmap

        #v initialise starting subunit sprites
        gamelongscript.unitsetup(self)

        self.allunitlist = []
        self.allsubunitlist = []
        for group in (self.team0army, self.team1army, self.team2army):
            for army in group:
                self.allunitlist.append(army) # list of every parentunit in game alive

        self.allunitindex = [army.gameid for army in self.allunitlist] # list of every parentunit index alive

        for unit in self.allunitlist: # create troop number text sprite
            self.troopnumbersprite.add(gameunit.Troopnumber(unit))

        for subunit in self.subunit: # list of all subunit alive in game
            self.allsubunitlist.append(subunit)

        self.team0poslist = {} # team 0 parentunit position
        self.team1poslist = {} # team 1 parentunit position
        self.team2poslist = {} # same for team 2
        #^ End start subunit sprite

    def setuparmyicon(self):
        """Setup army selection list in army selector ui top left of screen"""
        row = 30
        startcolumn = 25
        column = startcolumn
        armylist = self.team1army
        if self.enactment == True: # include another team army icon as well in enactment mode
            armylist = self.allunitlist
        currentindex = int(self.armyselector.currentrow * self.armyselector.maxcolumnshow) # the first index of current row
        self.armyselector.logsize = len(armylist) / self.armyselector.maxcolumnshow

        if self.armyselector.logsize.is_integer() == False:
            self.armyselector.logsize = int(self.armyselector.logsize) + 1

        if self.armyselector.currentrow > self.armyselector.logsize - 1:
            self.armyselector.currentrow = self.armyselector.logsize - 1
            currentindex = int(self.armyselector.currentrow * self.armyselector.maxcolumnshow)
            self.selectscroll.changeimage(newrow=self.armyselector.currentrow)

        if len(self.armyicon) > 0:  # Remove all old icon first before making new list
            for icon in self.armyicon:
                icon.kill()
                del icon

        for index, army in enumerate(armylist): # add army icon for drawing according to appopriate current row
            if index >= currentindex:
                self.armyicon.add(gameui.Armyicon((column, row), army))
                column += 40
                if column > 250:
                    row += 50
                    column = startcolumn
                if row > 100: break # do not draw for the third row
        self.selectscroll.changeimage(logsize=self.armyselector.logsize)

    def checksplit(self, whoinput):
        """Check if army can be splitted, if not remove splitting button"""
        #v split by middle collumn
        if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None": # can only split if both parentunit size will be larger than 10 and second leader exist
            self.battleui.add(self.colsplitbutton)
        elif self.colsplitbutton in self.battleui:
            self.colsplitbutton.kill()
        #^ End col

        #v split by middle row
        if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and whoinput.leader[
            1].name != "None":
            self.battleui.add(self.rowsplitbutton)
        elif self.rowsplitbutton in self.battleui:
            self.rowsplitbutton.kill()

    def popoutlorebook(self, section, gameid):
        """open and draw enclycopedia at the specified subsection, used for when user right click at icon that has encyclopedia section"""
        self.gamestate = 0
        self.battlemenu.mode = 2
        self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll, *self.lorebuttonui)

        self.lorebook.changesection(section, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.battleui)
        self.lorebook.changesubsection(gameid, self.pagebutton, self.battleui)
        self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

    def uimouseover(self):
        """mouse over ui that is not subunit card and armybox (topbar and commandbar)"""
        for ui in self.gameui:
            if ui in self.battleui and ui.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                break
        return self.clickany

    def armyiconmouseover(self, mouseup, mouseright):
        """process user mouse input on army icon, left click = select, right click = go to parentunit position on map"""
        self.clickany = True
        self.uiclick = True
        for icon in self.armyicon:
            if icon.rect.collidepoint(self.mousepos):
                if mouseup:
                    self.lastselected = icon.army
                    self.lastselected.justselected = True
                    self.lastselected.selected = True

                elif mouseright:
                    self.basecamerapos = pygame.Vector2(icon.army.basepos[0], icon.army.basepos[1])
                    self.camerapos = self.basecamerapos * self.camerascale
                break
        return self.clickany

    def buttonmouseover(self, mouseright):
        """process user mouse input on various ui buttons"""
        for button in self.buttonui:
            if button in self.battleui and button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True  # for avoiding selecting subunit under ui
                break
        return self.clickany

    def leadermouseover(self, mouseright):
        """process user mouse input on leader portrait in command ui"""
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mousepos):
                if leader.parentunit.commander:
                    armyposition = self.leaderposname[leader.armyposition]
                else:
                    armyposition = self.leaderposname[leader.armyposition+4]

                self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name) # popup leader name when mouse over
                self.battleui.add(self.leaderpopup)
                leadermouseover = True

                if mouseright:
                    self.popoutlorebook(8, leader.gameid)
                break
        return leadermouseover

    def effecticonmouseover(self, iconlist, mouseright):
        effectmouseover = False
        for icon in iconlist:
            if icon.rect.collidepoint(self.mousepos):
                checkvalue = self.gameui[2].value2[icon.type]
                self.effectpopup.pop(self.mousepos, checkvalue[icon.gameid])
                self.battleui.add(self.effectpopup)
                effectmouseover = True
                if mouseright:
                    if icon.type == 0:  # Trait
                        section = 7
                    elif icon.type == 1:  # Skill
                        section = 6
                    else:
                        section = 5  # Status effect
                    self.popoutlorebook(section, icon.gameid)
                break
        return effectmouseover

    def camerafix(self):
        if self.basecamerapos[0] > 999: # camera cannot go further than 999 x
            self.basecamerapos[0] = 999
        elif self.basecamerapos[0] < 0: # camera cannot go less than 0 x
            self.basecamerapos[0] = 0

        if self.basecamerapos[1] > 999:  # same for y
            self.basecamerapos[1] = 999
        elif self.basecamerapos[1] < 0:
            self.basecamerapos[1] = 0

    def rungame(self):
        #v Create Starting Values
        self.mixervolume = SoundVolume
        self.gamestate = 1
        self.mousetimer = 0 # This is timer for checking double mouse click, use realtime
        self.uitimer = 0 # This is timer for ui update function, use realtime
        self.dramatimer = 0 # This is timer for combat related function, use game time (realtime * gamespeed)
        self.dt = 0  # Realtime used for in game calculation
        self.uidt = 0  # Realtime used for ui timer
        self.combattimer = 0 # This is timer for combat related function, use game time (realtime * gamespeed)
        self.lastmouseover = 0 # Which subunit last mouse over
        self.gamespeed = 1 # Current game speed
        self.gamespeedset = (0, 0.5, 1, 2, 4, 6) # availabe game speed
        self.leadernow = [] # list of showing leader in command ui
        self.uiclick = False # for checking if mouse click is on ui
        self.clickany = False  # For checking if mouse click on anything, if not close ui related to parentunit
        self.newarmyclick = False  #  For checking if another subunit is clicked when inspect ui open
        self.inspectui = False # For checking if inspect ui is currently open or not
        self.lastselected = None # Which army is selected last update loop
        self.mapviewmode = 0 # default, another one show height map
        self.subunitselected = None # which subunit in inspect ui is selected in last update loop
        self.beforeselected = None # Which army is selected before
        self.splithappen = False # Check if parentunit get split in that loop
        self.currentweather = None
        self.showtroopnumber = True # for toggle troop number on/off
        self.weatherscreenadjust = SCREENRECT.width / SCREENRECT.height # for weather sprite spawn position
        self.rightcorner = SCREENRECT.width - 5
        self.bottomcorner = SCREENRECT.height - 5
        self.centerscreen = [SCREENRECT.width / 2, SCREENRECT.height / 2] # center position of the screen
        self.battlemousepos = [[0,0], [0, 0]] # mouse position list in game not screen, the first without zoom and the second with camera zoom adjust
        self.teamtroopnumber = [1, 1, 1] # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.lastteamtroopnumber = [1, 1, 1]
        self.armyselector.currentrow = 0
        #^ End start value

        self.setuparmyicon()
        self.selectscroll.changeimage(newrow=self.armyselector.currentrow)
        self.unitupdater.update(self.currentweather, self.subunit, self.dt, self.camerascale,
                                self.battlemousepos[0], False)   # run once at the start of battle to avoid combat bug
        self.effectupdater.update(self.allunitlist, self.dt, self.camerascale)

        # self.leaderupdater.update()
        # self.subunitupdater.update(self.currentweather, self.dt, self.camerascale, self.combattimer)

        while True: # game running
            self.fpscount.fpsshow(self.clock)
            keypress = None
            self.mousepos = pygame.mouse.get_pos() # current mouse pos based on screen
            mouse_up = False # left click
            mouse_down = False # hold left click
            mouse_right = False # right click
            double_mouse_right = False # double right click
            keystate = pygame.key.get_pressed()

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT: # quit game
                    self.battleui.clear(self.screen, self.background)
                    self.battlecamera.clear(self.screen, self.background)
                    pygame.quit()
                    sys.exit()

                elif event.type == self.SONG_END: # change music track
                    # pygame.mixer.music.unload()
                    self.pickmusic = random.randint(1, 1)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)

                elif event.type == KEYDOWN and event.key == K_ESCAPE: # open/close menu
                    if self.gamestate == 1: # in battle
                        self.gamestate = 0 # open munu
                        self.battleui.add(self.battlemenu) # add menu to drawer
                        self.battleui.add(*self.battlemenubutton) # add menu button to

                    else: # in menu
                        if self.battlemenu.mode in (0,1):  # in menu or option
                            if self.battlemenu.mode == 1: # option menu
                                self.mixervolume = self.oldsetting
                                pygame.mixer.music.set_volume(self.mixervolume)
                                self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)
                                self.battlemenu.changemode(0)

                            self.battleui.remove(self.battlemenu)
                            self.battleui.remove(*self.battlemenubutton)
                            self.battleui.remove(*self.escoptionmenubutton)
                            self.battleui.remove(*self.escslidermenu)
                            self.battleui.remove(*self.escvaluebox)
                            self.gamestate = 1

                        elif self.battlemenu.mode == 2: # encyclopedia
                            self.battleui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist)

                            for name in self.subsectionname:
                                name.kill()
                                del name
                            self.battlemenu.changemode(0)

                            if self.battlemenu not in self.battleui:
                                self.gamestate = 1

                if pygame.mouse.get_pressed()[0]:  # Hold left click
                    mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_up = True

                    elif event.button == 4: # Mouse scroll down
                        if self.gamestate == 0 and self.battlemenu.mode == 2:  # Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.currentsubsectionrow -= 1
                                if self.lorebook.currentsubsectionrow < 0:
                                    self.lorebook.currentsubsectionrow = 0
                                else:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

                    elif event.button == 5: # Mouse scroll up
                        if self.gamestate == 0 and self.battlemenu.mode == 2:  # Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.currentsubsectionrow += 1
                                if self.lorebook.currentsubsectionrow + self.lorebook.maxsubsectionshow - 1 < self.lorebook.logsize:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)
                                else:
                                    self.lorebook.currentsubsectionrow -= 1

                #v register user input during gameplay
                if self.gamestate == 1: # game in battle state
                    #v Mouse input
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 3:  # Right Click
                            mouse_right = True
                            if self.mousetimer == 0:
                                self.mousetimer = 0.001  # Start timer after first mouse click
                            elif self.mousetimer < 0.3: # if click again within 0.3 second for it to be considered double click
                                double_mouse_right = True # double right click
                                self.mousetimer = 0

                        elif event.button == 4: # Mouse scroll up
                            if self.eventlog.rect.collidepoint(self.mousepos):  # Scrolling when mouse at event log
                                self.eventlog.currentstartrow -= 1
                                if self.eventlog.currentstartrow < 0: # can go no further than the first log
                                    self.eventlog.currentstartrow = 0
                                else:
                                    self.eventlog.recreateimage() # recreate eventlog image
                                    self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)

                            elif self.armyselector.rect.collidepoint(self.mousepos):  # Scrolling when mouse at army selector
                                self.armyselector.currentrow -= 1
                                if self.armyselector.currentrow < 0:
                                    self.armyselector.currentrow = 0
                                else:
                                    self.setuparmyicon()
                                    self.selectscroll.changeimage(newrow=self.armyselector.currentrow)

                            else:  # Scrolling in game map to zoom
                                self.camerascale += 1
                                if self.camerascale > 10:
                                    self.camerascale = 10
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.mapshown.changescale(self.camerascale)

                        elif event.button == 5: # Mouse scroll down
                            if self.eventlog.rect.collidepoint(self.mousepos):  # Scrolling when mouse at event log
                                self.eventlog.currentstartrow += 1
                                if self.eventlog.currentstartrow + self.eventlog.maxrowshow - 1 < self.eventlog.lencheck and self.eventlog.lencheck > 9:
                                    self.eventlog.recreateimage()
                                    self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)
                                else:
                                    self.eventlog.currentstartrow -= 1

                            elif self.armyselector.rect.collidepoint(self.mousepos):  # Scrolling when mouse at army selector ui
                                self.armyselector.currentrow += 1
                                if self.armyselector.currentrow < self.armyselector.logsize:
                                    self.setuparmyicon()
                                    self.selectscroll.changeimage(newrow=self.armyselector.currentrow)
                                else:
                                    self.armyselector.currentrow -= 1
                                    if self.armyselector.currentrow < 0:
                                        self.armyselector.currentrow = 0

                            else:  # Scrolling in game map to zoom
                                self.camerascale -= 1
                                if self.camerascale < 1:
                                    self.camerascale = 1
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.mapshown.changescale(self.camerascale)
                    #^ End mouse input

                    #v keyboard input
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            if self.mapviewmode == 0:  # Currently in normal mode
                                self.mapviewmode = 1
                                self.showmap.changemode(self.mapviewmode)
                            else:  # Currently in height mode
                                self.mapviewmode = 0
                                self.showmap.changemode(self.mapviewmode)
                            self.mapshown.changescale(self.camerascale)

                        elif event.key == pygame.K_o:  # Speed Pause/unpause Button
                            if self.showtroopnumber:
                                self.showtroopnumber = False
                                self.effectupdater.remove(*self.troopnumbersprite)
                                self.battlecamera.remove(*self.troopnumbersprite)
                            else: # speed currently pause
                                self.showtroopnumber = True
                                self.effectupdater.add(*self.troopnumbersprite)
                                self.battlecamera.add(*self.troopnumbersprite)

                        elif event.key == pygame.K_p:  # Speed Pause/unpause Button
                            if self.gamespeed >= 0.5: #
                                self.gamespeed = 0 # pause game speed
                            else: # speed currently pause
                                self.gamespeed = 1 # unpause game and set to speed 1
                            self.speednumber.speedupdate(self.gamespeed)

                        elif event.key == pygame.K_KP_MINUS: # reduce game speed
                            newindex = self.gamespeedset.index(self.gamespeed) - 1
                            if newindex >= 0: # cannot reduce game speed than what is available
                                self.gamespeed = self.gamespeedset[newindex]
                            self.speednumber.speedupdate(self.gamespeed)

                        elif event.key == pygame.K_KP_PLUS: # increase game speed
                            newindex = self.gamespeedset.index(self.gamespeed) + 1
                            if newindex < len(self.gamespeedset):  # cannot increase game speed than what is available
                                self.gamespeed = self.gamespeedset[newindex]
                            self.speednumber.speedupdate(self.gamespeed)

                        elif event.key == pygame.K_PAGEUP:  # Go to top of event log
                            self.eventlog.currentstartrow = 0
                            self.eventlog.recreateimage()
                            self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)

                        elif event.key == pygame.K_PAGEDOWN:  # Go to bottom of event log
                            if self.eventlog.lencheck > self.eventlog.maxrowshow:
                                self.eventlog.currentstartrow = self.eventlog.lencheck - self.eventlog.maxrowshow
                                self.eventlog.recreateimage()
                                self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)

                        elif event.key == pygame.K_SPACE and self.lastselected is not None:
                            whoinput.command(self.battlemousepos, mouse_right, double_mouse_right,
                                             self.lastmouseover, keystate, othercommand=1)

                        #v FOR DEVELOPMENT DELETE LATER
                        elif event.key == pygame.K_1:
                            self.textdrama.queue.append('Hello and Welcome to update video')
                        elif event.key == pygame.K_2:
                            self.textdrama.queue.append('Showcase: Complete overhaul of battle mechanic')
                        elif event.key == pygame.K_3:
                            self.textdrama.queue.append('Now each sub-unit is a sprite instead of a whole unit')
                        elif event.key == pygame.K_4:
                            self.textdrama.queue.append('The combat mechanic will be much more dynamic')
                        elif event.key == pygame.K_5:
                            self.textdrama.queue.append('Will take a while for everything to work again')
                        elif event.key == pygame.K_6:
                            self.textdrama.queue.append('Current special effect still need rework')
                        elif event.key == pygame.K_n and self.lastselected is not None:
                            if whoinput.team == 1:
                                self.allunitindex = whoinput.switchfaction(self.team1army, self.team2army, self.team1poslist, self.allunitindex,
                                                                           self.enactment)
                            else:
                                self.allunitindex = whoinput.switchfaction(self.team2army, self.team1army, self.team2poslist, self.allunitindex,
                                                                           self.enactment)
                        elif event.key == pygame.K_l and self.lastselected is not None:
                            for subunit in whoinput.subunitsprite:
                                subunit.basemorale = 0
                        elif event.key == pygame.K_k and self.lastselected is not None:
                            # for index, subunit in enumerate(self.lastselected.subunitsprite):
                            #     subunit.unithealth -= subunit.unithealth
                            self.subunitselected.who.unithealth -= self.subunitselected.who.unithealth
                        elif event.key == pygame.K_m and self.lastselected is not None:
                            self.lastselected.leader[0].health -= 1000
                        #^ End For development test

                        else: # pressing other keys (Not hold)
                            keypress = event.key
                    #^ End keyboard input
                #^ End register input

            self.battleui.clear(self.screen, self.background)  # Clear sprite before update new one
            if self.gamestate == 1: # game in battle state
                self.uiupdater.update()  # update ui
                self.teamtroopnumber = [1, 1, 1] # reset troop count

                #v Camera movement
                if keystate[K_s] or self.mousepos[1] >= self.bottomcorner:  # Camera move down
                    self.basecamerapos[1] += 5 * (11 - self.camerascale) # need "11 -" for converting cameral scale so the further zoom camera move faster
                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale # resize camera pos
                    self.camerafix()

                elif keystate[K_w] or self.mousepos[1] <= 5:  # Camera move up
                    self.basecamerapos[1] -= 5 * (11 - self.camerascale)
                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                    self.camerafix()

                if keystate[K_a] or self.mousepos[0] <= 5:  # Camera move left
                    self.basecamerapos[0] -= 5 * (11 - self.camerascale)
                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                    self.camerafix()

                elif keystate[K_d] or self.mousepos[0] >= self.rightcorner:  # Camera move right
                    self.basecamerapos[0] += 5 * (11 - self.camerascale)
                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                    self.camerafix()

                self.cameraupcorner = (self.camerapos[0] - self.centerscreen[0], self.camerapos[1] - self.centerscreen[1]) # calculate top left corner of camera position
                #^ End camera movement

                self.battlemousepos[0] = pygame.Vector2((self.mousepos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                        self.mousepos[1] - self.centerscreen[1] + self.camerapos[1]) # mouse pos on the map based on camare position
                self.battlemousepos[1] = self.battlemousepos[0] / self.camerascale # mouse pos on the map at current camera zoom scale

                if self.mousetimer != 0: # player click mouse once before
                    self.mousetimer += self.uidt # increase timer for mouse click using real time
                    if self.mousetimer >= 0.3: # time pass 0.3 second no longer count as double click
                        self.mousetimer = 0

                if self.terraincheck in self.battleui and (
                        self.terraincheck.pos != self.mousepos or keystate[K_s] or keystate[K_w] or keystate[K_a] or keystate[K_d]):
                    self.battleui.remove(self.terraincheck) # remove terrain popup when move mouse or camera

                if mouse_up or mouse_right or mouse_down:
                    self.uiclick = False # reset mouse check on ui, if stay false it mean mouse click is not on any ui
                    if mouse_up:
                        self.clickany = False
                        self.newarmyclick = False
                    if self.minimap.rect.collidepoint(self.mousepos): # mouse position on mini map
                        if mouse_up: # move game camera to position clicked on mini map
                            posmask = pygame.Vector2(int(self.mousepos[0] - self.minimap.rect.x), int(self.mousepos[1] - self.minimap.rect.y))
                            self.basecamerapos = posmask * 5
                            self.camerapos = self.basecamerapos * self.camerascale
                            self.clickany = True
                            self.uiclick = True
                        elif mouse_right: # nothing happen with mouse right
                            if self.lastselected is not None:
                                self.uiclick = True

                    elif self.logscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before event log ui
                        self.clickany = True
                        self.uiclick = True
                        if mouse_down or mouse_up:
                            newrow = self.logscroll.update(self.mousepos)
                            if self.eventlog.currentstartrow != newrow:
                                self.eventlog.currentstartrow = newrow
                                self.eventlog.recreateimage()

                    elif self.selectscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before army select ui
                        self.clickany = True
                        self.uiclick = True
                        if mouse_down or mouse_up:
                            newrow = self.selectscroll.update(self.mousepos)
                            if self.armyselector.currentrow != newrow:
                                self.armyselector.currentrow = newrow
                                self.setuparmyicon()

                    elif self.eventlog.rect.collidepoint(self.mousepos): # check mouse collide for event log ui
                        self.clickany = True
                        self.uiclick = True

                    elif self.timeui.rect.collidepoint(self.mousepos): # check mouse collide for time bar ui
                        self.clickany = True
                        self.uiclick = True

                    elif self.armyselector.rect.collidepoint(self.mousepos): # check mouse collide for army selector ui
                        self.armyiconmouseover(mouse_up, mouse_right)

                    elif self.uimouseover(): # check mouse collide for other ui
                        pass

                    elif self.buttonmouseover(mouse_right): # check mouse collide for button
                        pass

                    elif mouse_right and self.lastselected is None and self.uiclick == False: # draw terrain popup ui when right click at map with no selected parentunit
                        if self.battlemousepos[1][0] >= 0 and self.battlemousepos[1][0] <= 999 and self.battlemousepos[1][1] >= 0 and \
                                self.battlemousepos[1][1] <= 999: # not draw if pos is off the map
                            terrainpop, featurepop = self.battlemapfeature.getfeature(self.battlemousepos[1], self.battlemapbase)
                            featurepop = self.battlemapfeature.featuremod[featurepop]
                            heightpop = self.battlemapheight.getheight(self.battlemousepos[1])
                            self.terraincheck.pop(self.mousepos, featurepop, heightpop)
                            self.battleui.add(self.terraincheck)

                    for index, button in enumerate(self.screenbuttonlist):  # Event log button and timer button click
                        if button.rect.collidepoint(self.mousepos):
                            if index in (0, 1, 2, 3, 4, 5):  # eventlog button
                                self.uiclick = True
                                if mouse_up:
                                    if button.event in (0, 1, 2, 3): # change tab mode
                                        self.eventlog.changemode(button.event)
                                    elif button.event == 4: # delete tab log button
                                        self.eventlog.cleartab()
                                    elif button.event == 5: # delete all tab log button
                                        self.eventlog.cleartab(alltab=True)

                            elif index in (6, 7, 8):  # timer button
                                self.uiclick = True
                                if mouse_up:
                                    if button.event == 0: # pause button
                                        self.gamespeed = 0
                                    elif button.event == 1: # reduce speed button
                                        newindex = self.gamespeedset.index(self.gamespeed) - 1
                                        if newindex >= 0:
                                            self.gamespeed = self.gamespeedset[newindex]
                                    elif button.event == 2: # increase speed button
                                        newindex = self.gamespeedset.index(self.gamespeed) + 1
                                        if newindex < len(self.gamespeedset):
                                            self.gamespeed = self.gamespeedset[newindex]
                                    self.speednumber.speedupdate(self.gamespeed)
                            break

                #v Event log timer
                if self.eventschedule is not None and self.eventlist != [] and self.timenumber.timenum >= self.eventschedule:
                    self.eventlog.addlog(None,None,eventmapid=self.eventmapid)
                    for event in self.eventlog.mapevent:
                        if self.eventlog.mapevent[event][3] is not None and self.eventlog.mapevent[event][3] > self.timenumber.timenum:
                            self.eventmapid = event
                            self.eventschedule = self.eventlog.mapevent[event][3]
                            break
                    self.eventlist = self.eventlist[1:]
                #^ End event log timer

                #v Weather system
                if self.weatherschedule is not None and self.timenumber.timenum >= self.weatherschedule:
                    del self.currentweather
                    weather = self.weatherevent[0]

                    if weather[0] != 0:
                        self.currentweather = gameweather.Weather(self.timeui, weather[0], weather[2], self.allweather)
                    else: # Random weather
                        self.currentweather = gameweather.Weather(self.timeui, random.randint(0, 11), random.randint(0, 2), self.allweather)
                    self.weatherevent.pop(0)
                    self.showmap.addeffect(self.battlemapheight, self.weathereffectimgs[self.currentweather.type][self.currentweather.level])

                    try: # Get end time of next event which is now index 0
                        self.weatherschedule = self.weatherevent[0][1]
                    except:
                        self.weatherschedule = None

                if self.currentweather.spawnrate > 0 and len(self.weathermatter) < self.currentweather.speed:
                    spawnnum = range(0, int(self.currentweather.spawnrate * self.dt * random.randint(0, 10))) # number of sprite to spawn at this time
                    for spawn in spawnnum: # spawn each weather sprite
                        truepos = (random.randint(10, SCREENRECT.width), 0) # starting pos
                        target = (truepos[0], SCREENRECT.height) # final target pos

                        if self.currentweather.spawnangle == 225: # top right to bottom left movement
                            startpos = random.randint(10, SCREENRECT.width * 2) # starting x pos that can be higher than screen width
                            truepos = (startpos, 0)
                            if startpos >= SCREENRECT.width: # x higher than screen width will spawn on the right corner of screen but not at top
                                startpos = SCREENRECT.width # revert x back to screen width
                                truepos = (startpos, random.randint(0, SCREENRECT.height))

                            if truepos[1] > 0:  # start position simulate from beyond top right of screen
                                target = (truepos[1] * self.weatherscreenadjust, SCREENRECT.height)
                            elif truepos[0] < SCREENRECT.width:  # start position inside screen width
                                target = (0, truepos[0] / self.weatherscreenadjust)

                        elif self.currentweather.spawnangle == 270: # right to left movement
                            truepos = (SCREENRECT.width, random.randint(0, SCREENRECT.height))
                            target = (0, truepos[1])

                        randompic = random.randint(0, len(self.weathermatterimgs[self.currentweather.type]) - 1)
                        self.weathermatter.add(gameweather.Mattersprite(truepos, target,
                                                                        self.currentweather.speed,
                                                                        self.weathermatterimgs[self.currentweather.type][randompic]))

                #v code that only run when any subunit is selected
                if self.lastselected is not None and self.lastselected.state != 100:
                    whoinput = self.lastselected
                    if self.beforeselected is None:  # add back the pop up ui to group so it get shown when click subunit with none selected before
                        self.gameui = self.popgameui
                        self.battleui.add(*self.gameui[0:2])  # add leader and top ui
                        self.battleui.add(self.inspectbutton)  # add inspection ui open/close button

                        if whoinput.control:
                            self.battleui.add(self.buttonui[7])  # add decimation button
                            self.battleui.add(*self.switchbuttonui[0:6])  # add parentunit behaviour change button
                            self.switchbuttonui[0].event = whoinput.useskillcond
                            self.switchbuttonui[1].event = whoinput.fireatwill
                            self.switchbuttonui[2].event = whoinput.hold
                            self.switchbuttonui[3].event = whoinput.useminrange
                            self.switchbuttonui[4].event = whoinput.shoothow
                            self.switchbuttonui[5].event = whoinput.runtoggle
                            self.checksplit(whoinput)  # check if selected parentunit can split, if yes draw button

                        self.leadernow = whoinput.leader
                        self.battleui.add(*self.leadernow) # add leader portrait to draw
                        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)

                    elif self.beforeselected != self.lastselected:  # change subunit information on ui when select other parentunit
                        if self.inspectui == True: # change inspect ui
                            self.newarmyclick = True
                            self.battleui.remove(*self.inspectsubunit)

                            for index, subunit in enumerate(whoinput.subunitspritearray.flat):
                                if subunit is not None:
                                    self.inspectsubunit[index].addsubunit(subunit)
                                    self.battleui.add(self.inspectsubunit[index])

                            self.subunitselected = self.inspectsubunit[0]
                            self.subunitselectedborder.pop(self.subunitselected.pos)
                            self.battleui.add(self.subunitselectedborder)
                            self.gameui[2].valueinput(who=self.subunitselected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                      splithappen=self.splithappen)
                        self.battleui.remove(*self.leadernow)

                        if whoinput.control:
                            self.battleui.add(self.buttonui[7])  # add decimation button
                            self.battleui.add(*self.switchbuttonui[0:6])  # add parentunit behaviour change button
                            self.switchbuttonui[0].event = whoinput.useskillcond
                            self.switchbuttonui[1].event = whoinput.fireatwill
                            self.switchbuttonui[2].event = whoinput.hold
                            self.switchbuttonui[3].event = whoinput.useminrange
                            self.switchbuttonui[4].event = whoinput.shoothow
                            self.switchbuttonui[5].event = whoinput.runtoggle
                            self.checksplit(whoinput)
                        else:
                            if self.rowsplitbutton in self.battleui:
                                self.rowsplitbutton.kill()
                            if self.colsplitbutton in self.battleui:
                                self.colsplitbutton.kill()
                            self.battleui.remove(self.buttonui[7])  # add decimation button
                            self.battleui.remove(*self.switchbuttonui[0:6])  # add parentunit behaviour change button

                        self.leadernow = whoinput.leader
                        self.battleui.add(*self.leadernow)
                        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)

                    else: # Update topbar and command ui value every 1.1 seconds
                        if self.uitimer >= 1.1:
                            self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                            self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)
                    if self.inspectbutton.rect.collidepoint(self.mousepos) or (
                            mouse_up and self.inspectui and self.newarmyclick): # mouse on inspect ui open/close button
                        if self.inspectbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Inspect Subunit")
                            self.battleui.add(self.buttonnamepopup)
                            if mouse_right:
                                self.uiclick = True # for some reason the loop mouse check above does not work for inspect button, so it here instead
                        if mouse_up:
                            if self.inspectui == False:  # Add army inspect ui when left click at ui button or when change subunit with inspect open
                                self.inspectui = True
                                self.battleui.add(*self.gameui[2:4])
                                self.battleui.add(*self.unitcardbutton)
                                for index, subunit in enumerate(whoinput.subunitspritearray.flat):
                                    if subunit is not None:
                                        self.inspectsubunit[index].addsubunit(subunit)
                                        self.battleui.add(self.inspectsubunit[index])
                                self.subunitselected = self.inspectsubunit[0]
                                self.subunitselectedborder.pop(self.subunitselected.pos)
                                self.battleui.add(self.subunitselectedborder)
                                self.gameui[2].valueinput(who=self.subunitselected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                          splithappen=self.splithappen)

                                if self.gameui[2].option == 2: # blit skill icon is previous mode is skill
                                    self.traitskillblit()
                                    self.effecticonblit()
                                    self.countdownskillicon()

                            elif self.inspectui:  # Remove when click again and the ui already open
                                self.battleui.remove(*self.inspectsubunit)
                                self.battleui.remove(self.subunitselectedborder)
                                for ui in self.gameui[2:4]: ui.kill()
                                for button in self.unitcardbutton: button.kill()
                                self.inspectui = False
                                self.newarmyclick = False

                    elif self.gameui[1] in self.battleui and (self.gameui[1].rect.collidepoint(self.mousepos) or keypress is not None): # mouse position on command ui
                        if whoinput.control:
                            if self.switchbuttonui[0].rect.collidepoint(self.mousepos) or keypress == pygame.K_g:
                                if mouse_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                    whoinput.useskillcond += 1
                                    if whoinput.useskillcond > 3:
                                        whoinput.useskillcond = 0
                                    self.switchbuttonui[0].event = whoinput.useskillcond
                                if self.switchbuttonui[0].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                    self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[0].event])
                                    self.battleui.add(self.buttonnamepopup)

                            elif self.switchbuttonui[1].rect.collidepoint(self.mousepos) or keypress == pygame.K_f:
                                if mouse_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                    whoinput.fireatwill += 1
                                    if whoinput.fireatwill > 1:
                                        whoinput.fireatwill = 0
                                    self.switchbuttonui[1].event = whoinput.fireatwill
                                if self.switchbuttonui[1].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Fire at will", "Hold fire until order")
                                    self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[1].event])
                                    self.battleui.add(self.buttonnamepopup)

                            elif self.switchbuttonui[2].rect.collidepoint(self.mousepos) or keypress == pygame.K_h:
                                if mouse_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                    whoinput.hold += 1
                                    if whoinput.hold > 2:
                                        whoinput.hold = 0
                                    self.switchbuttonui[2].event = whoinput.hold
                                if self.switchbuttonui[2].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                    self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[2].event])
                                    self.battleui.add(self.buttonnamepopup)

                            elif self.switchbuttonui[3].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                    whoinput.useminrange += 1
                                    if whoinput.useminrange > 1:
                                        whoinput.useminrange = 0
                                    self.switchbuttonui[3].event = whoinput.useminrange
                                if self.switchbuttonui[3].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Shoot from min range", "Shoot from max range")
                                    self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[3].event])
                                    self.battleui.add(self.buttonnamepopup)

                            elif self.switchbuttonui[4].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                    whoinput.shoothow += 1
                                    if whoinput.shoothow > 2:
                                        whoinput.shoothow = 0
                                    self.switchbuttonui[4].event = whoinput.shoothow
                                if self.switchbuttonui[4].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Allow both arc and direct shot", "Allow only arc shot", "Allow only direct shot")
                                    self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[4].event])
                                    self.battleui.add(self.buttonnamepopup)

                            elif self.switchbuttonui[5].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                    whoinput.runtoggle += 1
                                    if whoinput.runtoggle > 1:
                                        whoinput.runtoggle = 0
                                    self.switchbuttonui[5].event = whoinput.runtoggle
                                if self.switchbuttonui[5].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                    poptext = ("Toggle walk", "Toggle run")
                                    self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[5].event])
                                    self.battleui.add(self.buttonnamepopup)

                            elif self.colsplitbutton in self.battleui and self.colsplitbutton.rect.collidepoint(self.mousepos):
                                self.buttonnamepopup.pop(self.mousepos, "Split by middle column")
                                self.battleui.add(self.buttonnamepopup)
                                if mouse_up and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                                    self.splitunit(whoinput, 1)
                                    self.splithappen = True
                                    self.checksplit(whoinput)
                                    self.battleui.remove(*self.leadernow)
                                    self.leadernow = whoinput.leader
                                    self.battleui.add(*self.leadernow)
                                    self.setuparmyicon()

                            elif self.rowsplitbutton in self.battleui and self.rowsplitbutton.rect.collidepoint(self.mousepos):
                                self.buttonnamepopup.pop(self.mousepos, "Split by middle row")
                                self.battleui.add(self.buttonnamepopup)
                                if mouse_up and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                                    self.splitunit(whoinput, 0)
                                    self.splithappen = True
                                    self.checksplit(whoinput)
                                    self.battleui.remove(*self.leadernow)
                                    self.leadernow = whoinput.leader
                                    self.battleui.add(*self.leadernow)
                                    self.setuparmyicon()

                            elif self.buttonui[7].rect.collidepoint(self.mousepos):  # decimation effect
                                self.buttonnamepopup.pop(self.mousepos, "Decimation")
                                self.battleui.add(self.buttonnamepopup)
                                if mouse_up and whoinput.state == 0:
                                    for subunit in whoinput.subunitsprite:
                                        subunit.statuseffect[98] = self.gameunitstat.statuslist[98].copy()
                                        subunit.unithealth -= round(subunit.unithealth * 0.1)
                        if self.leadermouseover(mouse_right):
                            self.battleui.remove(self.buttonnamepopup)
                            pass
                    else:
                        self.battleui.remove(self.leaderpopup) # remove leader name popup if no mouseover on any button
                        self.battleui.remove(self.buttonnamepopup)  # remove popup if no mouseover on any button

                    if self.inspectui: # if inspect ui is openned
                        # self.battleui.add(*self.inspectsubunit)
                        if mouse_up or mouse_right:
                            if self.gameui[3].rect.collidepoint(self.mousepos): # if mouse pos inside armybox ui when click
                                self.clickany = True # for avoding right click or  subunit
                                self.uiclick = True  # for avoiding clicking subunit under ui
                                for subunit in self.inspectsubunit:
                                    if subunit.rect.collidepoint(self.mousepos) and subunit in self.battleui:  # Change showing stat to the clicked subunit one
                                        if mouse_up:
                                            self.subunitselected = subunit
                                            self.subunitselectedborder.pop(self.subunitselected.pos)
                                            self.eventlog.addlog(
                                                [0, str(self.subunitselected.who.boardpos) + " " + str(self.subunitselected.who.name) + " in " +
                                                 self.subunitselected.who.parentunit.leader[0].name + "'s parentunit is selected"], [3])
                                            self.battleui.add(self.subunitselectedborder)
                                            self.gameui[2].valueinput(who=self.subunitselected.who, weaponlist=self.allweapon,
                                                                      armourlist=self.allarmour, splithappen=self.splithappen)

                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            else:
                                                for icon in self.skillicon.sprites(): icon.kill()
                                                for icon in self.effecticon.sprites(): icon.kill()

                                        elif mouse_right:
                                            self.popoutlorebook(3, subunit.unitid)
                                        break

                            elif self.gameui[2].rect.collidepoint(self.mousepos): # mouse position in subunit card
                                self.clickany = True
                                self.uiclick = True  # for avoiding clicking subunit under ui
                                for button in self.unitcardbutton:  # Change subunit card option based on button clicking
                                    if button.rect.collidepoint(self.mousepos):
                                        self.clickany = True
                                        self.uiclick = True
                                        if self.gameui[2].option != button.event:
                                            self.gameui[2].option = button.event
                                            self.gameui[2].valueinput(who=self.subunitselected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                      changeoption=1, splithappen=self.splithappen)

                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            else:
                                                for icon in self.skillicon.sprites(): icon.kill()
                                                for icon in self.effecticon.sprites(): icon.kill()
                                        break

                        if (self.uitimer >= 1.1 and self.gameui[2].option != 0) or \
                                self.beforeselected != self.lastselected:  # Update value of the clicked subunit every 1.1 second
                            self.gameui[2].valueinput(who=self.subunitselected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                      splithappen=self.splithappen)
                            if self.gameui[2].option == 2: # skill and status effect card
                                self.countdownskillicon()
                                self.effecticonblit()
                                if self.beforeselected != self.lastselected: # change subunit, reset trait icon as well
                                    self.traitskillblit()
                                    self.countdownskillicon()
                            else:
                                for icon in self.skillicon.sprites(): icon.kill()
                                for icon in self.effecticon.sprites(): icon.kill()

                        if self.gameui[2].option == 2:
                            if self.effecticonmouseover(self.skillicon, mouse_right):
                                pass
                            elif self.effecticonmouseover(self.effecticon, mouse_right):
                                pass
                            else:
                                self.battleui.remove(self.effectpopup)

                        if self.splithappen:  # change showing subunit in inspectui if split happen
                            self.battleui.remove(*self.inspectsubunit)
                            self.inspectsubunit = whoinput.subunitsprite
                            self.battleui.add(*self.inspectsubunit)
                            self.splithappen = False
                    else:
                        for icon in self.skillicon.sprites(): icon.kill()
                        for icon in self.effecticon.sprites(): icon.kill()

                    if (mouse_up or mouse_right) and self.uiclick == False: # Unit command
                        whoinput.command(self.battlemousepos, mouse_right, double_mouse_right,
                                         self.lastmouseover, keystate)

                    self.beforeselected = self.lastselected

                    if self.uitimer >= 1.1: # reset ui timer every 1.1 seconds
                        self.uitimer -= 1.1
                #^ End subunit selected code

                self.lastmouseover = 0  # reset last parentunit mouse over
                # fight_sound.play()

                #v Drama text function
                if self.dramatimer == 0 and len(self.textdrama.queue) != 0:  # Start timer and add to allui If there is event queue
                    self.battleui.add(self.textdrama)
                    self.textdrama.processqueue()
                    self.dramatimer = 0.1
                elif self.dramatimer > 0:
                    self.textdrama.playanimation()
                    self.dramatimer += self.uidt
                    if self.dramatimer > 3:
                        self.dramatimer = 0
                        self.battleui.remove(self.textdrama)
                #^ End drama

                #v Updater
                tree = KDTree([sprite.basepos for sprite in self.allsubunitlist]) # collision loop check
                collisions = tree.query_pairs(self.collidedistance)
                for one, two in collisions:
                    if self.allsubunitlist[one].frontsidepos.distance_to(self.allsubunitlist[two].basepos) < 2: # first subunit collision
                        self.allsubunitlist[one].frontcollide.append(self.allsubunitlist[two])
                        self.allsubunitlist[one].parentunit.collide = True
                    else:
                        self.allsubunitlist[one].sidecollide.append(self.allsubunitlist[two])
                    if self.allsubunitlist[two].frontsidepos.distance_to(self.allsubunitlist[one].basepos) < 2: # second subunit
                        self.allsubunitlist[two].frontcollide.append(self.allsubunitlist[one])
                        self.allsubunitlist[two].parentunit.collide = True
                    else:
                        self.allsubunitlist[two].sidecollide.append(self.allsubunitlist[one])

                self.unitupdater.update(self.currentweather, self.subunit, self.dt, self.camerascale,
                                        self.battlemousepos[0], mouse_up)
                self.leaderupdater.update()
                self.subunitupdater.update(self.currentweather, self.dt, self.camerascale, self.combattimer,
                                         self.battlemousepos[0], mouse_up)

                if self.uitimer > 1:
                    self.scaleui.changefightscale(self.teamtroopnumber) # change fight colour scale on timeui bar
                    self.lastteamtroopnumber = self.teamtroopnumber

                if self.combattimer >= 0.5: # reset combat timer every 0.5 seconds
                    self.combattimer -= 0.5 # not reset to 0 because higher speed can cause inconsistency in update timing
                    for subunit in self.subunit: # Reset every subunit battleside after updater since doing it in updater cause bug for defender
                        subunit.battleside = [None, None, None, None]  # Reset battleside to defualt
                        subunit.battlesideid = [0, 0, 0, 0]

                self.effectupdater.update(self.subunit, self.dt, self.camerascale)
                self.weatherupdater.update(self.dt, self.timenumber.timenum)
                self.camera.update(self.camerapos, self.battlecamera)
                self.minimap.update(self.camerascale, [self.camerapos, self.cameraupcorner], self.team1poslist, self.team2poslist)
                #^ End updater

                #v Remove the subunit ui when click at no group
                if self.clickany == False: # not click at any parentunit
                    if self.lastselected is not None: # any parentunit is selected
                        self.lastselected = None # reset lastselected


                    self.gameui[2].option = 1 # reset subunit card option
                    for ui in self.gameui: ui.kill() # remove ui
                    for button in self.buttonui[0:8]: button.kill() # remove button
                    for icon in self.skillicon.sprites(): icon.kill() # remove skill and trait icon
                    for icon in self.effecticon.sprites(): icon.kill() # remove effect icon
                    self.battleui.remove(*self.switchbuttonui) # remove change parentunit behaviour button
                    self.battleui.remove(*self.inspectsubunit) # remove subunit sprite in army inspect ui
                    self.inspectui = False # inspect ui close
                    self.beforeselected = None # reset before selected parentunit after remove last selected
                    self.battleui.remove(*self.leadernow) # remove leader image from command ui
                    self.subunitselected = None # reset subunit selected
                    self.battleui.remove(self.subunitselectedborder) # remove subunit selected border sprite
                    self.leadernow = [] # clear leader list in command ui
                #^ End remove

                #v Update game time
                self.dt = self.clock.get_time() / 1000 # dt before gamespeed
                self.uitimer += self.dt # ui update by real time instead of game time to reduce workload
                self.uidt = self.dt # get ui timer before apply game speed
                self.dt = self.dt * self.gamespeed # apply dt with gamespeed for ingame calculation
                self.combattimer += self.dt # update combat timer
                self.timenumber.timerupdate(self.dt*10) # update ingame time with 5x speed
                #^ End update game time

            else: # Complete game pause when open either esc menu or enclycopedia
                if self.battlemenu.mode == 0: # main esc menu
                    for button in self.battlemenubutton:
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1] # change button image to mouse over one
                            if mouse_up: # click on button
                                button.image = button.images[2] # change button image to clicked one
                                if button.text == "Resume": # resume game
                                    self.gamestate = 1 # resume battle gameplay state
                                    self.battleui.remove(self.battlemenu, *self.battlemenubutton, *self.escslidermenu, *self.escvaluebox) # remove menu sprite

                                elif button.text == "Encyclopedia": # open encyclopedia
                                    self.battlemenu.mode = 2 # change to enclycopedia mode
                                    self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll, *self.lorebuttonui) # add sprite related to encyclopedia
                                    self.lorebook.changesection(0, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.battleui)
                                    # self.lorebook.setupsubsectionlist(self.lorenamelist, listgroup)

                                elif button.text == "Option": # open option menu
                                    self.battlemenu.changemode(1) # change to option menu mode
                                    self.battleui.remove(*self.battlemenubutton) # remove main esc menu button
                                    self.battleui.add(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox)
                                    self.oldsetting = self.escslidermenu[0].value  # Save previous setting for in case of cancel

                                elif button.text == "Main Menu": # back to main menu
                                    self.battleui.clear(self.screen, self.background) # remove all sprite
                                    self.battlecamera.clear(self.screen, self.background) # remove all sprite

                                    self.battleui.remove(self.battlemenu, *self.battlemenubutton, *self.escslidermenu,
                                                         *self.escvaluebox)  # remove menu sprite
                                    for group in (self.subunit, self.armyleader, self.team0army, self.team1army, self.team2army,
                                                  self.armyicon, self.troopnumbersprite, self.inspectsubunit):
                                        for stuff in group:
                                            stuff.delete()
                                            stuff.kill()
                                            del stuff
                                    for arrow in self.arrows: # remove all range attack
                                        arrow.kill()
                                        del arrow
                                    self.subunitselected = None
                                    self.allunitlist = []
                                    self.team0poslist, self.team1poslist, self.team2poslist = {}, {}, {}
                                    self.beforeselected = None

                                    return # end battle game loop

                                elif button.text == "Desktop": # quit game
                                    self.battleui.clear(self.screen, self.background) # remove all sprite
                                    self.battlecamera.clear(self.screen, self.background) # remove all sprite
                                    sys.exit() # quit
                                break # found clicked button, break loop
                        else:
                            button.image = button.images[0]

                elif self.battlemenu.mode == 1: # option menu
                    for button in self.escoptionmenubutton: # check if any button get collided with mouse or clicked
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1] # change button image to mouse over one
                            if mouse_up: # click on button
                                button.image = button.images[2] # change button image to clicked one
                                if button.text == "Confirm": # confirm button, save the setting and close option menu
                                    self.oldsetting = self.mixervolume # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume) # set new music player volume
                                    main.editconfig('DEFAULT', 'SoundVolume', str(slider.value), 'configuration.ini', config) # save to config file
                                    self.battlemenu.changemode(0) # go back to main esc menu
                                    self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox) # remove option menu sprite
                                    self.battleui.add(*self.battlemenubutton) # add main esc menu buttons back

                                elif button.text == "Apply": # apply button, save the setting
                                    self.oldsetting = self.mixervolume # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume) # set new music player volume
                                    main.editconfig('DEFAULT', 'SoundVolume', str(slider.value), 'configuration.ini', config) # save to config file

                                elif button.text == "Cancel": # cancel button, revert the setting to the last saved one
                                    self.mixervolume = self.oldsetting # revert to old setting
                                    pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                    self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True) # update slider bar
                                    self.battlemenu.changemode(0) # go back to main esc menu
                                    self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox) # remove option menu sprite
                                    self.battleui.add(*self.battlemenubutton) # add main esc menu buttons back

                        else: # no button currently collided with mouse
                            button.image = button.images[0] # revert button image back to the idle one

                    for slider in self.escslidermenu:
                        if slider.rect.collidepoint(self.mousepos) and (mouse_down or mouse_up): # mouse click on slider bar
                            slider.update(self.mousepos, self.escvaluebox[0]) # update slider button based on mouse value
                            self.mixervolume = float(slider.value / 100) # for now only music volume slider exist

                elif self.battlemenu.mode == 2:  # Encyclopedia mode
                    if mouse_up or mouse_down: # mouse down (hold click) only for subsection listscroller
                        if mouse_up:
                            for button in self.lorebuttonui:
                                if button in self.battleui and button.rect.collidepoint(self.mousepos): # click button
                                    if button.event in range(0, 11): # section button
                                        self.lorebook.changesection(button.event, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.battleui) # change to section of that button
                                    elif button.event == 19:  # Close button
                                        self.battleui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist) # remove enclycopedia related sprites
                                        for name in self.subsectionname: # remove subsection name
                                            name.kill()
                                            del name
                                        self.battlemenu.changemode(0) # change menu back to default 0
                                        if self.battlemenu not in self.battleui: # in case open encyclopedia via right click on icon or other way
                                            self.gamestate = 1 # resume gameplay
                                    elif button.event == 20:  # Previous page button
                                        self.lorebook.changepage(self.lorebook.page - 1, self.pagebutton, self.battleui) # go back 1 page
                                    elif button.event == 21:  # Next page button
                                        self.lorebook.changepage(self.lorebook.page + 1, self.pagebutton, self.battleui) # go forward 1 page
                                    break # found clicked button, break loop

                            for name in self.subsectionname: # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                if name.rect.collidepoint(self.mousepos): # click on subsection name
                                    self.lorebook.changesubsection(name.subsection, self.pagebutton, self.battleui) # change subsection
                                    break # found clicked subsection, break loop

                        if self.lorescroll.rect.collidepoint(self.mousepos): # click on subsection list scroller
                            self.lorebook.currentsubsectionrow = self.lorescroll.update(self.mousepos) # update the scroller and get new current subsection
                            self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname) # update subsection name list

            self.screen.blit(self.camera.image, (0, 0))  # Draw the game camera and everything that appear in it
            self.battleui.draw(self.screen)  # Draw the UI
            pygame.display.update() # update game display, draw everything
            self.clock.tick(60) # clock update even if game pause

        if pygame.mixer: # close music player
            pygame.mixer.music.fadeout(1000)

        pygame.time.wait(1000) # wait a bit before closing
        pygame.quit()
