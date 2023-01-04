import pygame

from gamescript.common import utility

from gamescript.common.damagesprite import play_animation


class EffectSprite(pygame.sprite.Sprite):
    effect_sprite_pool = None
    effect_animation_pool = None
    screen_scale = (1, 1)

    set_rotate = utility.set_rotate

    play_animation = play_animation.play_animation  # use play_animation from damage sprite

    def __init__(self, start_pos, target, angle, duration, sprite_type, sprite_direction, sprite_name):
        self._layer = 49
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.camera_scale = 1
        self.show_frame = 0
        self.animation_timer = 0
        self.angle = angle
        self.rotate = False

        self.base_pos = start_pos
        self.base_target = target
        self.duration = duration

        self.sprite_direction = sprite_direction
        self.current_animation = self.effect_animation_pool[sprite_type][self.sprite_direction][sprite_name]

        self.image = self.current_animation[self.show_frame]

        self.image_original = self.image.copy()

        if self.angle != 0:
            self.image = pygame.transform.rotate(self.angle)

    def update(self, dt, camera_scale):
        done, just_start = self.play_animation(0.1, dt, False)

        if self.duration > 0:
            self.duration -= dt
            if self.duration <= 0:  # kill effect when duration end
                self.kill()
        elif done:  # no duration, kill effect when animation end
            if self.show_frame:
                self.kill()

        if self.camera_scale != camera_scale:
            self.camera_scale = camera_scale
            if self.camera_scale == 1:
                self.image = self.image_original.copy()
            else:
                self.image = pygame.transform.smoothscale(self.image_original,
                                                          (int(self.image_original.get_width() / self.camera_scale),
                                                           int(self.image_original.get_height() / self.camera_scale)))

            if self.angle != 0:
                self.image = pygame.transform.rotate(self.angle)
