# Released under the MIT License. See LICENSE for details.
sqlfile = "/bss/NewZakara.dmb"
from playersData import pdata
from serverData import serverdata
from chatHandle.ChatCommands import Main
from tools import logger, servercheck
from chatHandle.chatFilter import ChatFilter
from features import EndVote
import sms_tencent
from . import animater
import json
import ba, _ba
import ba.internal
import setting
import zakaraServerTool
import time
#汉化by edMedic
#QQ2091341667
#Email：medic163@163.com/edmedic@outlook.com
#禁止未经授权用于开服
#授权id：82B51274EA94336EB3D7DDEA4D1E738D
settings = setting.get_settings_data()


def filter_chat_message(msg, client_id):
    if client_id == -1:
        if msg.startswith("/"):
            Main.Command(msg, client_id)
            return None
        return msg
    acid = ""
    displaystring = ""
    currentname = ""

    for i in ba.internal.get_game_roster():
        if i['client_id'] == client_id:
            acid = i['account_id']
            try:
                currentname = i['players'][0]['name_full']
            except:
                currentname = "<in-lobby>"
            displaystring = i['display_string']
    if acid:
        msg = ChatFilter.filter(msg, acid, client_id)
    try:
        msg = int(msg)
    except:
        pass
    with open("telist.json") as file:
        telist = dict(json.load(file))
        if acid in list(telist.keys()):
            if telist[acid]["isPass"] == True:
                pass
            else:
                if len(msg) == 6 and type(msg) == int :
                    if int(msg) == telist[acid]["code"]:
                        telist[acid]["isPass"] = True
                        ba.internal.chatmessage("验证码正确！现在您可以进行游戏内聊天了！",client_id)
                        ba.internal.chatmessage("请注意游戏内言行举止，如果您存在恶意聊天消息，将会被封禁！",client_id)
                        ba.internal.chatmessage("您也可以随时举报他人的不文明发言！更多问题请在群内联系服主！",client_id)
                        ba.internal.chatmessage("祝您游戏愉快！",client_id)
                        return None
                    else:
                        ba.internal.chatmessage("验证码错误，请检查！你刚刚输入的验证码是"+str(msg) ,client_id)
                        return None
                else:
                    ba.internal.chatmessage("格式错误！验证码是6位数字！",client_id)
                    return None
        else:
            if len(msg) == 11 and type(msg) == int:

                lastNum = [0,0,0,0]
                for i in msg:
                    lastNum[3] = i
                    if lastNum[0] == lastNum[1] and lastNum[1] == lastNum[2] and lastNum[2] == lastNum[3]:
                        ba.internal.chatmessage("手机号不正确！您不想验证可以不验证",client_id)
                    elif lastNum[0] == lastNum[2] and lastNum[1] == lastNum[3]:
                        ba.internal.chatmessage("手机号不正确！您不想验证可以不验证",client_id)
                    elif lastNum[0]+1 == lastNum[1] and lastNum[1]+1 == lastNum[2] and lastNum[2]+1 == lastNum[3]:
                        ba.internal.chatmessage("手机号不正确！您不想验证可以不验证",client_id)
                    elif lastNum[0]-1 == lastNum[1] and lastNum[1]-1 == lastNum[2] and lastNum[2] -1 == lastNum[3]:
                        ba.internal.chatmessage("手机号不正确！您不想验证可以不验证",client_id)
                telist[acid]["isPass"] = False
                telist[acid]["code"] = None
                ba.internal.chatmessage("您的手机号是"+msg+", 正在发送验证码...",client_id)
                with open("telist.json","w") as f:
                    json.dump(telist,f)
                code = sms_tencent.sendsms(msg)
                telist[acid]["code"] = str(code)
                ba.internal.chatmessage("验证码已发送到您的手机上了，请直接在这里发送您接收到的6位数验证码",client_id)
                return None
            else:
                ba.internal.chatmessage("您好，尊敬的玩家！很抱歉您刚刚的发言被屏蔽了...",client_id)
                ba.internal.chatmessage("近期服务器出现大量不文明发言，包括侮辱性或其他带有攻击性发言等",client_id)
                ba.internal.chatmessage("所以，为了管控这一现象，本服现试开启短信验证来过滤掉低素质人群或其他脚本程序",client_id)
                ba.internal.chatmessage("如果你只是一个普通的玩家，你只需要发送你的手机号然后接收我们的短信验证码即可解除限制",client_id)
                ba.internal.chatmessage("我们不会收取任何费用，也绝不会泄露或出售您的信息，仅作为账户识别来屏蔽掉低素质玩家",client_id)
                ba.internal.chatmessage("如果你已经准备好了，请直接发送您的11位手机号码（手机号不会发给其他人！）",client_id)
                ba.internal.chatmessage("您只有一次机会。如果输入错误，请加群寻找服主帮助",client_id)
                ba.internal.chatmessage("感谢您的配合！如果您有任何意见，欢迎在群内提出！",client_id)
                return None
    with open("telist.json","w") as f:
        json.dump(telist,f)
    if msg == None:
        return
    if msg.startswith("/"):
        Main.Command(msg, client_id)
        return None
    if acid == 'pb-IF4XV3oqVw==':
        return msg
    if "蒙飞" in msg or "飞哥" in msg or "蒙腾" in msg or "官方认证" in msg or "封不了我" in msg or "一群傻逼" in msg or "蒙哥" in msg or "豪哥科技" in msg or "神秋" in msg:
        ba.internal.disconnect_client(int(client_id))
    if "蒙飞" in currentname or "卍" in currentname or "蒙飞" in currentname or "官方认证" in currentname or "卐" in currentname or "神秋" in currentname or "Medic" in currentname:
        ba.internal.disconnect_client(int(client_id))
    if "<in-lobby>" in currentname:
        return None
    if msg.startswith("/"):
        Main.Command(msg, client_id)

    if msg.startswith(",") and settings["allowTeamChat"]:
        return Main.QuickAccess(msg, client_id)
    if msg.startswith(".") and settings["allowInGameChat"]:
        return Main.QuickAccess(msg, client_id)

    if msg == "end" and settings["allowEndVote"]:
        EndVote.vote_end(acid, client_id)

    logger.log(acid + " | " + displaystring + "|" + currentname + "| " + msg, "chat")
    print(acid + " | " + displaystring + "|" + currentname + "| " + msg)
    import sqlite3
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    sql = """INSERT INTO chatmsg(
            time,aid,id,name,text)
            VALUES(?,?,?,?,?)"""
    info = (time.time(),acid,displaystring,currentname,msg)
    c.execute(sql,info)
    conn.commit()
    conn.close()
    if acid in serverdata.clients and serverdata.clients[acid]["verified"]:

        if serverdata.muted:
            _ba.screenmessage("服务器全员禁言中...", transient=True, clients=[client_id])
            return
        elif "mute" in zakaraServerTool.baner(acid):
            _ba.screenmessage("您当前已被管理员或系统禁言，因此你无法发送任何消息\n想获得解禁时间或更多信息，请发送“/封禁查询”", transient=True, clients=[client_id])
            return None
        elif serverdata.clients[acid]["isMuted"]:
            _ba.screenmessage("你被禁言啦～", transient=True, clients=[client_id])
            return None
        elif servercheck.get_account_age(serverdata.clients[acid]["accountAge"]) < settings['minAgeToChatInHours']:
            _ba.screenmessage("新账户不能发言哦～多玩一会儿吧", transient=True, clients=[client_id])
            return None
        else:
            if msg == "":
                animater.message(currentname+"吐了个泡泡",acid)
                return None
            elif msg in ["6","66","666"]:
                animater.message(currentname+"冒了个泡并说6",acid)
                return None
            elif "屎" in msg:
                animater.message(currentname+"发了依托答辩",acid)
                return None
            elif "骚操作" in msg :
                animater.message(currentname+"说你们的操作很骚",acid)
                return None
            elif "合作" in msg :
                animater.message(currentname+"想合作？但是被禁止了",acid)
                return None
            elif "居然能这么玩" in msg:
                animater.message(currentname+"感叹了这把游戏",acid)
                return None
            elif "能别打队友吗" in msg:
                animater.message(currentname+"的队友似乎在打队友？",acid)
                return None
            if "傻" in msg:
                animater.message(currentname+"说了一句话，但是被拦截了",acid)
                return None
            elif "你妈" in msg:
                animater.message(currentname+"问候了某人的母亲",acid)
                return None
            elif "脑残" in msg:
                animater.message(currentname+"表达了不满",acid)
                return None
            elif "爸爸" in msg:
                animater.message(currentname+"似乎有什么不满？",acid)
                return None
            elif "fuck" in msg:
                animater.message(currentname+"seems to be unhappy?",acid)
                return None
            else:
                animater.message(currentname+": "+msg,acid)
                return msg


    else:
        _ba.screenmessage("新账户不能发言哦！请重新加入", transient=True, clients=[client_id])
        return None
