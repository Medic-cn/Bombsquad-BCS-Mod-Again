# Released under the MIT License. See LICENSE for details.
#
"""Implements football games (both co-op and teams varieties)."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import random
from bastd.actor.spaz import Spaz
from bastd.game.hockey import PuckDiedMessage, Player, Team, HockeyGame
from bastd.gameutils import SharedObjects
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage
from bastd.actor.spazfactory import SpazFactory

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class NewPlayerSpaz(PlayerSpaz):
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.HitMessage):
            source_player = msg.get_source_player(type(self._player))
            if source_player:
                self.last_player_attacked_by = source_player
                self.last_attacked_time = ba.time()
                self.last_attacked_type = (msg.hit_type, msg.hit_subtype)

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
                if msg.hit_type != 'punch':
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 0, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                if self.node.hold_node:
                    self.node.hold_node = None
                damage = 0
                sound = SpazFactory.get().punch_sound
                ba.playsound(sound, 1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(100 * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                ba.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(100 * 0.04)),
                          scale=0.9,
                          spread=0.28)

                # Momentary flash.
                hurtiness = 100 * 0.003
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

            activity = self._activity()
            if activity is not None and self._player.exists():
                activity.handlemessage(PlayerSpazHurtMessage(self))
        else:
            super().handlemessage(msg)

class Puck(ba.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, SoccerGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': ba.getmodel('frostyPelvis'),
                                   'color_texture':
                                        ba.gettexture('achievementSuperPunch'),
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        ba.animate(self.node, 'model_scale', {0: 0, 0.2: 1.2, 0.26: 1.0})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, ba.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, ba.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            # If this hit came from a player, log them as the last to touch us.
            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = self._activity()
                if activity:
                    if s_player in activity.players:
                        self.last_players_to_touch[s_player.team.id] = s_player
        else:
            super().handlemessage(msg)


# ba_meta export game
class SoccerGame(HockeyGame):
    """Football game for teams mode."""

    name = '足球'
    description = 'MOD: oore282；汉化byMedic'
    available_settings = [
        ba.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
            increment=1,
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
        ba.BoolSetting('Boxing Gloves', default=False),
        ba.BoolSetting('Enable Powerups', default=True),
        ba.BoolSetting('Ice Floor', default=True),
        ba.BoolSetting('Hit Players', default=False),
        ba.BoolSetting('Epic Mode', default=False),
    ]

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('hockey')

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = ba.getsound('cheer')
        self._chant_sound = ba.getsound('crowdChant')
        self._foghorn_sound = ba.getsound('foghorn')
        self._swipsound = ba.getsound('swip')
        self._whistle_sound = ba.getsound('refWhistle')
        self._boxing_gloves = bool(settings.get('Boxing Gloves', False))
        self._enable_powerups = bool(settings.get('Enable Powerups', True))
        self._ice_floor = bool(settings.get('Ice Floor', True))
        self._hit_players = bool(settings['Hit Players'])
        self._epic_mode = bool(settings['Epic Mode'])
        # Base class overrides:
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC
                              if self._epic_mode else ba.MusicType.FOOTBALL)
        self.puck_material = ba.Material()
        self.puck_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 0.5)))
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', False))
        self.puck_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )

        # Keep track of which player last touched the puck
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=('call', 'at_connect', self._handle_puck_player_collide))

        # We want the puck to kill powerups; not get stopped by them
        self.puck_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', ba.DieMessage())))
        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

    def on_transition_in(self) -> None:
        super().on_transition_in()
        shared = SharedObjects.get()
        activity = ba.getactivity()
        if self._ice_floor:
            activity.map.is_hockey = True
        else:
            activity.map.is_hockey = False
        activity.map.node.materials = [shared.footing_material]
        activity.map.floor.materials = [shared.footing_material]
        activity.map.floor.color = (0.2, 1.0, 0.2)

    def on_begin(self) -> None:
        self.setup_standard_time_limit(self._time_limit)
        if self._enable_powerups:
            self.setup_standard_powerup_drops()
        else:
            pass
        self._puck_spawn_pos = self.map.get_flag_position(None)
        self._spawn_puck()

        # Set up the two score regions.
        defs = self.map.defs
        self._score_regions = []
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': defs.boxes['goal1'][0:3],
                               'scale': defs.boxes['goal1'][6:9],
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': defs.boxes['goal2'][0:3],
                               'scale': defs.boxes['goal2'][6:9],
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))
        self._update_scoreboard()
        ba.playsound(self._chant_sound)

    def spawn_player(self, player: Player) -> ba.Actor:
        from ba import _math
        from ba._gameutils import animate
        from ba._coopsession import CoopSession

        if isinstance(self.session, ba.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            # otherwise do free-for-all spawn locations
            position = self.map.get_ffa_start_position(self.players)
        angle = None

        name = player.getname()
        color = player.color
        highlight = player.highlight

        light_color = _math.normalized_color(color)
        display_color = ba.safecolor(color, target_intensity=0.75)

        if self._hit_players:
            spaz = PlayerSpaz(color=color,
                              highlight=highlight,
                              character=player.character,
                              player=player)
        else:
            spaz = NewPlayerSpaz(color=color,
                                  highlight=highlight,
                                  character=player.character,
                                  player=player)

        player.actor = spaz
        assert spaz.node

        # If this is co-op and we're on Courtyard or Runaround, add the
        # material that allows us to collide with the player-walls.
        # FIXME: Need to generalize this.
        if isinstance(self.session, CoopSession) and self.map.getname() in [
                'Courtyard', 'Tower D'
        ]:
            mat = self.map.preloaddata['collide_with_wall_material']
            assert isinstance(spaz.node.materials, tuple)
            assert isinstance(spaz.node.roller_materials, tuple)
            spaz.node.materials += (mat, )
            spaz.node.roller_materials += (mat, )

        spaz.node.name = name
        spaz.node.name_color = display_color
        spaz.connect_controls_to_player()

        if self._boxing_gloves:
            spaz.equip_boxing_gloves()

        # Move to the stand position and add a flash of light.
        spaz.handlemessage(
            ba.StandMessage(
                position,
                angle if angle is not None else random.uniform(0, 360)))
        ba.playsound(self._spawn_sound, 1, position=spaz.node.position)
        light = ba.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        ba.timer(0.5, light.delete)
        return spaz

    def _spawn_puck(self) -> None:
        ba.playsound(self._swipsound)
        ba.playsound(self._whistle_sound)
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)
