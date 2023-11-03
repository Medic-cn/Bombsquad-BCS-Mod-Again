# Made by MattZ45986 on GitHub
# Ported by: Freaku / @[Just] Freak#4999
#汉化：炸队汉化组 QQ群161073376 联系邮箱：cntsl@inker.ga
#发行/修补/资源收录：药服技术社 QQ群527575487 联系邮箱：ink@inker.ga(技术支持) mod@inker.ga（投稿mod）

# Bug Fixes & Improvements as well...

# Join BCS:
# https://discord.gg/ucyaesh


from __future__ import annotations
from typing import TYPE_CHECKING
import _ba
import ba
import random
import math
from bastd.actor.flag import Flag, FlagPickedUpMessage
from bastd.actor.playerspaz import PlayerSpaz
if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional


class Player(ba.Player['Team']):
    def __init__(self) -> None:
        self.done: bool = False
        self.survived: bool = True


class Team(ba.Team[Player]):
    def __init__(self) -> None:
        self.score = 0


# ba_meta require api 7
# ba_meta export game
class MFGame(ba.TeamGameActivity[Player, Team]):
    name = '旗子争夺战'
    description = "抢旗子！！！\n抢不到的就被淘汰！！！!"

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
            ba.BoolSetting('Epic Mode', default=False),
            ba.BoolSetting('允许跑', default=True),
            ba.BoolSetting('允许打', default=False),
            ba.BoolSetting('底部署名', True)
        ]
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Doom Shroom']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.nodes = []
        self._dingsound = ba.getsound('dingSmall')
        self._epic_mode = bool(settings['Epic Mode'])
        self.credit_text = bool(settings['底部署名'])
        self._time_limit = float(settings['Time Limit'])
        self.is_punch = bool(settings['允许打'])
        self.is_run = bool(settings['允许跑'])

        self._textRound = ba.newnode('text',
                                     attrs={'text': '',
                                            'position': (0, -38),
                                            'scale': 1,
                                            'shadow': 1.0,
                                            'flatness': 1.0,
                                            'color': (1.0, 0.0, 1.0),
                                            'opacity': 1,
                                            'v_attach': 'top',
                                            'h_attach': 'center',
                                            'h_align': 'center',
                                            'v_align': 'center'})

        self.slow_motion = self._epic_mode
        # A cool music, matching our gamemode theme
        self.default_music = ba.MusicType.FLAG_CATCHER

    def get_instance_description(self) -> Union[str, Sequence]:
        return '抢旗子！！！\n抢不到的就被淘汰！！！!'

    def get_instance_description_short(self) -> Union[str, Sequence]:
        return '抢旗子！！！\n抢不到的就被淘汰！！！!'

    def on_player_join(self, player: Player) -> None:
        if self.has_begun():
            ba.screenmessage(
                ba.Lstr(resource='playerDelayedJoinText',
                        subs=[('${PLAYER}', player.getname(full=True))]),
                color=(0, 1, 0), transient=True)
            player.survived = False
            return
        self.spawn_player(player)

    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
        # A departing player may trigger game-over.
        self.checkEnd()

    def on_begin(self) -> None:
        super().on_begin()
        self.roundNum = 0
        self.numPickedUp = 0
        self.nodes = []
        self.flags = []
        self.spawned = []
        self.setup_standard_time_limit(self._time_limit)
        if self.credit_text:
            t = ba.newnode('text',
                           attrs={'text': "升级 Freaku  作者 MattZ45986  汉化：炸队汉化组🚩",  # Disable 'Enable Bottom Credits' when making playlist, No need to edit this lovely...
                                  'scale': 0.7,
                                  'position': (0, 0),
                                  'shadow': 0.5,
                                  'flatness': 1.2,
                                  'color': (1, 1, 1),
                                  'h_align': 'center',
                                  'v_attach': 'bottom'})
        self.makeRound()
        self._textRound.text = "第 " + str(self.roundNum)+" 回合"
        ba.timer(5, self.checkEnd)

    def makeRound(self):
        for player in self.players:
            if player.survived:
                player.team.score += 1
        self.roundNum += 1
        self._textRound.text = "第 "+ str(self.roundNum)+" 回合"
        self.flags = []
        self.spawned = []
        angle = random.randint(0, 359)
        c = 0
        for player in self.players:
            if player.survived:
                c += 1
        spacing = 10
        for player in self.players:
            player.done = False
            if player.survived:
                if not player.is_alive():
                    self.spawn_player(player, (.5, 5, -4))
                self.spawned.append(player)
        try:
            spacing = 360 // (c)
        except:
            self.checkEnd()
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (0, 0, 0),
                  (0.5, 0.8, 0), (0, 0.8, 0.5), (0.8, 0.25, 0.7), (0, 0.27, 0.55), (2, 2, 0.6), (0.4, 3, 0.85)]
        # Smart Mathematics:
        # All Flags spawn same distance from the players
        for i in range(c-1):
            angle += spacing
            angle %= 360
            x = 6 * math.sin(math.degrees(angle))
            z = 6 * math.cos(math.degrees(angle))
            flag = Flag(position=(x+.5, 5, z-4), color=colors[i]).autoretain()
            self.flags.append(flag)

    def killRound(self):
        self.numPickedUp = 0
        for player in self.players:
            if player.is_alive():
                player.actor.handlemessage(ba.DieMessage())
        for flag in self.flags:
            flag.node.delete()
        for light in self.nodes:
            light.delete()

    def spawn_player(self, player: Player, pos: tuple = (0, 0, 0)) -> ba.Actor:
        spaz = self.spawn_player_spaz(player)
        if pos == (0, 0, 0):
            pos = (-.5+random.random()*2, 3+random.random()*2, -5+random.random()*2)
        spaz.connect_controls_to_player(enable_punch=self.is_punch,
                                        enable_bomb=False, enable_run=self.is_run)
        spaz.handlemessage(ba.StandMessage(pos))
        return spaz

    def check_respawn(self, player):
        if not player.done and player.survived:
            self.respawn_player(player, 2.5)

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, ba.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            ba.timer(0.1, ba.Call(self.check_respawn, player))
            ba.timer(0.5, self.checkEnd)
        elif isinstance(msg, FlagPickedUpMessage):
            self.numPickedUp += 1
            msg.node.getdelegate(PlayerSpaz, True).getplayer(Player, True).done = True
            l = ba.newnode('light',
                           owner=None,
                           attrs={'color': msg.node.color,
                                  'position': (msg.node.position_center),
                                  'intensity': 1})
            self.nodes.append(l)
            msg.flag.handlemessage(ba.DieMessage())
            msg.node.handlemessage(ba.DieMessage())
            msg.node.delete()
            if self.numPickedUp == len(self.flags):
                for player in self.spawned:
                    if not player.done:
                        try:
                            player.survived = False
                            ba.screenmessage("淘汰者： "+player.getname()+" 😖")
                            player.actor.handlemessage(ba.StandMessage((0, 3, -2)))
                            ba.timer(0.5, ba.Call(player.actor.handlemessage, ba.FreezeMessage()))
                            ba.timer(3, ba.Call(player.actor.handlemessage, ba.ShouldShatterMessage()))
                        except:
                            pass
                ba.timer(3.5, self.killRound)
                ba.timer(3.55, self.makeRound)
        else:
            return super().handlemessage(msg)
        return None

    def checkEnd(self):
        i = 0
        for player in self.players:
            if player.survived:
                i += 1
        if i <= 1:
            for player in self.players:
                if player.survived:
                    player.team.score += 10
            ba.timer(2.5, self.end_game)

    def end_game(self) -> None:
        results = ba.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
