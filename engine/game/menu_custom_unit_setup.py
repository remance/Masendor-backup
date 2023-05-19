import pygame

from engine.uimenu import uimenu
from engine.uibattle import uibattle
from engine import utility

setup_list = utility.setup_list
list_scroll = utility.list_scroll
load_image = utility.load_image


def menu_custom_unit_setup(self, mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up, mouse_scroll_down,
                           esc_press):
    self.main_ui_updater.remove(self.single_text_popup)
    if mouse_left_up or mouse_left_down or mouse_right_up:
        if mouse_left_up or mouse_right_up:
            for this_team in self.team_coa:  # User select any team by clicking on coat of arm
                if this_team.rect.collidepoint(self.mouse_pos):
                    self.team_selected = this_team.team
                    this_team.change_select(True)

                    for this_team2 in self.team_coa:
                        if self.team_selected != this_team2.team and this_team2.selected:
                            this_team2.change_select(False)

                    unit_list = create_unit_list(self, this_team)
                    self.current_map_row = 0
                    setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, unit_list,
                               self.map_namegroup, self.unit_list_box, self.main_ui_updater)
                    unit_change_team_unit(self, new_faction=True)
                    break

            if mouse_right_up and self.map_preview.rect.collidepoint(self.mouse_pos):
                for icon in self.unit_icon:
                    if icon.selected:
                        map_pos = (
                            int(self.mouse_pos[0] - self.map_preview.rect.x) * self.map_preview.map_scale_width,
                            int((self.mouse_pos[1] - self.map_preview.rect.y) * self.map_preview.map_scale_height))
                        if icon.who.name != "+":  # choose pos of selected unit
                            self.play_map_data["unit"]["pos"][icon.who.team][icon.who.index] = map_pos
                            self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                         camp_pos_list=self.camp_pos,
                                                         selected=self.play_map_data["unit"]["pos"][icon.who.team][
                                                             icon.who.index])
                            unit_change_team_unit(self, old_selected=icon.who.index)
                        break

    if self.unit_list_box.rect.collidepoint(self.mouse_pos):  # mouse on unit preset list
        if self.unit_list_box.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_up:
                self.current_map_row = self.unit_list_box.scroll.player_input(
                    self.mouse_pos)  # update the scroll and get new current subsection
                for coa in self.team_coa:
                    if coa.selected:  # get unit for selected team
                        unit_list = create_unit_list(self, coa)
                        setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, unit_list,
                                   self.map_namegroup, self.unit_list_box, self.main_ui_updater)
        else:
            for index, name in enumerate(self.map_namegroup):  # player select unit preset in name list
                if name.rect.collidepoint(self.mouse_pos):
                    for coa in self.team_coa:
                        if coa.selected:  # get unit for selected team
                            unit_data = create_unit_list(self, coa, unit_selected=name.name)
                            popup_text = [self.leader_data.leader_list[unit_data["Leader ID"]]["Name"]]
                            for troop in unit_data["Troop"]:
                                popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                               str(unit_data["Troop"][troop][0]) + " + " +
                                               str(unit_data["Troop"][troop][1])]
                            self.single_text_popup.pop(self.mouse_pos, popup_text)
                            self.main_ui_updater.add(self.single_text_popup)
                            break
                    if mouse_left_up:
                        has_unit_selected = False
                        for this_unit in self.unit_icon:
                            if this_unit.selected:
                                if this_unit.who.name == "+":  # add new unit
                                    self.play_map_data["unit"][coa.team].append(unit_data.copy())
                                    old_selected = None
                                else:  # change existed
                                    self.play_map_data["unit"][coa.team][this_unit.who.index] = unit_data.copy()
                                    old_selected = this_unit.who.index
                                has_unit_selected = True
                                unit_change_team_unit(self, old_selected=old_selected)
                                self.map_preview.change_mode(1,
                                                             team_pos_list=self.play_map_data["unit"]["pos"],
                                                             camp_pos_list=self.camp_pos, selected=old_selected)
                                break

                        if not has_unit_selected:  # no unit selected, consider as adding new unit
                            for coa in self.team_coa:
                                if coa.selected:  # add unit for selected team
                                    unit_data = create_unit_list(self, coa, unit_selected=name.name)
                                    self.play_map_data["unit"][coa.team].append(unit_data.copy())
                                    unit_change_team_unit(self)
                                    self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                                 camp_pos_list=self.camp_pos)

    if self.unit_list_box.rect.collidepoint(self.mouse_pos):
        for coa in self.team_coa:
            if coa.selected:  # get unit data of selected team
                unit_list = create_unit_list(self, coa)
                self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                   self.unit_list_box.scroll, self.unit_list_box,
                                                   self.current_map_row, unit_list, self.map_namegroup,
                                                   self.main_ui_updater)
                break

    elif self.unit_selector.rect.collidepoint(self.mouse_pos):
        if mouse_scroll_up:
            if self.unit_selector.current_row > 0:
                self.unit_selector.current_row -= 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif mouse_scroll_down:
            if self.unit_selector.current_row < self.unit_selector.row_size:
                self.unit_selector.current_row += 1
                self.unit_selector.scroll.change_image(new_row=self.unit_selector.current_row,
                                                       row_size=self.unit_selector.row_size)
                self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        elif self.unit_selector.scroll.rect.collidepoint(self.mouse_pos):
            if mouse_left_down or mouse_left_up:
                new_row = self.unit_selector.scroll.player_input(self.mouse_pos)
                if self.unit_selector.current_row != new_row:
                    self.unit_selector.current_row = new_row
                    self.unit_selector.scroll.change_image(new_row=new_row, row_size=self.unit_selector.row_size)
                    self.unit_selector.setup_unit_icon(self.unit_icon, self.preview_unit)

        else:
            for icon in self.unit_icon:  # select unit
                if icon.rect.collidepoint(self.mouse_pos):
                    if icon.who.name != "+":  # add popup showing leader and troop in unit
                        popup_text = [self.leader_data.leader_list[
                                          self.play_map_data["unit"][icon.who.team][icon.who.index]["Leader ID"]][
                                          "Name"]]
                        for troop in self.play_map_data["unit"][icon.who.team][icon.who.index]["Troop"]:
                            popup_text += [self.troop_data.troop_list[troop]["Name"] + ": " +
                                           str(self.play_map_data["unit"][icon.who.team][icon.who.index]["Troop"][
                                                   troop][0]) + " + " +
                                           str(self.play_map_data["unit"][icon.who.team][icon.who.index]["Troop"][
                                                   troop][1])]
                        self.single_text_popup.pop(self.mouse_pos, popup_text)
                        self.main_ui_updater.add(self.single_text_popup)
                    if mouse_left_up:
                        for other_icon in self.unit_icon:
                            if other_icon.selected:  # unselected all others first
                                other_icon.selection()
                        icon.selection()
                        if icon.who.team in self.play_map_data["unit"]["pos"] and \
                                icon.who.index in self.play_map_data["unit"]["pos"][icon.who.team]:
                            # highlight selected unit in preview map
                            self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                         camp_pos_list=self.camp_pos,
                                                         selected=self.play_map_data["unit"]["pos"][icon.who.team][
                                                             icon.who.index])
                    elif mouse_right_up:  # remove unit
                        if icon.who.name != "+":
                            self.play_map_data["unit"][icon.who.team].pop(icon.who.index)
                            if icon.who.index in self.play_map_data["unit"]["pos"][icon.who.team]:
                                self.play_map_data["unit"]["pos"][icon.who.team].pop(icon.who.index)

                            for icon2 in self.unit_icon:
                                if icon2.who.index and icon2.who.index > icon.who.index:
                                    if icon2.who.index in self.play_map_data["unit"]["pos"][icon.who.team]:
                                        self.play_map_data["unit"]["pos"][icon.who.team][icon2.who.index - 1] = \
                                            self.play_map_data["unit"]["pos"][icon.who.team].pop(icon2.who.index)
                                    icon2.who.index -= 1

                            self.map_preview.change_mode(1, team_pos_list=self.play_map_data["unit"]["pos"],
                                                         camp_pos_list=self.camp_pos)
                            if not icon.selected:  # find new selected
                                for icon2 in self.unit_icon:
                                    if icon2.selected:
                                        self.map_preview.change_mode(1,
                                                                     team_pos_list=self.play_map_data["unit"]["pos"],
                                                                     camp_pos_list=self.camp_pos,
                                                                     selected=self.play_map_data["unit"]["pos"][
                                                                         icon2.who.team][icon2.who.index])
                                        break
                            icon.kill()
                    break

    if self.map_back_button.event or esc_press:
        self.main_ui_updater.remove(self.single_text_popup)
        self.menu_state = "custom_team_select"
        self.map_back_button.event = False
        self.current_map_row = 0
        self.main_ui_updater.remove(*self.menu_button, self.unit_list_box, self.unit_list_box.scroll,
                                    self.unit_icon)
        self.menu_button.remove(*self.menu_button)

        # Reset selected team
        for team in self.team_coa:
            team.change_select(False)
        self.team_selected = 1

        self.play_map_data["unit"] = {"pos": {}}

        self.map_preview.change_mode(1, camp_pos_list=self.camp_pos)  # revert map preview back to without unit dot

        for stuff in self.map_namegroup:  # remove map name item
            stuff.kill()
            del stuff

        setup_list(self.screen_scale, uimenu.NameList, self.current_source_row,
                   ["None"] + self.faction_data.faction_name_list,
                   self.source_namegroup, self.source_list_box, self.main_ui_updater)

        self.menu_button.add(*self.map_select_button)

        self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)

        self.main_ui_updater.add(*self.menu_button, self.custom_map_option_box, self.observe_mode_tick_box,
                                 self.night_battle_tick_box, self.source_list_box, self.source_list_box.scroll,
                                 self.unit_selector, self.unit_selector.scroll, self.team_coa,
                                 self.weather_custom_select, self.wind_custom_select)

    elif self.select_button.event:  # go to unit leader setup screen
        self.select_button.event = False
        can_continue = True
        if len(self.play_map_data) > 1:
            for team in self.play_map_data["unit"]:
                for coa in self.team_coa:
                    if coa.team == team and 0 not in coa.coa_images and (not self.play_map_data["unit"][team] or
                                                                         len(self.play_map_data["unit"][team]) != len(
                                self.play_map_data["unit"]["pos"][team])):
                        can_continue = False

        if can_continue is False:
            self.input_popup = ("confirm_input", "warning")
            self.input_ui.change_instruction("Teams need all units placed")
            self.main_ui_updater.add(self.inform_ui_popup)
        else:
            self.menu_state = "custom_leader_setup"
            self.unit_select_row = 0
            self.current_map_row = 0

            self.main_ui_updater.remove(self.unit_list_box, self.unit_list_box.scroll, self.unit_icon)

            for stuff in self.map_namegroup:  # remove name item
                stuff.kill()
                del stuff

            self.main_ui_updater.add(self.org_chart)
            for team in self.play_map_data["unit"]:
                if team != "pos":
                    for subunit in self.play_map_data["unit"][team]:
                        subunit["Temp Leader"] = ""

            leader_change_team_unit(self)


def leader_change_team_unit(self):
    for this_team in self.team_coa:
        if this_team.selected:
            for icon in self.preview_unit:
                icon.kill()
            self.preview_unit.empty()

            if this_team.team in self.play_map_data["unit"]:
                for unit_index, unit in enumerate(self.play_map_data["unit"][this_team.team]):
                    if unit["Leader ID"] in self.leader_data.images:
                        image = self.leader_data.images[unit["Leader ID"]]
                    else:
                        image = self.leader_data.leader_list[unit["Leader ID"]]["Name"].split(" ")[0]
                    self.preview_unit.add(uibattle.TempUnitIcon(self.screen_scale, this_team.team, image, unit_index))
            self.unit_selector.setup_unit_icon(self.unit_icon, [this_unit for this_unit in self.preview_unit if
                                                                this_unit.index is None or "Temp Leader" not in
                                                                self.play_map_data["unit"][this_team.team][
                                                                    this_unit.index] or
                                                                self.play_map_data["unit"][this_team.team][
                                                                    this_unit.index]["Temp Leader"] == ""])

            break


def unit_change_team_unit(self, new_faction=False, old_selected=None, add_plus=True):
    """Player select another team"""
    for this_team in self.team_coa:
        if this_team.selected:
            for icon in self.preview_unit:
                icon.kill()
            self.preview_unit.empty()

            unit_list = []
            if "Team Faction " + str(this_team.team) in self.play_map_data["info"]:
                for unit_index, unit in enumerate(self.play_map_data["unit"][this_team.team]):
                    if unit["Leader ID"] in self.leader_data.images:
                        image = self.leader_data.images[unit["Leader ID"]]
                    else:
                        image = self.leader_data.leader_list[unit["Leader ID"]]["Name"].split(" ")[0]

                    if unit_index in self.play_map_data["unit"]["pos"][this_team.team] and add_plus:
                        # unit placed on map, put in black-green colour in portrait
                        if type(image) is str:
                            done_subunit = uibattle.TempUnitIcon(self.screen_scale, this_team.team, image, unit_index)
                            self.preview_unit.add(done_subunit)
                            new_image = pygame.Surface(self.leader_data.images["0"].get_size(), pygame.SRCALPHA)
                            pygame.draw.circle(new_image, (20, 150, 60),
                                               (new_image.get_width() / 2, new_image.get_height() / 2),
                                               new_image.get_width() / 2, width=int(10 * self.screen_scale[1]))
                            done_subunit.portrait.blit(new_image, new_image.get_rect(topleft=(0, 0)))
                        else:
                            new_image = pygame.Surface(image.get_size())
                            new_image.blit(image, image.get_rect(topleft=(0, 0)))
                            pygame.draw.circle(new_image, (20, 150, 60),
                                               (new_image.get_width() / 2, new_image.get_height() / 2),
                                               new_image.get_width() / 2, width=int(10 * self.screen_scale[1]))
                            self.preview_unit.add(
                                uibattle.TempUnitIcon(self.screen_scale, this_team.team, new_image, unit_index))
                    else:
                        self.preview_unit.add(
                            uibattle.TempUnitIcon(self.screen_scale, this_team.team, image, unit_index))

                if add_plus:
                    self.preview_unit.add(uibattle.TempUnitIcon(self.screen_scale, this_team.team, "+", None))

                unit_list = create_unit_list(self, this_team)

            if new_faction:
                self.current_map_row = 0
                setup_list(self.screen_scale, uimenu.NameList, self.current_map_row, unit_list,
                           self.map_namegroup, self.unit_list_box, self.main_ui_updater)

            self.unit_selector.setup_unit_icon(self.unit_icon,
                                               [this_unit for this_unit in self.preview_unit if
                                                this_unit.index is None or "Temp Leader" not in
                                                self.play_map_data["unit"][this_team.team][this_unit.index] or
                                                self.play_map_data["unit"][this_team.team][this_unit.index][
                                                    "Temp Leader"] == ""])

            if old_selected is not None:
                for icon in self.unit_icon:
                    if icon.who.index == old_selected:
                        icon.selection()

            break


def create_unit_list(self, coa, unit_selected=None):
    unit_list = []
    unit_data = None
    for faction in coa.coa_images:
        if faction == 0:  # all faction
            for this_faction in self.faction_data.faction_unit_list:
                unit_list += list(self.faction_data.faction_unit_list[this_faction].keys())
                if unit_selected and unit_selected in self.faction_data.faction_unit_list[this_faction]:
                    unit_data = self.faction_data.faction_unit_list[this_faction][unit_selected]
        else:
            unit_list += list(self.faction_data.faction_unit_list[faction].keys())
            if unit_selected and unit_selected in self.faction_data.faction_unit_list[faction]:
                unit_data = self.faction_data.faction_unit_list[faction][unit_selected]

        unit_list = sorted((set(unit_list)), key=unit_list.index)
    if not unit_selected:
        return unit_list
    else:
        return unit_data
