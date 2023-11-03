#Pack-a-Punch v3 by Era0S
#汉化：炸队汉化组 QQ群161073376 联系邮箱：cntsl@inker.ga
#发行/修补/资源收录：药服技术社 QQ群527575487 联系邮箱：ink@inker.ga(技术支持) mod@inker.ga（投稿mod）
# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import inspect
from ba import _math
from bastd.actor.spazfactory import SpazFactory
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.actor.spaz import Spaz, BombDiedMessage, CurseExplodeMessage, PunchHitMessage, PickupMessage
from bastd.actor.spazbot import SpazBot, SpazBotDiedMessage, SpazBotSet
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.bomb import Blast
from bastd.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage
from bastd.game.elimination import Icon
from bastd.game.thelaststand import SpawnInfo
from bastd.actor.popuptext import PopupText
import random

if TYPE_CHECKING:
    from typing import Any, Sequence

_shieldbool = True
_gamemode = 1
POWERUP_WEAR_OFF_TIME = 20000
BASE_PUNCH_COOLDOWN = 400

LITE_BOT_COLOR = (1.2, 0.9, 0.2)
LITE_BOT_HIGHLIGHT = (1.0, 0.5, 0.6)
DEFAULT_BOT_COLOR = (0.6, 0.6, 0.6)
DEFAULT_BOT_HIGHLIGHT = (0.1, 0.3, 0.1)
PRO_BOT_COLOR = (1.0, 0.2, 0.1)
PRO_BOT_HIGHLIGHT = (0.6, 0.1, 0.05)
    
class spazpunch(PlayerSpaz):
    def invout(self) -> None:
        self.node.invincible = False
    def handlemessage(self, msg: Any) -> Any:
        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        assert not self.expired

        if isinstance(msg, ba.HitMessage):
            sourceplr = msg.get_source_player(type(self._player))
            if not self.node:
                return None
            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

            # If we were recently hit, don't count this as another.
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
            assert isinstance(local_time, int)
            if (self._last_hit_time is None
                    or local_time - self._last_hit_time > 1000):
                self._num_times_hit += 1
                self._last_hit_time = local_time

            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            # If they've got a shield, deliver it to that instead.
            if self.shield:
                if msg.flat_damage:
                    damage = msg.flat_damage * self.impact_scale
                else:
                    # Hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse.
                    assert msg.force_direction is not None
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 1, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])
                    damage = damage_scale * self.node.damage

                assert self.shield_hitpoints is not None
                self.shield_hitpoints -= int(damage)
                self.shield.hurt = (
                        1.0 -
                        float(self.shield_hitpoints) / self.shield_hitpoints_max)

                # Its a cleaner event if a hit just kills the shield
                # without damaging the player.
                # However, massive damage events should still be able to
                # damage the player. This hopefully gives us a happy medium.
                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:

                    # FIXME: Transition out perhaps?
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,
                                 1.0,
                                 position=self.node.position)

                    # Emit some cool looking sparks when the shield dies.
                    npos = self.node.position
                    ba.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                              velocity=self.node.velocity,
                              count=random.randrange(20, 30),
                              scale=1.0,
                              spread=0.6,
                              chunk_type='spark')

                else:
                    ba.playsound(SpazFactory.get().shield_hit_sound,
                                 0.5,
                                 position=self.node.position)

                # Emit some cool looking sparks on shield hit.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                # If they passed our spillover threshold,
                # pass damage along to spaz.
                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    # Scale down the magnitudes applied to spaz accordingly.
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True  # Good job shield!
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                # Hit it with an impulse and get the resulting damage.
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                    msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                    velocity_mag, msg.radius, 0, msg.force_direction[0],
                    msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                srcname = self._player.getname(full=True)
                self.on_punched(damage)

                global _shieldbool
                if damage > 250 and damage <= 500 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='normal',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 6:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 3)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并恢复了生命值!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max/10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 暴击!', msg.pos, msg.force_direction)
                elif damage > 500 and damage <= 750 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='sticky',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 5:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 4)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并被短暂无敌!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.node.invincible = True
                            ba.timer(1.5, self.invout)
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 3:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 粘性!', msg.pos, msg.force_direction)
                elif damage > 750 and damage <= 900 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='impact',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 5:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 2)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了！',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage/10)) + '% 脱落!', msg.pos, msg.force_direction)
                elif damage > 900 and damage < 1000 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 1000,
                          blast_type='tnt',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 4:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 3)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并被短暂无敌!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.node.invincible = True
                            ba.timer(1.5, self.invout)
                        elif power == 2:
                            PopupText(
                                text=srcname + '单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage/10)) + '% 脱落!', msg.pos, msg.force_direction)
                elif damage >= 1000 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=(damage / 5000),
                          blast_type='ice',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 3:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        PopupText(
                            text=srcname + ' 单走一个6并被短暂无敌!',
                            color=(0.7, 0.7, 1.0, 1),
                            scale=1.6,
                            position=self.node.position).autoretain()
                        self.node.invincible = True
                        ba.timer(1.5, self.invout)

                # Let's always add in a super-punch sound with boxing
                # gloves just to differentiate them.
                if msg.hit_subtype == 'super_punch':
                    ba.playsound(SpazFactory.get().punch_sound_stronger,
                                 1.0,
                                 position=self.node.position)
                if damage > 500:
                    sounds = SpazFactory.get().punch_sound_strong
                    sound = sounds[random.randrange(len(sounds))]
                else:
                    sound = SpazFactory.get().punch_sound
                ba.playsound(sound, 1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(damage * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                ba.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(damage * 0.04)),
                          scale=0.9,
                          spread=0.28)

                # Momentary flash.
                hurtiness = damage * 0.003
                punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                            msg.pos[1] + msg.force_direction[1] * 0.02,
                            msg.pos[2] + msg.force_direction[2] * 0.02)
                flash_color = (1.0, 0.8, 0.4)
                light = ba.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color
                    })
                ba.timer(0.06, light.delete)

                flash = ba.newnode('flash',
                                   attrs={
                                       'position': punchpos,
                                       'size': 0.17 + 0.17 * hurtiness,
                                       'color': flash_color
                                   })
                ba.timer(0.06, flash.delete)
            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)

            if self.hitpoints > 0:

                # It's kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount *if* it'll keep us alive
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    # Drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                # If we're cursed, *any* damage blows us up.
                if self._cursed and damage > 0:
                    ba.timer(
                        0.05,
                        ba.WeakCall(self.curse_explode,
                                    msg.get_source_player(ba.Player)))

                # If we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        ba.DieMessage(how=ba.DeathType.IMPACT))

            # If we're dead, take a look at the smoothed damage value
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough.
            if self.hitpoints <= 0:
                ba.show_damage_count('挂了!', msg.pos, (0, 0, 0))
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()
            if sourceplr:
                self.last_player_attacked_by = sourceplr
                self.last_attacked_time = ba.time()
                self.last_attacked_type = (msg.hit_type, msg.hit_subtype)
            super().handlemessage(msg)  # Augment standard behavior.
            activity = self._activity()
            if activity is not None and self._player.exists():
                activity.handlemessage(PlayerSpazHurtMessage(self))
            else:
                return super().handlemessage(msg)
            self.set_score_text(str(int(self.hitpoints / 10)) + 'HP')
            return None
        else:
            return super().handlemessage(msg)

class punchspazbot(SpazBot):
    def handlemessage(self, msg: Any) -> Any:
        # pylint: disable=too-many-branches
        assert not self.expired

        if isinstance(msg, ba.HitMessage):
            source_player = msg.get_source_player(ba.Player)
            if source_player:
                self.last_player_attacked_by = source_player
                self.last_attacked_time = ba.time()
                self.last_attacked_type = (msg.hit_type, msg.hit_subtype)
            sourceplr = msg.get_source_player(type(ba.Player))
            if not self.node:
                return None
            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

                # If we were recently hit, don't count this as another.
                # (so punch flurries and bomb pileups essentially count as 1 hit)
            local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
            assert isinstance(local_time, int)
            if (self._last_hit_time is None
                    or local_time - self._last_hit_time > 1000):
                self._num_times_hit += 1
                self._last_hit_time = local_time

            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            # If they've got a shield, deliver it to that instead.
            if self.shield:
                if msg.flat_damage:
                    damage = msg.flat_damage * self.impact_scale
                else:
                    # Hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse.
                    assert msg.force_direction is not None
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 1, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])
                    damage = damage_scale * self.node.damage

                assert self.shield_hitpoints is not None
                self.shield_hitpoints -= int(damage)
                self.shield.hurt = (
                        1.0 -
                        float(self.shield_hitpoints) / self.shield_hitpoints_max)

                # Its a cleaner event if a hit just kills the shield
                # without damaging the player.
                # However, massive damage events should still be able to
                # damage the player. This hopefully gives us a happy medium.
                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:

                    # FIXME: Transition out perhaps?
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,
                                 1.0,
                                 position=self.node.position)

                    # Emit some cool looking sparks when the shield dies.
                    npos = self.node.position
                    ba.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                              velocity=self.node.velocity,
                              count=random.randrange(20, 30),
                              scale=1.0,
                              spread=0.6,
                              chunk_type='spark')

                else:
                    ba.playsound(SpazFactory.get().shield_hit_sound,
                                 0.5,
                                 position=self.node.position)

                # Emit some cool looking sparks on shield hit.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                # If they passed our spillover threshold,
                # pass damage along to spaz.
                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    # Scale down the magnitudes applied to spaz accordingly.
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True  # Good job shield!
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                # Hit it with an impulse and get the resulting damage.
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                    msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                    velocity_mag, msg.radius, 0, msg.force_direction[0],
                    msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                srcname = '机器人'
                self.on_punched(damage)

                global _shieldbool
                if damage > 250 and damage <= 500 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='normal',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 6:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 3)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 吹!', msg.pos, msg.force_direction)
                elif damage > 500 and damage <= 750 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='sticky',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 5:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 4)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并被短暂无敌',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.node.invincible = True
                            ba.timer(1.5, self.invout)
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 3:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 粘性!', msg.pos, msg.force_direction)
                elif damage > 750 and damage <= 900 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='impact',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 5:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 2)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了！',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾！',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 脱落！', msg.pos, msg.force_direction)
                elif damage > 900 and damage < 1000 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 1000,
                          blast_type='tnt',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 4:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 3)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并被短暂无敌!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.node.invincible = True
                            ba.timer(1.5, self.invout)
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 脱落!', msg.pos, msg.force_direction)
                elif damage >= 1000 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=(damage / 5000),
                          blast_type='ice',
                          source_player=sourceplr).autoretain()
                    chance = random.randrange(1, 7)
                    if _shieldbool == True and chance >= 3:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        PopupText(
                            text=srcname + ' 单走一个6并被短暂无敌!',
                            color=(0.7, 0.7, 1.0, 1),
                            scale=1.6,
                            position=self.node.position).autoretain()
                        self.node.invincible = True
                        ba.timer(1.5, self.invout)

                # Let's always add in a super-punch sound with boxing
                # gloves just to differentiate them.
                if msg.hit_subtype == 'super_punch':
                    ba.playsound(SpazFactory.get().punch_sound_stronger,
                                 1.0,
                                 position=self.node.position)
                if damage > 500:
                    sounds = SpazFactory.get().punch_sound_strong
                    sound = sounds[random.randrange(len(sounds))]
                else:
                    sound = SpazFactory.get().punch_sound
                ba.playsound(sound, 1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(damage * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                ba.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(damage * 0.04)),
                          scale=0.9,
                          spread=0.28)

                # Momentary flash.
                hurtiness = damage * 0.003
                punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                            msg.pos[1] + msg.force_direction[1] * 0.02,
                            msg.pos[2] + msg.force_direction[2] * 0.02)
                flash_color = (1.0, 0.8, 0.4)
                light = ba.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color
                    })
                ba.timer(0.06, light.delete)

                flash = ba.newnode('flash',
                                   attrs={
                                       'position': punchpos,
                                       'size': 0.17 + 0.17 * hurtiness,
                                       'color': flash_color
                                   })
                ba.timer(0.06, flash.delete)
            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)

            if self.hitpoints > 0:

                # It's kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount *if* it'll keep us alive
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    # Drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                # If we're cursed, *any* damage blows us up.
                if self._cursed and damage > 0:
                    ba.timer(
                        0.05,
                        ba.WeakCall(self.curse_explode,
                                    msg.get_source_player(ba.Player)))

                # If we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        ba.DieMessage(how=ba.DeathType.IMPACT))

            # If we're dead, take a look at the smoothed damage value
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough.
            if self.hitpoints <= 0:
                ba.show_damage_count('挂了!', msg.pos, (0, 0, 0))
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()
            self.set_score_text(str(int(self.hitpoints / 10)) + 'HP')
        else:
            super().handlemessage(msg)

class BomberBot(punchspazbot):
    """A bot that throws regular bombs and occasionally punches.

    category: Bot Classes
    """
    character = 'Spaz'
    punchiness = 0.3
    points_mult = 3


class BomberBotLite(BomberBot):
    """A less aggressive yellow version of ba.BomberBot.

    category: Bot Classes
    """
    color = LITE_BOT_COLOR
    highlight = LITE_BOT_HIGHLIGHT
    punchiness = 0.2
    throw_rate = 0.7
    throwiness = 0.1
    charge_speed_min = 0.6
    charge_speed_max = 0.6
    points_mult = 3


class BomberBotStaticLite(BomberBotLite):
    """A less aggressive generally immobile weak version of ba.BomberBot.

    category: Bot Classes
    """
    static = True
    throw_dist_min = 0.0


class BomberBotStatic(BomberBot):
    """A version of ba.BomberBot who generally stays in one place.

    category: Bot Classes
    """
    static = True
    throw_dist_min = 0.0


class BomberBotPro(BomberBot):
    """A more powerful version of ba.BomberBot.

    category: Bot Classes
    """
    points_mult = 6
    color = PRO_BOT_COLOR
    highlight = PRO_BOT_HIGHLIGHT
    default_bomb_count = 3
    default_boxing_gloves = True
    punchiness = 0.7
    throw_rate = 1.3
    run = True
    run_dist_min = 6.0


class BomberBotProShielded(BomberBotPro):
    """A more powerful version of ba.BomberBot who starts with shields.

    category: Bot Classes
    """
    points_mult = 9
    default_shields = True


class BomberBotProStatic(BomberBotPro):
    """A more powerful ba.BomberBot who generally stays in one place.

    category: Bot Classes
    """
    static = True
    throw_dist_min = 0.0


class BomberBotProStaticShielded(BomberBotProShielded):
    """A powerful ba.BomberBot with shields who is generally immobile.

    category: Bot Classes
    """
    static = True
    throw_dist_min = 0.0


class BrawlerBot(punchspazbot):
    """A bot who walks and punches things.

    category: Bot Classes
    """
    character = 'Kronk'
    punchiness = 0.9
    charge_dist_max = 9999.0
    charge_speed_min = 1.0
    charge_speed_max = 1.0
    throw_dist_min = 9999
    throw_dist_max = 9999
    points_mult = 3


class BrawlerBotLite(BrawlerBot):
    """A weaker version of ba.BrawlerBot.

    category: Bot Classes
    """
    color = LITE_BOT_COLOR
    highlight = LITE_BOT_HIGHLIGHT
    punchiness = 0.3
    charge_speed_min = 0.6
    charge_speed_max = 0.6


class BrawlerBotPro(BrawlerBot):
    """A stronger version of ba.BrawlerBot.

    category: Bot Classes
    """
    color = PRO_BOT_COLOR
    highlight = PRO_BOT_HIGHLIGHT
    run = True
    run_dist_min = 4.0
    default_boxing_gloves = True
    punchiness = 0.95
    points_mult = 6


class BrawlerBotProShielded(BrawlerBotPro):
    """A stronger version of ba.BrawlerBot who starts with shields.

    category: Bot Classes
    """
    default_shields = True
    points_mult = 9


class ChargerBot(punchspazbot):
    """A speedy melee attack bot.

    category: Bot Classes
    """

    character = 'Snake Shadow'
    punchiness = 1.0
    run = True
    charge_dist_min = 10.0
    charge_dist_max = 9999.0
    charge_speed_min = 1.0
    charge_speed_max = 1.0
    throw_dist_min = 9999
    throw_dist_max = 9999
    points_mult = 6


class BouncyBot(punchspazbot):
    """A speedy attacking melee bot that jumps constantly.

    category: Bot Classes
    """

    color = (1, 1, 1)
    highlight = (1.0, 0.5, 0.5)
    character = 'Easter Bunny'
    punchiness = 1.0
    run = True
    bouncy = True
    default_boxing_gloves = True
    charge_dist_min = 10.0
    charge_dist_max = 9999.0
    charge_speed_min = 1.0
    charge_speed_max = 1.0
    throw_dist_min = 9999
    throw_dist_max = 9999
    points_mult = 6


class ChargerBotPro(ChargerBot):
    """A stronger ba.ChargerBot.

    category: Bot Classes
    """
    color = PRO_BOT_COLOR
    highlight = PRO_BOT_HIGHLIGHT
    default_shields = True
    default_boxing_gloves = True
    points_mult = 9


class ChargerBotProShielded(ChargerBotPro):
    """A stronger ba.ChargerBot who starts with shields.

    category: Bot Classes
    """
    default_shields = True
    points_mult = 12


class TriggerBot(punchspazbot):
    """A slow moving bot with trigger bombs.

    category: Bot Classes
    """
    character = 'Zoe'
    punchiness = 0.75
    throwiness = 0.7
    charge_dist_max = 1.0
    charge_speed_min = 0.3
    charge_speed_max = 0.5
    throw_dist_min = 3.5
    throw_dist_max = 5.5
    default_bomb_type = 'impact'
    points_mult = 6


class TriggerBotStatic(TriggerBot):
    """A ba.TriggerBot who generally stays in one place.

    category: Bot Classes
    """
    static = True
    throw_dist_min = 0.0


class TriggerBotPro(TriggerBot):
    """A stronger version of ba.TriggerBot.

    category: Bot Classes
    """
    color = PRO_BOT_COLOR
    highlight = PRO_BOT_HIGHLIGHT
    default_bomb_count = 3
    default_boxing_gloves = True
    charge_speed_min = 1.0
    charge_speed_max = 1.0
    punchiness = 0.9
    throw_rate = 1.3
    run = True
    run_dist_min = 6.0
    points_mult = 9


class TriggerBotProShielded(TriggerBotPro):
    """A stronger version of ba.TriggerBot who starts with shields.

    category: Bot Classes
    """
    default_shields = True
    points_mult = 12


class StickyBot(punchspazbot):
    """A crazy bot who runs and throws sticky bombs.

    category: Bot Classes
    """
    character = 'Mel'
    punchiness = 0.9
    throwiness = 1.0
    run = True
    charge_dist_min = 4.0
    charge_dist_max = 10.0
    charge_speed_min = 1.0
    charge_speed_max = 1.0
    throw_dist_min = 0.0
    throw_dist_max = 4.0
    throw_rate = 2.0
    default_bomb_type = 'sticky'
    default_bomb_count = 3
    points_mult = 9


class StickyBotStatic(StickyBot):
    """A crazy bot who throws sticky-bombs but generally stays in one place.

    category: Bot Classes
    """
    static = True


class ExplodeyBot(punchspazbot):
    """A bot who runs and explodes in 5 seconds.

    category: Bot Classes
    """
    character = 'Jack Morgan'
    run = True
    charge_dist_min = 0.0
    charge_dist_max = 9999
    charge_speed_min = 1.0
    charge_speed_max = 1.0
    throw_dist_min = 9999
    throw_dist_max = 9999
    start_cursed = True
    points_mult = 12


class ExplodeyBotNoTimeLimit(ExplodeyBot):
    """A bot who runs but does not explode on his own.

    category: Bot Classes
    """
    curse_time = None


class ExplodeyBotShielded(ExplodeyBot):
    """A ba.ExplodeyBot who starts with shields.

    category: Bot Classes
    """
    default_shields = True
    points_mult = 15

class Player(ba.Player['Team']):
    """Our player type for this game."""

    global _gamemode
    if _gamemode == 1 or _gamemode == 2:
        def __init__(self) -> None:
            global _gamemode
            if _gamemode == 1:
                self.lives = 0
                self.icons: list[Icon] = []

class Team(ba.Team[Player]):
    """Our team type for this game."""

    global _gamemode
    if _gamemode == 1 or _gamemode == 2:
        def __init__(self) -> None:
            global _gamemode
            if _gamemode == 1:
                self.survival_seconds: int | None = None
                self.spawn_order: list[Player] = []
            elif _gamemode == 2:
                self.score = 0

# ba_meta export game
class PackaPunchGame(ba.TeamGameActivity[Player, Team]):
    """Game type where we pack the best punches of our lives"""
    global _gamemode
    name = '打击气泡'
    description = '用拳头去打击你的对手吧~'
    scoreconfig = ba.ScoreConfig(label='Survived',
                                 scoretype=ba.ScoreType.SECONDS,
                                 none_is_winner=True)
    # Show messages when players die since it's meaningful here.
    announce_player_deaths = True

    allow_mid_activity_joins = False

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [
            ba.IntSetting(
                '玩家血量',
                default=500,
                min_value=100,
                increment=50,
            ),
            ba.IntChoiceSetting(
                'Time Limit',
                choices=[
                    ('None', 0),
                    ('1 Minute', 60),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600),
                    ('20 Minutes', 1200),
                ],
                default=0,
            ),
            ba.FloatChoiceSetting(
                'Respawn Times',
                choices=[
                    ('Shorter', 0.25),
                    ('Short', 0.5),
                    ('Normal', 1.0),
                    ('Long', 2.0),
                    ('Longer', 4.0),
                ],
                default=1.0,
            ),
            ba.BoolSetting('拳套', default=True),
            ba.BoolSetting('允许抓', default=True),
            ba.BoolSetting('随机概率复活', default=True),
            ba.IntChoiceSetting(
                '游戏模式',
                choices=[
                    ('消除战', 1),
                    ('死亡竞赛', 2)
                ],
                default=1
            ),
            ba.IntSetting(
                '杀死玩家数量',
                default=5,
                min_value=1,
                increment=1,
            ),
            ba.BoolSetting('Epic Mode', default=False),
        ]
        if issubclass(sessiontype, ba.DualTeamSession):
            settings.append(ba.BoolSetting('单挑模式（消除战）', default=False))
            settings.append(
                ba.BoolSetting('平衡总生命（消除战）', default=False))
        elif issubclass(sessiontype, ba.FreeForAllSession):
            settings.append(
                ba.BoolSetting('允许负分（死亡竞赛）', default=False))
        return settings

    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
        return ba.getmaps('melee')

    # We support teams, free-for-all, and co-op sessions.
    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession)
                or issubclass(sessiontype, ba.CoopSession))

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._new_wave_sound = ba.getsound('scoreHit01')
        self._winsound = ba.getsound('score')
        self._dingsound = ba.getsound('dingSmall')
        self._dingsoundhigh = ba.getsound('dingSmallHigh')
        self._score_to_win: int | None = None
        self._bots = SpazBotSet()
        self._bot_update_interval: float | None = None
        self._bot_update_timer: ba.Timer | None = None
        self._scoreboard = Scoreboard()
        self._score = 0
        self._spawn_center = (0, 5.5, -4.14)
        self._start_time: float | None = None
        self._vs_text: ba.Actor | None = None
        self._round_end_timer: ba.Timer | None = None
        self._epic_mode = bool(settings['Epic Mode'])
        self._lives_or_kills = int(settings['杀死玩家数量'])
        self._time_limit = float(settings['Time Limit'])
        self._balance_total_lives = bool(
            settings.get('平衡总生命（消除战）', False))
        self._solo_mode = bool(settings.get('单挑模式（消除战）', False))
        self._healthpoints = int(settings['玩家血量'])
        self._glovesbool = bool(settings['拳套'])
        self._grabbool = bool(settings['允许抓'])
        global _shieldbool
        _shieldbool = bool(settings['随机概率复活'])
        global _gamemode
        _gamemode = int(settings['游戏模式'])
        self._allow_negative_scores = bool(
            settings.get('允许负分（死亡竞赛）', False))

        # Base class overrides:
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC
                              if self._epic_mode else ba.MusicType.SURVIVAL)

    def get_instance_description(self) -> str | Sequence:
        global _gamemode
        if isinstance(self.session, ba.DualTeamSession):
            if _gamemode == 1:
                return '你的拳头就是炸弹！\n最后活着的队伍获胜'
            elif _gamemode == 2:
                return '你的拳头就是炸弹！\n 杀死 ${ARG1} 个敌人.', self._lives_or_kills
        elif isinstance(self.session, ba.FreeForAllSession):
            if _gamemode == 1:
                return '你的拳头就是炸弹！\n 最后活着的获胜'
            elif _gamemode == 2:
                return '你的拳头就是炸弹！\n 杀死 ${ARG1} 个敌人.', self._lives_or_kills
        else:
            return '你的拳头就是炸弹！\n! 活下去!'

    def get_instance_description_short(self) -> str | Sequence:
        global _gamemode
        if isinstance(self.session, ba.DualTeamSession):
            if _gamemode == 1:
                return '你的拳头就是炸弹！\n最后活着的队伍获胜'
            elif _gamemode == 2:
                return '你的拳头就是炸弹！\n 杀死 ${ARG1} 个敌人.', self._lives_or_kills
        elif isinstance(self.session, ba.FreeForAllSession):
            if _gamemode == 1:
                return '你的拳头就是炸弹！\n 最后活着的获胜.'
            elif _gamemode == 2:
                return '你的拳头就是炸弹！\n 杀死 ${ARG1} 个敌人.', self._lives_or_kills

    def on_player_join(self, player: Player) -> None:
        global _gamemode
        if _gamemode == 1:
            player.lives = self._lives_or_kills

            if self._solo_mode:
                player.team.spawn_order.append(player)
                self._update_solo_mode()
            else:
                # Create our icon and spawn.
                player.icons = [Icon(player, position=(0, 50), scale=0.8)]
                if player.lives > 0:
                    self.spawn_player(player)

            # Don't waste time doing this until begin.
            if self.has_begun():
                self._update_icons()
        elif _gamemode == 2:
            super().on_player_join(player)

    def on_team_join(self, team: Team) -> None:
        global _gamemode
        if _gamemode == 1:
            super().on_team_join(team)
        elif _gamemode == 2:
            if self.has_begun():
                self._update_scoreboard()
        elif _gamemode == 3:
            super().on_team_join(team)

    def on_begin(self) -> None:
        super().on_begin()
        self._start_time = ba.time()
        self.setup_standard_time_limit(self._time_limit)
        global _gamemode
        if _gamemode == 1:
            if self._solo_mode:
                self._vs_text = ba.NodeActor(
                    ba.newnode('text',
                               attrs={
                                   'position': (0, 105),
                                   'h_attach': 'center',
                                   'h_align': 'center',
                                   'maxwidth': 200,
                                   'shadow': 0.5,
                                   'vr_depth': 390,
                                   'scale': 0.6,
                                   'v_attach': 'bottom',
                                   'color': (0.8, 0.8, 0.3, 1.0),
                                   'text': ba.Lstr(resource='vsText')
                               }))

            # If balance-team-lives is on, add lives to the smaller team until
            # total lives match.
            if (isinstance(self.session, ba.DualTeamSession)
                    and self._balance_total_lives and self.teams[0].players
                    and self.teams[1].players):
                if self._get_total_team_lives(
                        self.teams[0]) < self._get_total_team_lives(self.teams[1]):
                    lesser_team = self.teams[0]
                    greater_team = self.teams[1]
                else:
                    lesser_team = self.teams[1]
                    greater_team = self.teams[0]
                add_index = 0
                while (self._get_total_team_lives(lesser_team) <
                       self._get_total_team_lives(greater_team)):
                    lesser_team.players[add_index].lives += 1
                    add_index = (add_index + 1) % len(lesser_team.players)

            self._update_icons()

            # We could check game-over conditions at explicit trigger points,
            # but lets just do the simple thing and poll it.
            ba.timer(1.0, self._update, repeat=True)
        elif _gamemode == 2:
            # Base kills needed to win on the size of the largest team.
            self._score_to_win = (self._lives_or_kills *
                                  max(1, max(len(t.players) for t in self.teams)))
            self._update_scoreboard()
        elif _gamemode == 3:
            ba.timer(0.001, ba.WeakCall(self._start_bot_updates))
            self._update_scores()

    def _update_solo_mode(self) -> None:
        # For both teams, find the first player on the spawn order list with
        # lives remaining and spawn them if they're not alive.
        for team in self.teams:
            # Prune dead players from the spawn order.
            team.spawn_order = [p for p in team.spawn_order if p]
            for player in team.spawn_order:
                assert isinstance(player, Player)
                if player.lives > 0:
                    if not player.is_alive():
                        self.spawn_player(player)
                    break

    def _update_icons(self) -> None:
        # pylint: disable=too-many-branches

        # In free-for-all mode, everyone is just lined up along the bottom.
        if isinstance(self.session, ba.FreeForAllSession):
            count = len(self.teams)
            x_offs = 85
            xval = x_offs * (count - 1) * -0.5
            for team in self.teams:
                if len(team.players) == 1:
                    player = team.players[0]
                    for icon in player.icons:
                        icon.set_position_and_scale((xval, 30), 0.7)
                        icon.update_for_lives()
                    xval += x_offs

        # In teams mode we split up teams.
        else:
            if self._solo_mode:
                # First off, clear out all icons.
                for player in self.players:
                    player.icons = []

                # Now for each team, cycle through our available players
                # adding icons.
                for team in self.teams:
                    if team.id == 0:
                        xval = -60
                        x_offs = -78
                    else:
                        xval = 60
                        x_offs = 78
                    is_first = True
                    test_lives = 1
                    while True:
                        players_with_lives = [
                            p for p in team.spawn_order
                            if p and p.lives >= test_lives
                        ]
                        if not players_with_lives:
                            break
                        for player in players_with_lives:
                            player.icons.append(
                                Icon(player,
                                     position=(xval, (40 if is_first else 25)),
                                     scale=1.0 if is_first else 0.5,
                                     name_maxwidth=130 if is_first else 75,
                                     name_scale=0.8 if is_first else 1.0,
                                     flatness=0.0 if is_first else 1.0,
                                     shadow=0.5 if is_first else 1.0,
                                     show_death=is_first,
                                     show_lives=False))
                            xval += x_offs * (0.8 if is_first else 0.56)
                            is_first = False
                        test_lives += 1
            # Non-solo mode.
            else:
                for team in self.teams:
                    if team.id == 0:
                        xval = -50
                        x_offs = -85
                    else:
                        xval = 50
                        x_offs = 85
                    for player in team.players:
                        for icon in player.icons:
                            icon.set_position_and_scale((xval, 30), 0.7)
                            icon.update_for_lives()
                        xval += x_offs

    def _get_spawn_point(self, player: Player) -> ba.Vec3 | None:
        del player  # Unused.

        # In solo-mode, if there's an existing live player on the map, spawn at
        # whichever spot is farthest from them (keeps the action spread out).
        if self._solo_mode:
            living_player = None
            living_player_pos = None
            for team in self.teams:
                for tplayer in team.players:
                    if tplayer.is_alive():
                        assert tplayer.node
                        ppos = tplayer.node.position
                        living_player = tplayer
                        living_player_pos = ppos
                        break
            if living_player:
                assert living_player_pos is not None
                player_pos = ba.Vec3(living_player_pos)
                points: list[tuple[float, ba.Vec3]] = []
                for team in self.teams:
                    start_pos = ba.Vec3(self.map.get_start_position(team.id))
                    points.append(
                        ((start_pos - player_pos).length(), start_pos))
                # Hmm.. we need to sorting vectors too?
                points.sort(key=lambda x: x[0])
                return points[-1][1]
        return None

    def spawn_player(self, player: Player) -> ba.Actor:
        if isinstance(self.session, ba.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            # otherwise do free-for-all spawn locations
            position = self.map.get_ffa_start_position(self.players)
        angle = None

        name = player.getname()
        light_color = _math.normalized_color(player.color)
        display_color = _ba.safecolor(player.color, target_intensity=0.75)

        spaz = spazpunch(color=player.color,
                                highlight=player.highlight,
                                character=player.character,
                                player=player)

        player.actor = spaz
        assert spaz.node

        # If this is co-op and we're on Courtyard or Runaround, add the
        # material that allows us to collide with the player-walls.
        # FIXME: Need to generalize this.
        if isinstance(self.session, ba.CoopSession) and self.map.getname() in [
            'Courtyard', 'Tower D'
        ]:
            mat = self.map.preloaddata['collide_with_wall_material']
            assert isinstance(spaz.node.materials, tuple)
            assert isinstance(spaz.node.roller_materials, tuple)
            spaz.node.materials += (mat,)
            spaz.node.roller_materials += (mat,)

        spaz.node.name = name
        spaz.node.name_color = display_color
        spaz.connect_controls_to_player(enable_bomb=False,
                                        enable_pickup=self._grabbool)

        # Move to the stand position and add a flash of light.
        spaz.handlemessage(
            ba.StandMessage(
                position,
                angle if angle is not None else random.uniform(0, 360)))
        _ba.playsound(self._spawn_sound, 1, position=spaz.node.position)
        light = _ba.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        ba.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        _ba.timer(0.5, light.delete)

        spaz.hitpoints_max = self._healthpoints * 10
        spaz.hitpoints = self._healthpoints * 10
        if self._glovesbool == True:
            spaz.equip_boxing_gloves()

        global _gamemode
        if _gamemode == 1:
            # If we have any icons, update their state.
            for icon in player.icons:
                icon.handle_player_spawned()

        return spaz

    def _print_lives(self, player: Player) -> None:
        from bastd.actor import popuptext

        # We get called in a timer so it's possible our player has left/etc.
        if not player or not player.is_alive() or not player.node:
            return

        popuptext.PopupText('x' + str(player.lives - 1),
                            color=(1, 1, 0, 1),
                            offset=(0, -0.8, 0),
                            random_offset=0.0,
                            scale=1.8,
                            position=player.node.position).autoretain()

    def on_player_leave(self, player: Player) -> None:
        global _gamemode
        if _gamemode == 1:
            super().on_player_leave(player)
            player.icons = []

            # Remove us from spawn-order.
            if self._solo_mode:
                if player in player.team.spawn_order:
                    player.team.spawn_order.remove(player)

            # Update icons in a moment since our team will be gone from the
            # list then.
            ba.timer(0, self._update_icons)

            # If the player to leave was the last in spawn order and had
            # their final turn currently in-progress, mark the survival time
            # for their team.
            if self._get_total_team_lives(player.team) == 0:
                assert self._start_time is not None
                player.team.survival_seconds = int(ba.time() - self._start_time)
        elif _gamemode == 2:
            super().on_player_leave(player)

    def _get_total_team_lives(self, team: Team) -> int:
        return sum(player.lives for player in team.players)

    def handlemessage(self, msg: Any) -> Any:
        global _gamemode
        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)
            player: Player = msg.getplayer(Player)

            if _gamemode == 1:
                player.lives -= 1
                if player.lives < 0:
                    ba.print_error(
                        "Got lives < 0 in Elim; this shouldn't happen. solo:" +
                        str(self._solo_mode))
                    player.lives = 0

                # If we have any icons, update their state.
                for icon in player.icons:
                    icon.handle_player_died()

                # Play big death sound on our last death
                # or for every one in Solo Mode (Elimination Exclusive).
                if self._solo_mode or player.lives == 0:
                    ba.playsound(SpazFactory.get().single_player_death_sound)

                # If we hit zero lives, we're dead (and our team might be too).
                if player.lives == 0:
                    # If the whole team is now dead, mark their survival time.
                    if self._get_total_team_lives(player.team) == 0:
                        assert self._start_time is not None
                        player.team.survival_seconds = int(ba.time() -
                                                           self._start_time)
                else:
                    # Otherwise, in regular mode, respawn.
                    if not self._solo_mode:
                        self.respawn_player(player)

                # In solo, put ourself at the back of the spawn order.
                if self._solo_mode:
                    player.team.spawn_order.remove(player)
                    player.team.spawn_order.append(player)
            elif _gamemode == 2:
                self.respawn_player(player)

                killer = msg.getkillerplayer(Player)
                if killer is None:
                    return None

                # Handle team-kills.
                if killer.team is player.team:

                    # In free-for-all, killing yourself loses you a point.
                    if isinstance(self.session, ba.FreeForAllSession):
                        new_score = player.team.score - 1
                        if not self._allow_negative_scores:
                            new_score = max(0, new_score)
                        player.team.score = new_score

                    # In teams-mode it gives a point to the other team.
                    else:
                        ba.playsound(self._dingsound)
                        for team in self.teams:
                            if team is not killer.team:
                                team.score += 1

                # Killing someone on another team nets a kill.
                else:
                    killer.team.score += 1
                    ba.playsound(self._dingsound)

                    # In FFA show scores since its hard to find on the scoreboard.
                    if isinstance(killer.actor, PlayerSpaz) and killer.actor:
                        killer.actor.set_score_text(str(killer.team.score) + '/' +
                                                    str(self._score_to_win),
                                                    color=killer.team.color,
                                                    flash=True)

                self._update_scoreboard()

                # If someone has won, set a timer to end shortly.
                # (allows the dust to clear and draws to occur if deaths are
                # close enough)
                assert self._score_to_win is not None
                if any(team.score >= self._score_to_win for team in self.teams):
                    ba.timer(0.5, self.end_game)
        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.score,
                                            self._score_to_win)

    def _update(self) -> None:
        if self._solo_mode:
            # For both teams, find the first player on the spawn order
            # list with lives remaining and spawn them if they're not alive.
            for team in self.teams:
                # Prune dead players from the spawn order.
                team.spawn_order = [p for p in team.spawn_order if p]
                for player in team.spawn_order:
                    assert isinstance(player, Player)
                    if player.lives > 0:
                        if not player.is_alive():
                            self.spawn_player(player)
                            self._update_icons()
                        break

        # If we're down to 1 or fewer living teams, start a timer to end
        # the game (allows the dust to settle and draws to occur if deaths
        # are close enough).
        if len(self._get_living_teams()) < 2:
            self._round_end_timer = ba.Timer(0.5, self.end_game)

    def _get_living_teams(self) -> list[Team]:
        return [
            team for team in self.teams
            if len(team.players) > 0 and any(player.lives > 0
                                             for player in team.players)
        ]

    def end_game(self) -> None:
        global _gamemode
        if _gamemode == 1:
            if self.has_ended():
                return
            results = ba.GameResults()
            self._vs_text = None  # Kill our 'vs' if its there.
            for team in self.teams:
                results.set_team_score(team, team.survival_seconds)
            self.end(results=results)
        elif _gamemode == 2:
            results = ba.GameResults()
            for team in self.teams:
                results.set_team_score(team, team.score)
            self.end(results=results)

# ba_meta export plugin
class Spaz(ba.Plugin):
    def invout(self) -> None:
        self.node.invincible = False
    def new_handlemessage(self, msg: Any) -> Any:
        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        assert not self.expired

        if isinstance(msg, ba.PickedUpMessage):
            if self.node:
                self.node.handlemessage('hurt_sound')
                self.node.handlemessage('picked_up')

            # This counts as a hit.
            self._num_times_hit += 1

        elif isinstance(msg, ba.ShouldShatterMessage):
            # Eww; seems we have to do this in a timer or it wont work right.
            # (since we're getting called from within update() perhaps?..)
            # NOTE: should test to see if that's still the case.
            ba.timer(0.001, ba.WeakCall(self.shatter))

        elif isinstance(msg, ba.ImpactDamageMessage):
            # Eww; seems we have to do this in a timer or it wont work right.
            # (since we're getting called from within update() perhaps?..)
            ba.timer(0.001, ba.WeakCall(self._hit_self, msg.intensity))

        elif isinstance(msg, ba.PowerupMessage):
            if self._dead or not self.node:
                return True
            if self.pick_up_powerup_callback is not None:
                self.pick_up_powerup_callback(self)
            if msg.poweruptype == 'triple_bombs':
                tex = PowerupBoxFactory.get().tex_bomb
                self._flash_billboard(tex)
                self.set_bomb_count(3)
                if self.powerups_expire:
                    self.node.mini_billboard_1_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_1_start_time = t_ms
                    self.node.mini_billboard_1_end_time = (
                            t_ms + POWERUP_WEAR_OFF_TIME)
                    self._multi_bomb_wear_off_flash_timer = (ba.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000),
                        ba.WeakCall(self._multi_bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._multi_bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._multi_bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'land_mines':
                self.set_land_mine_count(min(self.land_mine_count + 3, 3))
            elif msg.poweruptype == 'impact_bombs':
                self.bomb_type = 'impact'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                            t_ms + POWERUP_WEAR_OFF_TIME)
                    self._bomb_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'sticky_bombs':
                self.bomb_type = 'sticky'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                            t_ms + POWERUP_WEAR_OFF_TIME)
                    self._bomb_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'punch':
                tex = PowerupBoxFactory.get().tex_punch
                self._flash_billboard(tex)
                self.equip_boxing_gloves()
                if self.powerups_expire:
                    self.node.boxing_gloves_flashing = False
                    self.node.mini_billboard_3_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_3_start_time = t_ms
                    self.node.mini_billboard_3_end_time = (
                            t_ms + POWERUP_WEAR_OFF_TIME)
                    self._boxing_gloves_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._gloves_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._boxing_gloves_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._gloves_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'shield':
                factory = SpazFactory.get()

                # Let's allow powerup-equipped shields to lose hp over time.
                self.equip_shields(decay=factory.shield_decay_rate > 0)
            elif msg.poweruptype == 'curse':
                self.curse()
            elif msg.poweruptype == 'ice_bombs':
                self.bomb_type = 'ice'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                            t_ms + POWERUP_WEAR_OFF_TIME)
                    self._bomb_wear_off_flash_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME - 2000,
                        ba.WeakCall(self._bomb_wear_off_flash),
                        timeformat=ba.TimeFormat.MILLISECONDS))
                    self._bomb_wear_off_timer = (ba.Timer(
                        POWERUP_WEAR_OFF_TIME,
                        ba.WeakCall(self._bomb_wear_off),
                        timeformat=ba.TimeFormat.MILLISECONDS))
            elif msg.poweruptype == 'health':
                if self._cursed:
                    self._cursed = False

                    # Remove cursed material.
                    factory = SpazFactory.get()
                    for attr in ['materials', 'roller_materials']:
                        materials = getattr(self.node, attr)
                        if factory.curse_material in materials:
                            setattr(
                                self.node, attr,
                                tuple(m for m in materials
                                      if m != factory.curse_material))
                    self.node.curse_death_time = 0
                self.hitpoints = self.hitpoints_max
                self._flash_billboard(PowerupBoxFactory.get().tex_health)
                self.node.hurt = 0
                self._last_hit_time = None
                self._num_times_hit = 0

            self.node.handlemessage('flash')
            if msg.sourcenode:
                msg.sourcenode.handlemessage(ba.PowerupAcceptMessage())
            return True

        elif isinstance(msg, ba.FreezeMessage):
            if not self.node:
                return None
            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return None
            if self.shield:
                return None
            if not self.frozen:
                self.frozen = True
                self.node.frozen = True
                ba.timer(5.0, ba.WeakCall(self.handlemessage,
                                          ba.ThawMessage()))
                # Instantly shatter if we're already dead.
                # (otherwise its hard to tell we're dead)
                if self.hitpoints <= 0:
                    self.shatter()

        elif isinstance(msg, ba.ThawMessage):
            if self.frozen and not self.shattered and self.node:
                self.frozen = False
                self.node.frozen = False

        elif isinstance(msg, ba.HitMessage):
            if not self.node:
                return None
            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

            # If we were recently hit, don't count this as another.
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
            assert isinstance(local_time, int)
            if (self._last_hit_time is None
                    or local_time - self._last_hit_time > 1000):
                self._num_times_hit += 1
                self._last_hit_time = local_time

            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            # If they've got a shield, deliver it to that instead.
            if self.shield:
                if msg.flat_damage:
                    damage = msg.flat_damage * self.impact_scale
                else:
                    # Hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse.
                    assert msg.force_direction is not None
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 1, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])
                    damage = damage_scale * self.node.damage

                assert self.shield_hitpoints is not None
                self.shield_hitpoints -= int(damage)
                self.shield.hurt = (
                        1.0 -
                        float(self.shield_hitpoints) / self.shield_hitpoints_max)

                # Its a cleaner event if a hit just kills the shield
                # without damaging the player.
                # However, massive damage events should still be able to
                # damage the player. This hopefully gives us a happy medium.
                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:

                    # FIXME: Transition out perhaps?
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,
                                 1.0,
                                 position=self.node.position)

                    # Emit some cool looking sparks when the shield dies.
                    npos = self.node.position
                    ba.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                              velocity=self.node.velocity,
                              count=random.randrange(20, 30),
                              scale=1.0,
                              spread=0.6,
                              chunk_type='spark')

                else:
                    ba.playsound(SpazFactory.get().shield_hit_sound,
                                 0.5,
                                 position=self.node.position)

                # Emit some cool looking sparks on shield hit.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                # If they passed our spillover threshold,
                # pass damage along to spaz.
                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    # Scale down the magnitudes applied to spaz accordingly.
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True  # Good job shield!
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                # Hit it with an impulse and get the resulting damage.
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                    msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                    velocity_mag, msg.radius, 0, msg.force_direction[0],
                    msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                if isinstance(self, PlayerSpaz):
                    srcname = self._player.getname(full=True)
                elif isinstance(self, SpazBot):
                    srcname = '机器人'
                else:
                    srcname = 'Null'
                self.on_punched(damage)

                if damage > 250 and damage <= 500 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='normal').autoretain()
                    chance = random.randrange(1, 7)
                    if chance >= 6:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 3)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 暴击!', msg.pos, msg.force_direction)
                elif damage > 500 and damage <= 750 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='sticky').autoretain()
                    chance = random.randrange(1, 7)
                    if chance >= 5:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 4)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并被短暂无敌!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.node.invincible = True
                            ba.timer(1.5, self.invout)
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 3:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage / 10)) + '% 粘性！', msg.pos, msg.force_direction)
                elif damage > 750 and damage <= 900 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 10000,
                          blast_type='impact').autoretain()
                    chance = random.randrange(1, 7)
                    if chance >= 5:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 2)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并复活了!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.hitpoints += self.hitpoints_max / 10
                            PopupText(
                                text='+' + str(int(self.hitpoints_max / 100)) + 'hp',
                                color=(0, 1, 0, 1),
                                scale=1,
                                position=self.node.position).autoretain()
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage/10)) + '% 脱落！', msg.pos, msg.force_direction)
                elif damage > 900 and damage < 1000 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=damage / 1000,
                          blast_type='tnt').autoretain()
                    chance = random.randrange(1, 7)
                    if chance >= 4:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        power = random.randrange(1, 3)
                        if power == 1:
                            PopupText(
                                text=srcname + ' 单走一个6并被短暂无敌!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.node.invincible = True
                            ba.timer(1.5, self.invout)
                        elif power == 2:
                            PopupText(
                                text=srcname + ' 单走一个6并获得护盾!',
                                color=(0.7, 0.7, 1.0, 1),
                                scale=1.6,
                                position=self.node.position).autoretain()
                            self.equip_shields()
                    ba.show_damage_count(str(int(damage/10)) + '% 脱落!', msg.pos, msg.force_direction)
                elif damage >= 1000 and self.hitpoints > 0:
                    Blast(position=self.node.position,
                          blast_radius=(damage / 5000),
                          blast_type='ice').autoretain()
                    chance = random.randrange(1, 7)
                    if chance >= 3:
                        ba.emitfx(position=self.node.position,
                                  scale=2.0, count=8, spread=1.2,
                                  chunk_type='spark')
                        PopupText(
                            text=srcname + ' 单走一个6并被短暂无敌!',
                            color=(0.7, 0.7, 1.0, 1),
                            scale=1.6,
                            position=self.node.position).autoretain()
                        self.node.invincible = True
                        ba.timer(1.5, self.invout)

                # Let's always add in a super-punch sound with boxing
                # gloves just to differentiate them.
                if msg.hit_subtype == 'super_punch':
                    ba.playsound(SpazFactory.get().punch_sound_stronger,
                                 1.0,
                                 position=self.node.position)
                if damage > 500:
                    sounds = SpazFactory.get().punch_sound_strong
                    sound = sounds[random.randrange(len(sounds))]
                else:
                    sound = SpazFactory.get().punch_sound
                ba.playsound(sound, 1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(damage * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                ba.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(damage * 0.04)),
                          scale=0.9,
                          spread=0.28)

                # Momentary flash.
                hurtiness = damage * 0.003
                punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                            msg.pos[1] + msg.force_direction[1] * 0.02,
                            msg.pos[2] + msg.force_direction[2] * 0.02)
                flash_color = (1.0, 0.8, 0.4)
                light = ba.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color
                    })
                ba.timer(0.06, light.delete)

                flash = ba.newnode('flash',
                                   attrs={
                                       'position': punchpos,
                                       'size': 0.17 + 0.17 * hurtiness,
                                       'color': flash_color
                                   })
                ba.timer(0.06, flash.delete)

            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)
            if self.hitpoints > 0:

                # It's kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount *if* it'll keep us alive
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    # Drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                # If we're cursed, *any* damage blows us up.
                if self._cursed and damage > 0:
                    ba.timer(
                        0.05,
                        ba.WeakCall(self.curse_explode,
                                    msg.get_source_player(ba.Player)))

                # If we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        ba.DieMessage(how=ba.DeathType.IMPACT))

            # If we're dead, take a look at the smoothed damage value
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough.
            if self.hitpoints <= 0:
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()

        elif isinstance(msg, BombDiedMessage):
            self.bomb_count += 1

        elif isinstance(msg, ba.DieMessage):
            wasdead = self._dead
            self._dead = True
            self.hitpoints = 0
            if msg.immediate:
                if self.node:
                    self.node.delete()
            elif self.node:
                self.node.hurt = 1.0
                if self.play_big_death_sound and not wasdead:
                    ba.playsound(SpazFactory.get().single_player_death_sound)
                self.node.dead = True
                ba.timer(2.0, self.node.delete)

        elif isinstance(msg, ba.OutOfBoundsMessage):
            # By default we just die here.
            self.handlemessage(ba.DieMessage(how=ba.DeathType.FALL))

        elif isinstance(msg, ba.StandMessage):
            self._last_stand_pos = (msg.position[0], msg.position[1],
                                    msg.position[2])
            if self.node:
                self.node.handlemessage('stand', msg.position[0],
                                        msg.position[1], msg.position[2],
                                        msg.angle)

        elif isinstance(msg, CurseExplodeMessage):
            self.curse_explode()

        elif isinstance(msg, PunchHitMessage):
            if not self.node:
                return None
            node = ba.getcollision().opposingnode

            # Only allow one hit per node per punch.
            if node and (node not in self._punched_nodes):

                punch_momentum_angular = (self.node.punch_momentum_angular *
                                          self._punch_power_scale)
                punch_power = self.node.punch_power * self._punch_power_scale

                # Ok here's the deal:  we pass along our base velocity for use
                # in the impulse damage calculations since that is a more
                # predictable value than our fist velocity, which is rather
                # erratic. However, we want to actually apply force in the
                # direction our fist is moving so it looks better. So we still
                # pass that along as a direction. Perhaps a time-averaged
                # fist-velocity would work too?.. perhaps should try that.

                # If its something besides another spaz, just do a muffled
                # punch sound.
                if node.getnodetype() != 'spaz':
                    sounds = SpazFactory.get().impact_sounds_medium
                    sound = sounds[random.randrange(len(sounds))]
                    ba.playsound(sound, 1.0, position=self.node.position)

                ppos = self.node.punch_position
                punchdir = self.node.punch_velocity
                vel = self.node.punch_momentum_linear

                self._punched_nodes.add(node)
                node.handlemessage(
                    ba.HitMessage(
                        pos=ppos,
                        velocity=vel,
                        magnitude=punch_power * punch_momentum_angular * 110.0,
                        velocity_magnitude=punch_power * 40,
                        radius=0,
                        srcnode=self.node,
                        source_player=self.source_player,
                        force_direction=punchdir,
                        hit_type='punch',
                        hit_subtype=('super_punch' if self._has_boxing_gloves
                                     else 'default')))

                # Also apply opposite to ourself for the first punch only.
                # This is given as a constant force so that it is more
                # noticeable for slower punches where it matters. For fast
                # awesome looking punches its ok if we punch 'through'
                # the target.
                mag = -400.0
                if self._hockey:
                    mag *= 0.5
                if len(self._punched_nodes) == 1:
                    self.node.handlemessage('kick_back', ppos[0], ppos[1],
                                            ppos[2], punchdir[0], punchdir[1],
                                            punchdir[2], mag)
        elif isinstance(msg, PickupMessage):
            if not self.node:
                return None

            try:
                collision = ba.getcollision()
                opposingnode = collision.opposingnode
                opposingbody = collision.opposingbody
            except ba.NotFoundError:
                return True

            # Don't allow picking up of invincible dudes.
            try:
                if opposingnode.invincible:
                    return True
            except Exception:
                pass

            # If we're grabbing the pelvis of a non-shattered spaz, we wanna
            # grab the torso instead.
            if (opposingnode.getnodetype() == 'spaz'
                    and not opposingnode.shattered and opposingbody == 4):
                opposingbody = 1

            # Special case - if we're holding a flag, don't replace it
            # (hmm - should make this customizable or more low level).
            held = self.node.hold_node
            if held and held.getnodetype() == 'flag':
                return True

            # Note: hold_body needs to be set before hold_node.
            self.node.hold_body = opposingbody
            self.node.hold_node = opposingnode
        elif isinstance(msg, ba.CelebrateMessage):
            if self.node:
                self.node.handlemessage('celebrate', int(msg.duration * 1000))

        else:
            """return super().new_handlemessage(msg)"""
        return None

    Spaz.handlemessage = new_handlemessage
    Spaz.invout = invout

# ba_meta export game
class CoopPaP(ba.CoopGameActivity[Player, Team]):
    """Slow motion how-long-can-you-last game."""

    name = '炸弹拳'
    description = '你的拳头就是炸弹！\n 最后活着的获胜'
    tips = [
        '祝你好运！汉化by炸队汉化组'
    ]

    # Show messages when players die since it matters here.
    announce_player_deaths = True

    # And of course the most important part.
    slow_motion = True

    default_music = ba.MusicType.EPIC

    def __init__(self, settings: dict):
        self.hdisply = None
        settings['map'] = 'Lake Frigid'
        super().__init__(settings)
        self._new_wave_sound = ba.getsound('scoreHit01')
        self._winsound = ba.getsound('score')
        self._cashregistersound = ba.getsound('cashRegister')
        self._spawn_center = (0, 0, 0)
        self._preset = str(settings.get('preset', 'default'))
        self._scoreboard: Scoreboard | None = None
        self._score = 0
        self._bots = SpazBotSet()
        self._dingsound = ba.getsound('dingSmall')
        self._dingsoundhigh = ba.getsound('dingSmallHigh')
        self._bot_update_interval: float | None = None
        self._bot_update_timer: ba.Timer | None = None
        self._allphp = 0
        self._initialallphp = 0

        # For each bot type: [spawnrate, increase, d_increase]
        self._bot_spawn_types = {
            BomberBot:              SpawnInfo(1.00, 0.00, 0.000),
            BomberBotPro:           SpawnInfo(0.00, 0.05, 0.001),
            BomberBotProShielded:   SpawnInfo(0.00, 0.02, 0.002),
            BrawlerBot:             SpawnInfo(1.00, 0.00, 0.000),
            BrawlerBotPro:          SpawnInfo(0.00, 0.05, 0.001),
            BrawlerBotProShielded:  SpawnInfo(0.00, 0.02, 0.002),
            TriggerBot:             SpawnInfo(0.30, 0.00, 0.000),
            TriggerBotPro:          SpawnInfo(0.00, 0.05, 0.001),
            TriggerBotProShielded:  SpawnInfo(0.00, 0.02, 0.002),
            ChargerBot:             SpawnInfo(0.30, 0.05, 0.000),
            StickyBot:              SpawnInfo(0.10, 0.03, 0.001),
            ExplodeyBot:            SpawnInfo(0.05, 0.02, 0.002)
        }  # yapf: disable

    def on_transition_in(self) -> None:
        super().on_transition_in()
        ba.timer(1.3, ba.Call(ba.playsound, self._new_wave_sound))
        self._scoreboard = Scoreboard(label=ba.Lstr(resource='scoreText'),
                                      score_split=0.5)

    def spoints(self) -> None:
        self._score += 1
        self._update_scores()
        ba.timer(1, self.spoints)

    def maketp(self) -> None:
        self._allphp = 0
        for player in self.players:
            self._allphp += (player.actor.hitpoints / 10)
        self._initialallphp = self._allphp
        self.hdisply = ba.newnode('text',
                                  attrs={
                                      'v_attach': 'top',
                                      'h_attach': 'center',
                                      'h_align': 'center',
                                      'color': (0, 1, 0, 1),
                                      'flatness': 0.5,
                                      'shadow': 0.5,
                                      'position': (0, -70),
                                      'scale': 1.4,
                                      'text': str(int(self._allphp)) + 'HP'
                                  })

    def updatetp(self) -> None:
        self._allphp = 0
        for player in self.players:
            self._allphp += (player.actor.hitpoints / 10)
        setattr(self.hdisply, 'text', str(int(self._allphp)) + 'HP')
        if self._allphp == 0:
            setattr(self.hdisply, 'text', 'GAME OVER')
            setattr(self.hdisply, 'color', (1, 0, 0, 1))
        elif (self._initialallphp/4) >= self._allphp >= 0:
            setattr(self.hdisply, 'color', (0.75, 0.25, 0, 1))
        elif ((self._initialallphp / 4) * 2) >= self._allphp >= (self._initialallphp / 4):
            setattr(self.hdisply, 'color', (0.5, 0.5, 0, 1))
        elif ((self._initialallphp / 4) * 3) >= self._allphp >= ((self._initialallphp / 4)*2):
            setattr(self.hdisply, 'color', (0.25, 0.75, 0, 1))
        elif ((self._initialallphp / 4) * 4) >= self._allphp >= ((self._initialallphp / 4)*3):
            setattr(self.hdisply, 'color', (0, 1, 0, 1))

    def on_begin(self) -> None:
        super().on_begin()

        ba.timer(0.001, ba.WeakCall(self._start_bot_updates))
        ba.timer(2, self.spoints)
        self.maketp()
        self.setup_low_life_warning_sound()
        self._update_scores()

    def on_player_leave(self, sessionplayer: _ba.SessionPlayer) -> None:
        super().on_player_leave(sessionplayer)
        self.updatetp()

    def spawn_player(self, player: Player) -> ba.Actor:
        if isinstance(self.session, ba.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            # otherwise do free-for-all spawn locations
            position = self.map.get_ffa_start_position(self.players)
        angle = None

        name = player.getname()
        light_color = _math.normalized_color(player.color)
        display_color = _ba.safecolor(player.color, target_intensity=0.75)

        spaz = spazpunch(color=player.color,
                         highlight=player.highlight,
                         character=player.character,
                         player=player)

        player.actor = spaz
        assert spaz.node

        # If this is co-op and we're on Courtyard or Runaround, add the
        # material that allows us to collide with the player-walls.
        # FIXME: Need to generalize this.
        if isinstance(self.session, ba.CoopSession) and self.map.getname() in [
            'Courtyard', 'Tower D'
        ]:
            mat = self.map.preloaddata['collide_with_wall_material']
            assert isinstance(spaz.node.materials, tuple)
            assert isinstance(spaz.node.roller_materials, tuple)
            spaz.node.materials += (mat,)
            spaz.node.roller_materials += (mat,)

        spaz.node.name = name
        spaz.node.name_color = display_color
        spaz.connect_controls_to_player(enable_bomb=False)

        # Move to the stand position and add a flash of light.
        spaz.handlemessage(
            ba.StandMessage(
                position,
                angle if angle is not None else random.uniform(0, 360)))
        _ba.playsound(self._spawn_sound, 1, position=spaz.node.position)
        light = _ba.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        ba.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        _ba.timer(0.5, light.delete)

        spaz.hitpoints_max = 10000
        spaz.hitpoints = 10000
        spaz.equip_boxing_gloves()

        return spaz

    def _start_bot_updates(self) -> None:
        self._bot_update_interval = 3.3 - 0.3 * (len(self.players))
        self._update_bots()
        self._update_bots()
        if len(self.players) > 2:
            self._update_bots()
        if len(self.players) > 3:
            self._update_bots()
        self._bot_update_timer = ba.Timer(self._bot_update_interval,
                                          ba.WeakCall(self._update_bots))

    def do_end(self, outcome: str) -> None:
        """End the game."""
        if outcome == 'defeat':
            self.fade_to_red()
        self.end(delay=2.0,
                 results={
                     'outcome': outcome,
                     'score': self._score,
                     'playerinfos': self.initialplayerinfos
                 })

    def _update_bots(self) -> None:
        assert self._bot_update_interval is not None
        self._bot_update_interval = max(0.5, self._bot_update_interval * 0.98)
        self._bot_update_timer = ba.Timer(self._bot_update_interval,
                                          ba.WeakCall(self._update_bots))
        botspawnpts: list[Sequence[float]] = [[-7, 2, -5],
                                              [0, 2, -5],
                                              [7, 2, -5],
                                              [-9, 2, 0],
                                              [9, 2, 0],
                                              [-7, 2, 5],
                                              [0, 2, 5],
                                              [7, 2, 5]]
        dists = [0.0, 0.0, 0.0]
        playerpts: list[Sequence[float]] = []
        for player in self.players:
            try:
                if player.is_alive():
                    assert isinstance(player.actor, PlayerSpaz)
                    assert player.actor.node
                    playerpts.append(player.actor.node.position)
            except Exception:
                ba.print_exception('Error updating bots.')
        for i in range(3):
            for playerpt in playerpts:
                dists[i] += abs(playerpt[0] - botspawnpts[i][0])
            dists[i] += random.random() * 5.0  # Minor random variation.
        if dists[0] > dists[1] and dists[0] > dists[2]:
            spawnpt = botspawnpts[0]
        elif dists[1] > dists[2]:
            spawnpt = botspawnpts[1]
        else:
            spawnpt = botspawnpts[2]

        spawnpt = (spawnpt[0] + 2.0 * (random.random() - 0.5), spawnpt[1],
                   spawnpt[2] + 2.0 * (random.random() - 0.5))

        # Normalize our bot type total and find a random number within that.
        total = 0.0
        for spawninfo in self._bot_spawn_types.values():
            total += spawninfo.spawnrate
        randval = random.random() * total

        # Now go back through and see where this value falls.
        total = 0
        bottype: type[SpazBot] | None = None
        for spawntype, spawninfo in self._bot_spawn_types.items():
            total += spawninfo.spawnrate
            if randval <= total:
                bottype = spawntype
                break
        spawn_time = 1.0
        assert bottype is not None
        self._bots.spawn_bot(bottype, pos=spawnpt, spawn_time=spawn_time)

        # After every spawn we adjust our ratios slightly to get more
        # difficult.
        for spawninfo in self._bot_spawn_types.values():
            spawninfo.spawnrate += spawninfo.increase
            spawninfo.increase += spawninfo.dincrease

    def _update_scores(self) -> None:
        score = self._score

        assert self._scoreboard is not None
        self._scoreboard.set_team_value(self.teams[0], score, max_score=None)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            player = msg.getplayer(Player)
            self.stats.player_was_killed(player)
            ba.timer(0.1, self._checkroundover)
            self.updatetp()

        elif isinstance(msg, ba.PlayerScoredMessage):
            self._score += msg.score
            self._update_scores()

        elif isinstance(msg, SpazBotDiedMessage):
            pts, importance = msg.spazbot.get_death_points(msg.how)
            target: Sequence[float] | None
            if msg.killerplayer:
                assert msg.spazbot.node
                target = msg.spazbot.node.position
                self.stats.player_scored(msg.killerplayer,
                                         pts,
                                         target=target,
                                         kill=True,
                                         screenmessage=False,
                                         importance=importance)
                ba.playsound(self._dingsound
                             if importance == 1 else self._dingsoundhigh,
                             volume=0.6)

            # Normally we pull scores from the score-set, but if there's no
            # player lets be explicit.
            else:
                self._score += pts
            self._update_scores()
        elif isinstance(msg, PlayerSpazHurtMessage):
            self.updatetp()
        else:
            super().handlemessage(msg)

    def _on_got_scores_to_beat(self, scores: list[dict[str, Any]]) -> None:
        self._show_standard_scores_to_beat_ui(scores)

    def end_game(self) -> None:
        # Tell our bots to celebrate just to rub it in.
        self._bots.final_celebrate()
        ba.setmusic(None)
        ba.pushcall(ba.WeakCall(self.do_end, 'defeat'))

    def _checkroundover(self) -> None:
        """End the round if conditions are met."""
        if not any(player.is_alive() for player in self.teams[0].players):
            self.end_game()

# ba_meta export plugin
class Survival(ba.Plugin):
    """Plugin which simply adds a coop level using our custom game."""
    def on_app_running(self) -> None:
        ba.app.add_coop_practice_level(
            ba.Level(name='炸弹拳',
                     displayname='${GAME}',
                     gametype=CoopPaP,
                     settings={},
                     preview_texture_name='lakeFrigidPreview'))