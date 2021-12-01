import csv
import math
import os
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import commonscript

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read

"""This file contains fuctions of various purposes"""

# Default game mechanic value

battlesidecal = (1, 0.5, 0.1, 0.5)  # battlesidecal is for melee combat side modifier
infinity = float("inf")

letterboard = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
numberboard = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
boardpos = []
for dd in numberboard:
    for ll in letterboard:
        boardpos.append(ll + dd)


# Data Loading gamescript

def load_game_data(game):
    """Load various game data"""

    SCREENRECT = game.SCREENRECT
    from gamescript import battleui, uniteditor
    from gamescript.tactical import unit, subunit, rangeattack

    unit.Unit.status_list = game.troop_data.status_list
    rangeattack.RangeArrow.gamemapheight = game.battlemap_height

    imgs = load_images(game.main_dir, ["ui", "unit_ui"])
    subunit.Subunit.images = imgs
    subunit.Subunit.gamemap = game.battlemap_base  # add gamebattle map to all parentunit class
    subunit.Subunit.gamemapfeature = game.battlemap_feature  # add gamebattle map to all parentunit class
    subunit.Subunit.gamemapheight = game.battlemap_height
    subunit.Subunit.weapon_list = game.allweapon
    subunit.Subunit.armour_list = game.allarmour
    subunit.Subunit.stat_list = game.troop_data
    subunit.Subunit.eventlog = game.eventlog  # Assign eventlog to subunit class to broadcast event to the log

    skill_header = game.troop_data.skill_list_header
    status_header = game.troop_data.status_list_header

    # v Get index of effect column for skill and status
    subunit.Subunit.skill_trooptype = skill_header['Troop Type']
    subunit.Subunit.skill_type = skill_header['Type']
    subunit.Subunit.skill_aoe = skill_header['Area of Effect']
    subunit.Subunit.skill_duration = skill_header['Duration']
    subunit.Subunit.skill_cd = skill_header['Cooldown']
    subunit.Subunit.skill_restriction = skill_header['Restriction']
    subunit.Subunit.skill_condition = skill_header['Condition']
    subunit.Subunit.skill_discipline_req = skill_header['Discipline Requirement']
    subunit.Subunit.skill_stamina_cost = skill_header['Stamina Cost']
    subunit.Subunit.skill_mana_cost = skill_header['Mana Cost']
    subunit.Subunit.skill_melee_attack = skill_header['Melee Attack Effect']
    subunit.Subunit.skill_melee_defence = skill_header['Melee Defence Effect']
    subunit.Subunit.skill_range_defence = skill_header['Ranged Defence Effect']
    subunit.Subunit.skill_speed = skill_header['Speed Effect']
    subunit.Subunit.skill_accuracy = skill_header['Accuracy Effect']
    subunit.Subunit.skill_range = skill_header['Range Effect']
    subunit.Subunit.skill_reload = skill_header['Reload Effect']
    subunit.Subunit.skill_charge = skill_header['Charge Effect']
    subunit.Subunit.skill_charge_defence = skill_header['Charge Defence Bonus']
    subunit.Subunit.skill_hp_regen = skill_header['HP Regeneration Bonus']
    subunit.Subunit.skill_stamina_regen = skill_header['Stamina Regeneration Bonus']
    subunit.Subunit.skill_morale = skill_header['Morale Bonus']
    subunit.Subunit.skill_discipline = skill_header['Discipline Bonus']
    subunit.Subunit.skill_critical = skill_header['Critical Effect']
    subunit.Subunit.skill_damage = skill_header['Damage Effect']
    subunit.Subunit.skill_sight = skill_header['Sight Bonus']
    subunit.Subunit.skill_hide = skill_header['Hidden Bonus']
    subunit.Subunit.skill_status = skill_header['Status']
    subunit.Subunit.skill_staminadmg = skill_header['Stamina Damage']
    subunit.Subunit.skill_moraledmg = skill_header['Morale Damage']
    subunit.Subunit.skill_enemy_status = skill_header['Enemy Status']
    subunit.Subunit.skill_element = skill_header['Element']

    subunit.Subunit.status_effect = status_header['Special Effect']
    subunit.Subunit.status_conflict = status_header['Status Conflict']
    subunit.Subunit.status_duration = status_header['Duration']
    subunit.Subunit.status_melee_attack = status_header['Melee Attack Effect']
    subunit.Subunit.status_melee_defence = status_header['Melee Defence Effect']
    subunit.Subunit.status_range_defence = status_header['Ranged Defence Effect']
    subunit.Subunit.status_armour = status_header['Armour Effect']
    subunit.Subunit.status_speed = status_header['Speed Effect']
    subunit.Subunit.status_accuracy = status_header['Accuracy Effect']
    subunit.Subunit.status_reload = status_header['Reload Effect']
    subunit.Subunit.status_charge = status_header['Charge Effect']
    subunit.Subunit.status_charge_defence = status_header['Charge Defence Bonus']
    subunit.Subunit.status_hp_regen = status_header['HP Regeneration Bonus']
    subunit.Subunit.status_stamina_regen = status_header['Stamina Regeneration Bonus']
    subunit.Subunit.status_morale = status_header['Morale Bonus']
    subunit.Subunit.status_discipline = status_header['Discipline Bonus']
    subunit.Subunit.status_sight = status_header['Sight Bonus']
    subunit.Subunit.status_hide = status_header['Hidden Bonus']
    subunit.Subunit.status_temperature = status_header['Temperature Change']
    # ^ End get index

    uniteditor.Unitbuildslot.images = imgs
    uniteditor.Unitbuildslot.weapon_list = game.allweapon
    uniteditor.Unitbuildslot.armour_list = game.allarmour
    uniteditor.Unitbuildslot.stat_list = game.troop_data
    uniteditor.Unitbuildslot.skill_trooptype = skill_header['Troop Type']

    game.sprite_width, game.sprite_height = imgs[0].get_width(), imgs[0].get_height()  # size of subnit image at closest zoom
    # ^ End subunit class

    # v Game Effect related class
    imgs = load_images(game.main_dir, ["effect"])
    # imgs = []
    # for img in imgsold:
    # x, y = img.get_width(), img.get_height()
    # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
    # imgs.append(img)
    rangeattack.RangeArrow.images = [imgs[0]]
    # ^ End game effect

    topimage = load_images(game.main_dir, ["ui", "battle_ui"])
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "commandbar_icon"])
    # Army select list ui
    game.unitselector = battleui.ArmySelect((0, 0), topimage[30])
    game.selectscroll = battleui.UIScroller(game.unitselector.rect.topright, topimage[30].get_height(),
                                            game.unitselector.max_row_show)  # scroller for unit select ui

    game.command_ui = battleui.GameUI(x=topimage[1].get_size()[0] / 2, y=(topimage[1].get_size()[1] / 2) + game.unitselector.image.get_height(),
                                      image=topimage[1], icon=iconimage,
                                      uitype="commandbar")  # Left top command ui with leader and parentunit behavious button
    game.gameui.add(game.command_ui)

    # Load all image of ui and icon from folder
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"])

    game.col_split_button = battleui.UIButton(game.command_ui.x - 115, game.command_ui.y + 26, topimage[8], 0)  # parentunit split by column button
    game.row_split_button = battleui.UIButton(game.command_ui.x - 115, game.command_ui.y + 56, topimage[9], 1)  # parentunit split by row button
    game.buttonui.add(game.col_split_button)
    game.buttonui.add(game.row_split_button)

    game.decimation_button = battleui.UIButton(game.command_ui.x + 100, game.command_ui.y + 56, topimage[14], 1)

    # Time bar ui
    game.timeui = battleui.TimeUI(game.unitselector.rect.topright, topimage[31])
    game.timenumber = battleui.Timer(game.timeui.rect.topleft)  # time number on time ui
    game.speednumber = battleui.SpeedNumber((game.timeui.rect.center[0] + 40, game.timeui.rect.center[1]),
                                            1)  # game speed number on the time ui

    image = pygame.Surface((topimage[31].get_width(), 15))
    game.scaleui = battleui.ScaleUI(game.timeui.rect.bottomleft, image)

    game.time_button = [battleui.UIButton(game.timeui.rect.center[0] - 30, game.timeui.rect.center[1], topimage[32], 0),  # time pause button
                        battleui.UIButton(game.timeui.rect.center[0], game.timeui.rect.center[1], topimage[33], 1),  # time decrease button
                        battleui.UIButton(game.timeui.rect.midright[0] - 60, game.timeui.rect.center[1], topimage[34], 2)]  # time increase button
    game.battleui.add(*game.time_button)

    # Right top bar ui that show rough information of selected battalions
    game.unitstat_ui = battleui.GameUI(x=SCREENRECT.width - topimage[0].get_size()[0] / 2, y=topimage[0].get_size()[1] / 2, image=topimage[0],
                                       icon=iconimage, uitype="topbar")
    game.gameui.add(game.unitstat_ui)
    game.unitstat_ui.unit_state_text = game.statetext

    game.inspectuipos = [game.unitstat_ui.rect.bottomleft[0] - game.sprite_width / 1.25,
                         game.unitstat_ui.rect.bottomleft[1] - game.sprite_height / 3]

    # Subunit information card ui
    game.inspect_ui = battleui.GameUI(x=SCREENRECT.width - topimage[5].get_size()[0] / 2, y=topimage[0].get_size()[1] * 4,
                                      image=topimage[5], icon="", uitype="unitbox")  # inspect ui that show subnit in selected parentunit
    game.gameui.add(game.inspect_ui)
    # v Subunit shown in inspect ui
    width, height = game.inspectuipos[0], game.inspectuipos[1]
    subunitnum = 0  # Number of subnit based on the position in row and column
    imgsize = (game.sprite_width, game.sprite_height)
    game.inspectsubunit = []
    for this_subunit in list(range(0, 64)):
        width += imgsize[0]
        game.inspectsubunit.append(battleui.InspectSubunit((width, height)))
        subunitnum += 1
        if subunitnum == 8:  # Reach the last subnit in the row, go to the next one
            width = game.inspectuipos[0]
            height += imgsize[1]
            subunitnum = 0
    # ^ End subunit shown

    # Behaviour button that once click switch to other mode for subunit behaviour
    game.switch_button = [battleui.SwitchButton(game.command_ui.x - 40, game.command_ui.y + 96, topimage[10:14]),  # skill condition button
                          battleui.SwitchButton(game.command_ui.x - 80, game.command_ui.y + 96, topimage[15:17]),  # fire at will button
                          battleui.SwitchButton(game.command_ui.x, game.command_ui.y + 96, topimage[17:20]),  # behaviour button
                          battleui.SwitchButton(game.command_ui.x + 40, game.command_ui.y + 96, topimage[20:22]),  # shoot range button
                          battleui.SwitchButton(game.command_ui.x - 125, game.command_ui.y + 96, topimage[35:38]),  # arcshot button
                          battleui.SwitchButton(game.command_ui.x + 80, game.command_ui.y + 96, topimage[38:40]),  # toggle run button
                          battleui.SwitchButton(game.command_ui.x + 120, game.command_ui.y + 96, topimage[40:43])]  # toggle melee mode

    game.inspect_button = battleui.UIButton(game.unitstat_ui.x - 206, game.unitstat_ui.y - 1, topimage[6], 1)  # unit inspect open/close button
    game.buttonui.add(game.inspect_button)

    game.battleui.add(game.logscroll, game.selectscroll)

    battleui.SelectedSquad.image = topimage[-1]  # subunit border image always the last one
    game.inspect_selected_border = battleui.SelectedSquad((15000, 15000))  # yellow border on selected subnit in inspect ui
    game.mainui.remove(game.inspect_selected_border)  # remove subnit border sprite from gamestart menu drawer

    # ^ End game ui


# Battle Start related gamescript

def add_unit(subunitlist, position, gameid, colour, leaderlist, leaderstat, control, coa, command, startangle, starthp, startstamina, team):
    """Create batalion object into the battle and leader of the parentunit"""
    from gamescript.tactical import unit, leader
    oldsubunitlist = subunitlist[~np.all(subunitlist == 0, axis=1)]  # remove whole empty column in subunit list
    subunitlist = oldsubunitlist[:, ~np.all(oldsubunitlist == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(position, gameid, subunitlist, colour, control, coa, command, abs(360 - startangle), starthp, startstamina, team)

    # add leader
    unit.leader = [leader.Leader(leaderlist[0], leaderlist[4], 0, unit, leaderstat),
                   leader.Leader(leaderlist[1], leaderlist[5], 1, unit, leaderstat),
                   leader.Leader(leaderlist[2], leaderlist[6], 2, unit, leaderstat),
                   leader.Leader(leaderlist[3], leaderlist[7], 3, unit, leaderstat)]
    return unit


def generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid):
    """generate unit data into game object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript.tactical import unit, subunit
    this_unit = add_unit(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                         colour, row[10] + row[11], gamebattle.leader_stat, control,
                         coa, command, row[13], row[14], row[15], row[16])
    whicharmy.add(this_unit)
    armysubunitindex = 0  # armysubunitindex is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    maxcolumn = len(this_unit.armysubunit[0])
    for subunitnum in np.nditer(this_unit.armysubunit, op_flags=["readwrite"], order="C"):
        if subunitnum != 0:
            addsubunit = subunit.Subunit(subunitnum, subunitgameid, this_unit, this_unit.subunit_position_list[armysubunitindex],
                                         this_unit.starthp, this_unit.startstamina, gamebattle.unitscale)
            gamebattle.subunit.add(addsubunit)
            addsubunit.board_pos = boardpos[armysubunitindex]
            subunitnum[...] = subunitgameid
            this_unit.subunit_sprite_array[row][column] = addsubunit
            this_unit.subunit_sprite.append(addsubunit)
            subunitgameid += 1
        else:
            this_unit.subunit_sprite_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == maxcolumn:
            column = 0
            row += 1
        armysubunitindex += 1
    gamebattle.troop_number_sprite.add(unit.TroopNumber(gamebattle.screen_scale, this_unit))  # create troop number text sprite

    return subunitgameid


def unitsetup(gamebattle):
    """read parentunit from unit_pos(source) file and create object with addunit function"""
    main_dir = gamebattle.main_dir
    # defaultunit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

    teamcolour = gamebattle.teamcolour
    teamarmy = (gamebattle.team0unit, gamebattle.team1unit, gamebattle.team2unit)

    with open(os.path.join(main_dir, "data", "ruleset", gamebattle.ruleset_folder, "map",
                           gamebattle.mapselected, gamebattle.source, gamebattle.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        subunitgameid = 1
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]

            control = False
            if gamebattle.playerteam == row[16] or gamebattle.enactment:  # player can control only his team or both in enactment mode
                control = True

            colour = teamcolour[row[16]]
            whicharmy = teamarmy[row[16]]

            command = False  # Not commander parentunit by default
            if len(whicharmy) == 0:  # First parentunit is commander
                command = True
            coa = pygame.transform.scale(gamebattle.coa[row[12]], (60, 60))  # get coa image and scale smaller to fit ui
            subunitgameid = generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid)
            # ^ End subunit setup

    unitfile.close()


def convertedit_unit(gamebattle, whicharmy, row, colour, coa, subunitgameid):
    for n, i in enumerate(row):
        if type(i) == str and i.isdigit():
            row[n] = int(i)
        if n in range(1, 12):
            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
    subunitgameid = generate_unit(gamebattle, whicharmy, row, True, True, colour, coa, subunitgameid)


# Battle related gamescript

def setrotate(self, set_target=None):
    """set base_target and new angle for sprite rotation"""
    if set_target is None:  # For auto chase rotate
        myradians = math.atan2(self.base_target[1] - self.base_pos[1], self.base_target[0] - self.base_pos[0])
    else:  # Command move or rotate
        myradians = math.atan2(set_target[1] - self.base_pos[1], set_target[0] - self.base_pos[0])
    newangle = math.degrees(myradians)

    # """upper left -"""
    if -180 <= newangle <= -90:
        newangle = -newangle - 90

    # """upper right +"""
    elif -90 < newangle < 0:
        newangle = (-newangle) - 90

    # """lower right -"""
    elif 0 <= newangle <= 90:
        newangle = -(newangle + 90)

    # """lower left +"""
    elif 90 < newangle <= 180:
        newangle = 270 - newangle

    return round(newangle)


def losscal(attacker, defender, hit, defence, dmgtype, defside=None):
    """Calculate dmg, type 0 is melee attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range attack)"""
    who = attacker
    target = defender

    heightadventage = who.height - target.height
    if dmgtype != 0:
        heightadventage = int(heightadventage / 2)  # Range attack use less height advantage
    hit += heightadventage

    if defence < 0 or who.ignore_def:  # Ignore def trait
        defence = 0

    hitchance = hit - defence
    if hitchance < 0:
        hitchance = 0
    elif hitchance > 80:  # Critical hit
        hitchance *= who.crit_effect  # modify with crit effect further
        if hitchance > 200:
            hitchance = 200
    else:  # infinity number can cause nan value
        hitchance = 200

    combatscore = round(hitchance / 100, 1)
    if combatscore == 0 and random.randint(0, 10) > 9:  # Final chence to not miss
        combatscore = 0.1

    if combatscore > 0:
        leaderdmgbonus = 0
        if who.leader is not None:
            leaderdmgbonus = who.leader.combat  # Get extra dmg from leader combat stat

        if dmgtype == 0:  # Melee melee_dmg
            dmg = random.uniform(who.melee_dmg[0], who.melee_dmg[1])
            if who.chargeskill in who.skill_effect:  # Include charge in melee_dmg if attacking
                if who.ignore_chargedef is False:  # Ignore charge defence if have ignore trait
                    sidecal = battlesidecal[defside]
                    if target.fulldef or target.temp_fulldef:  # defence all side
                        sidecal = 1
                    dmg = dmg + ((who.charge - (target.chargedef * sidecal)) * 2)
                    if (target.chargedef * sidecal) >= who.charge / 2:
                        who.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        who.charge_momentum -= (target.chargedef * sidecal) / who.charge
                else:
                    dmg = dmg + (who.charge * 2)
                    who.charge_momentum -= 1 / who.charge

            if target.chargeskill in target.skill_effect:  # Also include chargedef in melee_dmg if enemy charging
                if target.ignore_chargedef is False:
                    chargedefcal = who.chargedef - target.charge
                    if chargedefcal < 0:
                        chargedefcal = 0
                    dmg = dmg + (chargedefcal * 2)  # if charge def is higher than enemy charge then deal back addtional melee_dmg
            elif who.chargeskill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(who.melee_dmg[0], who.melee_dmg[1]) for x in range(who.meleespeed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combatscore

        else:  # Range Damage
            penetrate = dmgtype.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmgtype.dmg * penetrate * combatscore

        leaderdmg = dmg
        unitdmg = (dmg * who.troop_number) + leaderdmgbonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
            unitdmg = unitdmg * 1.25

        moraledmg = dmg / 50

        # Damage cannot be negative (it would heal instead), same for morale and leader dmg
        if unitdmg < 0:
            unitdmg = 0
        if leaderdmg < 0:
            leaderdmg = 0
        if moraledmg < 0:
            moraledmg = 0
    else:  # complete miss
        unitdmg = 0
        leaderdmg = 0
        moraledmg = 0

    return unitdmg, moraledmg, leaderdmg


def applystatustoenemy(statuslist, inflictstatus, receiver, attackerside, receiverside):
    """apply aoe status effect to enemy subunits"""
    for status in inflictstatus.items():
        if status[1] == 1 and attackerside == 0:  # only front enemy
            receiver.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            receiver.status_effect[status[0]] = statuslist[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = receiver.nearby_subunit_list[0:2]
                if receiverside in (1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [receiver.nearby_subunit_list[2], receiver.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 3:  # whole parentunit aoe
            for this_subunit in receiver.parentunit.subunit_sprite:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()


def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    final_dmg = round(dmg * dmgeffect * timermod)
    final_moraledmg = round(moraledmg * dmgeffect * timermod)
    if final_dmg > receiver.unit_health:  # dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    health_check = 0.1
    if receiver.max_health != infinity:
        health_check = 1 - (receiver.unit_health / receiver.max_health)
    receiver.base_morale -= (final_moraledmg + attacker.bonus_morale_dmg) * receiver.mental * health_check
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_border is False:
        receiver.imageblock.blit(receiver.images[11], receiver.corner_image_rect)
        receiver.red_border = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_moraledmg / 5))  # recover some morale when deal morale dmg to enemy

    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on subunit leader, only 10% chance
        finalleaderdmg = round(leaderdmg - (leaderdmg * receiver.leader.combat / 101) * timermod)
        if finalleaderdmg > receiver.leader.health:
            finalleaderdmg = receiver.leader.health
        receiver.leader.health -= finalleaderdmg


def dmgcal(attacker, target, attackerside, targetside, statuslist, combattimer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attackerside and targetside is the side attacking and defending respectively"""
    wholuck = random.randint(-50, 50)  # attacker luck
    targetluck = random.randint(-50, 50)  # defender luck
    whopercent = battlesidecal[attackerside]  # attacker attack side modifier

    """34 battlemaster fulldef or 91 allrounddef status = no flanked penalty"""
    if attacker.fulldef or 91 in attacker.status_effect:
        whopercent = 1
    targetpercent = battlesidecal[targetside]  # defender defend side

    if target.fulldef or 91 in target.status_effect:
        targetpercent = 1

    dmgeffect = attacker.front_dmg_effect
    targetdmgeffect = target.front_dmg_effect

    if attackerside != 0 and whopercent != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        whopercent = battlesidecal[attackerside] + (attacker.discipline / 300)
        dmgeffect = attacker.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
        if whopercent > 1:
            whopercent = 1

    if targetside != 0 and targetpercent != 1:  # same for the base_target defender
        targetpercent = battlesidecal[targetside] + (target.discipline / 300)
        targetdmgeffect = target.side_dmg_effect
        if targetpercent > 1:
            targetpercent = 1

    whohit = float(attacker.attack * whopercent) + wholuck
    whodefence = float(attacker.meleedef * whopercent) + wholuck
    targethit = float(attacker.attack * targetpercent) + targetluck
    targetdefence = float(target.meleedef * targetpercent) + targetluck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and targetside == 2) or (target.oblivious and targetside == 2) or (
            target.flanker and attackerside in (1, 3)):  # Apply only for attacker
        targetdefence = 0

    whodmg, whomoraledmg, wholeaderdmg = losscal(attacker, target, whohit, targetdefence, 0, targetside)  # get dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, attacker, targethit, whodefence, 0, attackerside)  # get dmg by defender

    timermod = combattimer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(attacker, target, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)  # Inflict dmg to defender
    complexdmg(target, attacker, targetdmg, targetmoraledmg, targetleaderdmg, targetdmgeffect, timermod)  # Inflict dmg to attacker

    # v Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        listloop = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if targetside in (0, 2):
            listloop = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearbysubunit
        for this_subunit in listloop:
            if this_subunit != 0 and this_subunit.state != 100:
                targethit, targetdefence = float(attacker.attack * targetpercent) + targetluck, float(
                    this_subunit.meleedef * targetpercent) + targetluck
                whodmg, whomoraledmg = losscal(attacker, this_subunit, whohit, targetdefence, 0)
                complexdmg(attacker, this_subunit, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)
    # ^ End attack corner

    # v inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire parentunit
    if attacker.inflictstatus != {}:
        applystatustoenemy(statuslist, attacker.inflictstatus, target, attackerside, targetside)
    if target.inflictstatus != {}:
        applystatustoenemy(statuslist, target.inflictstatus, attacker, targetside, attackerside)
    # ^ End inflict status


def die(who, battle, moralehit=True):
    """remove subunit when it dies"""
    if who.team == 1:
        group = battle.team1unit
        enemygroup = battle.team2unit
        battle.team1poslist.pop(who.gameid)
    else:
        group = battle.team2unit
        enemygroup = battle.team1unit
        battle.team2poslist.pop(who.gameid)

    if moralehit:
        if who.commander:  # more morale penalty if the parentunit is a command parentunit
            for army in group:
                for this_subunit in army.subunit_sprite:
                    this_subunit.base_morale -= 30

        for thisarmy in enemygroup:  # get bonus authority to the another army
            thisarmy.authority += 5

        for thisarmy in group:  # morale dmg to every subunit in army when allied parentunit destroyed
            for this_subunit in thisarmy.subunit_sprite:
                this_subunit.base_morale -= 20

    battle.allunitlist.remove(who)
    battle.allunitindex.remove(who.gameid)
    group.remove(who)
    who.got_killed = True


def change_leader(self, event):
    """Leader change subunit or gone/die, event can be "die" or "broken" """
    checkstate = [100]
    if event == "broken":
        checkstate = [99, 100]
    if self.leader is not None and self.leader.state != 100:  # Find new subunit for leader if there is one in this subunit
        for this_subunit in self.nearby_subunit_list:
            if this_subunit != 0 and this_subunit.state not in checkstate and this_subunit.leader is None:
                this_subunit.leader = self.leader
                self.leader.subunit = this_subunit
                for index, subunit2 in enumerate(self.parentunit.subunit_sprite):  # loop to find new subunit pos based on new subunit_sprite list
                    if subunit2 == self.leader.subunit:
                        self.leader.subunitpos = index
                        if self.unit_leader:  # set leader subunit to new one
                            self.parentunit.leadersubunit = subunit2
                            subunit2.unit_leader = True
                            self.unit_leader = False
                        break

                self.leader = None
                break

        if self.leader is not None:  # if can't find near subunit to move leader then find from first subunit to last place in parentunit
            for index, this_subunit in enumerate(self.parentunit.subunit_sprite):
                if this_subunit.state not in checkstate and this_subunit.leader is None:
                    this_subunit.leader = self.leader
                    self.leader.subunit = this_subunit
                    this_subunit.leader.subunitpos = index
                    self.leader = None
                    if self.unit_leader:  # set leader subunit to new one
                        self.parentunit.leadersubunit = this_subunit
                        this_subunit.unit_leader = True

                    break

            if self.leader is not None and event == "die":  # Still can't find new subunit so leader disappear with chance of different result
                self.leader.state = random.randint(97, 100)  # captured, retreated, wounded, dead
                self.leader.health = 0
                self.leader.gone()

        self.unit_leader = False


def add_new_unit(gamebattle, who, addunitlist=True):
    from gamescript.tactical import unit
    # generate subunit sprite array for inspect ui
    who.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    foundcount = 0  # for subunit_sprite index
    foundcount2 = 0  # for positioning
    for row in range(0, len(who.armysubunit)):
        for column in range(0, len(who.armysubunit[0])):
            if who.armysubunit[row][column] != 0:
                who.subunit_sprite_array[row][column] = who.subunit_sprite[foundcount]
                who.subunit_sprite[foundcount].unitposition = (who.subunit_position_list[foundcount2][0] / 10,
                                                               who.subunit_position_list[foundcount2][1] / 10)  # position in parentunit sprite
                foundcount += 1
            else:
                who.subunit_sprite_array[row][column] = None
            foundcount2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunit_sprite):  # reset leader subunitpos
        if this_subunit.leader is not None:
            this_subunit.leader.subunitpos = index

    who.zoom = 11 - gamebattle.camerascale
    who.new_angle = who.angle

    who.startset(gamebattle.subunit)
    who.set_target(who.front_pos)

    numberpos = (who.base_pos[0] - who.base_width_box,
                 (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotationxy(who.base_pos, numberpos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunit_sprite:
        this_subunit.gamestart(this_subunit.zoom)

    if addunitlist:
        gamebattle.allunitlist.append(who)
        gamebattle.allunitindex.append(who.gameid)

    numberspite = unit.TroopNumber(gamebattle.screen_scale, who)
    gamebattle.troop_number_sprite.add(numberspite)


def move_leader_subunit(this_leader, oldarmysubunit, newarmysubunit, alreadypick=()):
    """oldarmysubunit is armysubunit list that the subunit currently in and need to be move out to the new one (newarmysubunit),
    alreadypick is list of position need to be skipped"""
    replace = [np.where(oldarmysubunit == this_leader.subunit.gameid)[0][0],
               np.where(oldarmysubunit == this_leader.subunit.gameid)[1][0]]  # grab old array position of subunit
    newrow = int((len(newarmysubunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    newplace = int((len(newarmysubunit[newrow]) - 1) / 2)  # setup new column position
    placedone = False  # finish finding slot to place yet

    while placedone is False:
        if this_leader.subunit.parentunit.armysubunit.flat[newrow * newplace] != 0:
            for this_subunit in this_leader.subunit.parentunit.subunit_sprite:
                if this_subunit.gameid == this_leader.subunit.parentunit.armysubunit.flat[newrow * newplace]:
                    if this_subunit.leader is not None or (newrow, newplace) in alreadypick:
                        newplace += 1
                        if newplace > len(newarmysubunit[newrow]) - 1:  # find new column
                            newplace = 0
                        elif newplace == int(len(newarmysubunit[newrow]) / 2):  # find in new row when loop back to the first one
                            newrow += 1
                        placedone = False
                    else:  # found slot to replace
                        placedone = True
                        break
        else:  # fill in the subunit if the slot is empty
            placedone = True

    oldarmysubunit[replace[0]][replace[1]] = newarmysubunit[newrow][newplace]
    newarmysubunit[newrow][newplace] = this_leader.subunit.gameid
    newposition = (newplace, newrow)
    return oldarmysubunit, newarmysubunit, newposition


def splitunit(battle, who, how):
    """split parentunit either by row or column into two seperate parentunit"""  # TODO check split when moving
    from gamescript.tactical import unit, leader

    if how == 0:  # split by row
        newarmysubunit = np.array_split(who.armysubunit, 2)[1]
        who.armysubunit = np.array_split(who.armysubunit, 2)[0]
        newpos = pygame.Vector2(who.base_pos[0], who.base_pos[1] + (who.base_height_box / 2))
        newpos = who.rotationxy(who.base_pos, newpos, who.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] - (who.base_height_box / 2))
        who.base_pos = who.rotationxy(who.base_pos, base_pos, who.radians_angle)  # new position for original parentunit (front)
        who.base_height_box /= 2

    else:  # split by column
        newarmysubunit = np.array_split(who.armysubunit, 2, axis=1)[1]
        who.armysubunit = np.array_split(who.armysubunit, 2, axis=1)[0]
        newpos = pygame.Vector2(who.base_pos[0] + (who.base_width_box / 3.3), who.base_pos[1])  # 3.3 because 2 make new unit position overlap
        newpos = who.rotationxy(who.base_pos, newpos, who.radians_angle)  # new unit pos (right)
        base_pos = pygame.Vector2(who.base_pos[0] - (who.base_width_box / 2), who.base_pos[1])
        who.base_pos = who.rotationxy(who.base_pos, base_pos, who.radians_angle)  # new position for original parentunit (left)
        who.base_width_box /= 2
        frontpos = (who.base_pos[0], (who.base_pos[1] - who.base_height_box))  # find new front position of unit
        who.front_pos = who.rotationxy(who.base_pos, frontpos, who.radians_angle)
        who.set_target(who.front_pos)

    if who.leader[1].subunit.gameid not in newarmysubunit.flat:  # move the left sub-general leader subunit if it not in new one
        who.armysubunit, newarmysubunit, newposition = move_leader_subunit(who.leader[1], who.armysubunit, newarmysubunit)
        who.leader[1].subunitpos = newposition[0] * newposition[1]
    who.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a gamestart leader sub-unit

    alreadypick = []
    for this_leader in (who.leader[0], who.leader[2], who.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.gameid not in who.armysubunit:
            newarmysubunit, who.armysubunit, newposition = move_leader_subunit(this_leader, newarmysubunit, who.armysubunit, alreadypick)
            this_leader.subunitpos = newposition[0] * newposition[1]
            alreadypick.append(newposition)

    newleader = [who.leader[1], leader.Leader(1, 0, 1, who, battle.leader_stat), leader.Leader(1, 0, 2, who, battle.leader_stat),
                 leader.Leader(1, 0, 3, who, battle.leader_stat)]  # create new leader list for new parentunit

    who.subunit_position_list = []

    width, height = 0, 0
    subunitnum = 0  # Number of subunit based on the position in row and column
    for this_subunit in who.armysubunit.flat:
        width += who.imgsize[0]
        who.subunit_position_list.append((width, height))
        subunitnum += 1
        if subunitnum >= len(who.armysubunit[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += who.imgsize[1]
            subunitnum = 0

    # v Sort so the new leader subunit position match what set before
    subunitsprite = [this_subunit for this_subunit in who.subunit_sprite if
                     this_subunit.gameid in newarmysubunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for thisid in newarmysubunit.flat:
        for this_subunit in subunitsprite:
            if thisid == this_subunit.gameid:
                new_subunit_sprite.append(this_subunit)

    subunitsprite = [this_subunit for this_subunit in who.subunit_sprite if this_subunit.gameid in who.armysubunit.flat]
    who.subunit_sprite = []
    for thisid in who.armysubunit.flat:
        for this_subunit in subunitsprite:
            if thisid == this_subunit.gameid:
                who.subunit_sprite.append(this_subunit)
    # ^ End sort

    # v Reset position of sub-unit in inspectui for both old and new unit
    for sprite in (who.subunit_sprite, new_subunit_sprite):
        width, height = 0, 0
        subunitnum = 0
        for this_subunit in sprite:
            width += battle.sprite_width

            if subunitnum >= len(who.armysubunit[0]):
                width = 0
                width += battle.sprite_width
                height += battle.sprite_height
                subunitnum = 0

            this_subunit.inspposition = (width + battle.inspectuipos[0], height + battle.inspectuipos[1])
            this_subunit.rect = this_subunit.image.get_rect(topleft=this_subunit.inspposition)
            this_subunit.pos = pygame.Vector2(this_subunit.rect.centerx, this_subunit.rect.centery)
            subunitnum += 1
    # ^ End reset position

    # v Change the original parentunit stat and sprite
    originalleader = [who.leader[0], who.leader[2], who.leader[3], leader.Leader(1, 0, 3, who, battle.leader_stat)]
    for index, this_leader in enumerate(originalleader):  # Also change army position of all leader in that parentunit
        this_leader.armyposition = index  # Change army position to new one
        this_leader.imgposition = this_leader.baseimgposition[this_leader.armyposition]
        this_leader.rect = this_leader.image.get_rect(center=this_leader.imgposition)
    teamcommander = who.teamcommander
    who.teamcommander = teamcommander
    who.leader = originalleader

    add_new_unit(battle, who, False)
    # ^ End change original unit

    # v start making new parentunit
    if who.team == 1:
        whosearmy = battle.team1unit
    else:
        whosearmy = battle.team2unit
    newgameid = battle.allunitlist[-1].gameid + 1

    newunit = unit.Unit(startposition=newpos, gameid=newgameid, squadlist=newarmysubunit, colour=who.colour,
                        control=who.control, coa=who.coa, commander=False, startangle=who.angle, team=who.team)

    whosearmy.add(newunit)
    newunit.teamcommander = teamcommander
    newunit.leader = newleader
    newunit.subunit_sprite = new_subunit_sprite

    for this_subunit in newunit.subunit_sprite:
        this_subunit.parentunit = newunit

    for index, this_leader in enumerate(newunit.leader):  # Change army position of all leader in new parentunit
        this_leader.parentunit = newunit  # Set leader parentunit to new one
        this_leader.armyposition = index  # Change army position to new one
        this_leader.imgposition = this_leader.baseimgposition[this_leader.armyposition]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.imgposition)
        this_leader.poschangestat(this_leader)  # Change stat based on new army position

    add_new_unit(battle, newunit)

    # ^ End making new parentunit


# Other scripts

def playgif(imageset, framespeed=100):
    """framespeed in millisecond"""
    animation = {}
    frames = ["image1.png", "image2.png"]