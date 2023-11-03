# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Tuple, Union, Sequence, Optional


class Player(ba.Player['Team']):
    """Our player type for this game."""


class Team(ba.Team[Player]):
    """Our team type for this game."""


# ba_meta export game
class DeathMatchGame(ba.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = ''

    @classmethod
    def get_available_settings(
            cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
        settings = [
            ba.BoolSetting('Epic Mode', default=False),
        ]
        return settings

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        return (issubclass(sessiontype, ba.DualTeamSession)
                or issubclass(sessiontype, ba.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._epic_mode = bool(settings['Epic Mode'])

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC if self._epic_mode else
                              ba.MusicType.TO_THE_DEATH)

    def on_begin(self) -> None:
        super().on_begin()
        from bastd.actor.powerupbox import PowerupBox
        for i in range(6):
            PowerupBox(
                position=(-3,3,-3+i*1.1),
                poweruptype='bunny',
                expire=False).autoretain()

        for i in range(7):
            PowerupBox(
                position=(-7,3,-3+i*1.1),
                poweruptype='bunny',
                expire=False).autoretain()
        for i in range(7):
            PowerupBox(
                position=(-8,3,-3+i*1.1),
                poweruptype='bunny',
                expire=False).autoretain()
        for i in range(7):
            PowerupBox(
                position=(-9,3,-3+i*1.1),
                poweruptype='bunny',
                expire=False).autoretain()

    def spawn_player(self, player: Player) -> ba.Actor:

        # Let's spawn close to the center.
        spawn_center = (0, 3, -2)
        spaz = self.spawn_player_spaz(player, position=spawn_center)
        spaz.hitpoints = spaz.hitpoints_max = 3000
        spaz.impact_scale = 0.7
        return spaz

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, ba.PlayerDiedMessage):

            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

        else:
            return super().handlemessage(msg)
        return None
