import random


def add_original_trait(self):
    """Add troop preset, race, mount, grade, and armour trait to original stat"""

    melee_attack_modifier = 1
    melee_def_modifier = 1
    range_def_modifier = 1
    accuracy_modifier = 1
    reload_modifier = 1
    speed_modifier = 1
    charge_modifier = 1

    morale_bonus = 0
    discipline_bonus = 0
    charge_def_bonus = 0
    sight_bonus = 0
    hidden_bonus = 0
    crit_bonus = 0
    mental_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0

    for trait in self.trait["Original"].values():
        melee_attack_modifier += trait["Melee Attack Effect"]
        melee_def_modifier += trait["Melee Defence Effect"]
        range_def_modifier += trait["Ranged Defence Effect"]
        speed_modifier += trait["Speed Effect"]
        accuracy_modifier += trait["Accuracy Effect"]
        reload_modifier += trait["Reload Effect"]
        charge_modifier += trait["Charge Effect"]
        charge_def_bonus += trait["Charge Defence Bonus"]
        sight_bonus += trait["Sight Bonus"]
        hidden_bonus += trait["Hidden Bonus"]
        hp_regen_bonus += trait["HP Regeneration Bonus"]
        stamina_regen_bonus += trait["Stamina Regeneration Bonus"]
        morale_bonus += trait["Morale Bonus"]
        discipline_bonus += trait["Discipline Bonus"]
        mental_bonus += trait["Mental Bonus"]
        crit_bonus += trait["Critical Bonus"]

        for element in self.original_element_resistance:
            self.original_element_resistance[element] += trait[element + " Resistance Bonus"]
        self.original_heat_resistance += trait["Heat Resistance Bonus"]
        self.original_cold_resistance += trait["Cold Resistance Bonus"]
        if 0 not in trait["Enemy Status"]:
            for effect in trait["Enemy Status"]:
                self.original_inflict_status[effect] = trait["Buff Range"]
        for effect in trait["Special Effect"]:  # trait from sources other than weapon activate permanent special status
            self.special_effect[self.troop_data.special_effect_list[effect]["Name"]][0][0] = True

    if self.special_effect_check("Varied Training"):  # Varied training
        self.original_melee_attack *= (random.randint(70, 120) / 100)
        self.original_melee_def *= (random.randint(70, 120) / 100)
        self.original_range_def *= (random.randint(70, 120) / 100)
        self.original_speed *= (random.randint(70, 120) / 100)
        self.original_accuracy *= (random.randint(70, 120) / 100)
        self.original_reload *= (random.randint(70, 120) / 100)
        self.original_charge *= (random.randint(70, 120) / 100)
        self.original_charge_def *= (random.randint(70, 120) / 100)
        self.original_morale += random.randint(-20, 10)
        self.original_discipline += random.randint(-20, 0)
        self.original_mental += random.randint(-20, 10)

    self.original_melee_attack *= melee_attack_modifier
    self.original_melee_def *= melee_def_modifier
    self.original_range_def *= range_def_modifier
    self.original_speed *= speed_modifier
    self.original_accuracy *= accuracy_modifier
    self.original_reload *= reload_modifier
    self.original_charge *= charge_modifier
    self.original_charge_def += charge_def_bonus
    self.original_hp_regen += hp_regen_bonus
    self.original_stamina_regen += stamina_regen_bonus
    self.original_morale += morale_bonus
    self.original_discipline += discipline_bonus
    self.original_crit_effect += crit_bonus
    self.original_mental += mental_bonus
    self.original_sight += sight_bonus
    self.original_hidden += hidden_bonus
