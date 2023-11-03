# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)
#进口by炸队汉化组
#QQ群161073376
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import json
import random
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.game.elimination import Icon

if TYPE_CHECKING:
    from typing import Any, Sequence


lang = ba.app.lang.language


name = '单挑'
enable_powerups = '启用拳套'



class Player(ba.Player['Team']):
    """Our player type for this game."""
    def __init__(self) -> None:
        self.icons: List[Icon] = []
        self.in_game: bool = False
        self.playervs1: bool = False
        self.playervs2: bool = False


class Team(ba.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


# ba_meta export game
class DuelClassicGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = name
    description = 'Kill a set number of enemies to win.'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @classmethod
    def get_available_settings(
            cls, sessiontype: type[ba.Session]) -> list[ba.Setting]:
        settings = [
            ba.IntSetting(
                'Kills to Win Per Player',
                min_value=1,
                default=5,
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
            ba.BoolSetting(enable_powerups, default=True),
            ba.BoolSetting('Epic Mode', default=False),
            ba.BoolSetting('Allow Negative Scores', default=False),
        ]
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: type[ba.Session]) -> List[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: int | None = None
        self._vs_text: ba.Actor | None = None
        self.spawn_order: list[Player] = []
        self._dingsound = ba.getsound('dingSmall')
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False))
        self._players_vs_1: bool = False
        self._players_vs_2: bool = False
        self._count_1 = ba.getsound('announceOne')
        self._count_2 = ba.getsound('announceTwo')
        self._count_3 = ba.getsound('announceThree')
        self._boxing_bell = ba.getsound('boxingBell')
        self._epic_mode = bool(settings['Epic Mode'])
        self._kills_to_win_per_player = int(
            settings['Kills to Win Per Player'])
        self._enable_powerups = bool(settings[enable_powerups])

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.TO_THE_DEATH)

    def get_instance_description(self) -> str | Sequence:
        return 'Crush ${ARG1} of your enemies.', self._score_to_win

    def get_instance_description_short(self) -> str | Sequence:
        return 'kill ${ARG1} enemies', self._score_to_win

    def on_player_join(self, player: Player) -> None:
        self.spawn_order.append(player)
        self._update_order()

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
        player.icons = []
        if player.playervs1:
            player.playervs1 = False
            self._players_vs_1 = False
            player.in_game = False
        elif player.playervs2:
            player.playervs2 = False
            self._players_vs_2 = False
            player.in_game = False
        if player in self.spawn_order:
            self.spawn_order.remove(player)
        self._update_order()

    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        if self._enable_powerups:
            self.setup_standard_powerup_drops()
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

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = (self._kills_to_win_per_player *
                              max(1, max(len(t.players) for t in self.teams)))
        self._update_scoreboard()

    def spawn_player(self, player: PlayerType) -> ba.Actor:
        spaz = self.spawn_player_spaz(player, self._get_spawn_point(player))
        spaz.equip_boxing_gloves()
        return spaz

    def _update_spawn(self, player: Player) -> None:
        if self._players_vs_1 and self._players_vs_2:
            if not player.is_alive():
                self.spawn_player(player)
        else:
            if not player.is_alive():
                self.spawn_player(player)

    def _get_spawn_point(self, player: Player) -> ba.Vec3 | None:
        del player  # Unused.

        # In solo-mode, if there's an existing live player on the map, spawn at
        # whichever spot is farthest from them (keeps the action spread out).
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

    def _update_order(self) -> None:
        for player in self.spawn_order:
            assert isinstance(player, Player)
            if not player.is_alive():
                if not self._players_vs_1:
                    self._players_vs_1 = True
                    player.playervs1 = True
                    player.in_game = True
                    self.spawn_order.remove(player)
                    self._update_spawn(player)
                elif not self._players_vs_2:
                    self._players_vs_2 = True
                    player.playervs2 = True
                    player.in_game = True
                    self.spawn_order.remove(player)
                    self._update_spawn(player)
                self._update_icons()

    def _update_icons(self) -> None:
        # pylint: disable=too-many-branches

        for player in self.players:
            player.icons = []

            if player.in_game:
                if player.playervs1:
                    xval = -60
                    x_offs = -78
                elif player.playervs2:
                    xval = 60
                    x_offs = 78
                player.icons.append(
                    Icon(player,
                         position=(xval, 40),
                         scale=1.0,
                         name_maxwidth=130,
                         name_scale=0.8,
                         flatness=0.0,
                         shadow=0.5,
                         show_death=True,
                         show_lives=False))
            else:
                xval = 125
                xval2 = -125
                x_offs = 78
                for player in self.spawn_order:
                    player.icons.append(
                        Icon(player,
                             position=(xval, 25),
                             scale=0.5,
                             name_maxwidth=75,
                             name_scale=1.0,
                             flatness=1.0,
                             shadow=1.0,
                             show_death=False,
                             show_lives=False))
                    xval += x_offs * 0.56
                    player.icons.append(
                        Icon(player,
                             position=(xval2, 25),
                             scale=0.5,
                             name_maxwidth=75,
                             name_scale=1.0,
                             flatness=1.0,
                             shadow=1.0,
                             show_death=False,
                             show_lives=False))
                    xval2 -= x_offs * 0.56

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)

            if player.playervs1:
                player.playervs1 = False
                self._players_vs_1 = False
                player.in_game = False
                self.spawn_order.append(player)
            elif player.playervs2:
                player.playervs2 = False
                self._players_vs_2 = False
                player.in_game = False
                self.spawn_order.append(player)
            ba.timer(0.1, self._update_order)

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

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
