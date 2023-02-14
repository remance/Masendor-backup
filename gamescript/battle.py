import datetime
import glob
import os
import random
import sys

import pygame
import pygame.freetype
from gamescript import camera, weather, battleui, menu, subunit, datasprite, damagesprite
from gamescript.common import utility

direction_list = datasprite.direction_list

from pygame.locals import *
from scipy.spatial import KDTree

from pathlib import Path

load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
load_sound = utility.load_sound
edit_config = utility.edit_config
setup_list = utility.setup_list
clean_group_object = utility.clean_group_object

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"


class Battle:
    empty_method = utility.empty_method

    # Import from common.battle
    add_sound_effect_queue = empty_method
    battle_keyboard_process = empty_method
    battle_mouse_process = empty_method
    cal_shake_value = empty_method
    camera_fix = empty_method
    camera_process = empty_method
    change_battle_state = empty_method
    check_subunit_collision = empty_method
    generate_unit = empty_method
    mouse_scrolling_process = empty_method
    play_sound_effect = empty_method
    setup_battle_troop = empty_method
    setup_battle_ui = empty_method
    shake_camera = empty_method
    spawn_weather_matter = empty_method
    time_update = empty_method

    # Import common.ui
    countdown_skill_icon = empty_method
    effect_icon_mouse_over = empty_method
    escmenu_process = empty_method
    kill_effect_icon = empty_method
    wheel_ui_process = empty_method

    for folder in ("battle", "ui"):
        for entry in os.scandir(Path(script_dir + "/common/" + folder + "/")):  # load and replace modules from common
            if entry.is_file():
                if ".pyc" in entry.name:
                    file_name = entry.name[:-4]
                elif ".py" in entry.name:
                    file_name = entry.name[:-3]
                exec(f"from gamescript.common." + folder.replace("/", ".") + " import " + file_name)
                exec(f"" + file_name + " = " + file_name + "." + file_name)

    start_camera_mode = "Follow"

    def __init__(self, main, window_style):
        self.player_char = None  # player subunit for genre that allow player to directly control only one subunit
        self.main = main

        self.config = main.config
        self.master_volume = main.master_volume
        self.play_music_volume = main.play_music_volume
        self.play_effect_volume = main.play_effect_volume
        self.play_voice_volume = main.play_voice_volume
        self.screen_rect = main.screen_rect
        self.main_dir = main.main_dir
        self.screen_scale = main.screen_scale
        self.battle_camera = main.battle_camera
        self.battle_ui_updater = main.battle_ui_updater

        self.subunit_updater = main.subunit_updater
        self.ui_updater = main.ui_updater
        self.weather_updater = main.weather_updater
        self.effect_updater = main.effect_updater

        self.cursor = main.cursor

        self.battle_map_base = main.battle_base_map
        self.battle_map_feature = main.battle_feature_map
        self.battle_map_height = main.battle_height_map
        self.battle_map = main.battle_map

        self.sprite_indicator = main.sprite_indicator

        self.mini_map = main.mini_map
        self.button_ui = main.button_ui

        self.fps_count = main.fps_count

        self.single_text_popup = main.single_text_popup
        self.drama_text = main.drama_text

        self.skill_icon = main.skill_icon
        self.effect_icon = main.effect_icon

        self.battle_menu = main.battle_menu
        self.battle_menu_button = main.battle_menu_button
        self.esc_option_menu_button = main.esc_option_menu_button

        self.input_button = main.input_button
        self.input_box = main.input_box
        self.input_ui = main.input_ui
        self.input_ok_button = main.input_ok_button
        self.input_cancel_button = main.input_cancel_button
        self.input_ui_popup = main.input_ui_popup
        self.confirm_ui = main.confirm_ui
        self.confirm_ui_popup = main.confirm_ui_popup

        self.unit_selector = main.unit_selector
        self.char_icon = main.char_icon

        self.time_ui = main.time_ui
        self.time_number = main.time_number

        self.battle_scale_ui = main.battle_scale_ui

        self.weather_matter = main.weather_matter
        self.weather_effect = main.weather_effect

        self.status_images = main.status_images
        self.role_images = main.role_images
        self.trait_images = main.trait_images
        self.skill_images = main.skill_images

        self.sound_effect_pool = main.sound_effect_pool
        self.sound_effect_queue = {}

        self.map_corner = (1000, 1000)
        self.max_camera = (1000, 1000)

        self.map_move_array = []  # array for pathfinding
        self.map_def_array = []  # array for defence calculation

        self.troop_ai_logic_queue = []

        self.esc_slider_menu = main.esc_slider_menu
        self.esc_value_boxes = main.esc_value_boxes

        self.wheel_ui = main.wheel_ui

        self.unit_behaviour_wheel = \
            {"Main": {"Team Order": "Team Order", "Formation": "Formation", "Setting": "Setting"},
             "Formation": {"Formation Style": "Formation Style",
                           "Formation Phase": "Formation Phase",
                           "Formation List": "Formation List",
                           "Formation Position": "Formation Position",
                           "Formation Density": "Formation Density",
                           "Formation Order": "Formation Order"},
             "Team Order": {"Defend Me": "Defend Me", "Follow Me": "Follow Me", "Hold Location": "Hold Location",
                            "Attack": "Attack"},
             "Formation Phase": {"Skirmish Phase": "Skirmish Phase", "Melee Phase": "Melee Phase",
                                 "Bombard Phase": "Bombard Phase"},
             "Formation Style": {"Infantry Flank": "Infantry Flank", "Cavalry Flank": "Cavalry Flank"},
             "Formation Density": {"Very Tight": "Very Tight", "Tight": "Tight",
                                   "Very Loose": "Very Loose", "Loose": "Loose"},
             "Formation Position": {"Behind": "Behind", "Ahead": "Behind", "Left": "Left", "Right": "Right",
                                    "Around": "Around"},
             "Formation Order": {"Stay Formation": "Stay Formation", "Follow": "Follow", "Free": "Free",
                                 "Stay Here": "Stay Here"},
             "Setting": {"Height Map": "Height Map", "UI Hide": "UI Hide", "UI Show": "UI Show"}}

        self.command_ui = main.command_ui
        self.event_log = main.event_log

        self.battle_done_box = main.battle_done_box
        self.battle_done_button = main.battle_done_button

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.right_corner = self.screen_rect.width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_rect.height - (5 * self.screen_scale[1])
        self.center_screen = [self.screen_rect.width / 2, self.screen_rect.height / 2]  # center position of the screen

        # data specific to ruleset
        self.faction_data = None
        self.coa_list = None

        self.troop_data = None
        self.leader_data = None

        self.battle_map_data = None
        self.weather_data = None
        self.weather_matter_images = None
        self.weather_effect_images = None
        self.day_effect_images = None
        self.weather_list = None
        self.feature_mod = None

        self.current_weather = weather.Weather(self.time_ui, 4, 0, 0, self.weather_data)

        self.generic_animation_pool = None
        self.gen_body_sprite_pool = None
        self.gen_weapon_sprite_pool = None
        self.gen_armour_sprite_pool = None
        self.effect_sprite_pool = None
        self.effect_animation_pool = None
        self.weapon_joint_list = None
        self.team_colour = None

        self.generic_action_data = None
        self.subunit_animation_pool = None

        self.game_speed = 0
        self.game_speed_list = (0, 0.5, 1, 2, 4, 6)  # available game speed
        self.day_time = "Day"
        self.old_day_time = self.day_time
        self.all_team_subunit = {1: pygame.sprite.Group(),
                                 2: pygame.sprite.Group()}  # more team can be added later
        self.team_troop_number = []  # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.last_team_troop_number = []
        self.battle_scale = []
        self.start_troop_number = []
        self.wound_troop_number = []
        self.death_troop_number = []
        self.flee_troop_number = []
        self.capture_troop_number = []
        self.faction_pick = 0
        self.current_pop_up_row = 0

        self.player_input_state = None  # specific player command input and ui
        self.previous_player_input_state = None

        self.active_subunit_list = []  # list of all subunit alive in battle, need to be in list for collision check
        self.visible_subunit_list = {}  # list of subunit visible to the team

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, window_style, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(self.screen_rect.size, window_style | pygame.RESIZABLE,
                                              self.best_depth)  # set up self screen

        # Assign battle variable to some classes
        subunit.Subunit.battle = self
        subunit.Subunit.sound_effect_pool = self.sound_effect_pool
        damagesprite.DamageSprite.sound_effect_pool = self.sound_effect_pool

        # Create the game camera
        self.camera_mode = "Follow"  # mode of game camera
        self.true_camera_pos = pygame.Vector2(500, 500)  # camera pos on map
        self.camera_pos = pygame.Vector2(self.true_camera_pos[0] * self.screen_scale[0],
                                         self.true_camera_pos[1] * self.screen_scale[1]) * 5  # Camera pos with screen scale

        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.screen_shake_value = 0  # count for how long to shake camera

        self.camera_topleft_corner = (self.camera_pos[0] - self.center_screen[0],
                                      self.camera_pos[1] - self.center_screen[
                                          1])  # calculate top left corner of camera position

        camera.Camera.screen_rect = self.screen_rect
        self.camera = camera.Camera(self.shown_camera_pos)

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.background = pygame.Surface(self.screen_rect.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

        self.battle_mouse_pos = [0, 0]  # mouse position list in battle map not screen without zoom
        self.battle_mouse_pos = [0, 0]  # with camera zoom adjust but without screen scale
        self.command_mouse_pos = [0, 0]  # with zoom and screen scale for unit command

    def prepare_new_game(self, ruleset, ruleset_folder, team_selected, map_selected,
                         map_source, char_selected):
        """Setup stuff when start new battle"""
        self.language = self.main.language

        self.ruleset = ruleset  # current ruleset used
        self.ruleset_folder = ruleset_folder  # the folder of rulseset used
        self.map_selected = map_selected  # map folder name
        self.map_source = str(map_source)
        self.team_selected = team_selected  # player selected team

        self.char_selected = char_selected

        self.faction_data = self.main.faction_data
        self.coa_list = self.faction_data.coa_list

        self.troop_data = self.main.troop_data
        self.leader_data = self.main.leader_data

        self.generic_animation_pool = self.main.generic_animation_pool
        self.gen_body_sprite_pool = self.main.gen_body_sprite_pool
        self.gen_weapon_sprite_pool = self.main.gen_weapon_sprite_pool
        self.gen_armour_sprite_pool = self.main.gen_armour_sprite_pool
        self.effect_sprite_pool = self.main.effect_sprite_pool
        self.effect_animation_pool = self.main.effect_animation_pool
        self.weapon_joint_list = self.main.weapon_joint_list
        self.team_colour = self.main.team_colour

        # Load weather schedule
        try:
            self.weather_event = csv_read(self.main_dir, "weather.csv",
                                          ("data", "ruleset", self.ruleset_folder, "map", self.map_selected,
                                           self.map_source), output_type="list")
            self.weather_event = self.weather_event[1:]
            utility.convert_str_time(self.weather_event)
        except (FileNotFoundError,
                TypeError):  # If no weather found or no map use light sunny weather start at 9:00 and wind direction at 0 angle
            new_time = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
            self.weather_event = ((4, new_time, 0, 0),)  # default weather light sunny all day
        self.weather_playing = self.weather_event[0][1]  # used as the reference for map starting time

        # Random music played from list
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(os.path.join(self.main_dir, "data", "sound", "music", "*.ogg"))
            try:
                self.music_event = csv_read(self.main_dir, "music_event.csv",
                                            ("data", "ruleset", self.ruleset_folder, "map", self.map_selected),
                                            output_type="list")
                self.music_event = self.music_event[1:]
                if self.music_event:
                    utility.convert_str_time(self.music_event)
                    self.music_schedule = list(dict.fromkeys([item[1] for item in self.music_event]))
                    new_list = []
                    for time in self.music_schedule:
                        new_event_list = []
                        for event in self.music_event:
                            if time == event[1]:
                                new_event_list.append(event[0])
                        new_list.append(new_event_list)
                    self.music_event = new_list
                else:
                    self.music_schedule = [self.weather_playing]
                    self.music_event = []
            except:  # any reading error will play random custom music instead
                self.music_schedule = [self.weather_playing]
                self.music_event = []  # TODO change later when has custom playlist

        try:  # get new map event for event log
            map_event = csv_read(self.main_dir, "eventlog_" + self.language + ".csv",
                                 ("data", "ruleset", self.ruleset_folder, "map", self.map_selected, self.map_source),
                                 header_key=True)
            battleui.EventLog.map_event = map_event
        except Exception:  # can't find any event file
            map_event = {}  # create empty list

        self.event_log.make_new_log()  # reset old event log

        self.event_log.add_event_log(map_event)

        self.event_schedule = None
        self.event_list = []
        for index, event in enumerate(self.event_log.map_event):
            if self.event_log.map_event[event]["Time"] is not None:
                if index == 0:
                    self.event_id = event
                    self.event_schedule = self.event_log.map_event[event]["Time"]
                self.event_list.append(event)

        self.time_number.start_setup(self.weather_playing)

        images = load_images(self.main_dir, subfolder=("ruleset", self.ruleset_folder, "map", self.map_selected))
        self.battle_map_base.draw_image(images["base"])
        self.battle_map_feature.draw_image(images["feature"])
        self.battle_map_height.draw_image(images["height"])

        try:  # place_name map layer is optional, if not existed in folder then assign None
            place_name_map = images["place_name"]
        except Exception:
            place_name_map = None
        self.battle_map.draw_image(self.battle_map_base, self.battle_map_feature, place_name_map, self)

        self.map_corner = (
            len(self.battle_map_base.map_array[0]),
            len(self.battle_map_base.map_array))  # get map size that troop can move

        self.max_camera = ((self.battle_map_height.image.get_width() - 1),
                           (self.battle_map_height.image.get_height() - 1))  # reset max camera to new map size

        self.active_subunit_list = []
        self.visible_subunit_list = {}

        self.camera_mode = self.start_camera_mode
        self.setup_battle_troop(self.subunit_updater)
        self.all_team_subunit = {1: pygame.sprite.Group(),
                                 2: pygame.sprite.Group()}  # more team can be added later
        self.team_troop_number = [0 for _ in range(len(self.all_team_subunit) + 1)]  # reset list of troop number in each team
        self.battle_scale = [1 for _ in self.team_troop_number]
        self.start_troop_number = [0 for _ in self.team_troop_number]
        self.death_troop_number = [0 for _ in self.team_troop_number]
        self.visible_subunit_list = {key: {} for key in self.all_team_subunit.keys()}

        self.battle_scale_ui.change_fight_scale(self.battle_scale)

        subunit_to_make = tuple(set([this_subunit.troop_id for this_subunit in self.subunit_updater]))
        who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key in subunit_to_make}
        who_todo |= {key: value for key, value in self.leader_data.leader_list.items() if key in subunit_to_make}
        self.subunit_animation_pool = self.main.create_troop_sprite_pool(who_todo)

    def run_game(self):
        # Create Starting Values
        self.game_state = "battle"  # battle mode
        self.current_pop_up_row = 0
        self.input_popup = (None, None)  # no popup asking for user text input state
        self.player_char = None  # Which unit is currently selected
        self.drama_text.queue = []  # reset drama text popup queue

        self.change_battle_state()

        if self.char_selected is not None:  # select player char by default if control only one
            for this_subunit in self.active_subunit_list:  # get player char
                if this_subunit.game_id == self.char_selected:
                    self.player_char = this_subunit
                    self.player_char.player_manual_control = True
                    self.battle_camera.change_layer(self.player_char, 999999)
                    self.command_ui.add_leader_image(this_subunit.portrait)
                    if self.camera_mode == "Follow":
                        self.true_camera_pos = pygame.Vector2(self.player_char.base_pos)
                        self.camera_fix()
                    break

        self.setup_battle_ui("add")

        self.shown_camera_pos = self.camera_pos

        self.player_char_input_delay = 0
        self.text_delay = 0
        self.mouse_timer = 0  # This is timer for checking double mouse click, use realtime
        self.screen_shake_value = 0
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.weather_spawn_timer = 0
        self.click_any = False  # For checking if mouse click on anything, if not close ui related to unit
        self.new_unit_click = False  # For checking if another subunit is clicked when inspect ui open

        self.player_input_state = None
        self.previous_player_input_state = None

        self.battle_mouse_pos = [0, 0]  # mouse position list in battle map not screen without zoom
        self.battle_mouse_pos = [0, 0]  # with camera zoom adjust but without screen scale
        self.command_mouse_pos = [0, 0]  # with zoom and screen scale for unit command
        self.unit_selector.current_row = 0

        self.time_update()

        self.effect_updater.update(self.active_subunit_list, self.dt)

        # self.map_def_array = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        while True:  # self running
            self.fps_count.fps_show(self.clock)
            event_key_press = None
            mouse_left_up = False  # left click
            mouse_left_down = False  # hold left click
            mouse_right_up = False  # right click
            mouse_right_down = False  # hold right click
            double_mouse_right = False  # double right click
            mouse_scroll_down = False
            mouse_scroll_up = False
            key_state = pygame.key.get_pressed()
            esc_press = False
            self.click_any = False

            self.true_dt = self.clock.get_time() / 1000  # dt before game_speed

            self.battle_ui_updater.remove(self.single_text_popup)  # remove button text popup every update

            self.mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen

            self.cursor.update(self.mouse_pos)

            self.base_mouse_pos = pygame.Vector2((self.mouse_pos[0] - self.center_screen[0] + self.camera_pos[0]),
                                                 (self.mouse_pos[1] - self.center_screen[1] + self.camera_pos[
                                                     1]))  # mouse pos on the map based on camera position
            self.battle_mouse_pos = self.base_mouse_pos / 5  # mouse pos on the map at current camera zoom scale
            self.command_mouse_pos = pygame.Vector2(self.battle_mouse_pos[0] / self.screen_scale[0],
                                                    self.battle_mouse_pos[1] / self.screen_scale[
                                                        1])  # with screen scale

            self.battle_ui_updater.clear(self.screen, self.background)  # Clear sprite before update new one

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit self
                    self.input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.battle_ui_updater.add(*self.confirm_ui_popup)

                elif event.type == self.SONG_END:  # change music track
                    pygame.mixer.music.unload()
                    self.picked_music = random.randint(0, len(self.playing_music) - 1)
                    pygame.mixer.music.load(self.music_list[self.playing_music[self.picked_music]])
                    pygame.mixer.music.play(fade_ms=100)

                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # open/close menu
                    esc_press = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_left_up = True
                        self.new_unit_click = False
                    elif event.button == 3:  # Right Click
                        mouse_right_up = True
                        if self.mouse_timer == 0:
                            self.mouse_timer = 0.001  # Start timer after first mouse click
                        elif self.mouse_timer < 0.3:  # if click again within 0.3 second for it to be considered double click
                            double_mouse_right = True  # double right click
                            self.mouse_timer = 0
                    elif event.button == 4:  # Mouse scroll up
                        mouse_scroll_up = True
                    elif event.button == 5:  # Mouse scroll down
                        mouse_scroll_down = True

                elif event.type == pygame.KEYDOWN:
                    if self.input_popup[0] == "text_input":  # event update to input box
                        self.input_box.player_input(event, key_state)
                        self.text_delay = 0.1
                    else:
                        event_key_press = event.key

            if pygame.mouse.get_pressed()[0]:  # Hold left click
                mouse_left_down = True
            elif pygame.mouse.get_pressed()[2]:  # Hold left click
                mouse_right_down = True

            if self.player_char_input_delay:  # delay for command input
                self.player_char_input_delay -= self.dt
                if self.player_char_input_delay < 0:
                    self.player_char_input_delay = 0

            if self.input_popup == (None, None):
                if esc_press:  # open/close menu
                    if self.game_state == "battle":  # in battle
                        self.game_state = "menu"  # open menu
                        self.battle_ui_updater.add(self.battle_menu,
                                                   *self.battle_menu_button)  # add menu and its buttons to drawer
                        esc_press = False  # reset esc press, so it not stops esc menu when open

                if self.game_state == "battle":  # game in battle state
                    if self.player_input_state is None:  # register user input during gameplay
                        if mouse_scroll_up or mouse_scroll_down:  # Mouse scroll
                            self.mouse_scrolling_process(mouse_scroll_up, mouse_scroll_down)

                        # keyboard input
                        if event_key_press is not None:
                            self.battle_keyboard_process(event_key_press)

                        self.camera_process(key_state)

                        if self.mouse_timer != 0:  # player click mouse once before
                            self.mouse_timer += self.ui_dt  # increase timer for mouse click using real time
                            if self.mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                                self.mouse_timer = 0

                        if mouse_left_up or mouse_right_up or mouse_left_down or mouse_right_down or key_state:
                            self.battle_mouse_process(mouse_left_up, mouse_right_up, double_mouse_right,
                                                      mouse_left_down, mouse_right_down, key_state, event_key_press)

                    else:  # register and process ui that require player input and block everything else
                        if type(self.player_input_state) is not str:  # ui input state
                            choice = self.player_input_state.selection(self.mouse_pos)
                            if self.player_input_state == self.wheel_ui:  # wheel ui process
                                if mouse_left_up:
                                    self.wheel_ui_process(choice)
                                elif event_key_press == pygame.K_TAB:  # Close unit command wheel ui
                                    self.battle_ui_updater.remove(self.wheel_ui)
                                    old_player_input_state = self.player_input_state
                                    self.player_input_state = self.previous_player_input_state
                                    self.previous_player_input_state = old_player_input_state

                    # Drama text function
                    if not self.drama_timer and self.drama_text.queue:  # Start timer and draw if there is event queue
                        self.battle_ui_updater.add(self.drama_text)
                        self.drama_text.process_queue()
                        self.drama_timer = 0.1
                    elif self.drama_timer:
                        self.drama_text.play_animation()
                        self.drama_timer += self.ui_dt
                        if self.drama_timer > 3:
                            self.drama_timer = 0
                            self.battle_ui_updater.remove(self.drama_text)

                    if self.dt:  # Part that run when game not pause only
                        # Event log
                        if self.event_schedule is not None and self.event_list != [] and self.time_number.time_number >= self.event_schedule:
                            self.event_log.add_log(None, event_id=self.event_id)
                            for event in self.event_log.map_event:
                                if self.event_log.map_event[event]["Time"] is not None and self.event_log.map_event[event][
                                    "Time"] > self.time_number.time_number:
                                    self.event_id = event
                                    self.event_schedule = self.event_log.map_event[event]["Time"]
                                    break
                            self.event_list = self.event_list[1:]

                        # Weather system
                        if self.weather_playing is not None and self.time_number.time_number >= self.weather_playing:
                            this_weather = self.weather_event[0]

                            if this_weather[0] != 0 and this_weather[0] in self.weather_data:
                                self.current_weather.__init__(self.time_ui, this_weather[0], this_weather[2],
                                                              this_weather[3], self.weather_data)
                            else:  # Clear weather when no weather found, also for when input weather not in ruleset
                                self.current_weather.__init__(self.time_ui, 4, 0, 0, self.weather_data)
                            self.weather_event.pop(0)
                            if self.current_weather.name in self.weather_effect_images:
                                self.battle_map.add_effect(effect_image=
                                                           self.weather_effect_images[self.current_weather.name][
                                                               self.current_weather.level],
                                                           time_image=self.day_effect_images[self.day_time])

                            if self.weather_event:  # Get end time of next event which is now index 0
                                self.weather_playing = self.weather_event[0][1]
                            else:
                                self.weather_playing = None

                        if self.current_weather.spawn_rate:
                            self.weather_spawn_timer += self.dt
                            if self.weather_spawn_timer >= self.current_weather.spawn_rate:
                                self.weather_spawn_timer = 0
                                self.spawn_weather_matter()

                        # Screen shaking
                        self.shown_camera_pos = self.camera_pos  # reset camera pos first
                        if self.screen_shake_value:
                            self.screen_shake_value -= 1
                            self.shake_camera()
                            if self.screen_shake_value < 0:
                                self.screen_shake_value = 0

                        # Music System
                        if self.music_schedule and self.time_number.time_number >= self.music_schedule[0] and \
                                self.music_event:
                            pygame.mixer.music.unload()
                            self.playing_music = self.music_event[0].copy()
                            self.picked_music = random.randint(0, len(self.playing_music) - 1)
                            pygame.mixer.music.load(self.music_list[self.playing_music[self.picked_music]])
                            pygame.mixer.music.play(fade_ms=100)
                            self.music_schedule = self.music_schedule[1:]
                            self.music_event = self.music_event[1:]

                    # Run troop ai logic no more than limit number of subunit per update to prevent stutter
                    if self.troop_ai_logic_queue:
                        limit = int(len(self.troop_ai_logic_queue) / 10)
                        if limit < 10:
                            limit = 10
                        for index, this_subunit in enumerate(self.troop_ai_logic_queue):
                            this_subunit.troop_ai_logic()
                            if index == limit:
                                break
                        self.troop_ai_logic_queue = self.troop_ai_logic_queue[10:]

                    # Battle related updater
                    self.subunit_updater.update(self.dt)
                    self.effect_updater.update(self.active_subunit_list, self.dt)
                    self.weather_updater.update(self.dt, self.time_number.time_number)

                    self.ui_updater.update()  # update ui

                    self.camera.update(self.shown_camera_pos, self.battle_camera)

                    for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                        self.play_sound_effect(key, value[0], shake=value[1])
                    self.sound_effect_queue = {}

                    # Update game time
                    self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
                    if self.ui_timer >= 0.4:
                        self.mini_map.update([self.camera_pos, self.camera_topleft_corner], self.active_subunit_list)
                        self.command_ui.value_input(who=self.player_char)
                        self.countdown_skill_icon()
                        self.battle_scale = [(value / sum(self.team_troop_number) * 100) for value in
                                             self.team_troop_number]
                        self.battle_scale_ui.change_fight_scale(
                            self.battle_scale)  # change fight colour scale on time_ui bar
                        self.ui_timer -= -0.4
                    self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                    self.ui_dt = self.dt  # get ui timer before apply self

                    if self.dt > 0.1:
                        self.dt = 0.1  # make it so stutter and lag does not cause overtime issue

                    self.time_number.timer_update(self.dt * 100)  # update battle time
                    self.time_update()

                elif self.game_state == "end":
                    if self.battle_done_box not in self.battle_ui_updater:
                        if not self.active_subunit_list:  # draw
                            self.battle_done_box.pop("Draw")
                        else:
                            for key, value in self.all_team_subunit.items():
                                if value:
                                    self.battle_done_box.pop(key)
                                    break

                        self.battle_done_button.rect = self.battle_done_button.image.get_rect(
                            midtop=self.battle_done_button.pos)
                        self.battle_ui_updater.add(self.battle_done_box, self.battle_done_button)
                    else:
                        if mouse_left_up and self.battle_done_button.rect.collidepoint(self.mouse_pos):
                            return
                            # coa_list = [None, None]
                            # for index, coa in enumerate(self.team_coa):
                            #     coa_list[index] = coa.image
                            # self.battle_done_box.show_result(coa_list[0], coa_list[1],
                            #                                  (self.start_troop_number, self.team_troop_number,
                            #                                   self.wound_troop_number, self.death_troop_number,
                            #                                   self.flee_troop_number, self.capture_troop_number))
                            # self.battle_done_button.rect = self.battle_done_button.image.get_rect(
                            #     center=(self.battle_done_box.rect.midbottom[0],
                            #             self.battle_done_box.rect.midbottom[
                            #                 1] / 1.3))

                elif self.game_state == "menu":  # Complete self pause when open either esc menu or encyclopedia
                    command = self.escmenu_process(mouse_left_up, mouse_left_down, esc_press, mouse_scroll_up,
                                                   mouse_scroll_down, self.battle_ui_updater)
                    if command == "end_battle":
                        return

            elif self.input_popup != (
                    None, None):  # currently, have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down)

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.input_popup[1] == "quit":  # quit game
                        self.battle_ui_updater.clear(self.screen, self.background)
                        self.battle_camera.clear(self.screen, self.background)
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.battle_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup)

                elif self.input_cancel_button.event or esc_press:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.battle_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup)

                elif self.input_popup[0] == "text_input":
                    if self.text_delay == 0:
                        if event_key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_state)
                            self.text_delay = 0.1
                    else:
                        self.text_delay += self.true_dt
                        if self.text_delay >= 0.3:
                            self.text_delay = 0

            self.screen.blit(self.camera.image, (0, 0))  # Draw the self camera and everything that appear in it
            self.battle_ui_updater.draw(self.screen)  # Draw the UI
            pygame.display.update()  # update self display, draw everything
            self.clock.tick(60)  # clock update even if self pause

    def exit_battle(self):
        self.battle_ui_updater.clear(self.screen, self.background)  # remove all sprite
        self.battle_camera.clear(self.screen, self.background)  # remove all sprite

        self.setup_battle_ui("remove")  # remove ui from group

        self.battle_ui_updater.remove(self.battle_menu, *self.battle_menu_button, *self.esc_slider_menu,
                                      *self.esc_value_boxes, self.battle_done_box,
                                      self.battle_done_button)  # remove menu

        # remove all reference from battle object
        self.player_char = None

        self.command_ui.last_who = None

        self.active_subunit_list = []
        self.map_move_array = []
        self.map_def_array = []

        self.troop_ai_logic_queue = []

        clean_group_object((self.subunit_updater, self.char_icon,
                            self.effect_updater, self.weather_matter))

        self.subunit_animation_pool = None
        self.generic_action_data = None

        self.sound_effect_queue = {}

        self.battle_map_base.clear_image()
        self.battle_map_feature.clear_image()
        self.battle_map_height.clear_image()
        self.battle_map.clear_image()

        self.drama_timer = 0  # reset drama text popup
        self.battle_ui_updater.remove(self.drama_text)
