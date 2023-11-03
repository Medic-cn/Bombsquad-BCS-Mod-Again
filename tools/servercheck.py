# Released under the MIT License. See LICENSE for details.


from serverData import serverdata
from playersData import pdata
import _ba
import ba.internal
import urllib.request
import json
import datetime
import time
import ba
from ba._general import Call
import threading
import setting
import _thread
import zaqr
from tools import logger
from features import profanity
from playersData import pdata

blacklist = pdata.get_blacklist()

settings = setting.get_settings_data()
ipjoin = {}

class checkserver(object):
    def start(self):
        self.players = []

        self.t1 = ba.Timer(1, ba.Call(self.check), repeat=True,  timetype=ba.TimeType.REAL)

    def check(self):
        newPlayers = []
        ipClientMap = {}
        deviceClientMap = {}
        for ros in ba.internal.get_game_roster():
            ip = _ba.get_client_ip(ros["client_id"])
            device_id = _ba.get_client_public_device_uuid(ros["client_id"])
            # if not ros["account_id"]:
            #     logger.log(f'Player disconnected, None account Id || {ros["display_string"] } IP {ip} {device_id}' ,
            #             "playerjoin")
                # ba.internal.disconnect_client(ros["client_id"], 0)
            if device_id not in deviceClientMap:
                deviceClientMap[device_id] = [ros["client_id"]]
            else:
                deviceClientMap[device_id].append(ros["client_id"])
                if len(deviceClientMap[device_id]) >= settings['maxAccountPerIP']:
                    _ba.chatmessage(f"每个IP只允许 {settings['maxAccountPerIP']} 个设备加入，此设备无法加入❌", clients=[ros["client_id"]])
                    ba.internal.disconnect_client(ros["client_id"])
                    logger.log(f'玩家断开连接，因为IP达到最大连接数 || {ros["account_id"]}' ,
                        "playerjoin")
                    zaqr.sendLog(f'玩家断开连接，因为IP达到最大连接数 || {ros["account_id"]}')
                    continue
            if ip not in ipClientMap:
                ipClientMap[ip] = [ros["client_id"]]
            else:
                ipClientMap[ip].append(ros["client_id"])
                if len(ipClientMap[ip]) >= settings['maxAccountPerIP']:
                    _ba.chatmessage(f"每个IP只允许 {settings['maxAccountPerIP']} 个设备加入，此设备无法加入❌", clients=[ros["client_id"]])
                    ba.internal.disconnect_client(ros["client_id"])
                    logger.log(f'玩家断开连接，因为IP达到最大连接数 || {ros["account_id"]}'  ,
                        "playerjoin")
                    zaqr.sendLog(f'玩家断开连接，因为IP达到最大连接数 || {ros["account_id"]}')
                    continue
            newPlayers.append(ros['account_id'])
            if ros['account_id'] not in self.players and ros[
                'client_id'] != -1:
                # new player joined lobby

                d_str = ros['display_string']
                d_str2 = profanity.censor(d_str)
                try:
                    logger.log(
                        f'{d_str}  || {ros["account_id"]} || 加入服务器！',
                        "playerjoin")
                    logger.log(f'{ros["account_id"]} {ip} {device_id}')
                    zaqr.sendLog(f'{d_str}  || {ros["account_id"]} || 加入服务器！')
                except:
                    pass
                if d_str2 != d_str:
                    _ba.screenmessage(
                        "非法ID！请检查你的ID是否合法",
                        color=(1, 0, 0), transient=True,
                        clients=[ros['client_id']])
                    try:
                        logger.log(f'{d_str} || { ros["account_id"] } || 非法ID被踢出',
                                   "sys")
                        zaqr.sendLog(f'{d_str} || { ros["account_id"] } || 非法ID被踢出')
                    except:
                        pass
                    ba.internal.disconnect_client(ros['client_id'], 1)
                    return

                if settings["whitelist"] and ros["account_id"] != None:
                    if ros["account_id"] not in pdata.CacheData.whitelist:
                        _ba.screenmessage("你不在玩家白名单内，请联系管理员！",
                                          color=(1, 0, 0), transient=True,
                                          clients=[ros['client_id']])
                        logger.log(f'{d_str}  || { ros["account_id"]} | 非白名单被踢出')
                        zaqr.sendLog(f'{d_str} || { ros["account_id"] } || 非白名单被踢出')
                        ba.internal.disconnect_client(ros['client_id'])

                        return

                if ros['account_id'] != None:
                    if ros['account_id'] in serverdata.clients:
                        on_player_join_server(ros['account_id'],
                                              serverdata.clients[
                                                  ros['account_id']], ip)
                    else:
                        LoadProfile(ros['account_id'], ip).start() # from local cache, then call on_player_join_server

        self.players = newPlayers


def on_player_join_server(pbid, player_data, ip):
    global ipjoin
    now = time.time()
    # player_data=pdata.get_info(pbid)
    clid = 113
    device_string = ""
    for ros in ba.internal.get_game_roster():
        if ros["account_id"] == pbid:
            clid = ros["client_id"]
            device_string = ros['display_string']
    if ip in ipjoin:
        lastjoin = ipjoin[ip]["lastJoin"]
        joincount = ipjoin[ip]["count"]
        if now - lastjoin < 15:
            joincount += 1
            if joincount > 2:
                _ba.screenmessage("加入太快了，请慢点...",
                                  color=(1, 0, 1), transient=True,
                                  clients=[clid])
                logger.log(f'{pbid} || 加入过于频繁被踢出')
                zaqr.sendLog(f'{pbid} || 加入过于频繁被踢出')
                ba.internal.disconnect_client(clid)
                _thread.start_new_thread(reportSpam, (pbid,))
                return
        else:
            joincount = 0

        ipjoin[ip]["count"] = joincount
        ipjoin[ip]["lastJoin"] = now
    else:
        ipjoin[ip] = {"lastJoin":now,"count":0}
    if pbid in serverdata.clients:
        serverdata.clients[pbid]["lastJoin"] = now

    if player_data != None: # player data not in serevrdata or in local.json cache
        serverdata.recents.append({"client_id":clid,"deviceId":device_string,"pbid":pbid})
        serverdata.recents = serverdata.recents[-20:]
        if player_data["isBan"] or get_account_age(player_data["accountAge"]) < \
            settings["minAgeToJoinInHours"]:
            for ros in ba.internal.get_game_roster():
                if ros['account_id'] == pbid:
                    if not player_data["isBan"]:
                        _ba.screenmessage(
                            "检测到你是新账户，请稍后再加入...",
                            color=(1, 0, 0), transient=True,
                            clients=[ros['client_id']])
                    logger.log(pbid + " | 检测到封禁账户踢出")
                    zaqr.sendLog(pbid + " | 检测到封禁账户踢出")
                    _ba.screenmessage(
                            "服务器不支持你的账户类型，请联系腐竹",
                            color=(1, 0, 0), transient=True,
                            clients=[ros['client_id']])
                    ba.internal.disconnect_client(ros['client_id'])

            return
        else:
            if pbid not in serverdata.clients:
                if check_ban(clid,pbid):
                    return
                serverdata.clients[pbid] = player_data
                serverdata.clients[pbid]["warnCount"] = 0
                serverdata.clients[pbid]["lastWarned"] = time.time()
                serverdata.clients[pbid]["verified"] = False
                serverdata.clients[pbid]["rejoincount"] = 1
                serverdata.clients[pbid]["lastJoin"] = time.time()
                if not player_data["canStartKickVote"]:
                    _ba.disable_kickvote(pbid)


            serverdata.clients[pbid]["lastIP"] = ip

            device_id = _ba.get_client_public_device_uuid(clid)
            if(device_id==None):
                device_id = _ba.get_client_device_uuid(clid)
            serverdata.clients[pbid]["deviceUUID"] = device_id
            verify_account(pbid, player_data) # checked for spoofed ids
            logger.log(pbid+" ip: "+serverdata.clients[pbid]["lastIP"]+", Device id: "+device_id)
            _ba.screenmessage(settings["regularWelcomeMsg"] + " " + device_string,
                              color=(0.60, 0.8, 0.6), transient=True,
                              clients=[clid])
    else:
        # fetch id for first time.
        thread = FetchThread(
            target=my_acc_age,
            callback=save_age,
            pb_id=pbid,
            display_string=device_string
        )

        thread.start()
        _ba.screenmessage(settings["firstTimeJoinMsg"], color=(0.6, 0.8, 0.6),
                          transient=True, clients=[clid])

    # pdata.add_profile(pbid,d_string,d_string)

def check_ban(clid, pbid):
    ip = _ba.get_client_ip(clid)

    device_id = _ba.get_client_public_device_uuid(clid)
    if(device_id==None):
        device_id = _ba.get_client_device_uuid(clid)
    if (ip in blacklist["ban"]['ips'] or device_id in blacklist['ban']['deviceids'] or pbid in blacklist["ban"]["ids"]):
        _ba.chatmessage('抱歉，你的账户被服主封禁了，联系服主解封吧',clients=[clid])
        logger.log(pbid + " | 被踢出 > 原因: 账户被封禁")
        zaqr.sendLog(pbid + " | 被踢出 > 原因: 账户被封禁")
        ba.internal.disconnect_client(clid)
        return True
    return False

def verify_account(pb_id, p_data):
    d_string = ""
    for ros in ba.internal.get_game_roster():
        if ros['account_id'] == pb_id:
            d_string = ros['display_string']

    if d_string not in p_data['display_string']:

        thread2 = FetchThread(
            target=get_device_accounts,
            callback=save_ids,
            pb_id=pb_id,
            display_string=d_string
        )
        thread2.start()
    else:
        serverdata.clients[pb_id]["verified"] = True


# ============== IGNORE BELOW CODE  =======================

def _make_request_safe(request, retries=2, raise_err=True):
    try:
        return request()
    except:
        if retries > 0:
            time.sleep(1)
            return _make_request_safe(request, retries=retries - 1,
                                      raise_err=raise_err)
        if raise_err:
            raise


def get_account_creation_date(pb_id):
    # thanks rikko
    account_creation_url = "http://bombsquadgame.com/accountquery?id=" + pb_id
    account_creation = _make_request_safe(
        lambda: urllib.request.urlopen(account_creation_url))
    if account_creation is not None:
        try:
            account_creation = json.loads(account_creation.read())
        except ValueError:
            pass
        else:
            creation_time = account_creation["created"]
            creation_time = map(str, creation_time)
            creation_time = datetime.datetime.strptime("/".join(creation_time),
                                                       "%Y/%m/%d/%H/%M/%S")
            # Convert to IST
            creation_time += datetime.timedelta(hours=5, minutes=30)
            return str(creation_time)


def get_device_accounts(pb_id):
    url = "http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID=" + pb_id
    data = _make_request_safe(lambda: urllib.request.urlopen(url))
    if data is not None:
        try:
            accounts = json.loads(data.read())["accountDisplayStrings"]
        except ValueError:
            return ['???']
        else:
            return accounts


# =======  yes fucking threading code , dont touch ==============


# ============ file I/O =============

class LoadProfile(threading.Thread):
    def __init__(self, pb_id, ip):
        threading.Thread.__init__(self)
        self.pbid = pb_id
        self.ip = ip

    def run(self):
        player_data = pdata.get_info(self.pbid)
        _ba.pushcall(Call(on_player_join_server, self.pbid, player_data, self.ip),
                     from_other_thread=True)


# ================ http ================
class FetchThread(threading.Thread):
    def __init__(self, target, callback=None, pb_id="ji",
                 display_string="XXX"):
        super(FetchThread, self).__init__(target=self.target_with_callback,
                                          args=(pb_id, display_string,))
        self.callback = callback
        self.method = target

    def target_with_callback(self, pb_id, display_string):
        data = self.method(pb_id)
        if self.callback is not None:
            self.callback(data, pb_id, display_string)


def my_acc_age(pb_id):
    return get_account_creation_date(pb_id)


def save_age(age, pb_id, display_string):
    _ba.pushcall(Call(pdata.add_profile,pb_id, display_string,display_string, age), from_other_thread=True)
    time.sleep(2)
    thread2 = FetchThread(
        target=get_device_accounts,
        callback=save_ids,
        pb_id=pb_id,
        display_string=display_string
    )
    thread2.start()
    if get_account_age(age) < settings["minAgeToJoinInHours"]:
        msg = "新账户请等待明天再加入awa..."
        logger.log(pb_id + "|| 被踢出 > 新账户加入")
        zaqr.sendLog(pb_id + "|| 被踢出 > 新账户加入")
        _ba.pushcall(Call(kick_by_pb_id, pb_id, msg), from_other_thread=True)


def save_ids(ids, pb_id, display_string):
    pdata.update_display_string(pb_id, ids)

    if display_string not in ids:
        msg = "你的ID是假的，gun"
        _ba.pushcall(Call(kick_by_pb_id, pb_id, msg), from_other_thread=True)
        serverdata.clients[pb_id]["verified"] = False
        logger.log(
            pb_id + "|| 被踢出 使用假ID " + display_string)
        zaqr.sendLog(pb_id + "|| 被踢出 使用假ID " + display_string)
    else:
        serverdata.clients[pb_id]["verified"] = True


def kick_by_pb_id(pb_id, msg):
    for ros in ba.internal.get_game_roster():
        if ros['account_id'] == pb_id:
            _ba.screenmessage(msg, transient=True, clients=[ros['client_id']])
            ba.internal.disconnect_client(ros['client_id'])


def get_account_age(ct):
    creation_time = datetime.datetime.strptime(ct, "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    delta = now - creation_time
    delta_hours = delta.total_seconds() / (60 * 60)
    return delta_hours


def reportSpam(id):
    now = time.time()
    profiles = pdata.get_profiles()
    if id in profiles:
        count = profiles[id]["spamCount"]

        if now - profiles[id]["lastSpam"] < 2 * 24 * 60 * 60:
            count += 1
            if count > 3:
                logger.log(id+" 自动封禁 滥消息")
                zaqr.sendLog(id+" 自动封禁 滥消息")
                profiles[id]["isBan"] = True
        else:
            count = 0

        profiles[id]["spamCount"] = count
        profiles[id]["lastSpam"] = now
        pdata.commit_profiles(profiles)

def on_join_request(ip):
    now = time.time()
    if ip in serverdata.ips:
        lastRequest = serverdata.ips[ip]["lastRequest"]
        count = serverdata.ips[ip]["count"]
        if now - lastRequest < 5:
            count +=1
            if count > 40:
                _ba.ban_ip(ip)
        else:
            count = 0
        serverdata.ips[ip] = {"lastRequest":time.time(),"count":count}
    else:
        serverdata.ips[ip]={"lastRequest":time.time(),"count":0}
