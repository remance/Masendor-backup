import ast
import csv
import os

from pathlib import Path

import pygame

from engine.weather import weather
from engine import utility

from engine.data.datastat import GameData

stat_convert = utility.stat_convert
load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
fcv = utility.filename_convert_readable


class BattleMapData(GameData):
    def __init__(self):
        """
        For keeping all data related to battle map.
        """
        GameData.__init__(self)
        self.terrain_colour = {}
        with open(os.path.join(self.module_dir, "map", "terrain.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    self.terrain_colour[row[0]] = row[1:]
        self.terrain_list = tuple(self.terrain_colour.keys())
        self.terrain_colour = tuple([value[0] for value in self.terrain_colour.values()])

        self.feature_colour = {}
        with open(os.path.join(self.module_dir, "map", "feature.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    self.feature_colour[row[0]] = row[1:]

        self.feature_list = tuple(self.feature_colour.keys())
        self.feature_colour = tuple([value[0] for value in self.feature_colour.values()])

        # read terrain feature mode
        self.feature_mod = {}
        with open(os.path.join(self.module_dir, "map", "terrain_effect.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            mod_column = ("Infantry Speed Effect", "Infantry Attack Effect", "Infantry Defence Effect",
                          "Cavalry Speed Effect", "Cavalry Attack Effect", "Cavalry Defence Effect")
            int_column = ("ID", "Range Defence Bonus", "Hide Bonus", "Discipline Bonus",
                          "Day Temperature", "Night Temperature", "Dust")  # value int only
            tuple_column = ("Status",)
            mod_column = [index for index, item in enumerate(header) if item in mod_column]
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for row in rd[1:]:  # skip convert header row
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, mod_column=mod_column, tuple_column=tuple_column,
                                       int_column=int_column)
                self.feature_mod[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}

                # Add twilight temperature
                self.feature_mod[row[0]]["Twilight Temperature"] = \
                    int((self.feature_mod[row[0]]["Day Temperature"] +
                         self.feature_mod[row[0]]["Night Temperature"]) / 2)
        edit_file.close()

        self.feature_mod_lore = self.localisation.create_lore_data("terrain_effect")

        self.empty_image = pygame.Surface((0, 0))  # empty texture image
        self.camp_image = load_image(self.module_dir, (1, 1), "camp.png",
                                     ("map", "texture"))  # war camp texture image

        self.map_texture = []
        self.texture_folder = [item["Name"] for item in self.feature_mod.values() if
                               item["Name"] != ""]

        for index, folder in enumerate(self.texture_folder):
            images = load_images(self.module_dir, subfolder=("map", "texture", fcv(folder, revert=True)),
                                 key_file_name_readable=True)
            self.map_texture.append(list(images.values()))

        self.day_effect_images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                             subfolder=("map", "day"), key_file_name_readable=True)

        self.battle_map_colour = {}
        with open(os.path.join(self.module_dir, "map", "map_colour.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    self.battle_map_colour[row[0]] = row[1:]

        self.weather_data = {}
        with open(os.path.join(self.module_dir, "map", "weather", "weather.csv"),
                  encoding="utf-8", mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            int_column = ("ID",)  # value int only
            tuple_column = ("Element", "Status", "Spell")
            int_column = [index for index, item in enumerate(header) if item in int_column]
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, int_column=int_column)
                self.weather_data[row[0]] = {header[index + 1]: stuff for index, stuff in enumerate(row[1:])}
        edit_file.close()

        weather_list = [item["Name"] for item in self.weather_data.values()]
        strength_list = ("Light ", "Normal ", "Strong ")
        self.weather_list = []
        for item in weather_list:  # list of weather with different strength
            for strength in strength_list:
                self.weather_list.append(strength + item)
        self.weather_list = tuple(self.weather_list)
        edit_file.close()

        self.weather_lore = self.localisation.create_lore_data("weather")

        self.weather_matter_images = {}
        for this_weather in weather_list:  # Load weather matter sprite image
            try:
                images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                     subfolder=("map", "weather", "matter", fcv(this_weather, revert=True)))
                self.weather_matter_images[this_weather] = tuple(images.values())
            except FileNotFoundError:
                self.weather_matter_images[this_weather] = ()

        self.weather_effect_images = {}
        for this_weather in weather_list:  # Load weather effect sprite image
            try:
                images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                     subfolder=("map", "weather", "effect", fcv(this_weather, revert=True)))
                self.weather_effect_images[this_weather] = tuple(images.values())
            except FileNotFoundError:
                self.weather_effect_images[this_weather] = ()

        weather_icon_list = load_images(self.module_dir, screen_scale=self.screen_scale,
                                        subfolder=("map", "weather", "icon"))  # Load weather icon
        new_weather_icon = {}
        for weather_icon in weather_list:
            for strength in range(0, 3):
                new_name = weather_icon + "_" + str(strength)
                for item in weather_icon_list:
                    if new_name == fcv(item):
                        new_weather_icon[new_name] = weather_icon_list[item]
                        break

        weather.Weather.weather_icons = new_weather_icon

        read_folder = Path(os.path.join(self.module_dir, "map", "preset"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]

        self.preset_map_list = []  # map name list for map selection list
        self.preset_map_folder = []  # folder for reading later
        self.battle_campaign = {}

        for file_campaign in sub1_directories:
            read_folder = Path(os.path.join(self.module_dir, "map", "preset", file_campaign))
            campaign_file_name = os.sep.join(os.path.normpath(file_campaign).split(os.sep)[-1:])
            sub2_directories = [x for x in read_folder.iterdir() if x.is_dir()]
            for file_map in sub2_directories:
                map_file_name = os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:])
                self.preset_map_folder.append(map_file_name)
                map_name = self.localisation.grab_text(key=("preset_map", campaign_file_name,
                                                            "info", map_file_name, "Name"))
                self.preset_map_list.append(map_name)
                self.battle_campaign[map_file_name] = campaign_file_name

        # Load custom map list
        read_folder = Path(os.path.join(self.module_dir, "map", "custom"))
        sub1_directories = [x for x in read_folder.iterdir() if x.is_dir()]

        self.battle_map_list = self.preset_map_list.copy() + ["Random"]
        self.battle_map_folder = self.preset_map_folder.copy() + ["Random"]

        for file_map in sub1_directories:
            self.battle_map_folder.append(os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:]))

            map_name = self.localisation.grab_text(key=("custom_map",
                                                        os.sep.join(os.path.normpath(file_map).split(os.sep)[-1:]),
                                                        "Name"))
            self.battle_map_list.append(map_name)
