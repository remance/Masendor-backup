import math
import pygame

follow_distance = 30
stay_formation_distance = 1


def ai_move(self):
    if self.leader:  # has higher leader
        if self.is_leader:
            follow_order = self.leader.unit_follow_order
        else:
            follow_order = self.leader.troop_follow_order

        if follow_order != "Free":  # move to assigned location
            if follow_order in ("Stay Formation", "Stay Here"):
                follow = stay_formation_distance
            else:
                follow = follow_distance
            distance = self.follow_target.distance_to(self.base_pos)
            if "charge" in self.leader.current_action and follow_order != "Stay Here":  # charge
                # leader charging, charge with leader do not auto move to enemy on its own
                if self.equipped_weapon != self.melee_weapon_set[0]:  # swap to melee weapon for charge
                    self.swap_weapon(self.melee_weapon_set[0])
                    self.in_melee_combat_timer = 3  # consider as in melee to prevent swap back to range weapon
                else:  # already equipped melee weapon
                    # charge movement based on angle instead of formation pos
                    if self.available_move_skill and not self.command_action:  # use move skill first
                        self.skill_command_input(0, self.available_move_skill)
                    else:
                        run_speed = self.run_speed
                        if run_speed > self.unit_leader.run_speed:  # use unit leader run speed instead if faster
                            run_speed = self.unit_leader.run_speed

                        charge_target = pygame.Vector2(self.base_pos[0] -
                                                       (run_speed * math.sin(math.radians(self.leader.angle))),
                                                       self.base_pos[1] -
                                                       (run_speed * math.cos(math.radians(self.leader.angle))))
                        if charge_target.distance_to(self.base_pos) > 0:
                            self.command_target = charge_target
                            attack_index = 0
                            if not self.melee_range[0]:
                                attack_index = 1

                            if "charge" not in self.current_action:
                                self.interrupt_animation = True
                            self.command_action = self.charge_command_action[attack_index]
                            self.move_speed = run_speed

            elif distance > follow:  # too far from follow target pos, start moving toward it
                self.command_target = self.follow_target
                if 0 < distance < 20:  # only walk if not too far
                    if ("movable" in self.current_action and "walk" not in self.current_action) or \
                            "hold" in self.current_action:
                        self.interrupt_animation = True
                    self.command_action = self.walk_command_action
                    self.move_speed = self.walk_speed
                else:  # run if too far
                    if distance > 100 and self.leader and self.available_move_far_skill and not self.command_action:
                        # use move far skill first if leader
                        self.skill_command_input(0, self.available_move_far_skill)
                    elif self.available_move_skill and not self.command_action:  # use move skill
                        self.skill_command_input(0, self.available_move_skill)
                    else:
                        if ("movable" in self.current_action and "run" not in self.current_action) or "hold" in self.current_action:
                            self.interrupt_animation = True
                        self.command_action = self.run_command_action
                        self.move_speed = self.run_speed

            elif self.attack_target and self.max_melee_range > 0:  # enemy nearby and follow target not too far
                distance = self.attack_target.base_pos.distance_to(self.base_pos) - self.max_melee_range
                if distance < follow or self.impetuous:
                    # enemy nearby and self not too far from follow_target
                    if distance > self.max_melee_range:  # move closer to enemy in range
                        # charge to front of near target
                        if distance > 100 and self.leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                            self.skill_command_input(0, self.available_move_far_skill)
                        elif self.available_move_skill and not self.command_action:  # use move skill
                            self.skill_command_input(0, self.available_move_skill)
                        else:
                            if "movable" in self.current_action and "charge" not in self.current_action:
                                self.interrupt_animation = True

                            if self.melee_range[0] > 0:
                                self.command_action = self.charge_command_action[0]
                            else:
                                self.command_action = self.charge_command_action[1]

                            # move enough to be in melee attack range
                            base_angle = self.set_rotate(self.attack_target.base_pos)
                            self.command_target = pygame.Vector2(self.base_pos[0] -
                                                                 (distance * math.sin(math.radians(base_angle))),
                                                                 self.base_pos[1] -
                                                                 (distance * math.cos(math.radians(base_angle))))
                            self.move_speed = self.run_speed

        else:  # move to attack nearby enemy in free order
            if not self.attack_target:  # no enemy to hit yet
                distance = self.nearest_enemy[0].base_pos.distance_to(self.front_pos)
                if self.shoot_range[0] + self.shoot_range[1] > 0:  # has range weapon, move to maximum shoot range position
                    max_shoot = max(self.shoot_range[0], self.shoot_range[1]) * 1.1
                    if distance > max_shoot:  # further than can shoot
                        distance -= max_shoot
                        if distance > 100 and self.leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                            self.skill_command_input(0, self.available_move_far_skill)
                        elif self.available_move_skill and not self.command_action:  # use move skill first
                            self.skill_command_input(0, self.available_move_skill)
                        else:
                            angle = self.set_rotate(self.nearest_enemy[0].base_pos)
                            self.follow_target = pygame.Vector2(self.base_pos[0] - (distance * math.sin(math.radians(angle))),
                                                                self.base_pos[1] - (distance * math.cos(math.radians(angle))))
                            self.command_action = self.run_command_action
                            self.command_target = self.follow_target
                            self.move_speed = self.run_speed

                else:  # no range weapon, move to melee
                    distance = self.nearest_enemy[0].base_pos.distance_to(self.base_pos) - self.max_melee_range
                    if distance > self.max_melee_range > 0:  # too far move closer
                        if distance > 100 and self.leader and self.available_move_far_skill and not self.command_action:  # use move far skill first if leader
                            self.skill_command_input(0, self.available_move_far_skill)
                        elif self.available_move_skill and not self.command_action:  # use move skill first
                            self.skill_command_input(0, self.available_move_skill)
                        else:
                            self.follow_target = self.nearest_enemy[0].base_pos
                            if distance > self.melee_range[0] > 0:
                                self.command_action = self.charge_command_action[0]
                            else:
                                self.command_action = self.charge_command_action[1]
                            self.command_target = self.follow_target
                            self.move_speed = self.run_speed

    if not self.current_action and not self.command_action and self.available_idle_skill:  # idle, use idle skill
        self.skill_command_input(0, self.available_idle_skill)
