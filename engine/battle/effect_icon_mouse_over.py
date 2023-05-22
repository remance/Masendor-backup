from engine.lorebook import lorebook

status_section = lorebook.Lorebook.status_section
skill_section = lorebook.Lorebook.skill_section


def effect_icon_mouse_over(self, icon_list, mouse_right):
    effect_mouse_over = False
    for icon in icon_list:
        if icon in self.battle_ui_updater and icon.rect.collidepoint(self.self.player1_battle_cursor.pos):
            self.single_text_popup.popup(self.player1_battle_cursor.rect, icon.name)
            self.add_ui_updater(self.single_text_popup)
            effect_mouse_over = True
            break
    return effect_mouse_over
