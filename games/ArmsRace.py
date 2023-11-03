# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)
#汉化：炸队汉化组 QQ群161073376 联系邮箱：cntsl@inker.ga
#发行/修补/资源收录：药服技术社 QQ群527575487 联系邮箱：ink@inker.ga(技术支持) mod@inker.ga（投稿mod）
from __future__ import annotations

from typing import TYPE_CHECKING

import ba
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard

if TYPE_CHECKING:
	from typing import Any, Sequence


lang = ba.app.lang.language

#if lang == 'Spanish':
#	name = 'Carrera de Armas'
#	description = ('Mejora tu arma eliminando enemigos.\n'
#				  'Gana la partida siendo el primer jugador\n'
#				  'en matar con la Maldición.')
#	description_ingame = 'Mejora tu arma eliminando enemigos.'
#	description_short = 'Elimina {} Jugadores para ganar'
#	basic_bombs = 'Bombas Básicas'
#	frozen_bombs = 'Bombas de Hielo'
#	sticky_bombs = 'Bombas Pegajosas'
#	impact_bombs = 'Insta-Bombas'
#	grabbing_bombs = 'Solo Agarrando'
#	punching_bombs = 'Solo Golpeando'
#	cursed = 'Maldito'
#else:
#	name = 'Arms Race'
#	description = ('Upgrade your weapon by eliminating enemies.\n'
#				  'Win the match by being the first player\n'
#				  'to get a kill while cursed.')
#	description_ingame = 'Upgrade your weapon by eliminating enemies.'
#	description_short = 'Kill {} Players to win'
#	basic_bombs = 'Basic Bombs'
#	frozen_bombs = 'Frozen Bombs'
#	sticky_bombs = 'Sticky Bombs'
#	impact_bombs = 'Impact Bombs'
#	grabbing_bombs = 'Grabbing only'
#	punching_bombs = 'Punching only'
#	cursed = 'Cursed'

name = '武器升级战'
description = ('杀死敌人来升级你的炸弹.\n'
			  '第一个lv7的人获胜\n'
			  '去杀死对面吧( ‵▽′)ψ.\n'
			  '#汉化：炸队汉化组 QQ群161073376 联系邮箱：cntsl@inker.ga\n发行/修补/资源收录：药服技术社 QQ群527575487')
description_ingame = '杀死敌人，升级武器( ‵▽′)ψ'
description_short = '#汉化：炸队汉化组 cntsl@inker.ga'
basic_bombs = 'LV0.普通炸弹'
frozen_bombs = 'LV1.冰冻炸弹'
sticky_bombs = 'LV2.黏黏炸弹'
impact_bombs = 'LV3.触感炸弹'
grabbing_bombs = 'LV4.抓'
punching_bombs = 'LV5.打'
cursed = 'LV6.自爆！'

class State:

	def __init__(self,
				 bomb: str = None,
				 grab: bool = False,
				 punch: bool = False,
				 curse: bool = False,
				 required: bool = False,
				 final: bool = False,
				 name: str = ""):
		self.bomb = bomb
		self.grab = grab
		self.punch = punch
		self.pickup = False
		self.curse = curse
		self.required = required or final
		self.final = final
		self.name = name
		self.next = None
		self.index = None

	def apply(self, spaz: Player) -> None:
		spaz.disconnect_controls_from_player()
		spaz.connect_controls_to_player(enable_punch=self.punch,
										enable_bomb=bool(self.bomb),
										enable_pickup=self.grab)
		if self.curse:
			spaz.curse_time = None
			spaz.curse()
		if self.bomb:
			spaz.bomb_type = self.bomb
		spaz.set_score_text(self.name)

	def getsetting(self) -> None:
		return ba.BoolSetting(self.name, default=True)


class Player(ba.Player['Team']):
	"""Our player type for this game."""
	def __init__(self) -> None:
		self.state: Any = None


class Team(ba.Team[Player]):
	"""Our team type for this game."""

	def __init__(self) -> None:
		self.score = 0


# ba_meta export game
class ArmsRaceGame(ba.TeamGameActivity[Player, Team]):

	name = name
	description = description

	# Print messages when players die since it matters here.
	announce_player_deaths = True

	states = [
		State(bomb='normal', name=basic_bombs),
		State(bomb='ice', name=frozen_bombs),
		State(bomb='sticky', name=sticky_bombs),
		State(bomb='impact', name=impact_bombs),
		State(grab=True, name=grabbing_bombs),
		State(punch=True, name=punching_bombs),
		State(curse=True, name=cursed, final=True)
	]

	@classmethod
	def get_available_settings(
		cls, sessiontype: type[ba.Session]
	) -> list[ba.Setting]:
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
		]
		for state in cls.states:
			if not state.required:
				settings.append(state.getsetting())
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
		return issubclass(sessiontype, ba.DualTeamSession) or issubclass(
			sessiontype, ba.FreeForAllSession
		)

	@classmethod
	def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
		return ba.getmaps('melee')

	def __init__(self, settings: dict):
		self.states = [s for s in self.states if settings.get(s.name, True)]
		for i, state in enumerate(self.states):
			if i < len(self.states) and not state.final:
				state.next = self.states[i + 1]
			state.index = i
		super().__init__(settings)
		self._scoreboard = Scoreboard()
		self._score_to_win: int | None = None
		self._dingsound = ba.getsound('dingSmall')
		self._epic_mode = bool(settings['Epic Mode'])
		self._time_limit = float(settings['Time Limit'])

		# Base class overrides.
		self.slow_motion = self._epic_mode
		self.default_music = (
			ba.MusicType.EPIC if self._epic_mode else ba.MusicType.TO_THE_DEATH
		)

	def get_instance_description(self) -> str | Sequence:
		return description_ingame

	def get_instance_description_short(self) -> str | Sequence:
		return description_short.format(len(self.states))

	def on_begin(self) -> None:
		super().on_begin()
		self.setup_standard_time_limit(self._time_limit)

		# Base kills needed to win on the size of the largest team.
		self._score_to_win = len(self.states)
		self._update_scoreboard()

	def on_player_join(self, player: Player) -> None:
		player.state = self.states[0]
		self.spawn_player(player)

	def spawn_player(self, player: Player) -> ba.Actor:
		state = player.state
		actor = self.spawn_player_spaz(player)
		state.apply(actor)
		return actor

	def handlemessage(self, msg: Any) -> Any:

		if isinstance(msg, ba.PlayerDiedMessage):

			# Augment standard behavior.
			super().handlemessage(msg)

			player = msg.getplayer(Player)
			self.respawn_player(player)

			killer = msg.getkillerplayer(Player)
			if killer is None:
				return None

			# Handle team-kills.
			if killer.team is player.team:
				return

			# Killing someone on another team nets a kill.
			else:
				killer.team.score += 1
				ba.playsound(self._dingsound)

				if not killer.state.final:
					killer.state = killer.state.next
					killer.state.apply(killer.actor)

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
			self._scoreboard.set_team_value(
				team, team.score, self._score_to_win
			)

	def end_game(self) -> None:
		results = ba.GameResults()
		for team in self.teams:
			results.set_team_score(team, team.score)
		self.end(results=results)
