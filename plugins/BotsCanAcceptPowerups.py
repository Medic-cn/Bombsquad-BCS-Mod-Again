#汉化by炸队汉化组
#QQ群161073376
# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)
#汉化by edMedic
#QQ2091341667
#Email：medic163@163.com/edmedic@outlook.com
#禁止未经授权用于开服
#授权id：82B51274EA94336EB3D7DDEA4D1E738D
from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

import ba
import random
from bastd.actor.spaz import Spaz
from bastd.actor.spazbot import SpazBot

if TYPE_CHECKING:
    from typing import Any, Optional, List, Tuple, Sequence, Type, Callable
    from bastd.actor.flag import Flag


def __init__(self) -> None:
    """Instantiate a spaz-bot."""
    Spaz.__init__(self,color=self.color,
                     highlight=self.highlight,
                     character=self.character,
                     source_player=None,
                     start_invincible=False,
                     can_accept_powerups=True)

    # If you need to add custom behavior to a bot, set this to a callable
    # which takes one arg (the bot) and returns False if the bot's normal
    # update should be run and True if not.
    self.update_callback: Optional[Callable[[SpazBot], Any]] = None
    activity = self.activity
    assert isinstance(activity, ba.GameActivity)
    self._map = weakref.ref(activity.map)
    self.last_player_attacked_by: Optional[ba.Player] = None
    self.last_attacked_time = 0.0
    self.last_attacked_type: Optional[Tuple[str, str]] = None
    self.target_point_default: Optional[ba.Vec3] = None
    self.held_count = 0
    self.last_player_held_by: Optional[ba.Player] = None
    self.target_flag: Optional[Flag] = None
    self._charge_speed = 0.5 * (self.charge_speed_min +
                                self.charge_speed_max)
    self._lead_amount = 0.5
    self._mode = 'wait'
    self._charge_closing_in = False
    self._last_charge_dist = 0.0
    self._running = False
    self._last_jump_time = 0.0

    self._throw_release_time: Optional[float] = None
    self._have_dropped_throw_bomb: Optional[bool] = None
    self._player_pts: Optional[List[Tuple[ba.Vec3, ba.Vec3]]] = None

    # These cooldowns didn't exist when these bots were calibrated,
    # so take them out of the equation.
    self._jump_cooldown = 0
    self._pickup_cooldown = 0
    self._fly_cooldown = 0
    self._bomb_cooldown = 0

    if self.start_cursed:
        self.curse()


# ba_meta export plugin
class BotsCanAcceptPowerupsPlugin(ba.Plugin):
    SpazBot.__init__ = __init__
