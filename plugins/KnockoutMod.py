#汉化by炸队汉化组
#QQ群161073376
# Released under the MIT License. See LICENSE for details.
# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)
#汉化by edMedic
#QQ2091341667
#Email：medic163@163.com/edmedic@outlook.com
#禁止未经授权用于开服
#授权id：82B51274EA94336EB3D7DDEA4D1E738D
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.spaz import Spaz

if TYPE_CHECKING:
    pass


# 睡觉觉mod | 作者: byANG3L | 汉化:Medic
knockout_jump = False #按跳跃键睡觉
knockout_pickup = False #按举起键睡觉
knockout_punch = False #按拳击键睡觉
knockout_bomb = False #按炸弹键睡觉
knockout_time = 1.0 #昏迷（睡觉）时间（单位：秒）

# ba_meta export plugin
class KnockoutPlugin(ba.Plugin):
    
    Spaz.old_on_jump_press = Spaz.on_jump_press
    def on_jump_press(self) -> None:
        if knockout_jump:
            if not self.node:
                return
            self.node.handlemessage(
                'knockout', knockout_time * 1000)
        else:
            self.old_on_jump_press()
    Spaz.on_jump_press = on_jump_press
    
    Spaz.old_on_pickup_press = Spaz.on_pickup_press
    def on_pickup_press(self) -> None:
        if knockout_pickup:
            if not self.node:
                return
            self.node.handlemessage(
                'knockout', knockout_time * 1000)
        else:
            self.old_on_pickup_press()
    Spaz.on_pickup_press = on_pickup_press
    
    Spaz.old_on_punch_press = Spaz.on_punch_press
    def on_punch_press(self) -> None:
        if knockout_punch:
            if not self.node:
                return
            self.node.handlemessage(
                'knockout', knockout_time * 1000)
        else:
            self.old_on_punch_press()
    Spaz.on_punch_press = on_punch_press
    
    Spaz.old_on_bomb_press = Spaz.on_bomb_press
    def on_bomb_press(self) -> None:
        if knockout_bomb:
            if not self.node:
                return
            self.node.handlemessage(
                'knockout', knockout_time * 1000)
        else:
            self.old_on_bomb_press()
    Spaz.on_bomb_press = on_bomb_press