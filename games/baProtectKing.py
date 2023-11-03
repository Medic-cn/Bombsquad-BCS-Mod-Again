# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba, _ba, random

from bastd.actor.scoreboard import Scoreboard
from bastd.actor.spazfactory import SpazFactory
from bastd.game.elimination import Icon
from bastd.actor.powerupbox import PowerupBox, PowerupBoxFactory
from bastd.actor import playerspaz

PlayerSpaz = playerspaz.PlayerSpaz

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional

def petage(a: float, b: float, c: int = 2):
    try: value = round(100 * a / b, c)
    except: value = 0
    return value

def getlanguage(text, subs: str = ''):
    lang = _ba.app.lang.language
    translate = {"Name":
                      {"Spanish": "Protege al Rey",
                       "Chinese": "保护国王",
                       "English": "Protect King",
                       "Portuguese": "Proteja o Rei"},
                 "Info":
                      {"Chinese": "击败对面的国王，记得保护自己的国王",
                       "Spanish": "Derrota al Rey del equipo rival.",
                       "English": "Defeat the King of the opposing team.",
                       "Portuguese": "Derrotar o Rei da equipe adversária."},
                 "S: Powerups":
                      {"Chinese": "禁用道具",
                       "Spanish": "Aparecer Potenciadores",
                       "English": "Powerups Spawn",
                       "Portuguese": "Habilitar Potenciadores"}}
                
    languages = ['Spanish','Portuguese','English','Chinese']
    lang = "Chinese"

    if text not in translate:
        return text
    return translate[text][lang]

class Player(ba.Player['Team']):
    """Our player type for this game."""
    icons: List[Icon] = []

class Team(ba.Team[Player]):
    """Our team type for this game."""
    hp: int = 100
    score: int = 0
    king: Player = None

class Icon(Icon):
    def __init__(self, *args, **kwargs):
        self._lives_text = None
        super().__init__(*args, **kwargs)
        if kwargs.get('show_lives', None):
            self._lives_text.text = '100%'
            self._lives_text.opacity = 0.8
            
    def update_percentage(self, pct: int):
        if self._lives_text:
            self._lives_text.text = str(pct) + '%好果汁'
  
    def handle_player_spawned(self) -> None:
        """Our player spawned; hooray!"""
        if not self.node: return
        self.node.opacity = 1.0

class Scoreboard(Scoreboard):
    def __init__(self, label: ba.Lstr = None, score_split: float = 0.7):
        super().__init__(label, score_split)
        self._scale = 1.3
        self._pos = (450.0, -70.0)
        self.v_entries: list = []
        
    def set_team_value(self,
                       team: ba.Team,
                       score: float,
                       max_score: float = None,
                       countdown: bool = False,
                       flash: bool = True,
                       show_value: bool = True) -> None:
        super().set_team_value(team, score, max_score, countdown, flash, show_value)
        cls_team = self._entries[team.id]
        bar = cls_team._score_text.node
        bar.scale = cls_team._scale * 0.9 + 0.4
        bar.text += '%'
        
    def _update_teams(self) -> None:
        pos = list(self._pos)
        self.v_entries = list(self._entries.values())
        for entry in self.v_entries:
            entry.set_position(pos)
            tpos = entry._score_text.node.position
            entry._cover.node.opacity = 0
            entry._score_text.node.position = (tpos[0] - 50, tpos[1])
            pos[0] -= self._spacing * self._scale - 300


class OldPlayerSpaz(PlayerSpaz):
    pass

class PkPlayerSpaz(PlayerSpaz):
    king: bool = False
    king_shield: ba.Node = None

    def has_king(myclass):
        myclass.king = True
        if myclass.king_shield is None:
            myclass.king_shield = ba.newnode('shield', owner=myclass.node, attrs={'color': (1.2, 1.2, 1.2), 'radius': 1.75})
            myclass.node.connectattr('position_center', myclass.king_shield, 'position')
        
    def validate_king(self, player: Player) -> bool:
        act = self._activity()
        for team in act.teams:
            if team.king is player:
                return True
        return False
        
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.OutOfBoundsMessage):
            assert self._activity()
            if self.king:
                a = self._activity()
                team = self._player.team
                if team.id == 0:
                    position = a.map.defs.points['spawn1']
                else: position = a.map.defs.points['spawn2']
                self.handlemessage(ba.StandMessage(position))
            else: return super().handlemessage(msg)
        elif isinstance(msg, ba.PowerupMessage):
            if not self.king:
                return super().handlemessage(msg)
            else:
                if 'bomb' in msg.poweruptype:
                    return super().handlemessage(msg)
        elif isinstance(msg, ba.DieMessage):
            super().handlemessage(msg)
            if self.king:
                ba.timer(0.5, self._activity().end_game)
        elif isinstance(msg, ba.FreezeMessage):
            if not self.king:
                return super().handlemessage(msg)
        elif isinstance(msg, ba.HitMessage):
            if not self.node:
                return None

            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

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
                    assert msg.force_direction is not None
                    if not self.king:
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

                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:

                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,
                                 1.0,
                                 position=self.node.position)

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

                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                    msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                    velocity_mag, msg.radius, 0, msg.force_direction[0],
                    msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)

                player = (msg.srcnode.source_player if msg.srcnode
                          else msg.get_source_player(ba.Player))
                if self.validate_king(player):
                    if self._player is not player:
                        damage = int(damage * 1.50)
                
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                self.on_punched(damage)

                # If damage was significant, lets show it.
                if damage > 350:
                    assert msg.force_direction is not None
                    ba.show_damage_count('-' + str(int(damage / 10)) + '%',
                                         msg.pos, msg.force_direction)

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
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                if self._cursed and damage > 0:
                    ba.timer(
                        0.05,
                        ba.WeakCall(self.curse_explode,
                                    msg.get_source_player(ba.Player)))

                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        ba.DieMessage(how=ba.DeathType.IMPACT))

            if self.hitpoints <= 0:
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()
            self._activity()._update_scoreboard()
        else:
           return super().handlemessage(msg)
        
# ba_meta export game
class PTKGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = getlanguage('Name')
    description = getlanguage('Info')

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
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
            ba.BoolSetting('Epic Mode', default=False),
            ba.BoolSetting(getlanguage('S: Powerups'), default=False),
        ]

        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return issubclass(sessiontype, ba.DualTeamSession)

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        maps = ba.getmaps('melee')
        maps.remove('Happy Thoughts')
        maps.append('Tower D')
        return maps

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard('')
        self._score_to_win: Optional[int] = None
        self._epic_mode = bool(settings['Epic Mode'])
        self._time_limit = float(settings['Time Limit'])
        
        #New settings
        self._enable_powerups = bool(
            settings[getlanguage('S: Powerups')])
            
        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.SURVIVAL)

    def get_instance_description(self) -> Union[str, Sequence]:
        return getlanguage('Info')

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return getlanguage('Info')

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def spawn_player(self, player: Player) -> ba.Actor:
        playerspaz.PlayerSpaz = PkPlayerSpaz
        spaz = self.spawn_player_spaz(player)
        playerspaz.PlayerSpaz = OldPlayerSpaz
        return spaz

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        
        if self._enable_powerups:
            self.setup_standard_powerup_drops()
        
        for team in self.teams:
            if len(team.players) > 0:
                player = team.king = random.choice(team.players)
                player.actor.has_king()
                player.actor.hitpoints += 23000
                player.actor.hitpoints_max = player.actor.hitpoints
                player.icons = [Icon(player, position=(0, 50), scale=0.8, show_lives=True)]
            else: ba.timer(1.0, self.end_game)

        ba.timer(0.01, self._update_icons)
        self._update_scoreboard()

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            if player.team.king is not player:
                self.respawn_player(player)
        else: return super().handlemessage(msg)
        
    def team_points(self, team: Team, score: int):
        for tm in self.teams:
            if tm is not team:
                tm.score = score
        
    def _update_scoreboard(self) -> None:
        for team in self.teams:
            res = 100
            if team.king is not None:
                actor = team.king.actor
                if actor.node:
                    hp = actor.hitpoints
                    hp_max = actor.hitpoints_max
                    res = int(petage(hp, hp_max))
                    res = (max(res, 1) if hp > 0 else 0)
                    for icon in team.king.icons:
                        icon.update_percentage(res)
            self.team_points(team, (100 - res))
            self._scoreboard.set_team_value(team, res, 100)

    def _standard_drop_powerup(self, index: int, expire: bool = True) -> None:
        # pylint: disable=cyclic-import
        powerups_banned = ['punch']

        get_powerup_type = PowerupBoxFactory.get(
            ).get_random_powerup_type(excludetypes=powerups_banned)
        
        PowerupBox(
            position=self.map.powerup_spawn_points[index],
            poweruptype=get_powerup_type,
            expire=expire).autoretain()

    def _update_icons(self) -> None:
        for team in self.teams:
            if team.id == 0:
                xval = -50
                x_offs = -85
            else:
                xval = 50
                x_offs = 85
                
            if team.king is None:
                continue

            for icon in team.king.icons:
                icon.set_position_and_scale((xval*1.4, 50), 1.1)
                xval += x_offs

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)