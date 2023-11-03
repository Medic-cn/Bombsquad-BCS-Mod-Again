from .Handlers import send
import ba, _ba
import ba.internal
from stats import mystats
from ba._general import Call
import _thread
Commands = ['me', 'list', 'uniqeid','ping']
CommandAliases = ['stats', 'score', 'rank', 'myself', 'l', 'id', 'pb-id', 'pb', 'accountid']



def ExcelCommand(command, arguments, clientid, accountid):
    """
    Checks The Command And Run Function

    Parameters:
        command : str
        arguments : str
        clientid : int
        accountid : int

    Returns:
        None
    """
    if command in ['me', 'stats', 'score', 'rank', 'myself']:
        fetch_send_stats(accountid,clientid)

    elif command in ['list', 'l']:
        list(clientid)

    elif command in ['uniqeid', 'id', 'pb-id', 'pb' , 'accountid']:
        accountid_request(arguments, clientid, accountid)

    elif command in ['ping']:
        get_ping(arguments, clientid)





def get_ping(arguments, clientid):
    if arguments == [] or arguments == ['']:
        send(f"你的延迟是 {_ba.get_client_ping(clientid)}ms ", clientid)

    else:
        try:
            session = ba.internal.get_foreground_host_session()

            for index, player in enumerate(session.sessionplayers):
                name = player.getname(full=True,icon = False),
                if player.inputdevice.client_id == int(arguments[0]):
                    ping = _ba.get_client_ping(int(arguments[0]))
                    send(f" {name}的 网络延迟有{ping}ms", clientid)
        except:
            return


def stats(ac_id,clientid):
    stats=mystats.get_stats_by_id(ac_id)
    if stats:
        reply="总得分:"+str(stats["scores"])+"\n游戏次数:"+str(stats["games"])+"\n击杀数:"+str(stats["kills"])+"\n死亡数:"+str(stats["deaths"])+"\n平均:"+str(stats["avg_score"])
    else:
        reply="你还没有游戏数据😶‍🌫️"

    _ba.pushcall(Call(send,reply,clientid),from_other_thread=True)


def fetch_send_stats(ac_id,clientid):
    _thread.start_new_thread(stats,(ac_id,clientid,))


def list(clientid):
    """Returns The List Of Players Clientid and index"""

    p = u'{0:^16}{1:^15}{2:^10}'
    seprator = '\n______________________________\n'


    list = p.format('游戏名', '系统id' , '游戏id')+seprator
    session = ba.internal.get_foreground_host_session()


    for index, player in enumerate(session.sessionplayers):
        list += p.format(player.getname(icon = False),
        player.inputdevice.client_id, index)+"\n"

    send(list, clientid)




def accountid_request(arguments, clientid, accountid):
    """Returns The Account Id Of Players"""

    if arguments == [] or arguments == ['']:
        send(f"你的账户id是 {accountid} ", clientid)

    else:
        try:
            session = ba.internal.get_foreground_host_session()
            player = session.sessionplayers[int(arguments[0])]

            name = player.getname(full=True, icon=True)
            accountid = player.get_v1_account_id()

            send(f" {name}的账户id是 '{accountid}' ", clientid)
        except:
            return

