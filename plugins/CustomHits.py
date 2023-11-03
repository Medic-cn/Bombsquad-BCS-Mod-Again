#汉化by炸队汉化组
#QQ群161073376
#改进：medic
# ba_meta require api 7

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.spaz import Spaz

if TYPE_CHECKING:
    pass


####################################

first_damage = ('💤', (0, 1, 0), '6')
second_damage = ('🐵', (0, 1, 1), '2')
third_damage = ('✨', (0.8, 0.4, 1), '3')
fourth_damage = ('💥', (1, 1, 0), '4')
five_damage = ('👻', (1, 0, 0), '5')


def custom_effects(pos: float, effect: str = None) -> None:
    if effect == '1':
        ba.emitfx(
            position=pos,
            count=8,
            scale=0.4,
            spread=0.4,
            chunk_type='rock')
    elif effect == '2':
        ba.emitfx(
            position=pos,
            count=12,
            scale=0.5,
            spread=0.5,
            chunk_type='slime')
    elif effect == '3':
        ba.emitfx(
            position=pos,
            count=6,
            scale=0.3,
            spread=0.4,
            chunk_type='splinter')
    elif effect == '4':
        ba.emitfx(
            position=pos,
            count=8,
            scale=0.4,
            spread=0.4,
            chunk_type='ice')
    elif effect == '5':
        ba.emitfx(
            position=pos,
            count=16,
            scale=0.8,
            spread=1.5,
            chunk_type='spark')
    elif effect == '6':
        ba.emitfx(
            position=pos,
            count=8,
            scale=0.5,
            spread=0.4,
            chunk_type='metal')

####################################

# ba_meta export plugin
class CustomHitsPlugin(ba.Plugin):

    def on_punched(self, damage: int) -> None:
        pos = self.node.position
        def custom_text(msg: str, color: float) -> None:
            text = ba.newnode(
                'text',
                attrs={
                    'text': msg,
                    'color': color,
                    'in_world': True,
                    'h_align': 'center',
                    'shadow': 0.5,
                    'flatness': 1.0})
            ba.animate_array(text, 'position', 3, {
                0.0: (pos[0], pos[1] + 1.2, pos[2]),
                2.0: (pos[0], pos[1] + 1.7, pos[2])
            })
            ba.animate(text, 'opacity', {
                0.8: 1.0,
                2.0: 0.0
            })
            ba.animate(text, 'scale', {
                0: 0,
                0.1: 0.017,
                0.15: 0.014,
                2.0: 0.016
            })
            ba.timer(2.0, text.delete)
        if damage < 200:
            custom_text(first_damage[0], first_damage[1])
            custom_effects(pos, first_damage[2])
        elif damage < 500:
            custom_text(second_damage[0], second_damage[1])
            custom_effects(pos, second_damage[2])
        elif damage < 800:
            custom_text(third_damage[0], third_damage[1])
            custom_effects(pos, third_damage[2])
        elif damage < 1000:
            custom_text(fourth_damage[0], fourth_damage[1])
            custom_effects(pos, fourth_damage[2])
        else:
            custom_text(five_damage[0], five_damage[1])
            custom_effects(pos, five_damage[2])
    Spaz.on_punched = on_punched
