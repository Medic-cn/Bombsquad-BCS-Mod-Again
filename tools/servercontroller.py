
from typing import TYPE_CHECKING
from efro.terminal import Clr
import _ba
import ba
if TYPE_CHECKING:
    from typing import Any


def _access_check_response(self, data) -> None:

        if data is None:
            print('端口检查失败(但你的房间可能已经公开了)')
        else:
            addr = data['address']
            port = data['port']

            addrstr = f' {addr}'
            poststr = ''
            _ba.our_ip = addr
            _ba.our_port = port
            if data['accessible']:
                # _fetch_public_servers()
                _ba.queue_chcker_timer = ba.Timer(8, ba.Call(simple_queue_checker), repeat=True,  timetype=ba.TimeType.REAL)
                print(
                    f'{Clr.SBLU}主服务器访问{addrstr}'
                    f' UDP端口 {port} 成功🥳\n'
                    f'你的服务器可以'
                    f' 被互联网访问了 .{poststr}{Clr.RST}'
                )
                if self._config.party_is_public:
                    print(
                        f'{Clr.SBLU}你的派对 {self._config.party_name}'
                        f' 已在服务器列表公开.{Clr.RST}'
                    )
                else:
                    print(
                        f'{Clr.SBLU}你的私人派对 {self._config.party_name}'
                        f'可以通过 {addrstr} {port}.加入了{Clr.RST}'
                    )
            else:
                print(
                    f'{Clr.SRED}主服务器检查{addrstr}'
                    f' UDP端口 {port} 失败.\n'
                    f'你的服务器'
                    f' 无法从互联网连接，请检查防火墙和安全组是否放行端口.{poststr}{Clr.RST}'
                )


def _fetch_public_servers():
    ba.internal.add_transaction(
                {
                    'type': 'PUBLIC_PARTY_QUERY',
                    'proto': ba.app.protocol_version,
                    'lang': ba.app.lang.language,
                 },
                callback=ba.Call(_on_public_party_response),
                )
    ba.internal.run_transactions()

def _on_public_party_response(result):
    if result is None:
        return
    parties_in = result['l']
    queue_id = None
    for party_in in parties_in:
        addr = party_in['a']
        assert isinstance(addr, str)
        port = party_in['p']
        assert isinstance(port, int)
        if addr == _ba.our_ip and str(port) == str(_ba.our_port):
            queue_id = party_in['q']
    #  aah sad , public party result dont include our own server
    if queue_id:
        _ba.our_queue_id = queue_id
        _ba.queue_chcker_timer = ba.timer(6, ba.Call(check_queue), repeat=True)
    else:
        print("有些不对劲，为什么我们的服务器不在公共列表中。")
def check_queue():
        ba.internal.add_transaction(
                    {'type': 'PARTY_QUEUE_QUERY', 'q': _ba.our_queue_id},
                    callback=ba.Call(on_update_response),
                )
        ba.internal.run_transactions()
        # lets dont spam our own queue
        ba.internal.add_transaction(
                    {'type': 'PARTY_QUEUE_REMOVE', 'q': _ba.our_queue_id}
                )
        ba.internal.run_transactions()

def on_update_response(response):
    allowed_to_join = response["c"]
    players_in_queue = response["e"]
    max_allowed_in_server = _ba.app.server._config.max_party_size
    current_players = len(_ba.get_game_roster())
    # print(allowed_to_join)
    if allowed_to_join:
        #  looks good , yipee
        _ba.set_public_party_queue_enabled(True)
        return
    if not allowed_to_join and len(players_in_queue) > 1 and current_players < max_allowed_in_server:
        #  something is wrong , lets disable queue for some time
        _ba.set_public_party_queue_enabled(False)

def simple_queue_checker():
    max_allowed_in_server = _ba.app.server._config.max_party_size
    current_players = len(_ba.get_game_roster())

    if current_players < max_allowed_in_server:
        _ba.set_public_party_queue_enabled(False)
    else:
        _ba.set_public_party_queue_enabled(True)


