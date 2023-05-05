import random

from engine.battlemap import battlemap
from engine import utility

load_images = utility.load_images


def create_preview_map(self):
    # Create map preview image
    if self.battle_map_folder[self.current_map_select] != "Random":
        map_images = load_images(self.module_dir, subfolder=("map", "preset", self.battle_map_folder[self.current_map_select]))
    else:  # random map
        terrain, feature, height = battlemap.create_random_map(self.battle_map_data.terrain_colour,
                                                               self.battle_map_data.feature_colour,
                                                               random.randint(1, 3), random.randint(4, 9),
                                                               random.randint(1, 4))
        map_images = {"base": terrain, "feature": feature, "height": height}
    self.map_preview.change_map(map_images["base"], map_images["feature"], map_images["height"])
    self.main_ui_updater.add(self.map_preview)

    # Create map title at the top
    self.map_title.change_name(self.battle_map_list[self.current_map_select])
    self.main_ui_updater.add(self.map_title)

    # Create map description
    self.map_info = self.read_selected_map_data(self.battle_map_folder, "info_" + self.language + ".csv")

    description = [self.map_info[self.battle_map_list[self.current_map_select]]["Description 1"],
                   self.map_info[self.battle_map_list[self.current_map_select]]["Description 2"]]
    self.map_description.change_text(description)
