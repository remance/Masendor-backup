from engine.uimenu import uimenu
from engine.uibattle.uibattle import TempUnitIcon
from engine.utility import setup_list


def menu_custom_map_select(self, esc_press):
    if self.map_back_button.event or esc_press:

        self.remove_ui_updater(*self.map_select_button, self.custom_map_list_box, self.faction_list_box,
                               self.custom_map_option_box, self.unit_selector,
                               self.unit_selector.scroll, self.weather_custom_select, self.wind_custom_select,
                               self.custom_map_option_box, self.night_battle_tick_box, self.map_preview,
                               self.unit_model_room)

        for group in (self.map_namegroup, self.team_coa):
            for stuff in group:
                stuff.kill()
                del stuff

        self.back_mainmenu()

    elif self.select_button.event:  # select this map and team list, go to unit setup screen
        if len([coa for coa in self.team_coa if coa.name is not None and coa.name != "None"]) > 1:
            self.menu_state = "custom_unit_setup"
            self.unit_select_row = 0

            self.play_map_data["unit"] = {"pos": {}}

            self.add_ui_updater(self.unit_list_box, self.map_list_box)

            self.remove_ui_updater(self.custom_map_option_box, self.night_battle_tick_box, self.weather_custom_select,
                                   self.wind_custom_select, self.faction_list_box)

            for coa in self.team_coa:
                if coa.coa_images and coa.team not in self.play_map_data["unit"]:
                    self.play_map_data["unit"][coa.team] = []
                    self.play_map_data["unit"]["pos"][coa.team] = {}
                elif coa.team in self.play_map_data["unit"]:  # non existence team
                    self.play_map_data["unit"].pop(coa.team)
                    self.play_map_data["unit"]["pos"].pop(coa.team)

            self.add_ui_updater(self.unit_list_box, self.unit_list_box.scroll)
            for coa in self.team_coa:
                if coa.selected:  # get unit for selected team
                    unit_list = []
                    for faction in coa.coa_images:
                        if faction == 0:  # all faction
                            for this_faction in self.faction_data.faction_unit_list:
                                unit_list += list(self.faction_data.faction_unit_list[this_faction].keys())
                        else:
                            unit_list += list(self.faction_data.faction_unit_list[faction].keys())

                        unit_list = sorted((set(unit_list)), key=unit_list.index)

                    # setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, unit_list,
                    #            self.map_namegroup, self.unit_list_box, self.main_ui_updater)
                    break
        else:
            self.input_popup = ("confirm_input", "warning")
            self.input_ui.change_instruction("Require at least 2 teams")
            self.add_ui_updater(self.inform_ui_popup)

    if self.popup_list_box in self.main_ui_updater:
        if self.popup_list_box.scroll.event:
            new_row = self.popup_list_box.scroll.player_input(self.cursor.pos)
            if new_row is not None:
                self.current_popup_row = new_row
                setup_list(self.screen_scale, uimenu.NameList, self.current_popup_row,
                           self.battle_map_data.weather_list,
                           self.popup_namegroup, self.popup_list_box, self.main_ui_updater)

        elif self.popup_list_box.mouse_over:
            for index, name in enumerate(self.popup_namegroup):  # click on popup list
                if name.event_press:
                    self.weather_custom_select.rename("Weather: " + name.name)
                    battle_time = "09:00:00"
                    if self.night_battle_tick_box.tick:  # check for night battle
                        battle_time = "21:00:00"
                    self.play_map_data["info"]["weather"] = \
                        [[int(self.battle_map_data.weather_list.index(name.name) / 3), battle_time,
                          self.play_map_data["info"]["weather"][0][2],
                          ("Light", "Normal", "Strong").index(name.name.split(" ")[0])]]
                    for this_name in self.popup_namegroup:  # remove name list
                        this_name.kill()
                        del this_name
                    self.remove_ui_updater(self.popup_list_box, self.popup_list_box.scroll)
                    break

        elif self.cursor.is_select_just_down:  # click other stuffs
            for this_name in self.popup_namegroup:  # remove name list
                this_name.kill()
                del this_name
            self.remove_ui_updater(self.popup_list_box, self.popup_list_box.scroll)

    change_team_coa(self)
    for index, name in enumerate(self.source_namegroup):  # player select faction name list
        if name.mouse_over:
            for coa in self.team_coa:
                if coa.selected:
                    if name.name != "None":
                        faction_index = self.faction_data.faction_name_list.index(name.name)
                        if name.event_press:
                            if "Team Faction " + str(coa.team) in self.play_map_data["info"]:
                                if faction_index not in self.play_map_data["info"][
                                    "Team Faction " + str(coa.team)]:
                                    self.play_map_data["info"]["Team Faction " + str(coa.team)].append(
                                        faction_index)
                            else:
                                self.play_map_data["info"]["Team Faction " + str(coa.team)] = [faction_index]
                            coa.change_coa(
                                {int(faction): self.faction_data.coa_list[int(faction)] for faction in
                                 self.play_map_data["info"]["Team Faction " + str(coa.team)]},
                                self.faction_data.faction_list[self.play_map_data["info"][
                                    "Team Faction " + str(coa.team)][0]]["Name"])
                        elif self.cursor.is_mouse_right_just_up:
                            if faction_index in self.play_map_data["info"]["Team Faction " + str(coa.team)]:
                                self.play_map_data["info"]["Team Faction " + str(coa.team)].remove(
                                    faction_index)
                            if self.play_map_data["info"]["Team Faction " + str(coa.team)]:  # still not empty
                                coa.change_coa(
                                    {int(faction): self.faction_data.coa_list[int(faction)] for faction in
                                     self.play_map_data["info"]["Team Faction " + str(coa.team)]},
                                    self.faction_data.faction_list[self.play_map_data["info"][
                                        "Team Faction " + str(coa.team)][0]]["Name"])
                            else:  # list empty remove data
                                self.play_map_data["info"].pop("Team Faction " + str(coa.team))
                                coa.change_coa({0: None}, "None")
                    else:
                        if name.event_press and "Team Faction " + str(coa.team) in self.play_map_data["info"]:
                            self.play_map_data["info"].pop("Team Faction " + str(coa.team))
                        coa.change_coa({0: None}, "None")

                    if "Team Faction " + str(coa.team) in self.play_map_data["info"]:  # camp, team exist
                        if coa.team not in self.camp_pos:  # new team, camp not exist
                            self.camp_pos[coa.team] = []
                            for icon in self.camp_icon:
                                icon.kill()
                            self.camp_icon = []
                        else:
                            for camp in self.camp_pos[coa.team]:
                                self.camp_icon.append(TempUnitIcon(self.screen_scale, coa.team,
                                                                            camp[1], 0))
                        if not self.camp_icon or self.camp_icon[-1].name != "+":
                            self.camp_icon.append(TempUnitIcon(self.screen_scale, coa.team, "+", 0))

                    else:  # team no longer exist
                        if coa.team in self.camp_pos:
                            self.camp_pos.pop(coa.team)
                            for icon in self.camp_icon:
                                icon.kill()
                            self.camp_icon = []
                    self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)
                    break

    if self.custom_map_option_box.mouse_over:
        if self.night_battle_tick_box.event_press:
            if self.night_battle_tick_box.tick is False:
                self.night_battle_tick_box.change_tick(True)
            else:
                self.night_battle_tick_box.change_tick(False)
            battle_time = "09:00:00"
            if self.night_battle_tick_box.tick:  # check for night battle
                battle_time = "21:00:00"
            self.play_map_data["info"]["weather"][0][1] = battle_time

        elif self.weather_custom_select.event_press:
            self.current_popup_row = 0
            self.popup_list_open(self.weather_custom_select.rect.bottomleft,
                                 self.battle_map_data.weather_list, "weather", "top")

        elif self.wind_custom_select.event_press:
            print('test')
            self.input_popup = ("text_input", "wind")
            self.input_ui.change_instruction("Wind Direction Degree:")
            self.add_ui_updater(self.input_ui_popup)

    if self.cursor.is_mouse_right_just_up and self.map_preview.mouse_over:
        for index, icon in enumerate(self.unit_icon):  # place selected camp on map, require camp size input
            if icon.selected:
                map_pos = (
                    (int(self.cursor.pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width),
                    int((self.cursor.pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                if icon.who.name == "+":
                    self.input_popup = ("text_input", "custom_camp_size/" + str(map_pos) + "/" +
                                        str(icon.who.team))
                    self.input_ui.change_instruction("Camp Size Value:")
                    self.add_ui_updater(self.input_ui_popup)
                else:
                    self.camp_pos[icon.who.team][index][0] = map_pos
                self.map_preview.change_mode(1, camp_pos_list=self.camp_pos)
                break


    elif self.unit_selector.mouse_over:
        if self.cursor.scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        elif self.cursor.scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        elif self.unit_selector.scroll.event:
            new_row = self.unit_selector.scroll.player_input(self.cursor.pos)
            if self.unit_selector.current_row != new_row:
                self.unit_selector.current_row = new_row
                self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        else:
            for index, icon in enumerate(self.unit_icon):
                if icon.mouse_over:
                    if icon.event_press:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                    elif self.cursor.is_mouse_right_just_up:  # right click remove icon
                        if icon.who.name != "+":
                            self.camp_pos[icon.who.team].pop(index)
                            icon.kill()
                            self.camp_icon.pop(index)
                            self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)
                    self.map_preview.change_mode(1, camp_pos_list=self.camp_pos)
                    break


def change_team_coa(self):
    for this_team in self.team_coa:  # User select any team by clicking on coat of arm
        if this_team.event_press:
            self.team_selected = this_team.team
            this_team.change_select(True)

            for icon in self.camp_icon:
                icon.kill()
            self.camp_icon = []
            if this_team.team in self.camp_pos:
                for camp in self.camp_pos[this_team.team]:
                    self.camp_icon.append(TempUnitIcon(this_team.team, camp[1], 0))
                self.camp_icon.append(TempUnitIcon(this_team.team, "+", 0))
            self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

            for this_team2 in self.team_coa:
                if self.team_selected != this_team2.team and this_team2.selected:
                    this_team2.change_select(False)
            break
