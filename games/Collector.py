# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)
#汉化：炸队汉化组 QQ群161073376 联系邮箱：cntsl@inker.ga
#发行/修补/资源收录：药服技术社 QQ群527575487 联系邮箱：ink@inker.ga(技术支持) mod@inker.ga（投稿mod）
'''
	Gamemode: Collector
	Creator: TheMikirog
	Website: https://bombsquadjoyride.blogspot.com/

	这是一个纯粹由我制作的游戏模式，只是为了刁难未受挑战的改装者
	在外面向市场投放垃圾。
	我们不想要现有的游戏模式
	一些新奇的东西！玩家应该得到更多！


	在这个游戏模式中，你必须杀死其他人才能得到他们的胶囊。
	胶囊可以收集并存放在您的库存中，
	你要多少？
	在你杀死携带其中一些的敌人后，
	他们丢弃各自数量的胶囊，他们携带+两个以上。
	你的任务是收集这些胶囊，
	拿到旗子，给他们KOTH风格的分数。
	如果你没有任何胶囊，你就不能得分。
	第一个到达所需安曼蒙特的玩家或团队获胜。
	这是一个试图生存的游戏模式
	选择你的战斗来赢得胜利。
	炸弹小队中的一项罕见技能，在那里每个人都过于好斗。

'''

from __future__ import annotations

import weakref
from enum import Enum
from typing import TYPE_CHECKING

import ba
import random
from bastd.actor.flag import Flag
from bastd.actor.popuptext import PopupText
from bastd.actor.playerspaz import PlayerSpaz
from bastd.actor.scoreboard import Scoreboard
from bastd.gameutils import SharedObjects

if TYPE_CHECKING:
	from typing import Any, Sequence


lang = ba.app.lang.language

name = '收集豆'
description = ('杀死敌人可以得到豆子\n'
			  '在旗帜下面把豆子换成游戏得分!')
description_ingame = '杀死敌人，然后收集 ${ARG1} 个豆子.'
description_short = '收集 ${ARG1} 个豆子'
tips = [(
	'让你的对手掉出地图，他的豆子就浪费了！\n'
	'尽量不要把敌人扔下悬崖来杀死他们。'),
	'不要太鲁莽。你会很快失去你的战利品！',
	('不要让领先的玩家在旗帜得分！ '
	'\n如果可以的话，一起围攻他!'),
	('有8%的概率会出现4个豆子 '
	'你是不是那个幸运儿呢( $ _ $ )!'),
	('#汉化：炸队汉化组 QQ群161073376 联系邮箱：cntsl@inker.ga\n#发行/修补/资源收录：药服技术社 QQ群527575487 \n联系邮箱：ink@inker.ga(技术支持) mod@inker.ga（投稿mod） '),
]
capsules_to_win = '收集豆子'
capsules_death = '死亡豆'
lucky_capsules = '有幸运豆'
bonus = '砰!'
full_capacity = '口袋装不下啦!'


class FlagState(Enum):
	"""States our single flag can be in."""

	NEW = 0
	UNCONTESTED = 1
	CONTESTED = 2
	HELD = 3


class Player(ba.Player['Team']):
	"""Our player type for this game."""

	def __init__(self) -> None:
		self.time_at_flag = 0
		self.capsules = 0
		self.light = None


class Team(ba.Team[Player]):
	"""Our team type for this game."""

	def __init__(self) -> None:
		self.score = 0


# ba_meta export game
class CollectorGame(ba.TeamGameActivity[Player, Team]):

	name = name
	description = description
	tips = tips

	# Print messages when players die since it matters here.
	announce_player_deaths = True

	@classmethod
	def get_available_settings(
		cls, sessiontype: type[ba.Session]
	) -> list[ba.Setting]:
		settings = [
			ba.IntSetting(
				capsules_to_win,
				min_value=1,
				default=10,
				increment=1,
			),
			ba.IntSetting(
				capsules_death,
				min_value=1,
				max_value=10,
				default=2,
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
			ba.BoolSetting(lucky_capsules, default=True),
			ba.BoolSetting('Epic Mode', default=False),
		]
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: type[ba.Session]) -> bool:
		return issubclass(sessiontype, ba.DualTeamSession) or issubclass(
			sessiontype, ba.FreeForAllSession
		)

	@classmethod
	def get_supported_maps(cls, sessiontype: type[ba.Session]) -> list[str]:
		return ba.getmaps('keep_away')

	def __init__(self, settings: dict):
		super().__init__(settings)
		shared = SharedObjects.get()
		self._scoreboard = Scoreboard()
		self._score_to_win: int | None = None
		self._swipsound = ba.getsound('swip')
		self._lucky_sound = ba.getsound('ding')

		self._flag_pos: Sequence[float] | None = None
		self._flag_state: FlagState | None = None
		self._flag: Flag | None = None
		self._flag_light: ba.Node | None = None
		self._scoring_team: weakref.ref[Team] | None = None
		self._time_limit = float(settings['Time Limit'])
		self._epic_mode = bool(settings['Epic Mode'])

		self._capsules_to_win = int(settings[capsules_to_win])
		self._capsules_death = int(settings[capsules_death])
		self._lucky_capsules = bool(settings[lucky_capsules])
		self._capsules: list[Any] = []

		self._capsule_model = ba.getmodel('bomb')
		self._capsule_tex = ba.gettexture('bombColor')
		self._capsule_lucky_tex = ba.gettexture('bombStickyColor')
		self._collect_sound = ba.getsound('powerup01')
		self._lucky_collect_sound = ba.getsound('cashRegister2')

		self._capsule_material = ba.Material()
		self._capsule_material.add_actions(
			conditions=('they_have_material', shared.player_material),
			actions=('call', 'at_connect', self._on_capsule_player_collide),
		)

		self._flag_region_material = ba.Material()
		self._flag_region_material.add_actions(
			conditions=('they_have_material', shared.player_material),
			actions=(
				('modify_part_collision', 'collide', True),
				('modify_part_collision', 'physical', False),
				(
					'call',
					'at_connect',
					ba.Call(self._handle_player_flag_region_collide, True),
				),
				(
					'call',
					'at_disconnect',
					ba.Call(self._handle_player_flag_region_collide, False),
				),
			),
		)

		# Base class overrides.
		self.slow_motion = self._epic_mode
		self.default_music = (
			ba.MusicType.EPIC if self._epic_mode else ba.MusicType.SCARY
		)

	def get_instance_description(self) -> str | Sequence:
		return description_ingame, self._score_to_win

	def get_instance_description_short(self) -> str | Sequence:
		return description_short, self._score_to_win

	def create_team(self, sessionteam: ba.SessionTeam) -> Team:
		return Team()

	def on_team_join(self, team: Team) -> None:
		self._update_scoreboard()

	def on_begin(self) -> None:
		super().on_begin()
		shared = SharedObjects.get()
		self.setup_standard_time_limit(self._time_limit)
		self.setup_standard_powerup_drops()

		# Base kills needed to win on the size of the largest team.
		self._score_to_win = self._capsules_to_win * max(
			1, max(len(t.players) for t in self.teams)
		)
		self._update_scoreboard()

		if isinstance(self.session, ba.FreeForAllSession):
			self._flag_pos = self.map.get_flag_position(random.randint(0, 1))
		else:
			self._flag_pos = self.map.get_flag_position(None)

		ba.timer(1.0, self._tick, repeat=True)
		self._flag_state = FlagState.NEW
		Flag.project_stand(self._flag_pos)
		self._flag = Flag(
			position=self._flag_pos, touchable=False, color=(1, 1, 1)
		)
		self._flag_light = ba.newnode(
			'light',
			attrs={
				'position': self._flag_pos,
				'intensity': 0.2,
				'height_attenuated': False,
				'radius': 0.4,
				'color': (0.2, 0.2, 0.2),
			},
		)
		# Flag region.
		flagmats = [self._flag_region_material, shared.region_material]
		ba.newnode(
			'region',
			attrs={
				'position': self._flag_pos,
				'scale': (1.8, 1.8, 1.8),
				'type': 'sphere',
				'materials': flagmats,
			},
		)
		self._update_flag_state()

	def _tick(self) -> None:
		self._update_flag_state()

		if self._scoring_team is None:
			scoring_team = None
		else:
			scoring_team = self._scoring_team()

		if not scoring_team:
			return

		if isinstance(self.session, ba.FreeForAllSession):
			players = self.players
		else:
			players = scoring_team.players

		for player in players:
			if player.time_at_flag > 0:
				self.stats.player_scored(
					player, 3, screenmessage=False, display=False
				)
				if player.capsules > 0:
					if self._flag_state != FlagState.HELD:
						return
					if scoring_team.score >= self._score_to_win:
						return

					player.capsules -= 1
					scoring_team.score += 1
					self._handle_capsule_storage((
						self._flag_pos[0],
						self._flag_pos[1]+1,
						self._flag_pos[2]
					), player)
					ba.playsound(
						self._collect_sound,
						0.8,
						position=self._flag_pos)

					self._update_scoreboard()
					if player.capsules > 0:
						assert self._flag is not None
						self._flag.set_score_text(
							str(self._score_to_win - scoring_team.score))

					# winner
					if scoring_team.score >= self._score_to_win:
						self.end_game()

	def end_game(self) -> None:
		results = ba.GameResults()
		for team in self.teams:
			results.set_team_score(team, team.score)
		self.end(results=results, announce_delay=0)

	def _update_flag_state(self) -> None:
		holding_teams = set(
			player.team for player in self.players if player.time_at_flag
		)
		prev_state = self._flag_state
		assert self._flag_light
		assert self._flag is not None
		assert self._flag.node
		if len(holding_teams) > 1:
			self._flag_state = FlagState.CONTESTED
			self._scoring_team = None
			self._flag_light.color = (0.6, 0.6, 0.1)
			self._flag.node.color = (1.0, 1.0, 0.4)
		elif len(holding_teams) == 1:
			holding_team = list(holding_teams)[0]
			self._flag_state = FlagState.HELD
			self._scoring_team = weakref.ref(holding_team)
			self._flag_light.color = ba.normalized_color(holding_team.color)
			self._flag.node.color = holding_team.color
		else:
			self._flag_state = FlagState.UNCONTESTED
			self._scoring_team = None
			self._flag_light.color = (0.2, 0.2, 0.2)
			self._flag.node.color = (1, 1, 1)
		if self._flag_state != prev_state:
			ba.playsound(self._swipsound)

	def _handle_player_flag_region_collide(self, colliding: bool) -> None:
		try:
			spaz = ba.getcollision().opposingnode.getdelegate(PlayerSpaz, True)
		except ba.NotFoundError:
			return

		if not spaz.is_alive():
			return

		player = spaz.getplayer(Player, True)

		# Different parts of us can collide so a single value isn't enough
		# also don't count it if we're dead (flying heads shouldn't be able to
		# win the game :-)
		if colliding and player.is_alive():
			player.time_at_flag += 1
		else:
			player.time_at_flag = max(0, player.time_at_flag - 1)

		self._update_flag_state()

	def _update_scoreboard(self) -> None:
		for team in self.teams:
			self._scoreboard.set_team_value(
				team, team.score, self._score_to_win
			)

	def _drop_capsule(self, player: Player) -> None:
		pt = player.node.position

		# Throw out capsules that the victim has + 2 more to keep the game running
		for i in range(player.capsules + self._capsules_death):
			# How far from each other these capsules should spawn
			w = 0.6
			# How much these capsules should fly after spawning
			s = 0.005 - (player.capsules * 0.01)
			self._capsules.append(
				Capsule(
					position=(pt[0] + random.uniform(-w, w),
							  pt[1] + 0.75 + random.uniform(-w, w),
							  pt[2]),
					velocity=(random.uniform(-s, s),
							  random.uniform(-s, s),
							  random.uniform(-s, s)),
					lucky=False))
		if random.randint(1, 12) == 1 and self._lucky_capsules:
			# How far from each other these capsules should spawn
			w = 0.6
			# How much these capsules should fly after spawning
			s = 0.005
			self._capsules.append(
				Capsule(
					position=(pt[0] + random.uniform(-w, w),
							  pt[1] + 0.75 + random.uniform(-w, w),
							  pt[2]),
					velocity=(random.uniform(-s, s),
							  random.uniform(-s, s),
							  random.uniform(-s, s)),
					lucky=True))

	def _on_capsule_player_collide(self) -> None:
		if self.has_ended():
			return
		collision = ba.getcollision()

		# Be defensive here; we could be hitting the corpse of a player
		# who just left/etc.
		try:
			capsule = collision.sourcenode.getdelegate(Capsule, True)
			player = collision.opposingnode.getdelegate(
				PlayerSpaz, True
			).getplayer(Player, True)
		except ba.NotFoundError:
			return

		if not player.is_alive():
			return

		if capsule.node.color_texture == self._capsule_lucky_tex:
			player.capsules += 4
			PopupText(
				bonus,
				color=(1, 1, 0),
				scale=1.5,
				position=capsule.node.position
			).autoretain()
			ba.playsound(
				self._lucky_collect_sound,
				1.0,
				position=capsule.node.position)
			ba.emitfx(
				position=capsule.node.position,
				velocity=(0, 0, 0),
				count=int(6.4+random.random()*24),
				scale=1.2,
				spread=2.0,
				chunk_type='spark');
			ba.emitfx(
				position=capsule.node.position,
				velocity=(0, 0, 0),
				count=int(4.0+random.random()*6),
				emit_type='tendrils');
		else:
			player.capsules += 1
			ba.playsound(
				self._collect_sound,
				0.6,
				position=capsule.node.position)
		# create a flash
		light = ba.newnode(
			'light',
			attrs={
				'position': capsule.node.position,
				'height_attenuated': False,
				'radius': 0.1,
				'color': (1, 1, 0)})

		# Create a short text informing about your inventory
		self._handle_capsule_storage(player.position, player)

		ba.animate(light, 'intensity', {
			0: 0,
			0.1: 0.5,
			0.2: 0
		}, loop=False)
		ba.timer(0.2, light.delete)
		capsule.handlemessage(ba.DieMessage())

	def _update_player_light(self, player: Player, capsules: int) -> None:
		if player.light:
			intensity = 0.04 * capsules
			ba.animate(player.light, 'intensity', {
				0.0: player.light.intensity,
				0.1: intensity
			})
			def newintensity():
				player.light.intensity = intensity
			ba.timer(0.1, newintensity)
		else:
			player.light = ba.newnode(
				'light',
				attrs={
					'height_attenuated': False,
					'radius': 0.2,
					'intensity': 0.0,
					'color': (0.2, 1, 0.2)
				})
			player.node.connectattr('position', player.light, 'position')

	def _handle_capsule_storage(self, pos: float, player: Player) -> None:
		capsules = player.capsules
		text = str(capsules)
		scale = 1.75 + (0.02 * capsules)
		if capsules > 10:
			player.capsules = 10
			text = full_capacity
			color = (1, 0.85, 0)
		elif capsules > 7:
			color = (1, 0, 0)
			scale = 2.4
		elif capsules > 5:
			color = (1, 0.4, 0.4)
			scale = 2.1
		elif capsules > 3:
			color = (1, 1, 0.4)
			scale = 2.0
		else:
			color = (1, 1, 1)
			scale = 1.9
		PopupText(
			text,
			color=color,
			scale=scale,
			position=(pos[0], pos[1]-1, pos[2])
		).autoretain()
		self._update_player_light(player, capsules)

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, ba.PlayerDiedMessage):
			super().handlemessage(msg)  # Augment default.
			# No longer can count as time_at_flag once dead.
			player = msg.getplayer(Player)
			player.time_at_flag = 0
			self._update_flag_state()
			self._drop_capsule(player)
			player.capsules = 0
			self._update_player_light(player, 0)
			self.respawn_player(player)
		else:
			return super().handlemessage(msg)


class Capsule(ba.Actor):

	def __init__(self,
				 position: Sequence[float] = (0.0, 1.0, 0.0),
				 velocity: Sequence[float] = (0.0, 0.5, 0.0),
				 lucky: bool = False):
		super().__init__()
		shared = SharedObjects.get()
		activity = self.getactivity()

		# spawn just above the provided point
		self._spawn_pos = (position[0], position[1], position[2])

		if lucky:
			ba.playsound(activity._lucky_sound, 1.0, self._spawn_pos)

		self.node = ba.newnode(
			'prop',
			attrs={
				'model': activity._capsule_model,
				'color_texture': activity._capsule_lucky_tex if lucky else (
					activity._capsule_tex),
				'body': 'crate' if lucky else 'capsule',
				'reflection': 'powerup' if lucky else 'soft',
				'body_scale': 0.65 if lucky else 0.3,
				'density':6.0 if lucky else 4.0,
				'reflection_scale': [0.15],
				'shadow_size': 0.65 if lucky else 0.6,
				'position': self._spawn_pos,
				'velocity': velocity,
				'materials': [
					shared.object_material, activity._capsule_material]
			},
			delegate=self)
		ba.animate(self.node, 'model_scale', {
			0.0: 0.0,
			0.1: 0.9 if lucky else 0.6,
			0.16: 0.8 if lucky else 0.5
		})
		self._light_capsule = ba.newnode(
			'light',
			attrs={
				'position': self._spawn_pos,
				'height_attenuated': False,
				'radius': 0.5 if lucky else 0.1,
				'color': (0.2, 0.2, 0) if lucky else (0.2, 1, 0.2)
			})
		self.node.connectattr('position', self._light_capsule, 'position')

	def handlemessage(self, msg: Any):
		if isinstance(msg, ba.DieMessage):
			self.node.delete()
			ba.animate(self._light_capsule, 'intensity', {
				0: 1.0,
				0.05: 0.0
			}, loop=False)
			ba.timer(0.05, self._light_capsule.delete)
		elif isinstance(msg, ba.OutOfBoundsMessage):
			self.handlemessage(ba.DieMessage())
		elif isinstance(msg, ba.HitMessage):
			self.node.handlemessage(
				'impulse',
				msg.pos[0], msg.pos[1], msg.pos[2],
				msg.velocity[0]/8, msg.velocity[1]/8, msg.velocity[2]/8,
				1.0*msg.magnitude, 1.0*msg.velocity_magnitude, msg.radius, 0,
				msg.force_direction[0], msg.force_direction[1],
				msg.force_direction[2])
		else:
			return super().handlemessage(msg)
