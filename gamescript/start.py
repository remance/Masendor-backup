import csv
import gc
import glob
import os.path
import sys
import configparser
import screeninfo
from pathlib import Path

# import basic pygame modules
import pygame
import pygame.freetype
from gamescript import map, weather, lorebook, drama, battleui, commonscript, popup, menu, uniteditor

from pygame.locals import *

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read
load_sound = commonscript.load_sound
edit_config = commonscript.edit_config
make_bar_list = commonscript.make_bar_list
load_base_button = commonscript.load_base_button
text_objects = commonscript.text_objects
setup_list = commonscript.setup_list
list_scroll = commonscript.list_scroll
version_name = "Dream Decision"

# Will keep leader, subunit, unit and other state as magic number since changing them take too much space, see below for refencing

unit_state_text = {0: "Idle", 1: "Walking", 2: "Running", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)",
                  7: "Walk (F)", 8: "Run (F)", 10: "Fighting", 11: "shooting", 65: "Sleeping", 66: "Camping", 67: "Resting", 68: "Dancing",
                  69: "Partying", 95: "Disobey", 96: "Retreating", 97: "Collapse", 98: "Retreating", 99: "Broken", 100: "Destroyed"}

subunit_state_text = {0: "Idle", 1: "Walk", 2: "Run", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)", 10: "Melee", 11: "Shoot",
                                  12: "Walk (S)", 13: "Run (S)", 95: "Disobey", 96: "Flee", 97: "Rest", 98: "Flee", 99: "Broken", 100: "Dead"}

leader_state_text = {96: "Flee", 97: "POW", 98: "MIA", 99: "WIA", 100: "KIA"}

morale_state_text = {0: "Broken", 1: "Fleeing", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                             6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready", 11: "Merry", 12: "Elated", 13: "Ecstatic",
                             14: "Inspired", 15: "Fervent"}  # parentunit morale state name

stamina_state_text = {0: "Collapse", 1: "Exhausted", 2: "Severed", 3: "Very Tired", 4: "Tired", 5: "Winded", 6: "Moderate",
                 7: "Alert", 8: "Warmed Up", 9: "Active", 10: "Fresh"}  # parentunit stamina state name

quality_text = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")  # item quality name


class Mainmenu:
    leaderposname = ("Commander", "Sub-General", "Sub-General", "Sub-Commander", "General", "Sub-General", "Sub-General",
                     "Advisor")  # Name of leader position in parentunit, the first 4 is for commander parentunit
    teamcolour = ((255, 255, 255), (144, 167, 255), (255, 114, 114))  # team colour, Neutral, 1, 2
    popup_list_open = commonscript.popup_list_open
    lorebook_process = lorebook.lorebook_process

    def __init__(self, main_dir):
        pygame.init()  # Initialize pygame

        self.main_dir = main_dir

        # v Read config file
        config = configparser.ConfigParser()
        try:
            config.read_file(open("configuration.ini"))  # read config file
        except Exception:  # Create config file if not found with the default
            genre_folder = Path(os.path.join(self.main_dir, "gamescript"))
            genre_folder = [x for x in genre_folder.iterdir() if x.is_dir()]
            genre_folder = [str(foldername).split("\\")[-1].capitalize() for foldername in genre_folder]
            genre_folder.remove("__pycache__")  # just grab the first genre folder as default

            config = configparser.ConfigParser()

            screen = screeninfo.get_monitors()[0]
            screen_width = int(screen.width)
            screen_height = int(screen.height)

            config["DEFAULT"] = {"ScreenWidth": screen_width, "ScreenHeight": screen_height, "Fullscreen": "0",
                                 "PlayerName": "Noname", "SoundVolume": "100.0", "MusicVolume": "0.0",
                                 "VoiceVolume": "0.0", "MaxFPS": "60", "Ruleset": "1", "Genre": genre_folder[-1]}
            with open("configuration.ini", "w") as cf:
                config.write(cf)
            config.read_file(open("configuration.ini"))

        self.config = config
        self.screen_height = int(self.config["DEFAULT"]["ScreenHeight"])
        self.screen_width = int(self.config["DEFAULT"]["ScreenWidth"])
        self.FULLSCREEN = int(self.config["DEFAULT"]["Fullscreen"])
        self.Soundvolume = float(self.config["DEFAULT"]["SoundVolume"])
        self.profile_name = str(self.config["DEFAULT"]["PlayerName"])
        self.genre = str(self.config["DEFAULT"]["Genre"])
        self.ruleset = 1  # for now default historical ruleset only
        # ^ End read config

        # v Set the display mode
        self.SCREENRECT = Rect(0, 0, self.screen_width, self.screen_height)
        self.screen_scale = (self.SCREENRECT.width / 1366, self.SCREENRECT.height / 768)
        self.winstyle = 0
        if FULLSCREEN == 1:  # FULLSCREEN
            self.winstyle = pygame.FULLSCREEN
        self.bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, self.winstyle, 32)
        self.screen = pygame.display.set_mode(self.SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)
        # ^ End set display

        self.ruleset_list = csv_read(self.main_dir, "ruleset_list.csv", ["data", "ruleset"])  # get ruleset list
        self.ruleset_folder = str(self.ruleset_list[self.ruleset][1]).strip("/").strip("\\")

        if not os.path.exists("../profile"):  # make profile folder if not existed
            os.makedirs("../profile")
            os.makedirs("../profile/unitpreset")
        if not os.path.exists("profile/unitpreset/" + str(self.ruleset)):  # create unitpreset folder for ruleset
            os.makedirs("profile/unitpreset/" + str(self.ruleset))
        try:
            customunitpresetlist = csv_read(self.main_dir, "custom_unitpreset.csv", ["profile", "unitpreset", str(self.ruleset)])
            del customunitpresetlist["presetname"]
            self.customunitpresetlist = {"New Preset": 0, **customunitpresetlist}
        except Exception:
            with open("profile/unitpreset/" + str(self.ruleset) + "/custom_unitpreset.csv", "w") as csvfile:
                filewriter = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(["presetname", "unitline2", "unitline2", "unitline3", "unitline4", "unitline15", "unitline6",
                                     "unitline7", "unitline8", "leader", "leaderposition", "faction"])  # create header
                csvfile.close()

            self.customunitpresetlist = {}

        # if not os.path.exists("\customunit"): # make custom subunit folder if not existed

        self.enactment = True
        self.state_text = unit_state_text

        self.map_source = 0  # current selected map source
        self.team_selected = 1
        self.current_popup_row = 0

        # v Decorate the game window
        # icon = load_image(self.main_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)
        # ^ End decorate

        # v Initialise Game Groups
        # gamestart menu object group
        self.main_ui = pygame.sprite.LayeredUpdates()  # sprite drawer group
        self.menu_button = pygame.sprite.Group()  # group of menu buttons that are currently get shown and update
        self.menu_icon = pygame.sprite.Group()  # mostly for option icon like volumne or scren resolution

        self.menu_slider = pygame.sprite.Group()
        self.map_listbox = pygame.sprite.Group()  # ui box for map list
        self.map_namegroup = pygame.sprite.Group()  # map name list group
        self.map_show = pygame.sprite.Group()  # preview image of selected map
        self.team_coa = pygame.sprite.Group()  # team coat of arm that also act as team selection icon
        self.map_title = pygame.sprite.Group()  # map title box
        self.map_description = pygame.sprite.Group()  # map description box in map select screen
        self.source_description = pygame.sprite.Group()  # map source description box in preset battle preparation screen
        self.army_stat = pygame.sprite.Group()  # ui box that show army stat in preset battle preparation screen

        self.source_namegroup = pygame.sprite.Group()  # source name list group

        self.tickbox = pygame.sprite.Group()  # option tick box

        self.lore_button_ui = pygame.sprite.Group()  # buttons for enclycopedia group
        self.value_box = pygame.sprite.Group()  # value number and box in esc menu option
        self.lore_name_list = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
        self.subsection_name = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lore_name_list

        self.troop_listbox = pygame.sprite.Group()  # ui box for troop name list
        self.troop_namegroup = pygame.sprite.Group()  # troop name list group
        self.filter_box = pygame.sprite.Group()
        self.popup_listbox = pygame.sprite.Group()
        self.popup_namegroup = pygame.sprite.Group()
        self.terrain_change_button = pygame.sprite.Group()  # button to change preview map base terrain
        self.feature_change_button = pygame.sprite.Group()  # button to change preview map terrain feature
        self.weather_change_button = pygame.sprite.Group()  # button to change preview map weather
        self.unit_build_slot = pygame.sprite.Group()  # slot for putting troop into unit preset during preparation mode
        self.unit_edit_border = pygame.sprite.Group()  # border that appear when selected sub-subunit
        self.preview_leader = pygame.sprite.Group()  # just to make preview leader class has containers
        self.unitpreset_namegroup = pygame.sprite.Group()  # preset name list

        # battle object group
        self.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer game camera, all image pos should be based on the map not screen
        # the camera layer is as followed 0 = terrain map, 1 = dead unit, 2 = map special feature, 3 = , 4 = subunit, 5 = sub-subunit,
        # 6 = flying parentunit, 7 = arrow/range, 8 = weather, 9 = weather matter, 10 = ui/button, 11 = subunit inspect, 12 pop up
        self.battle_ui = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

        self.unit_updater = pygame.sprite.Group()  # updater for parentunit objects
        self.subunit_updater = pygame.sprite.Group()  # updater for subunit objects
        self.leader_updater = pygame.sprite.Group()  # updater for leader objects
        self.ui_updater = pygame.sprite.Group()  # updater for ui objects
        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.effect_updater = pygame.sprite.Group()  # updater for in-game effect objects (e.g. range attack sprite)

        self.battle_map_base = pygame.sprite.Group()  # base terrain map object
        self.battle_map_feature = pygame.sprite.Group()  # terrain feature map object
        self.battle_map_height = pygame.sprite.Group()  # height map object
        self.show_map = pygame.sprite.Group()  # beautiful map object that is shown in gameplay

        self.team0_unit = pygame.sprite.Group()  # taem 0 units group
        self.team1_unit = pygame.sprite.Group()  # taem 1 units group
        self.team2_unit = pygame.sprite.Group()  # team 2 units group

        self.team0_subunit = pygame.sprite.Group()  # taem 0 units group
        self.team1_subunit = pygame.sprite.Group()  # taem 1 units group
        self.team2_subunit = pygame.sprite.Group()  # team 2 units group

        self.subunit = pygame.sprite.Group()  # all subunits group

        self.army_leader = pygame.sprite.Group()  # all leaders group

        self.range_attacks = pygame.sprite.Group()  # all range_attacks group and maybe other range effect stuff later
        self.direction_arrows = pygame.sprite.Group()
        self.troop_number_sprite = pygame.sprite.Group()  # troop text number that appear next to parentunit sprite

        self.dead_unit = pygame.sprite.Group()  # dead subunit group

        self.gameui = pygame.sprite.Group()  # various game ui group
        self.mini_map = pygame.sprite.Group()  # mini_map ui
        self.eventlog = pygame.sprite.Group()  # event log ui
        self.button_ui = pygame.sprite.Group()  # buttons for various ui group
        self.inspect_selected_border = pygame.sprite.Group()  # subunit selected border in inspect ui unit box
        self.fps_count = pygame.sprite.Group()  # fps number counter
        self.switch_button_ui = pygame.sprite.Group()  # button that switch image based on current setting (e.g. parentunit behaviour setting)

        self.terrain_check = pygame.sprite.Group()  # terrain information pop up ui
        self.buttonname_popup = pygame.sprite.Group()  # button name pop up ui when mouse over button
        self.leader_popup = pygame.sprite.Group()  # leader name pop up ui when mouse over leader image in command ui
        self.effect_popup = pygame.sprite.Group()  # effect name pop up ui when mouse over status effect icon
        self.drama_text = pygame.sprite.Group()  # dramatic text effect (announcement) object

        self.skill_icon = pygame.sprite.Group()  # skill and trait icon objects
        self.effect_icon = pygame.sprite.Group()  # status effect icon objects

        self.battle_menu = pygame.sprite.Group()  # esc menu object
        self.battle_menu_button = pygame.sprite.Group()  # buttons for esc menu object group
        self.escoption_menu_button = pygame.sprite.Group()  # buttons for esc menu option object group
        self.slidermenu = pygame.sprite.Group()  # volume slider in esc option menu

        self.unit_selector = pygame.sprite.Group()  # unit selector ui
        self.unit_icon = pygame.sprite.Group()  # unit icon object group in unit selector ui

        self.time_ui = pygame.sprite.Group()  # time bar ui
        self.time_number = pygame.sprite.Group()  # number text of in-game time
        self.speed_number = pygame.sprite.Group()  # number text of current game speed

        self.scale_ui = pygame.sprite.Group()  # battle scale bar

        self.weather_matter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen
        # ^ End initialise

        # v Assign default groups
        # gamestart menu containers
        menu.MenuButton.containers = self.menu_button
        menu.MenuIcon.containers = self.menu_icon
        menu.SliderMenu.containers = self.menu_slider, self.slidermenu
        menu.ValueBox.containers = self.value_box

        menu.ListBox.containers = self.map_listbox, self.troop_listbox, self.popup_listbox
        menu.NameList.containers = self.map_namegroup
        menu.MapShow.containers = self.map_show
        menu.TeamCoa.containers = self.team_coa
        menu.MapTitle.containers = self.map_title
        menu.MapDescription.containers = self.map_description
        menu.SourceDescription.containers = self.source_description
        menu.ArmyStat.containers = self.army_stat

        menu.SourceName.containers = self.source_namegroup, self.main_ui

        menu.TickBox.containers = self.tickbox

        lorebook.SubsectionList.containers = self.lore_name_list
        lorebook.SubsectionName.containers = self.subsection_name, self.main_ui, self.battle_ui

        battleui.UIButton.containers = self.lore_button_ui

        uniteditor.PreviewBox.main_dir = self.main_dir
        img = load_image(self.main_dir, "effect.png", "map")  # map special effect image
        uniteditor.PreviewBox.effectimage = img
        uniteditor.FilterBox.containers = self.filter_box
        uniteditor.PreviewChangeButton.containers = self.terrain_change_button, self.weather_change_button, self.feature_change_button
        uniteditor.Unitbuildslot.containers = self.unit_build_slot
        uniteditor.PreviewLeader.containers = self.preview_leader

        # battle containers
        map.BaseMap.containers = self.battle_map_base
        map.FeatureMap.containers = self.battle_map_feature
        map.HeightMap.containers = self.battle_map_height
        map.BeautifulMap.containers = self.show_map, self.battle_camera

        battleui.GameUI.containers = self.gameui, self.ui_updater
        battleui.Minimap.containers = self.mini_map, self.battle_ui
        battleui.FPScount.containers = self.battle_ui
        battleui.UIButton.containers = self.button_ui, self.lore_button_ui
        battleui.SwitchButton.containers = self.switch_button_ui, self.ui_updater
        battleui.SelectedSquad.containers = self.inspect_selected_border, self.unit_edit_border, self.main_ui, self.battle_ui
        battleui.SkillCardIcon.containers = self.skill_icon, self.battle_ui
        battleui.EffectCardIcon.containers = self.effect_icon, self.battle_ui
        battleui.EventLog.containers = self.eventlog
        battleui.ArmySelect.containers = self.unit_selector, self.battle_ui
        battleui.ArmyIcon.containers = self.unit_icon, self.battle_ui
        battleui.TimeUI.containers = self.time_ui, self.battle_ui
        battleui.Timer.containers = self.time_number, self.battle_ui
        battleui.ScaleUI.containers = self.scale_ui, self.battle_ui
        battleui.SpeedNumber.containers = self.speed_number, self.battle_ui

        popup.TerrainPopup.containers = self.terrain_check
        popup.OnelinePopup.containers = self.buttonname_popup, self.leader_popup
        popup.EffecticonPopup.containers = self.effect_popup

        drama.TextDrama.containers = self.drama_text

        menu.Escbox.containers = self.battle_menu
        menu.Escbutton.containers = self.battle_menu_button, self.escoption_menu_button

        weather.Mattersprite.containers = self.weather_matter, self.battle_ui, self.weather_updater
        weather.Specialeffect.containers = self.weather_effect, self.battle_ui, self.weather_updater
        # ^ End assign

        commonscript.load_game_data(self)  # load common data

        # v genre related stuff
        boximg = load_image(self.main_dir, "genre_box.png", "ui\\mainmenu_ui")
        self.genre_change_box = uniteditor.PreviewChangeButton(self.screen_scale, (boximg.get_width() / 2 * self.screen_scale[0],
                                                                      boximg.get_height() * self.screen_scale[1]), boximg, self.genre.capitalize())
        self.change_genre(self.genre)
        # ^ End genre

        self.clock = pygame.time.Clock()
        self.game_intro(self.screen, self.clock, False)  # run game intro

    def change_genre(self, genre):
        """Add new genre module here"""
        if type(genre) == int:
            self.genre = self.genrelist[genre].lower()
        else:
            self.genre = genre.lower()
        global battle, leader, longscript, unit, subunit, rangeattack, uniteditor
        if self.genre == "tactical":
            from gamescript.tactical import battle, leader, longscript, unit, subunit, rangeattack
            longscript.load_game_data(self)  # obtain game stat data and create lore book object
        elif self.genre == "arcade":
            from gamescript.arcade import battle, leader, longscript, unit, subunit, rangeattack
            longscript.load_game_data(self)
        uniteditor.Unitbuildslot.create_troop_stat = subunit.create_troop_stat
        self.genre_change_box.changetext(self.genre.capitalize())
        edit_config("DEFAULT", "genre", self.genre, "configuration.ini", self.config)


        unit.Unit.containers = self.unit_updater
        subunit.Subunit.containers = self.subunit_updater, self.subunit, self.battle_camera
        leader.Leader.containers = self.army_leader, self.leader_updater
        unit.TroopNumber.containers = self.troop_number_sprite, self.effect_updater, self.battle_camera

        rangeattack.RangeArrow.containers = self.range_attacks, self.effect_updater, self.battle_camera
        unit.DirectionArrow.containers = self.direction_arrows, self.effect_updater, self.battle_camera

        # v Create gamestart menu button
        imagelist = load_base_button(self.main_dir)
        for index, image in enumerate(imagelist):
            imagelist[index] = pygame.transform.scale(image, (int(image.get_width() * self.screen_scale[0]),
                                                              int(image.get_height() * self.screen_scale[1])))
        self.preset_map_button = menu.MenuButton(self.screen_scale, imagelist,
                                                 pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 8.5)),
                                                 menu_state="mainmenu", text="Preset Map")
        self.custom_map_button = menu.MenuButton(self.screen_scale, imagelist,
                                                 pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 7)),
                                                 menu_state="mainmenu", text="Custom Map")
        self.game_edit_button = menu.MenuButton(self.screen_scale, imagelist,
                                                pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 5.5)),
                                                menu_state="mainmenu", text="Unit Editor")
        self.lore_button = menu.MenuButton(self.screen_scale, imagelist,
                                           pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                           menu_state="mainmenu", text="Encyclopedia")
        self.option_button = menu.MenuButton(self.screen_scale, imagelist,
                                             pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                             menu_state="mainmenu", text="Option")
        self.quit_button = menu.MenuButton(self.screen_scale, imagelist,
                                           pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height())),
                                           menu_state="mainmenu", text="Quit")
        self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.game_edit_button,
                                self.lore_button, self.option_button, self.quit_button)
        # ^ End gamestart menu button

        # v Create battle map menu button
        bottomheight = self.SCREENRECT.height - imagelist[0].get_height()
        self.select_button = menu.MenuButton(self.screen_scale, imagelist, pos=(self.SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                             text="Select")
        self.start_button = menu.MenuButton(self.screen_scale, imagelist, pos=(self.SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                            text="Start")
        self.map_back_button = menu.MenuButton(self.screen_scale, imagelist,
                                               pos=(self.SCREENRECT.width - (self.SCREENRECT.width - imagelist[0].get_width()), bottomheight),
                                               text="Back")
        self.map_select_button = (self.select_button, self.map_back_button)
        self.battle_setup_button = (self.start_button, self.map_back_button)

        imgs = load_images(self.main_dir, ["ui", "mapselect_ui"], loadorder=False)
        self.map_listbox = menu.ListBox(self.screen_scale, (self.SCREENRECT.width / 25, self.SCREENRECT.height / 20), imgs[0])
        self.map_scroll = battleui.UIScroller(self.map_listbox.rect.topright, self.map_listbox.image.get_height(),
                                              self.map_listbox.maxshowlist, layer=14)  # scroller bar for map list

        self.source_listbox = menu.SourceListBox(self.screen_scale, (0, 0), imgs[1])  # source list ui box
        self.map_optionbox = menu.MapOptionBox(self.screen_scale, (self.SCREENRECT.width, 0), imgs[1],
                                               0)  # ui box for battle option during preparation screen

        self.tickbox_enactment = menu.TickBox(self.screen_scale, (self.map_optionbox.rect.bottomright[0] / 1.2, self.map_optionbox.rect.bottomright[1] / 4),
                                              imgs[5], imgs[6], "enactment")
        self.tickbox.add(self.tickbox_enactment)
        if self.enactment:
            self.tickbox_enactment.changetick(True)

        menu.MapDescription.image = imgs[2]
        menu.SourceDescription.image = imgs[3]
        menu.ArmyStat.image = imgs[4]

        self.current_map_row = 0
        self.current_map_select = 0

        self.current_source_row = 0
        # ^ End battle map menu button

        # v Create unit and subunit editor button in gamestart menu

        self.unit_edit_button = menu.MenuButton(self.screen_scale, imagelist,
                                                (self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                                text="Army Editor")
        self.subunit_create_button = menu.MenuButton(self.screen_scale, imagelist,
                                                     (self.SCREENRECT.width / 2, self.SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                                     text="Troop Creator")
        self.editor_back_button = menu.MenuButton(self.screen_scale, imagelist,
                                                  (self.SCREENRECT.width / 2, self.SCREENRECT.height - imagelist[0].get_height()),
                                                  text="Back")
        self.editor_button = (self.unit_edit_button, self.subunit_create_button, self.editor_back_button)
        # ^ End subunit editor

        # v Army editor ui and button
        boximg = load_image(self.main_dir, "unit_presetbox.png", "ui\\mainmenu_ui")
        self.unit_listbox = menu.ListBox(self.screen_scale, (0, self.SCREENRECT.height / 2.2), boximg)  # box for showing unit preset list
        self.unit_presetname_scroll = battleui.UIScroller(self.unit_listbox.rect.topright, self.unit_listbox.image.get_height(),
                                                          self.unit_listbox.maxshowlist, layer=14)  # preset name scroll
        self.presetselectborder = uniteditor.SelectedPresetBorder(self.unit_listbox.image.get_width() - int(15 * self.screen_scale[0]),
                                                                  int(25 * self.screen_scale[1]))

        self.troop_listbox = menu.ListBox(self.screen_scale, (self.SCREENRECT.width / 1.19, 0), imgs[0])

        self.troop_scroll = battleui.UIScroller(self.troop_listbox.rect.topright, self.troop_listbox.image.get_height(),
                                                self.troop_listbox.maxshowlist, layer=14)

        self.unit_delete_button = menu.MenuButton(self.screen_scale, imagelist,
                                                  pos=(imagelist[0].get_width() / 2, bottomheight),
                                                  text="Delete")
        self.unit_save_button = menu.MenuButton(self.screen_scale, imagelist,
                                                pos=((self.SCREENRECT.width - (self.SCREENRECT.width - (imagelist[0].get_width() * 1.7))),
                                                     bottomheight),
                                                text="Save")

        self.popup_listbox = menu.ListBox(self.screen_scale, (0, 0), boximg, 15)  # popup box need to be in higher layer
        self.popup_listscroll = battleui.UIScroller(self.popup_listbox.rect.topright,
                                                    self.popup_listbox.image.get_height(),
                                                    self.popup_listbox.maxshowlist,
                                                    layer=14)

        boximg = load_image(self.main_dir, "mapchange.png", "ui\\mainmenu_ui")
        self.terrain_change_button = uniteditor.PreviewChangeButton(self.screen_scale, (self.SCREENRECT.width / 3, self.SCREENRECT.height), boximg,
                                                                    "Temperate")  # start with temperate terrain
        self.feature_change_button = uniteditor.PreviewChangeButton(self.screen_scale, (self.SCREENRECT.width / 2, self.SCREENRECT.height), boximg,
                                                                    "Plain")  # start with plain feature
        self.weather_change_button = uniteditor.PreviewChangeButton(self.screen_scale, (self.SCREENRECT.width / 1.5, self.SCREENRECT.height), boximg,
                                                                    "Light Sunny")  # start with light sunny

        uniteditor.Unitbuildslot.sprite_width = self.sprite_width  # sprite_width and height generated in mode (e.g. tactical) file longscript.py
        uniteditor.Unitbuildslot.sprite_height = self.sprite_height
        startpos = [(self.SCREENRECT.width / 2) - (self.sprite_width * 5),
                    (self.SCREENRECT.height / 2) - (self.sprite_height * 4)]
        self.make_unit_slot(0, 1, 0, range(0, 64), startpos)  # make player custom unit slot

        self.preview_leader = [uniteditor.PreviewLeader(1, 0, 0, self.leader_stat),
                               uniteditor.PreviewLeader(1, 0, 1, self.leader_stat),
                               uniteditor.PreviewLeader(1, 0, 2, self.leader_stat),
                               uniteditor.PreviewLeader(1, 0, 3, self.leader_stat)]  # list of preview leader for unit editor
        self.leader_updater.remove(*self.preview_leader)  # remove preview leader from updater since not use in battle

        boximg = load_image(self.main_dir, "filter_box.png", "ui\\mainmenu_ui")  # filter box ui in editor
        self.filter_box = uniteditor.FilterBox(self.screen_scale, (self.SCREENRECT.width / 2.5, 0), boximg)
        img1 = load_image(self.main_dir, "team1_button.png", "ui\\mainmenu_ui")  # change unit slot to team 1 in editor
        img2 = load_image(self.main_dir, "team2_button.png", "ui\\mainmenu_ui")  # change unit slot to team 2 in editor
        self.teamchange_button = battleui.SwitchButton(self.filter_box.rect.topleft[0] + 220, self.filter_box.rect.topleft[1] + 30, [img1, img2])
        img1 = load_image(self.main_dir, "show_button.png", "ui\\mainmenu_ui")  # show unit slot ui in editor
        img2 = load_image(self.main_dir, "hide_button.png", "ui\\mainmenu_ui")  # hide unit slot ui in editor
        self.slotdisplay_button = battleui.SwitchButton(self.filter_box.rect.topleft[0] + 80, self.filter_box.rect.topleft[1] + 30, [img1, img2])
        img1 = load_image(self.main_dir, "deploy_button.png", "ui\\mainmenu_ui")  # deploy unit in unit slot to test map in editor
        self.deploy_button = battleui.UIButton(self.filter_box.rect.topleft[0] + 150, self.filter_box.rect.topleft[1] + 90, img1, 0)
        img1 = load_image(self.main_dir, "test_button.png", "ui\\mainmenu_ui")  # start test button in editor
        img2 = load_image(self.main_dir, "end_button.png", "ui\\mainmenu_ui")  # stop test button
        self.test_button = battleui.SwitchButton(self.scale_ui.rect.bottomleft[0] + 55, self.scale_ui.rect.bottomleft[1] + 25, [img1, img2])
        img1 = load_image(self.main_dir, "tick_box_no.png", "ui\\mainmenu_ui")  # start test button in editor
        img2 = load_image(self.main_dir, "tick_box_yes.png", "ui\\mainmenu_ui")  # stop test button
        self.tickbox_filter = [menu.TickBox(self.screen_scale, (self.filter_box.rect.bottomright[0] / 1.26, self.filter_box.rect.bottomright[1] / 8),
                                            img1, img2, "meleeinf"),
                               menu.TickBox(self.screen_scale, (self.filter_box.rect.bottomright[0] / 1.26, self.filter_box.rect.bottomright[1] / 1.7),
                                            img1, img2, "rangeinf"),
                               menu.TickBox(self.screen_scale, (self.filter_box.rect.bottomright[0] / 1.11, self.filter_box.rect.bottomright[1] / 8),
                                            img1, img2, "meleecav"),
                               menu.TickBox(self.screen_scale, (self.filter_box.rect.bottomright[0] / 1.11, self.filter_box.rect.bottomright[1] / 1.7),
                                            img1, img2, "rangecav")
                               ]
        for box in self.tickbox_filter:  # default start filter with all shown
            box.changetick(True)
        self.tickbox.add(*self.tickbox_filter)
        self.warningmsg = uniteditor.Warningmsg(self.screen_scale, (self.test_button.rect.bottomleft[0], self.test_button.rect.bottomleft[1]))
        # ^ End unit editor

        # v Input box popup
        input_ui_img = load_image(self.main_dir, "input_ui.png", "ui\\mainmenu_ui")
        self.inputui = menu.InputUI(self.screen_scale, input_ui_img,
                                    (self.SCREENRECT.width / 2, self.SCREENRECT.height / 2))  # user text input ui box popup
        self.input_ok_button = menu.MenuButton(self.screen_scale, imagelist,
                                               pos=(self.inputui.rect.midleft[0] + imagelist[0].get_width(),
                                                    self.inputui.rect.midleft[1] + imagelist[0].get_height()),
                                               text="Confirm", layer=31)
        self.input_cancel_button = menu.MenuButton(self.screen_scale, imagelist,
                                                   pos=(self.inputui.rect.midright[0] - imagelist[0].get_width(),
                                                        self.inputui.rect.midright[1] + imagelist[0].get_height()),
                                                   text="Cancel", layer=31)
        self.input_button = (self.input_ok_button, self.input_cancel_button)
        self.input_box = menu.InputBox(self.screen_scale, self.inputui.rect.center, self.inputui.image.get_width())  # user text input box

        self.inputui_pop = (self.inputui, self.input_box, self.input_ok_button, self.input_cancel_button)

        self.confirm_ui = menu.InputUI(self.screen_scale, input_ui_img,
                                       (self.SCREENRECT.width / 2, self.SCREENRECT.height / 2))  # user confirm input ui box popup
        self.confirmui_pop = (self.confirm_ui, self.input_ok_button, self.input_cancel_button)
        # ^ End input box popup

        # v profile box
        self.profile_name = self.profile_name
        img = load_image(self.main_dir, "profile_box.png", "ui\\mainmenu_ui")
        self.profile_box = menu.ProfileBox(self.screen_scale, img, (self.screen_width, 0),
                                           self.profile_name)  # profile name box at top right of screen at gamestart menu screen
        # ^ End profile box

        # v Create option menu button and icon
        self.back_button = menu.MenuButton(self.screen_scale, imagelist, (self.SCREENRECT.width / 2, self.SCREENRECT.height / 1.2), text="BACK")

        # Resolution changing bar that fold out the list when clicked
        img = load_image(self.main_dir, "scroll_normal.jpg", "ui\\mainmenu_ui")
        img2 = img
        img3 = load_image(self.main_dir, "scroll_click.jpg", "ui\\mainmenu_ui")
        imagelist = [img, img2, img3]
        self.resolution_scroll = menu.MenuButton(self.screen_scale, imagelist, (self.SCREENRECT.width / 2, self.SCREENRECT.height / 2.3),
                                                 text=str(self.screen_width) + " x " + str(self.screen_height), size=16)
        resolutionlist = ["1920 x 1080", "1600 x 900", "1366 x 768", "1280 x 720", "1024 x 768"]
        self.resolutionbar = make_bar_list(self.main_dir, self.screen_scale, listtodo=resolutionlist, menuimage=self.resolution_scroll)
        img = load_image(self.main_dir, "resolution_icon.png", "ui\\mainmenu_ui")
        self.resolutionicon = menu.MenuIcon([img], (self.resolution_scroll.pos[0] - (self.resolution_scroll.pos[0] / 4.5),
                                                    self.resolution_scroll.pos[1]), imageresize=50)
        # End resolution

        # Volume change scroller bar
        img = load_image(self.main_dir, "scroller.png", "ui\\mainmenu_ui")
        img2 = load_image(self.main_dir, "scoll_button_normal.png", "ui\\mainmenu_ui")
        img3 = load_image(self.main_dir, "scoll_button_click.png", "ui\\mainmenu_ui")
        img4 = load_image(self.main_dir, "numbervalue_icon.jpg", "ui\\mainmenu_ui")
        self.volumeslider = menu.SliderMenu(barimage=img, buttonimage=[img2, img3],
                                            pos=(self.SCREENRECT.width / 2, self.SCREENRECT.height / 3),
                                            value=self.Soundvolume)
        self.value_box = [menu.ValueBox(img4, (self.volumeslider.rect.topright[0] * 1.1, self.volumeslider.rect.topright[1]), self.Soundvolume)]
        img = load_image(self.main_dir, "volume_icon.png", "ui\\mainmenu_ui")
        self.volumeicon = menu.MenuIcon([img], (self.volumeslider.pos[0] - (self.volumeslider.pos[0] / 4.5), self.volumeslider.pos[1]),
                                        imageresize=50)
        # End volume change

        self.optioniconlist = (self.resolutionicon, self.volumeicon)
        self.optionmenu_button = (self.back_button, self.resolution_scroll)
        self.optionmenu_slider = self.volumeslider
        # ^ End option menu button

        pygame.mouse.set_visible(True)  # set mouse as visible

        # v Music player
        if pygame.mixer:
            self.mixervolume = float(self.Soundvolume / 100)
            pygame.mixer.music.set_volume(self.mixervolume)
            self.SONG_END = pygame.USEREVENT + 1
            self.musiclist = glob.glob(self.main_dir + "/data/sound/music/*.ogg")
            pygame.mixer.music.load(self.musiclist[0])
            pygame.mixer.music.play(-1)
        # ^ End music

        self.main_ui.remove(*self.menu_button)  # remove all button from drawing
        self.menu_button.remove(*self.menu_button)  # remove all button at the start and add later depending on menu_state
        self.menu_button.add(*self.mainmenu_button)  # add only gamestart menu button back

        self.mainmenu_ui_only = *self.menu_button, self.profile_box, self.genre_change_box
        self.main_ui.add(*self.mainmenu_ui_only)
        self.menu_state = "mainmenu"
        self.text_input_popup = (None, None)  # popup for texting text input state
        self.choosingfaction = True  # swap list between faction and subunit, always start with choose faction first as true

        self.battlegame = battle.Battle(self, self.winstyle)


    def game_intro(self, screen, clock, introoption):
        intro = introoption
        if introoption:
            intro = True
        timer = 0
        # The record is truthful, unbiased, correct and approved by appointed certified historians.
        # quote = ["Those attacker fail to learn from the mistakes of their predecessors are destined to repeat them. George Santayana",
        # "It is more important to outhink your enemy, than to outfight him, Sun Tzu"]
        while intro:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    intro = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            large_text = pygame.font.Font("freesansbold.ttf", 115)
            text_surf, text_rect = text_objects("Test Intro", large_text)
            text_rect.center = (700, 600)
            screen.blit(text_surf, text_rect)
            pygame.display.update()
            clock.tick(60)
            timer += 1
            if timer == 1000:
                intro = False

        pygame.display.set_caption(version_name + " " + self.genre.capitalize())  # set the game name on program border/tab

        # v Background image
        try:
            bgd_tile = load_image(self.main_dir, self.genre + ".png", "ui\\mainmenu_ui")
        except FileNotFoundError:
            bgd_tile = load_image(self.main_dir, "default.png", "ui\\mainmenu_ui")
        bgd_tile = pygame.transform.scale(bgd_tile, self.SCREENRECT.size)
        self.background = pygame.Surface(self.SCREENRECT.size)
        self.background.blit(bgd_tile, (0, 0))
        # ^ End background

    def back_mainmenu(self):
        self.menu_state = "mainmenu"

        self.main_ui.remove(*self.menu_button)

        self.menu_button.remove(*self.menu_button)
        self.menu_button.add(*self.mainmenu_button)

        self.main_ui.add(*self.mainmenu_ui_only)

    def read_map_data(self, map_list, file, source=False):
        if self.menu_state == "presetselect" or self.lastselect == "presetselect":
            if source:
                data = csv_read(self.main_dir, file,
                                ["data", "ruleset", self.ruleset_folder, "map", map_list[self.current_map_select], str(self.map_source), self.genre])
            else:
                data = csv_read(self.main_dir, file, ["data", "ruleset", self.ruleset_folder, "map", map_list[self.current_map_select]])
        else:
            data = csv_read(file, [self.main_dir, "data", "ruleset", self.ruleset_folder, "map/custom", map_list[self.current_map_select]])
        return data

    def make_team_coa(self, data, ui_class, one_team=False, team1_set_pos=None):
        for team in self.team_coa:
            team.kill()
            del team
        if team1_set_pos is None:
            team1_set_pos = (self.SCREENRECT.width / 2 - (300 * self.screen_scale[0]), self.SCREENRECT.height / 3)
        # position = self.map_show[0].get_rect()
        self.team_coa.add(menu.TeamCoa(self.screen_scale, team1_set_pos, self.coa[data[0]],
                                       1, self.allfaction.faction_list[data[0]][0]))  # team 1

        if one_team is False:
            self.team_coa.add(menu.TeamCoa(self.screen_scale, (self.SCREENRECT.width / 2 + (300 * self.screen_scale[0]), self.SCREENRECT.height / 3),
                                           self.coa[data[1]], 2, self.allfaction.faction_list[data[1]][0]))  # team 2
        ui_class.add(self.team_coa)

    def make_map(self, map_folder_list, map_list):
        # v Create map preview image
        for this_map in self.map_show:
            this_map.kill()
            del this_map
        if self.menu_state == "presetselect":
            imgs = load_images(self.main_dir, ["ruleset", self.ruleset_folder, "map", map_folder_list[self.current_map_select]],
                               loadorder=False)
        else:
            imgs = load_images(self.main_dir, ["ruleset", self.ruleset_folder, "map/custom", map_folder_list[self.current_map_select]],
                               loadorder=False)
        self.map_show.add(menu.MapShow(self.main_dir, self.screen_scale, (self.SCREENRECT.width / 2, self.SCREENRECT.height / 3), imgs[0], imgs[1]))
        self.main_ui.add(self.map_show)
        # ^ End map preview

        # v Create map title at the top
        for name in self.map_title:
            name.kill()
            del name
        self.map_title.add(menu.MapTitle(self.screen_scale, map_list[self.current_map_select], (self.SCREENRECT.width / 2, 0)))
        self.main_ui.add(self.map_title)
        # ^ End map title

        # v Create map description
        data = self.read_map_data(map_folder_list, "info.csv")
        description = [list(data.values())[1][0], list(data.values())[1][1]]
        for desc in self.map_description:
            desc.kill()
            del desc
        self.map_description.add(menu.MapDescription(self.screen_scale, (self.SCREENRECT.width / 2, self.SCREENRECT.height / 1.3), description))
        self.main_ui.add(self.map_description)
        # ^ End map description

        self.make_team_coa([list(data.values())[1][2], list(data.values())[1][3]], self.main_ui)

    def change_source(self, description_text, scale_value):
        """Change source description, add new subunit dot, change army stat when select new source"""
        for desc in self.source_description:
            desc.kill()
            del desc
        self.source_description.add(menu.SourceDescription(self.screen_scale, (self.SCREENRECT.width / 2, self.SCREENRECT.height / 1.3), description_text))
        self.main_ui.add(self.source_description)

        openfolder = self.mapfoldername
        if self.lastselect == "customselect":
            openfolder = self.mapcustomfoldername
        unit_info = self.read_map_data(openfolder, "unit_pos.csv", source=True)

        team1_pos = {row[8]: [int(item) for item in row[8].split(",")] for row in list(unit_info.values()) if row[15] == 1}
        team2_pos = {row[8]: [int(item) for item in row[8].split(",")] for row in list(unit_info.values()) if row[15] == 2}
        for thismap in self.map_show:
            thismap.change_mode(1, team1_pos_list=team1_pos, team2_pos_list=team2_pos)

        team1_army = []
        team2_army = []
        team1_commander = []
        team2_commander = []
        for index, row in enumerate(list(unit_info.values())):
            if row[15] == 1:
                listadd = team1_army
            elif row[15] == 2:
                listadd = team2_army
            for smallrow in row[0:7]:
                for item in smallrow.split(","):
                    listadd.append(int(item))

            for item in row[9].split(","):
                if row[15] == 1:
                    team1_commander.append(int(item))
                elif row[15] == 2:
                    team2_commander.append(int(item))

        team_total_troop = [0, 0]  # total troop number in army
        troop_type_list = [[0, 0, 0, 0], [0, 0, 0, 0]]  # total number of each troop type
        leader_name_list = (team1_commander, team2_commander)
        army_team_list = (team1_pos, team2_pos)  # for finding how many subunit in each team

        army_loop_list = (team1_army, team2_army)
        for index, team in enumerate(army_loop_list):
            for unit in team:
                if unit != 0:
                    team_total_troop[index] += int(self.troop_data.troop_list[unit][27] * scale_value[index])
                    troop_type = 0
                    if self.troop_data.troop_list[unit][22] != [1, 0] \
                            and self.troop_data.troop_list[unit][8] < self.troop_data.troop_list[unit][12]:  # range sub-unit
                        troop_type += 1  # range weapon and accuracy higher than melee attack
                    if self.troop_data.troop_list[unit][29] != [1, 0, 1]:  # cavalry
                        troop_type += 2
                    troop_type_list[index][troop_type] += int(self.troop_data.troop_list[unit][27] * scale_value[index])
            troop_type_list[index].append(len(army_team_list[index]))

        army_loop_list = ["{:,}".format(troop) + " Troops" for troop in team_total_troop]
        army_loop_list = [self.leader_stat.leader_list[leader_name_list[index][0]][0] + ": " + troop for index, troop in enumerate(army_loop_list)]

        for index, army in enumerate(self.army_stat):
            army.addstat(troop_type_list[index], army_loop_list[index])

    def make_unit_slot(self, gameid, team, unitid, rangetorun, startpos, columnonly=False):
        width, height = 0, 0
        slotnum = 0  # Number of subunit based on the position in row and column
        for subunit in rangetorun:  # generate player unit slot for filling troop into preview unit
            if columnonly is False:
                width += self.sprite_width
                self.unit_build_slot.add(uniteditor.Unitbuildslot(gameid, team, unitid, (width, height), startpos, slotnum, self.teamcolour))
                slotnum += 1
                if slotnum % 8 == 0:  # Pass the last subunit in the row, go to the next one
                    width = 0
                    height += self.sprite_height
            else:
                height += self.sprite_height
                self.unit_build_slot.add(uniteditor.Unitbuildslot(gameid, team, unitid, (width, height), startpos, slotnum, self.teamcolour))
                slotnum += 1
            gameid += 1
        return gameid

    def popout_lorebook(self, section, gameid):
        # v Seem like encyclopedia in battle cause container to change allui in gamestart to battle one, change back with this
        lorebook.SubsectionName.containers = self.subsection_name, self.main_ui
        # ^ End container change

        self.beforelorestate = self.menu_state
        self.menu_state = "encyclopedia"
        self.main_ui.add(self.lorebook, self.lorescroll, self.lore_name_list, *self.lore_button_ui)  # add sprite related to encyclopedia
        self.lorebook.change_section(section, self.lore_name_list, self.subsection_name, self.lorescroll,
                                     self.pagebutton, self.main_ui)
        self.lorebook.change_subsection(gameid, self.pagebutton, self.main_ui)
        self.lorescroll.change_image(new_row=self.lorebook.current_subsection_row)

    def run(self):
        while True:
            # v Get user input
            mouse_left_up = False
            mouse_left_down = False
            mouse_right_up = False
            mouse_scroll_down = False
            mouse_scroll_up = False
            esc_press = False
            input_esc = False
            key_press = pygame.key.get_pressed()
            if pygame.mouse.get_pressed()[0]:  # Hold left click
                mouse_left_down = True
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_left_up = True
                    elif event.button == 3:
                        mouse_right_up = True
                    elif event.button == 4:  # Mouse scroll down
                        mouse_scroll_up = True

                    elif event.button == 5:  # Mouse scroll up
                        mouse_scroll_down = True

                elif event.type == KEYDOWN:
                    if self.text_input_popup[0] is not None:  # event update to input box
                        if event.key == K_ESCAPE:
                            input_esc = True
                        elif self.text_input_popup[0] == "text_input":
                            self.input_box.user_input(event, key_press)
                    else:
                        if event.key == K_ESCAPE:
                            esc_press = True

                if event.type == QUIT or self.quit_button.event or (esc_press and self.menu_state == "mainmenu"):
                    self.quit_button.event = False
                    self.text_input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.main_ui.add(*self.confirmui_pop)

            self.mouse_pos = pygame.mouse.get_pos()
            # ^ End user input

            self.screen.blit(self.background, (0, 0))  # blit blackground over instead of clear() to reset screen

            if self.text_input_popup[0] is not None:  # currently have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down, "any")

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.text_input_popup[1] == "profile_name":
                        self.profile_name = self.input_box.text
                        self.profile_box.changename(self.profile_name)

                        edit_config("DEFAULT", "playername", self.profile_name, "configuration.ini", self.config)

                    elif self.text_input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        if pygame.mixer:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        pygame.quit()
                        sys.exit()
                        return

                    self.input_box.text_start("")
                    self.text_input_popup = (None, None)
                    self.main_ui.remove(*self.inputui_pop)

                elif self.input_cancel_button.event or input_esc:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.text_input_popup = (None, None)
                    self.main_ui.remove(*self.inputui_pop, *self.confirmui_pop)

            elif self.text_input_popup == (None, None):
                self.menu_button.update(self.mouse_pos, mouse_left_up, mouse_left_down, self.menu_state)
                if self.menu_state == "mainmenu":

                    if self.preset_map_button.event:  # preset map list menu
                        self.menu_state = "presetselect"
                        self.lastselect = self.menu_state
                        self.preset_map_button.event = False
                        self.main_ui.remove(*self.mainmenu_ui_only, self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.maplist, self.map_namegroup, self.map_listbox,
                                   self.main_ui)
                        self.make_map(self.mapfoldername, self.maplist)

                        self.menu_button.add(*self.map_select_button)
                        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

                    elif self.custom_map_button.event:  # custom map list menu
                        self.menu_state = "customselect"
                        self.lastselect = self.menu_state
                        self.custom_map_button.event = False
                        self.main_ui.remove(*self.mainmenu_ui_only, self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.mapcustomlist, self.map_namegroup, self.map_listbox,
                                   self.main_ui)
                        self.make_map(self.mapcustomfoldername, self.mapcustomlist)

                        self.menu_button.add(*self.map_select_button)
                        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

                    elif self.game_edit_button.event:  # custom subunit/sub-subunit editor menu
                        self.menu_state = "gamecreator"
                        self.game_edit_button.event = False
                        self.main_ui.remove(*self.mainmenu_ui_only, self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        self.menu_button.add(*self.editor_button)
                        self.main_ui.add(*self.editor_button)

                    elif self.option_button.event:  # change gamestart menu to option menu
                        self.menu_state = "option"
                        self.option_button.event = False
                        self.main_ui.remove(*self.mainmenu_ui_only, self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        self.menu_button.add(*self.optionmenu_button)
                        self.main_ui.add(*self.menu_button, self.optionmenu_slider, self.value_box)
                        self.main_ui.add(*self.optioniconlist)

                    elif self.lore_button.event:  # open encyclopedia
                        # v Seem like encyclopedia in battle cause container to change allui in gamestart to gamebattle one, change back with this
                        lorebook.SubsectionName.containers = self.subsection_name, self.main_ui
                        # ^ End container change

                        self.beforelorestate = self.menu_state
                        self.menu_state = "encyclopedia"
                        self.main_ui.add(self.lorebook, self.lore_name_list, *self.lore_button_ui,
                                         self.lorescroll)  # add sprite related to encyclopedia
                        self.lorebook.change_section(0, self.lore_name_list, self.subsection_name, self.lorescroll, self.pagebutton, self.main_ui)
                        self.lore_button.event = False

                    elif mouse_left_up and self.profile_box.rect.collidepoint(self.mouse_pos):
                        self.text_input_popup = ("text_input", "profile_name")
                        self.input_box.text_start(self.profile_name)
                        self.inputui.change_instruction("Profile Name:")
                        self.main_ui.add(self.inputui_pop)

                    elif mouse_left_up and self.genre_change_box.rect.collidepoint(self.mouse_pos):
                        self.popup_list_open(self.genre_change_box.rect.bottomleft, self.genrelist, "genre")

                    elif self.popup_listbox in self.main_ui:
                        if self.popup_listbox.rect.collidepoint(self.mouse_pos):
                            self.uiclick = True
                            for index, name in enumerate(self.popup_namegroup):
                                if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                                    self.change_genre(index)

                                    for thisname in self.popup_namegroup:  # remove troop name list
                                        thisname.kill()
                                        del thisname

                                    self.main_ui.remove(self.popup_listbox, self.popup_listscroll)
                                    break

                        elif self.popup_listscroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
                            self.uiclick = True
                            self.current_popup_row = self.popup_listscroll.update(
                                self.mouse_pos)  # update the scroller and get new current subsection
                            setup_list(self.screen_scale, menu.NameList, self.current_popup_row, self.genrelist,
                                       self.popup_namegroup, self.popup_listbox, self.main_ui)

                        # else:
                        #     self.main_ui.remove(self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

                elif self.menu_state == "presetselect" or self.menu_state == "customselect":
                    if mouse_left_up or mouse_left_down:
                        if mouse_left_up:
                            for index, name in enumerate(self.map_namegroup):  # user click on map name, change map
                                if name.rect.collidepoint(self.mouse_pos):
                                    self.current_map_select = index
                                    if self.menu_state == "presetselect":  # make new map image
                                        self.make_map(self.mapfoldername, self.maplist)
                                    else:
                                        self.make_map(self.mapcustomfoldername, self.mapcustomlist)
                                    break

                        if self.map_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroller
                            self.current_map_row = self.map_scroll.update(
                                self.mouse_pos)  # update the scroller and get new current subsection
                            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.maplist, self.map_namegroup, self.map_listbox,
                                       self.main_ui)

                    if self.map_listbox.rect.collidepoint(self.mouse_pos):
                        self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.map_scroll, self.map_listbox,
                                                                self.current_map_row, self.maplist, self.map_namegroup, self.main_ui)

                    if self.map_back_button.event or esc_press:
                        self.map_back_button.event = False
                        self.current_map_row = 0
                        self.current_map_select = 0

                        self.main_ui.remove(self.map_listbox, self.map_show, self.map_scroll, self.map_description,
                                            self.team_coa, self.map_title)

                        for group in (self.map_show, self.map_namegroup, self.team_coa):  # remove no longer related sprites in group
                            for stuff in group:
                                stuff.kill()
                                del stuff

                        self.back_mainmenu()

                    elif self.select_button.event:  # select this map, go to prepare setup
                        self.current_source_row = 0
                        self.menu_state = "battlemapset"
                        self.select_button.event = False

                        self.main_ui.remove(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)
                        self.menu_button.remove(*self.map_select_button)

                        for stuff in self.map_namegroup:  # remove map name item
                            stuff.kill()
                            del stuff

                        for team in self.team_coa:
                            if self.team_selected == team.team:
                                team.changeselect(True)

                        openfolder = self.mapfoldername
                        if self.lastselect == "customselect":
                            openfolder = self.mapcustomfoldername
                        try:
                            self.sourcelist = self.read_map_data(openfolder, "source.csv")
                            self.sourcenamelist = [value[0] for value in list(self.sourcelist.values())[1:]]
                            self.sourcescaletext = [value[1] for value in list(self.sourcelist.values())[1:]]
                            self.sourcescale = [(float(value[2]), float(value[3]), float(value[4]), float(value[5])) for value in
                                                list(self.sourcelist.values())[1:]]
                            self.sourcetext = [value[-1] for value in list(self.sourcelist.values())[1:]]
                        except Exception:  # no source.csv make empty list
                            self.sourcenamelist = [""]
                            self.sourcescaletext = [""]
                            self.sourcescale = [""]
                            self.sourcetext = [""]

                        setup_list(self.screen_scale, menu.SourceName, self.current_source_row, self.sourcenamelist, self.source_namegroup,
                                   self.source_listbox, self.main_ui)

                        self.sourcescroll = battleui.UIScroller(self.source_listbox.rect.topright, self.source_listbox.image.get_height(),
                                                                self.source_listbox.maxshowlist, layer=16)  # scroller bar for source list

                        for index, team in enumerate(self.team_coa):
                            if index == 0:
                                self.army_stat.add(
                                    menu.ArmyStat(self.screen_scale, (team.rect.bottomleft[0], self.SCREENRECT.height / 1.5)))  # left army stat
                            else:
                                self.army_stat.add(
                                    menu.ArmyStat(self.screen_scale, (team.rect.bottomright[0], self.SCREENRECT.height / 1.5)))  # right army stat

                        self.change_source([self.sourcescaletext[self.map_source], self.sourcetext[self.map_source]],
                                           self.sourcescale[self.map_source])

                        self.menu_button.add(*self.battle_setup_button)
                        self.main_ui.add(*self.battle_setup_button, self.map_optionbox, self.tickbox_enactment, self.source_listbox,
                                         self.sourcescroll, self.army_stat)

                elif self.menu_state == "battlemapset":
                    if mouse_left_up or mouse_left_down:
                        if mouse_left_up:
                            for thisteam in self.team_coa:  # User select any team by clicking on coat of arm
                                if thisteam.rect.collidepoint(self.mouse_pos):
                                    self.team_selected = thisteam.team
                                    thisteam.changeselect(True)

                                    # Reset team selected on team user not currently selected
                                    for thisteam2 in self.team_coa:
                                        if self.team_selected != thisteam2.team and thisteam2.selected:
                                            thisteam2.changeselect(False)
                                    break

                            for index, name in enumerate(self.source_namegroup):  # user select source
                                if name.rect.collidepoint(self.mouse_pos):  # click on source name
                                    self.map_source = index
                                    self.change_source([self.sourcescaletext[self.map_source], self.sourcetext[self.map_source]],
                                                       self.sourcescale[self.map_source])
                                    break

                            for box in self.tickbox:
                                if box in self.main_ui and box.rect.collidepoint(self.mouse_pos):
                                    if box.tick is False:
                                        box.changetick(True)
                                    else:
                                        box.changetick(False)
                                    if box.option == "enactment":
                                        self.enactment = box.tick

                        if self.sourcescroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroller
                            self.current_source_row = self.sourcescroll.update(
                                self.mouse_pos)  # update the scroller and get new current subsection
                            setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.sourcelist, self.source_namegroup,
                                       self.source_listbox, self.main_ui)
                    if self.source_listbox.rect.collidepoint(self.mouse_pos):
                        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.sourcescroll, self.source_listbox,
                                                                   self.current_source_row, self.sourcelist, self.source_namegroup, self.main_ui)

                    if self.map_back_button.event or esc_press:
                        self.menu_state = self.lastselect
                        self.map_back_button.event = False
                        self.main_ui.remove(*self.menu_button, self.map_listbox, self.map_optionbox, self.tickbox_enactment,
                                            self.source_listbox, self.sourcescroll, self.source_description)
                        self.menu_button.remove(*self.menu_button)

                        # v Reset selected team
                        for team in self.team_coa:
                            team.changeselect(False)
                        self.team_selected = 1
                        # ^ End reset selected team

                        self.map_source = 0
                        for thismap in self.map_show:
                            thismap.changemode(0)  # revert map preview back to without unit dot

                        for group in (self.source_namegroup, self.army_stat):
                            for stuff in group:  # remove map name item
                                stuff.kill()
                                del stuff

                        if self.menu_state == "presetselect":  # regenerate map name list
                            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.maplist, self.map_namegroup, self.map_listbox,
                                       self.main_ui)
                        else:
                            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.mapcustomlist, self.map_namegroup, self.map_listbox,
                                       self.main_ui)

                        self.menu_button.add(*self.map_select_button)
                        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)

                    elif self.start_button.event:  # start game button
                        self.start_button.event = False
                        self.battlegame.preparenewgame(self.ruleset, self.ruleset_folder, self.team_selected, self.enactment,
                                                       self.mapfoldername[self.current_map_select], self.map_source,
                                                       self.sourcescale[self.map_source], "battle")
                        self.battlegame.rungame()
                        pygame.mixer.music.unload()
                        pygame.mixer.music.set_endevent(self.SONG_END)
                        pygame.mixer.music.load(self.musiclist[0])
                        pygame.mixer.music.play(-1)
                        gc.collect()  # collect no longer used object in previous battle from memory

                elif self.menu_state == "gamecreator":
                    if self.editor_back_button.event or esc_press:
                        self.editor_back_button.event = False
                        self.back_mainmenu()

                    elif self.unit_edit_button.event:
                        self.unit_edit_button.event = False
                        self.battlegame.preparenewgame(self.ruleset, self.ruleset_folder, 1, True, None, 1, (1, 1, 1, 1), "uniteditor")
                        self.battlegame.rungame()
                        pygame.mixer.music.unload()
                        pygame.mixer.music.set_endevent(self.SONG_END)
                        pygame.mixer.music.load(self.musiclist[0])
                        pygame.mixer.music.play(-1)

                elif self.menu_state == "option":
                    for bar in self.resolutionbar:  # loop to find which resolution bar is selected, this happen outside of clicking check below
                        if bar.event:
                            bar.event = False

                            self.resolution_scroll.changestate(bar.text)  # change button value based on new selected value
                            resolutionchange = bar.text.split()
                            self.new_screen_width = resolutionchange[0]
                            self.new_screen_height = resolutionchange[2]

                            edit_config("DEFAULT", "screen_width", self.new_screen_width, "configuration.ini", self.config)
                            edit_config("DEFAULT", "screen_height", self.new_screen_height, "configuration.ini", self.config)
                            self.screen = pygame.display.set_mode(self.SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)

                            self.menu_button.remove(self.resolutionbar)

                            break

                    if self.back_button.event or esc_press:  # back to gamestart menu
                        self.back_button.event = False

                        self.main_ui.remove(*self.optioniconlist, self.optionmenu_slider, self.value_box)

                        self.back_mainmenu()

                    if mouse_left_up or mouse_left_down:
                        self.main_ui.remove(self.resolutionbar)

                        if self.resolution_scroll.rect.collidepoint(self.mouse_pos):  # click on resolution bar
                            if self.resolutionbar in self.main_ui:  # remove the bar list if click again
                                self.main_ui.remove(self.resolutionbar)
                                self.menu_button.remove(self.resolutionbar)
                            else:  # add bar list
                                self.main_ui.add(self.resolutionbar)
                                self.menu_button.add(self.resolutionbar)

                        elif self.volumeslider.rect.collidepoint(self.mouse_pos) and (mouse_left_down or mouse_left_up):  # mouse click on slider bar
                            self.volumeslider.update(self.mouse_pos, self.value_box[0])  # update slider button based on mouse value
                            self.mixervolume = float(self.volumeslider.value / 100)  # for now only music volume slider exist
                            edit_config("DEFAULT", "SoundVolume", str(self.volumeslider.value), "configuration.ini", self.config)
                            pygame.mixer.music.set_volume(self.mixervolume)

                elif self.menu_state == "encyclopedia":
                    command = self.lorebook_process(self.main_ui, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down)
                    if esc_press or command == "exit":
                        self.menu_state = "mainmenu"  # change menu back to default 0

            self.main_ui.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
