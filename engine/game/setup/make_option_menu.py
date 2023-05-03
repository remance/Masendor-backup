from engine.uimenu import uimenu
from engine import utility

load_image = utility.load_image
load_images = utility.load_images
make_bar_list = utility.make_bar_list


def make_option_menu(main_dir, screen_scale, screen_rect, screen_width, screen_height, image_list,
                     updater, config, keybind, battle_select_image):
    """
    This method create UI in option menu and keybinding menu

    :param main_dir: main directory
    :param screen_scale:
    :param screen_rect:
    :param screen_width: width of game screen
    :param screen_height: height of game screen
    :param image_list:
    :param updater:
    :param config: config
    :param keybind:
    :param battle_select_image:
    :return: dict of objects
    """
    # Create option menu button and icon
    font_size = int(36 * screen_scale[1])

    back_button = uimenu.MenuButton(screen_scale, image_list, (screen_rect.width / 3, screen_rect.height / 1.2),
                                  updater, text="Back")
    keybind_button = uimenu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 1.2),
                                     updater, text="Keybind")
    default_button = uimenu.MenuButton(screen_scale, image_list, (screen_rect.width / 1.5, screen_rect.height / 1.2),
                                     updater, text="Default")

    fullscreen_box = uimenu.TickBox((screen_rect.width / 2, screen_rect.height / 6.5),
                                  battle_select_image["untick"], battle_select_image["tick"], "fullscreen")

    if int(config["full_screen"]) == 1:
        fullscreen_box.change_tick(True)

    fullscreen_text = uimenu.OptionMenuText(
        (fullscreen_box.pos[0] - (fullscreen_box.pos[0] / 4.5), fullscreen_box.pos[1]),
        "Full Screen", font_size)

    # Volume change scroll bar
    option_menu_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "option_ui", "slider"))
    scroller_images = (option_menu_images["scroller_box"], option_menu_images["scroller"])
    scroll_button_images = (option_menu_images["scroll_button_normal"], option_menu_images["scroll_button_click"])
    volume_slider = {"master": uimenu.SliderMenu(scroller_images, scroll_button_images,
                                               (screen_rect.width / 2, screen_rect.height / 4),
                                               float(config["master_volume"])),
                     "music": uimenu.SliderMenu(scroller_images, scroll_button_images,
                                              (screen_rect.width / 2, screen_rect.height / 3),
                                              float(config["music_volume"])),
                     "voice": uimenu.SliderMenu(scroller_images, scroll_button_images,
                                              (screen_rect.width / 2, screen_rect.height / 2.4),
                                              float(config["voice_volume"])),
                     "effect": uimenu.SliderMenu(scroller_images, scroll_button_images,
                                               (screen_rect.width / 2, screen_rect.height / 2),
                                               float(config["effect_volume"])),
                     }
    value_box = {key: uimenu.ValueBox(option_menu_images["value"],
                                    (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                                    volume_slider[key].value, int(26 * screen_scale[1])) for key in volume_slider}

    volume_text = {key: uimenu.OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                             volume_slider[key].pos[1]), key.capitalize() + " Volume",
                                            font_size) for key in volume_slider}

    # Resolution changing bar that fold out the list when clicked
    image = load_image(main_dir, screen_scale, "drop_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = image
    image3 = load_image(main_dir, screen_scale, "drop_click.jpg", ("ui", "mainmenu_ui"))
    image_list = [image, image2, image3]
    resolution_drop = uimenu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 1.8),
                                      updater, text=str(screen_width) + " x " + str(screen_height),
                                      size=int(30 * screen_scale[1]))
    resolution_list = ("2560 x 1440", "2048 x 1152", "1920 x 1080", "1600 x 900", "1366 x 768",
                       "1280 x 720", "1136 x 640", "1024 x 600", "960 x 540", "848 x 480")  # add more here
    resolution_bar = make_bar_list(main_dir, screen_scale, resolution_list, resolution_drop, updater)

    resolution_text = uimenu.OptionMenuText((resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5),
                                           resolution_drop.pos[1]), "Display Resolution", font_size)

    keybind_text = {"Main Weapon Attack": uimenu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 5),
                                                              "Main Weapon Attack", font_size),
                    "Sub Weapon Attack": uimenu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 3.5),
                                                             "Sub Weapon Attack", font_size),
                    "Move Left": uimenu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 2.5),
                                                     "Move Left", font_size),
                    "Move Right": uimenu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 2),
                                                      "Move Right", font_size),
                    "Move Up": uimenu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.7),
                                                   "Move Up", font_size),
                    "Move Down": uimenu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.5),
                                                     "Move Down", font_size),
                    "Menu/Cancel": uimenu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 5),
                                                       "Menu/Cancel", font_size),
                    "Order Menu": uimenu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 3.5),
                                                      "Order Menu", font_size),
                    "Run Input": uimenu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 2.5),
                                                     "Run Input", font_size),
                    "Skill 1": uimenu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 2),
                                                   "Skill 1", font_size),
                    "Skill 2": uimenu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 1.7),
                                                   "Skill 2", font_size),
                    "Skill 3": uimenu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 1.5),
                                                   "Skill 3", font_size),
                    "Skill 4": uimenu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 5),
                                                   "Skill 4", font_size),
                    "Swap Weapon Set 1": uimenu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 3.5),
                                                             "Swap Weapon Set 1", font_size),
                    "Swap Weapon Set 2": uimenu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 2.5),
                                                             "Swap Weapon Set 2", font_size),
                    "Toggle Run": uimenu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 2),
                                                      "Toggle Run", font_size),
                    "Auto Move": uimenu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 1.7),
                                                     "Auto Move", font_size)}

    control_type = "keyboard"  # make default keyboard for now, get changed later when player enter keybind menu
    keybind = keybind[control_type]

    control_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "option_ui"))
    control_switch = uimenu.ControllerIcon((screen_rect.width / 2, screen_rect.height * 0.1),
                                           control_images, control_type)

    keybind_icon = {"Main Weapon Attack": uimenu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 5),
                                                           font_size, control_type,
                                                           keybind["Main Weapon Attack"]),
                    "Sub Weapon Attack": uimenu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 3.5),
                                                          font_size, control_type,
                                                          keybind["Sub Weapon Attack"]),
                    "Move Left": uimenu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 2.5), font_size,
                                                  control_type, keybind["Move Left"]),
                    "Move Right": uimenu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 2), font_size,
                                                   control_type, keybind["Move Right"]),
                    "Move Up": uimenu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.7), font_size,
                                                control_type, keybind["Move Up"]),
                    "Move Down": uimenu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.5), font_size,
                                                  control_type, keybind["Move Down"]),
                    "Menu/Cancel": uimenu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 5), font_size,
                                                    control_type, keybind["Menu/Cancel"]),
                    "Order Menu": uimenu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 3.5), font_size,
                                                   control_type, keybind["Order Menu"]),
                    "Run Input": uimenu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2.5), font_size,
                                                  control_type, keybind["Run Input"]),
                    "Skill 1": uimenu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2), font_size,
                                                control_type, keybind["Skill 1"]),
                    "Skill 2": uimenu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 1.7), font_size,
                                                control_type, keybind["Skill 2"]),
                    "Skill 3": uimenu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 1.5), font_size,
                                                control_type, keybind["Skill 3"]),
                    "Skill 4": uimenu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 5), font_size,
                                                control_type, keybind["Skill 4"]),
                    "Swap Weapon Set 1": uimenu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 3.5),
                                                          font_size, control_type,
                                                          keybind["Swap Weapon Set 1"]),
                    "Swap Weapon Set 2": uimenu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 2.5),
                                                          font_size, control_type,
                                                          keybind["Swap Weapon Set 2"]),
                    "Toggle Run": uimenu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 2),
                                                   font_size, control_type,
                                                   keybind["Toggle Run"]),
                    "Auto Move": uimenu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 1.7),
                                                  font_size, control_type,
                                                  keybind["Auto Move"])}

    return {"back_button": back_button, "keybind_button": keybind_button, "default_button": default_button,
            "resolution_drop": resolution_drop,
            "resolution_bar": resolution_bar, "resolution_text": resolution_text, "volume_sliders": volume_slider,
            "value_boxes": value_box, "volume_texts": volume_text, "fullscreen_box": fullscreen_box,
            "fullscreen_text": fullscreen_text, "keybind_text": keybind_text, "keybind_icon": keybind_icon,
            "control_switch": control_switch}