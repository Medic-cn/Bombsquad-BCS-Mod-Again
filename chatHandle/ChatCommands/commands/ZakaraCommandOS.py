#Made by inkMedic Studio 2023 Part 1
#扎卡拉指令系统 作者：inkMedic QQ2091341667 小群5527575487。
#作为服主，您可以在征得作者同意后使用扎卡拉指令系统，但如果您私自贩卖、出售本代码，我们将移交公安机关并依法处理。
#切勿私自修改版权信息，违者服务器发现将被攻击，包含但不限于以下手段：ddos，udpDos，端口爆破，网络劫持，自己看着办。
from .Handlers import handlemsg, handlemsg_all,send
from playersData import pdata
import ba.internal
import ba
import _ba
import bastd
import _thread
import time
import datetime
import sys
import random
from . import WsdxCommands
from . import Fun
from . import Cheats
from . import Management
from . import animater
from . import zaqr
sqlfile = "/bss/NewZakara.dmb"
version = str("3.0正式版Beta")
servername = str("鲨鱼俱乐部(SharkParty_CN_1)")
cmd = ["ban","mute","封禁","禁言",'启动扎卡拉','注册',"封禁查询",'注册喵','签到喵',"发红包","srp",
       "领红包","QQ","抢红包","grp",'我自己喵','我自己','签到',"刷新商店","商店",'购买',"背包",'fly', 
       'inv', 'hl', 'creepy', 'celeb', 'speed', 'flo','egg',"喵喵彩蛋","胜利动作","飞行指令","隐身指令",
       "回血指令","欢呼礼包","无人机","竞猜","生成机器人","makebot","mb","出拳力量","punchpower","pp","出拳间隔",
       "punchtime","pt","控制机器人","ctrlbot","cb","游泳指令","swim","设置玩家人数","setplayernum","sp","TNT炸弹",
       "闪光色","ai内杠","AI内杠","Ai内杠","kill","cur","sleep","punch","shield","freeze","unfreeze","gm","speed",
       "运行速度","杀人指令","诅咒指令","昏迷指令","拳套指令","护盾指令","冰冻指令","解冻指令","无敌指令","sm","史诗指令",
       "购买头衔","更改头衔","续费头衔","续费特效","购买特效","help","帮助"]
runNum = 1
storeNum = 0
flyNum=invNum=hlNum=creepyNum=celebNum=floNum=speedNum=randomColorNum=TNTBombNum=swimNum=ctrlbotNum=punchtimeNum=makebotNum=aiangryNum=punchpowerNum=killNum=curNum=sleepNum=punchNum=shieldNum=gmNum=unfreezeNum=freezeNum=smNum = 0
storeList=["fly","inv","hl","creepy","celeb","flo","aiangry","randomColor","TNTBomb","swim","punchtime","makebot","freeze","unfreeze","gm","shield","kill","cur","sleep","punch","speed","sm"]
storeListR=[2,2,2,1,3,1,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2]

def cmdCenter(cmd,agu,cid,aid):
    import sqlite3
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    sql = """INSERT INTO cmdlog(
            cmd,agu,aid,cid,return)
            VALUES(?,?,?,?,?)"""
    info = (cmd,str(agu),aid,cid,time.time())
    print(info)
    c.execute(sql,info)
    conn.commit()
    conn.close()
    if cmd == "启动扎卡拉":
        runcmd(cmd,agu,cid,aid)
    elif cmd == "QQ":
        Account.changeqq(cmd,agu,cid,aid)
    elif cmd == "购买头衔":
        Store.settag(cmd,agu,cid,aid)
    elif cmd == "更改头衔":
        Store.changetag(cmd,agu,cid,aid)
    elif cmd == "续费头衔":
        Store.renewaltag(cmd,agu,cid,aid)
    elif cmd == "刷新商店":
        Store.NewStoreThings(aid)
    elif cmd in ["注册","注册喵"]:
        CMDCenter.register_cmd(cmd,agu,cid,aid)
    elif cmd in ["发红包","srp"]:
        Store.sendRedPacket(cmd,agu,cid,aid)
    elif cmd in ["领红包","抢红包","grp"]:
        Store.getRedPacket(cmd,agu,cid,aid)
    elif cmd in ["我自己喵","我自己"]:
        CMDCenter.getInformation(cmd,agu,cid,aid)
    elif cmd in ["背包"]:
        CMDCenter.bag(cmd,agu,cid,aid)
    elif cmd in ["签到喵","签到"]:
        CMDCenter.getpass(cmd,agu,cid,aid)
    elif cmd in ['fly', 'inv', 'hl', 'creepy', 'celeb', 'speed', 'flo','egg',"飞行指令","隐身指令","回血指令","欢呼礼包","无人机","喵喵彩蛋","生成机器人","makebot","mb","出拳力量","punchpower","pp","出拳间隔","punchtime","pt","控制机器人","ctrlbot","cb","游泳指令","swim","设置玩家人数","setplayernum","sp","TNT炸弹","闪光色","ai内杠","AI内杠","Ai内杠","kill","cur","sleep","punch","shield","freeze","unfreeze","gm","运行速度","杀人指令","诅咒指令","昏迷指令","拳套指令","护盾指令","冰冻指令","解冻指令","无敌指令","sm","史诗指令"]:
        CMDCenter.usecmd(cmd,agu,cid,aid)
    elif "商店" in cmd:
        CMDCenter.fishstore(cmd,agu,cid,aid)
    elif "购买特效" in cmd:
        Store.seteffect(cmd,agu,cid,aid)
    elif "续费特效" in cmd:
        Store.renewaleffect(cmd,agu,cid,aid)
    elif cmd == "购买":
        CMDCenter.buything(cmd,agu,cid,aid)
    elif "竞猜" in cmd:
        CMDCenter.funcoin(cmd,agu,cid,aid)
    elif cmd == "help" or cmd == "帮助":
        CMDCenter.helper(cmd,agu,cid,aid)
    elif cmd in ["封禁","ban"]:
        Account.baner(cmd,agu,cid,aid)
    elif cmd in ["禁言","mute"]:
        Account.muter(cmd,agu,cid,aid)
    elif cmd in ["封禁查询"]:
        Account.checkbaner(cmd,agu,cid,aid)
class CMDCenter:
    def helper(cmd,agu,cid,aid):
        send("你好喵，我是zakara，我的中文名是扎卡拉",cid)
        send("我是这个服务器的指令系统喵，负责给你们提供好玩的服务",cid)
        send("喵喵你是新人嘛，跟我一起来熟悉服务器吧喵",cid)
        send("=====================================",cid)
        send("首先我是可以操控游戏的，比如放慢速度（史诗级），或者变出一个无人机喵",cid)
        send("各种好玩的我都可以给你们变出来喵，你只需要用指令告诉我需要什么喵",cid)
        send("当然喵喵也是会累的，所以我发明了背包喵，喏，送你",cid)
        send("既然你是新朋友，那喵喵就送你10个喵喵彩蛋吧喵",cid)
        send("你的背包已经存放喵喵彩蛋了，发送“/背包”就可以查看和使用它了喵",cid)
        send("如果背包的东西用完的话，你也可以来我的喵喵商店购买哦喵~",cid)
        send("不过来喵喵商店得先带足够的小鱼干（它是我们的货币），发送“/商店”即可",cid)
        send("商店有很多东西，但每天只能刷新一次，如果商店没有的话就买不到喵",cid)
        send("喵喵有时也会打瞌睡，所以如果有人利用bug请及时告诉本喵！",cid)
        send("喏，先送你一点小鱼干吧~",cid)
        send("如果小鱼干花完了别着急找我要，你可以通过每日签到获取小鱼干喵",cid)
        send("每次签到获得的小鱼干数量是随机的，就看你的运气了喵",cid)
        send("如果觉得签到太少了，可以试试输入“/竞猜”参与竞猜喵",cid)
        send("游戏规则是，如果你竞猜80小鱼干，你有可能获得80小鱼干，也可能什么事都没有",cid)
        send("当然，你也有可能被扣除80小鱼干喵，每一种结果都是随机的",cid)
        send("或者喵喵建议你去领红包哦，服务器时不时会有人发红包的喵",cid)
        send("对了，如果你想像他们一样有炫酷的头衔和特效，你可以用",cid)
        send("“/购买头衔”或“/购买特效”来购买喵🐱每次购买都会花费小鱼干",cid)
        send("那么到这里就结束了，如果还有对喵喵的疑惑欢迎来QQ群找我喵，我就先走啦",cid)
    def register_cmd(cmd,agu,cid,aid):
        if cmd in ["注册喵","注册"]:
            if agu ==[] or agu==['']:
                send("注册请输入”/注册喵 名字 QQ号“~~喵",cid)
                return
            name = agu[0]
            qqnum = agu[1]
        if name == "名字":
            send("让你输入你的游戏名，不是让你输入“名字”这俩字啊喂！！！~",cid)
            return
        if qqnum == "QQ号" or "qq" in qqnum:
            send("让你输入QQ号，不是让你输入“QQ”号这俩字啊喂~！！",cid)
            return
        Account.register(aid,name,qqnum,cid)
    def fishstore(cmd,agu,cid,aid):

        catcoin = Coin.getcoin(Getter.getzaid(aid))
        send("                      ========",cid)
        send("          ======小鱼干商店=====",cid)
        send("=【 今日特惠！   喵喵彩蛋  （180/枚）】 =",cid)
        if celebNum == 1:
            send("=【 ->指令区    胜利动作   （10/次） 】 =",cid)
        if flyNum == 1:
            send("=【 ->指令区    飞行指令   （20/次） 】 =",cid)
        if invNum == 1:
            send("=【 ->指令区    隐身指令   （20/次） 】 =",cid)
        if hlNum == 1:
            send("=【 ->指令区    回血指令   （20/次） 】 =",cid)
        if creepyNum == 1:
            send("=【 ->指令区    欢呼礼包   （60/次） 】 =",cid)
        if speedNum == 1:
            send("=【 ->指令区    运行速度  （40/次） 】 = ",cid)
        if killNum == 1:
            send("=【 ->指令区    杀人指令  （15/次） 】 = ",cid)
        if curNum == 1:
            send("=【 ->指令区    诅咒指令   （20/次） 】 =",cid)
        if sleepNum == 1:
            send("=【 ->指令区    昏迷指令   （15/次） 】 =",cid)
        if smNum == 1:
            send("=【 ->指令区    史诗指令   （40/次） 】 =",cid)
        if punchNum == 1:
            send("=【 ->道具区    拳套指令   （20/次） 】 =",cid)
        if shieldNum == 1:
            send("=【 ->道具区    护盾指令   （20/次） 】 =",cid)
        if freezeNum == 1:
            send("=【 ->道具区    冰冻指令   （20/次） 】 =",cid)
        if unfreezeNum == 1:
            send("=【 ->道具区    解冻指令   （20/次） 】 =",cid)
        if gmNum == 1:
            send("=【 ->指令区    无敌指令   （50/次） 】 =",cid)
        send("=【 ->鬼畜区    压缩毛巾   （9.9包邮） 】 =",cid)
        send("=【 ->鬼畜区      饼干    （9.9包邮） 】 =",cid)
        if floNum == 1:
            send("=【 ->指令区    无人机     （200/次） 】 =",cid)
        if aiangryNum == 1:
            send("=【 ->指令区    AI内杠    （20/次） 】 =",cid)
        if makebotNum == 1:
            send("=【 ->指令区    生成机器人   （30/次） 】 =",cid)
        if punchtimeNum == 1:
            send("=【 ->指令区    出拳间隔     （50/次） 】 =",cid)
        if punchpowerNum == 1:
            send("=【 ->指令区    出拳力量     （50/次） 】 =",cid)
        if ctrlbotNum == 1:
            send("=【 ->指令区    控制机器人     （20/次） 】 =",cid)
        if swimNum == 1:
            send("=【 ->指令区    游泳指令     （50/次） 】 =",cid)
        if TNTBombNum == 1:
            send("=【 ->指令区    TNT炸弹     （20/次） 】 =",cid)
        if randomColorNum == 1:
            send("=【 ->指令区    闪光色     （100/次） 】 =",cid)
        send("tips:你有"+str(catcoin)+"块小鱼干喵~~~",cid)
        send("tips:输入“/购买 商品名”即可购买！例如“/购买 飞行指令”",cid)
        send("tips:输入“/刷新商店”可刷新商店内物品噢",cid)
    def getInformation(cmd,agu,cid,aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        zaid = Getter.getzaid(aid)
        sql = f"""SELECT effecttime
                  FROM player
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        try:
            et = int(getreturn[0][0])
        except:
            et = "None"
        sql = f"""SELECT tagtime
                  FROM player
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        try:
            tt = int(getreturn[0][0])
        except:
            tt = "None"
        if et == "None" or et == "":
            eft = "无"
        else:
            eft = time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(et))
        if tt == "None" or tt == "":
            tat = "无"
        else:
            tat = time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(tt))
        if agu ==[] or agu==['']:
            inf = c.execute(f"""SELECT *
                            from player 
                            WHERE zaid ='{zaid}';""")
            inf = inf.fetchone()
            send("|===喵喵小档案=( •̀ ω •́ )✧==|",cid)
            send("|====================== |",cid)
            send("|==喵ID---->        "+str(inf[0])+"喵~",cid)
            send("|==唯一标识符---->"+inf[1]+"喵~",cid)
            send("|==喵名----> "+inf[2]+"喵~",cid)
            send("|==QQ---->  "+str(inf[3])+"喵~",cid)
            send("|==注册时间---->  "+inf[4]+"喵~",cid)
            send("|==头衔到期时间：==="+tat+"== |",cid)
            send("|=特效到期时间：====="+eft+"== |",cid)
            send("|====================== |",cid)
            send("|===当前版本："+version+"=== |",cid)
        conn.close()
    def bag(cmd,agu,cid,aid):
            import sqlite3
            conn = sqlite3.connect(sqlfile)
            c = conn.cursor()
            send("|=========喵喵背包======",cid)
            send("|======================",cid)
            zaid = Getter.getzaid(aid)
            coin = Coin.getcoin(zaid)
            inf = c.execute(f"""SELECT *
                            FROM bag1
                            WHERE ZAID ='{zaid}';""")
            inf = inf.fetchone()
            if int(inf[3]) != 0:
                send("|===飞行指令 x"+str(inf[3]),cid)
            if int(inf[4]) != 0:
                send("|===隐身指令 x"+str(inf[4]),cid)
            if int(inf[5]) != 0:
                send("|===回血指令 x"+str(inf[5]),cid)
            if int(inf[6]) != 0:
                send("|===欢呼礼包 x"+str(inf[6]),cid)
            if int(inf[7]) != 0:
                send("|===胜利动作 x"+str(inf[7]),cid)
            if int(inf[8]) != 0:
                send("|===无人机  x"+str(inf[8]),cid)
            if int(inf[9]) != 0:
                send("|===喵喵彩蛋 x"+str(inf[9]),cid)
            if int(inf[10]) != 0:
                send("|===闪光色 x"+str(inf[10]),cid)
            if int(inf[11]) != 0:
                send("|===TNT炸弹 x"+str(inf[11]),cid)
            if int(inf[12]) != 0:
                send("|===设置玩家人数 x"+str(inf[12]),cid)
            if int(inf[13]) != 0:
                send("|===游泳指令 x"+str(inf[13]),cid)
            if int(inf[14]) != 0:
                send("|===控制机器人 x"+str(inf[14]),cid)
            if int(inf[15]) != 0:
                send("|===出拳间隔 x"+str(inf[15]),cid)
            if int(inf[16]) != 0:
                send("|===生成机器人 x"+str(inf[16]),cid)
            if int(inf[17]) != 0:
                send("|===AI内杠 x"+str(inf[17]),cid)
            if int(inf[18]) != 0:
                send("|===出拳力量 x"+str(inf[18]),cid)
            if int(inf[19]) != 0:
                send("|===无敌指令 x"+str(inf[19]),cid)
            if int(inf[28]) != 0:
                send("|===史诗指令 x"+str(inf[28]),cid)
            if int(inf[20]) != 0:
                send("|===解冻指令 x"+str(inf[20]),cid)
            if int(inf[21]) != 0:
                send("|===冰冻指令 x"+str(inf[21]),cid)
            if int(inf[22]) != 0:
                send("|===护盾指令 x"+str(inf[22]),cid)
            if int(inf[23]) != 0:
                send("|===拳套指令 x"+str(inf[23]),cid)
            if int(inf[24]) != 0:
                send("|===昏迷指令 x"+str(inf[24]),cid)
            if int(inf[25]) != 0:
                send("|===诅咒指令 x"+str(inf[25]),cid)
            if int(inf[26]) != 0:
                send("|===杀人指令 x"+str(inf[26]),cid)
            if int(inf[27]) != 0:
                send("|===运行速度 x"+str(inf[27]),cid)
            send("====小鱼干 x"+str(coin),cid)
            send("发送/物品名 即可使用物品！如：“/无人机”",cid)
            conn.close()
    def getpass(cmd,agu,cid,aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        time = Getter.gettime(3)
        zaid = Getter.getzaid(aid)
        name = Getter.getname(zaid)
        inf = c.execute(f"""SELECT lastpass
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        lasttime = inf[0]
        if lasttime == time:
            send("您今日已经签过到了喵~",cid)
            send("明天再来吧喵~",cid)
        else:
            coin = random.randint(10,60)
            Coin.addcoin(zaid,coin)
            catcoin = Coin.getcoin(zaid)
            sql = f"""UPDATE player
                  SET lastpass = '{time}'
                  WHERE zaid ='{zaid}';"""
            c.execute(sql)
            conn.commit()
            if coin > 40:
                send("手气不错喵，努力签到吧~获得"+str(coin)+"块小鱼干",cid)
            elif coin < 20:
                send("啊噢，手气很糟糕呢，明天换个姿势再试试喵~获得"+str(coin)+"块小鱼干",cid)
            else:
                send("喵喵奖励你"+str(coin)+"块小鱼干喵~",cid)
            send("签到成功喵现在你有 "+str(catcoin)+" 块小鱼干喵~",cid)
            animater.animater("签到",name,coin,None)
        conn.close()
    def buything(cmd,agu,cid,aid):
        thing = agu[0]
        zaid = Getter.getzaid(aid)
    
        if thing == "喵喵彩蛋":
            thing = "egg"
            money = 180
            Store.buyer(zaid,thing,money,cid)
        elif thing == "胜利动作":
            if celebNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "celeb"
            money = 10
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/celeb",cid)
        elif thing == "飞行指令":
            if flyNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "fly"
            money = 20
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/fly",cid)
        elif thing == "隐身指令":
            if invNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "inv"
            money = 20
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/inv",cid)
        elif thing == "回血指令":
            if hlNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "hl"
            money = 20
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/hl",cid)
        elif thing == "欢呼礼包":
            if creepyNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "creepy"
            money = 10
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/creepy",cid)
        elif thing == "无人机":
            if floNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "flo"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/flo",cid)
        elif thing == "饼干":
            send("什么？这不是饼干，这是压缩毛巾",cid)
            send("我们这个压缩毛巾体积小方便携带，拆开一包，放水里就变大，怎么扯都扯不坏，用来擦脚，擦脸，擦嘴都是很好用的，你看打开以后像圆饼一样大小，放在水里遇水变大变高，吸水性很强的。打开以后，是一条加大加厚的毛巾，你看他怎么挣都挣不坏，好不掉毛不掉絮，使用七八次都没问题，出差旅行带上它非常方便，用它擦擦脚，再擦擦嘴，擦擦脸，干净卫生。什么?在哪里买?下方小黄车，买五包送五包，还包邮",cid)
        elif thing == "压缩毛巾":
            send("我们这个压缩毛巾体积小方便携带，拆开一包，放水里就变大，怎么扯都扯不坏，用来擦脚，擦脸，擦嘴都是很好用的，你看打开以后像圆饼一样大小，放在水里遇水变大变高，吸水性很强的。打开以后，是一条加大加厚的毛巾，你看他怎么挣都挣不坏，好不掉毛不掉絮，使用七八次都没问题，出差旅行带上它非常方便，用它擦擦脚，再擦擦嘴，擦擦脸，干净卫生。什么?在哪里买?下方小黄车，买五十包送一包，还包邮!",cid)
        elif thing == "无敌指令":
            if gmNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "gm"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/freeze",cid)
        elif thing == "解冻指令":
            if unfreezeNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "unfreeze"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/unfreeze",cid)
        elif thing == "冰冻指令":
            if freezeNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "freeze"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/freeze",cid)
        elif thing == "护盾指令":
            if shieldNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "shield"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/shield",cid)
        elif thing == "拳套指令":
            if punchNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "punch"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/punch",cid)
        elif thing == "昏迷指令":
            if sleepNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "sleep"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/sleep",cid)
        elif thing == "诅咒指令":
            if curNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "cur"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/cur",cid)
        elif thing == "杀人指令":
            if killNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "kill"
            money = 200
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/kill",cid)
        elif thing == "生成机器人":
            if makebotNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "makebot"
            money = 30
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/生成机器人 种类",cid)
        elif thing == "出拳力量":
            if punchpowerNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "punchpower"
            money = 50
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/pp 数字",cid)
        elif thing == "史诗指令":
            if smNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "sm"
            money = 40
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/sm",cid)
        elif thing == "出拳间隔":
            if punchtimeNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "punchtime"
            money = 50
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/pt 数字",cid)
        elif thing == "控制机器人":
            if ctrlbotNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "ctrlbot"
            money = 20
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/控制机器人",cid)
        elif thing == "游泳指令":
            if swimNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "swim"
            money = 10
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/游泳指令",cid)
        elif thing == "TNT炸弹":
            if TNTBombNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "TNTBomb"
            money = 20
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/TNT炸弹",cid)
        elif thing == "闪光色":
            if randomColorNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "randomColor"
            money = 100
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/闪光色",cid)
        elif thing == "AI内杠":
            if aiangryNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "aiangry"
            money = 25
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/ai内杠",cid)
        elif thing == "运行速度":
            if speedNum == 0:
                send("emm...这个指令貌似没出售哦~",cid)
                return
            thing = "speed"
            money = 40
            Store.buyer(zaid,thing,money,cid)
            send("tips:指令使用方法：/speed 数字",cid)
        elif thing == "？":
            send("？？？？",cid)
            return
    def funcoin(cmd,agu,cid,aid):
        zaid =  Getter.getzaid(aid)
        if agu ==[] or agu==['']:
            send("输入“/竞猜 金额”参与竞猜喵~~例如“/竞猜 20”",cid)
            return
        coin = agu[0]
        coin = int(coin)
        if coin > Coin.getcoin(zaid):
            send("喵呜你没有足够的钱参与竞猜喵！😖",cid)
            return
        if coin < 10:
            send("竞猜金额太少了喵！！😖",cid)
            return
        things = ["Yes","ok","No"]
        choice = [1,1,1]
        YorN = random.choices(things,weights=choice,k=1)
        YorN = YorN[0]
        if YorN == "Yes":
            Coin.addcoin(zaid,coin)
            send(str("恭喜"+Getter.getname(zaid)+"竞猜成功✅获得"+str(coin)+"小鱼干喵"),cid)
            animater.animater("竞猜成功✅",Getter.getname(zaid),coin,None)
        elif YorN == "ok":
            send(str(Getter.getname(zaid)+"没有竞猜成功😖没有获得小鱼干喵"),cid)
            animater.animater("竞猜中立💫",Getter.getname(zaid),None,None)
        elif YorN == "No":
            Coin.usecoin(zaid,coin)
            send(str("啊噢，"+Getter.getname(zaid)+"竞猜失败了❌扣除"+str(coin)+"小鱼干喵"),cid)
            animater.animater("竞猜失败❌",Getter.getname(zaid),coin,None)
    def usecmd(cmd,agu,cid,aid):

        zaid = Getter.getzaid(aid)
        if cmd in ["flo","无人机"]:
            thing = "flo"
        elif cmd in ["egg","喵喵彩蛋"]:
            thing = "egg"
        elif cmd in ["creepy","欢呼礼包"]:
            thing = "creepy"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["inv","隐身指令"]:
            thing = "inv"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["gm","无敌指令"]:
            thing = "gm"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/gm 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["unfreeze"," 解冻指令"]:
            thing = "unfreeze"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["freeze","冰冻指令"]:
            thing = "freeze"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["shield","护盾指令"]:
            thing = "shield"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["punch","拳套指令"]:
            thing = "punch"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["sleep","昏迷指令"]:
            thing = "sleep"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["cur","诅咒指令"]:
            thing = "cur"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["kill","杀人指令"]:
            thing = "kill"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
            elif agu == "all":
                send("你是来回报社会的吗",cid)
        elif cmd in ["hl","回血指令"]:
            thing = "hl"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["fly","飞行指令"]:
            thing = "fly"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["celeb","胜利动作"]:
            thing = "celeb"
            if agu ==[] or agu==['']:
              send("请输入玩家id喵！例如“/fly 2”",cid)
              send("查看玩家id请发送“/list”",cid)
              send("如果对象是全体玩家，请用all，例如“/fly all”",cid)
              return
        elif cmd in ["ai内杠","AI内杠","Ai内杠"]:
            thing = "aiangry"
            helptext = "执行失败，请联系管理员！"
        elif cmd in ["闪光色"]:
            thing = "randomColor"
            helptext = "执行失败，请联系管理员！"
        elif cmd in ["TNT炸弹"]: 
            thing = "TNTBomb"
            helptext = "执行失败，请联系管理员！"
        elif cmd in ["sm","史诗指令"]: 
            thing = "sm"
            helptext = "执行失败，请联系管理员！"
        elif cmd in ["设置玩家人数","setplayernum","sp"]:
            thing = "setplayernum"
            helptext = "请设置玩家人数！例如：/设置玩家人数 8"
            if agu ==[] or agu==['']:
                send(helptext,cid)
        elif cmd in ["游泳指令","swim"]:
            thing = "swim"
            helptext = "执行失败，请联系管理员！"
        elif cmd in ["控制机器人","ctrlbot","cb"]:
            thing = "ctrlbot"
            helptext = "执行失败，请联系管理员！"
        elif cmd in ["出拳间隔","punchtime","pt"]:
            thing = "punchtime"
            helptext = "请输入出拳间隔时间！例如：/出拳间隔 0.1"
            if agu ==[] or agu==['']:
                send(helptext,cid)
                return
        elif cmd in ["运行速度","speed"]:
            thing = "speed"
            helptext = "请输入运行倍速！例如：/speed 2"
            if agu ==[] or agu==['']:
                send(helptext,cid)
                return
            elif int(agu[0]) > 3:
                send("运行倍速不得大于3！",cid)
                return
        elif cmd in ["出拳力量","punchpower","pp"]:
            thing = "punchpower"
            helptext = "请输入力量数值！例如：/出拳力量 4"
            if agu ==[] or agu==['']:
                send(helptext,cid)
        elif cmd in ["生成机器人","makebot","mb"]:
            thing = "makebot"
            helptext = "执行失败，请联系管理员❌"
 #           helptext = "请输入生成玩家和机器人种类！例如/生成机器人 1 BomberBot"
        yn = Store.usething(zaid,thing,cid)
        if yn == False:
            return
#            helptext2 = "常见的机器人种类：[BomberBot,BrawlerBot,TriggerBot,ChargerBot,BomberBotPro,BrawlerBotPro,TriggerBotPro,BomberBotProShielded,ExplodeyBot,ChargerBotProShielded,StickyBot,BrawlerBotProShielded,TriggerBotProShielded]"
        if thing in ["randomColor","TNTBomb","setplayernum","swim","ctrlbot","punchtime","makebot","aiangry"]:
            nyn = WsdxCommands.commandCheck(cmd,agu,cid,aid)
            if nyn != True:
                send(helptext,cid)
                return

        if thing == "flo":
            Fun.floater(agu,cid)
        elif thing == "egg":
            Store.egger(cmd,agu,cid,aid)
        elif thing == "creepy":
            Fun.creep(agu)
        elif thing == "inv":
            Fun.invi(agu)
        elif thing == "hl":
            Fun.headless(agu)
        elif thing == "fly":
            Fun.fly(agu)
        elif thing == "celeb":
            Fun.celeb(agu)
        elif thing == "sm":
            Management.slow_motion()
        elif thing == "kill":
            Cheats.kill(agu,cid)
        elif thing == "cur":
            Cheats.curse(agu,cid)
        elif thing == "sleep":
            Cheats.sleep(agu,cid)
        elif thing == "punch":
            Cheats.gloves(agu,cid)
        elif thing == "shield":
            Cheats.shield(agu,cid)
        elif thing == "freeze":
            Cheats.freeze(agu,cid)
        elif thing == "unfreeze":
            Cheats.un_freeze(agu,cid)
        elif thing == "gm":
            Cheats.god_mode(agu,cid)
        elif thing == "speed":
            Fun.speed(agu)
            if nyn != True:
                send(helptext,cid)
        send("指令使用成功喵✅感觉背包少了些什么喵...",cid)
        name = Getter.getname(zaid)
        animater.animater("使用指令",Getter.getname(zaid),None,cmd)
def runcmd(cmd,agu,cid,aid):
    pass
class Getter:
    def getprice(thing):
        things = {"ice": 30,"sweat":40,"scorch": 30,"glow":20,"distortion":40,"slime": 30,"metal":30,"surrounder":40,"spark":300}
        print(things[thing])
        return things[thing]
    def getthingname(cnname):
        things = {"冰粒特效":"ice","火焰特效":"sweat","发光特效":"glow","闪光特效":"scorch","粘弹碎屑":"slime","烟雾特效":"distortion","金属碎屑":"metal","兔几附身":"surrounder","神":"spark"}
        print(things[cnname])
        return things[cnname]
    def gettime(t):
        if t == 3:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            return current_date
        now = int(time.time())
        timeArr = time.localtime(now)
        other_StyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArr)
        return other_StyleTime
    def gettimes():
        nowttime = int(time.time())
        return nowttime
    def getzaid(aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT zaid
                        from player 
                        WHERE PBID ='{aid}';""")
        inf = inf.fetchone()
        catcoin = inf[0]
        conn.close()
        return catcoin
    def getname(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT NAME
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        name = inf[0]
        conn.close()
        return name

class Account:
    def checkbaner(cmd,agu,cid,aid):
        mute = "None"
        ban = "None"
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT bant
                            from baner 
                            WHERE PBID ='{aid}';""")
        inf = inf.fetchall()
        inf = list(map(lambda x:x[0],inf))
        if not inf:
            ban = "None"
        else:
            for l in inf:
                for i in l:
                    if "None" in i:
                        continue
                    elif int(i)>Getter.gettimes():
                        ban=int(i)
                        break
                    else:
                        ban = "None"
        inf2 = c.execute(f"""SELECT mutet
                            from baner 
                            WHERE PBID ='{aid}';""")
        inf2 = inf2.fetchall()
        inf2 = list(map(lambda x:x[0],inf2))
        if not inf2:
            mute = "None"
        else:
            try:
                for l in inf2:
                    for i in l:
                        if "None" in i:
                            continue
                        elif int(i)>Getter.gettimes():
                            mute=int(i)
                            break
                        else:
                            mute = "None"
            except:
                mute = "None"
        conn.close()
        send("===当前账户封禁查询⚽===",cid)
        if ban != "None":
            send("-----❌封禁中...",cid)
            send("--------解禁时间："+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ban)),cid)
        if mute != "None":
            send("-----😶禁言中...",cid)
            send("-------解禁时间："+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mute)),cid)
        if mute == "None" and ban == "None":
            send("没有任何限制，现在，你的账户很干净！🫡",cid)
        send("（如有任何问题 请联系系统管理员获取支持🚩）",cid)
    def baner(cmd,agu,cid,aid):
        try:
            banid = agu[0]
        except:
            send("请输入正确的值（/ban 他的id 时间）",cid)
            return
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT id
                  FROM admin;"""
        results = c.execute(sql)
        admin = results.fetchall()
        admin = list(map(lambda x:x[0],admin))
        if aid not in admin:
            send("你并没有权限执行这些功能😶",cid)
            return
        banid = agu[0]
        bant = Getter.gettimes()+int(agu[1])*3600
        if 2==1+1:
            for ros in ba.internal.get_game_roster():
                print(ros)
                print(banid)
                if str(ros["client_id"])==banid:
                    device_id = _ba.get_client_public_device_uuid(cid)
                    if(device_id==None):
                        device_id = _ba.get_client_device_uuid(cid)
                    banids = (ros['account_id'])
                    sql = """INSERT INTO baner(
                            PBID,device,bant,mutet,maker,time)
                            VALUES(?,?,?,?,?,?);"""
                    inf = (banids,device_id,str(bant),"None",aid,Getter.gettimes())
                    print(sql)
                    print(inf)
                    c.execute(sql,inf)
                    ba.internal.disconnect_client(int(banid))
          #  except:
            #    send("请输入正确的值（/ban 他的id 时间）",cid)
        conn.commit()
        conn.close()
    def muter(cmd,agu,cid,aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT id
                  FROM admin;"""
        results = c.execute(sql)
        admin = results.fetchall()
        admin = list(map(lambda x:x[0],admin))
        print(admin)
        if aid not in admin:
            send("你并没有权限执行这些功能😶",cid)
            return
        try:
            banid = agu[0]
        except:
            send("请输入正确的值（/mute 他的id 时间）",cid)
            return

        bant = Getter.gettimes()+int(agu[1])*3600
        if 1==1:
            for ros in ba.internal.get_game_roster():
                if str(ros["client_id"])==banid:
                    device_id = _ba.get_client_public_device_uuid(cid)
                    if(device_id==None):
                        device_id = _ba.get_client_device_uuid(cid)
                    banids = (ros['account_id'])
                    sql = """INSERT INTO muter(
                                 PBID,device,bant,mutet,maker,time)
                                 VALUES(?,?,?,?,?,?);"""
                    inf = (banids,device_id,"None",str(bant),aid,Getter.gettimes())
                    c.execute(sql,inf)          
        conn.commit()
        conn.close()
        
    def changeqq(cmd,agu,cid,aid):
        if agu[0]== "" or agu[0] == " ":
            send("请输入你要更改的QQ号！",cid)
            return
        zaid = Getter.getzaid(aid)
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT QQ
                    FROM player
                    WHERE zaid = '{zaid}';"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        oqq = getreturn[0][0]
        if oqq != "None":
            send("请到服主那里更改QQ",cid)
            return
        qq = agu[0]
        try:
            qq = int(qq)
            qq = str(qq)
            if len(qq)<8 or len(qq)>10:
                send("请输入正确的QQ号❌",cid)
                conn.close()
                return
        except:
            send("请输入正确的QQ号❌",cid)
            conn.close()
            return
        sql = f"""UPDATE player
                  SET QQ = '{qq}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        conn.close()
        send("更改成功！喵喵欢迎您",cid)
    def geteffect(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT effect
                    FROM player
                    WHERE zaid = '{zaid}';"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        conn.close()
        tag = getreturn[0][0]
        print(tag)
        if tag == None:
            return "None"
        elif tag == "None":
            return "None"
        elif tag == "":
            return "None"
        else:
            return tag
    def seteffect(zaid,tag):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""UPDATE player
                  SET effect = '{tag}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        sql = f"""SELECT PBID
                FROM player
                WHERE zaid = '{zaid}';"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        aid = getreturn[0][0]
        pdata.set_effect(tag,aid)
        tagtime = Getter.gettimes()
        tagt = tagtime + 2592000
        tagt = int(tagt)
        sql = f"""UPDATE player
                  SET effecttime = '{tagt}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        conn.close()
        return True
    def renewaleffect(zaid,m):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT effecttime
                  FROM player
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        t = int(getreturn[0][0])
        tagt = t + m*2592000
        sql = f"""UPDATE player
                  SET effecttime = '{tagt}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        conn.close()
        return True
    def gettag(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        if zaid == "all":
            sql = f"""SELECT tag
                FROM player;"""
        else:
            sql = f"""SELECT tag
                    FROM player
                    WHERE zaid = '{zaid}';"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        conn.close()
        if zaid == "all":
            return getreturn
        tag = getreturn[0][0]
        if tag == None:
            return "None"
        elif tag == "None":
            return "None"
        elif tag == "":
            return "None"
        else:
            return tag
    def settag(zaid,tag):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""UPDATE player
                  SET tag = '{tag}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        sql = f"""SELECT PBID
                FROM player
                WHERE zaid = '{zaid}';"""
        results = c.execute(sql)
        conn.commit()
        getreturn = results.fetchall()
        aid = getreturn[0][0]
        pdata.set_tag(tag,aid)
        tagtime = Getter.gettimes()
        tagt = tagtime + 2592000
        tagt = int(tagt)
        sql = f"""UPDATE player
                  SET tagtime = '{tagt}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        conn.close()
        return True
    def renewaltag(zaid,m):
        price = 119
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT tagtime
                  FROM player
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        t = int(getreturn[0][0])
        coin = Coin.getcoin(zaid)
        if coin < m*price:
            conn.close()
            return False
        Coin.usecoin(zaid,m*price)
        tagt = t + m*2592000
        sql = f"""UPDATE player
                  SET tagtime = '{tagt}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        conn.close()
        return True
    def changetag(zaid,tag):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""UPDATE player
                  SET tag = '{tag}'
                  WHERE zaid = '{zaid}'"""
        results = c.execute(sql)
        conn.commit()
        sql = f"""SELECT PBID
                FROM player
                WHERE zaid = '{zaid}';"""
        results = c.execute(sql)
        conn.commit()
        getreturn = results.fetchall()
        aid = getreturn[0][0]
        pdata.remove_tag(aid)
        pdata.set_tag(tag,aid)
        return True
    def register(aid,name,qnum,cid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT *
                FROM player
                WHERE PBID = '{aid}';"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        if len(getreturn) != 0:
            send("你已经注册过了喵😖",cid)
            conn.close()
            return 
        sql = f"""SELECT *
                FROM player
                WHERE NAME = '{name}';"""
        results = c.execute(sql)
        getreturn = results.fetchall()
        if len(getreturn) != 0:
            send("这个名字已经注册过了喵😖换个名字试试喵",cid)
            conn.close()
            return
        try:
            qnum = int(qnum)
            qnum = str(qnum)
            if len(qnum) < 8 or len(qnum) > 10:
                send("请输入正确的QQ号❌",cid)
                return
        except:
            send("请输入正确的QQ号❌",cid)
            return
        time = Getter.gettime(4)
        notpass = "0"
        za = c.execute("SELECT headMsg  from zaidnum")
        za = c.fetchone()
        zaid = za[0]
        sql = """INSERT INTO player(
            zaid,PBID,NAME,QQ,TIME,lastpass,rp,tag,tagtime,effect,effecttime,ac)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"""
        inf = (zaid,aid,name,qnum,time,notpass,"No","None","None","None","None","N")
        c.execute(sql,inf)
        sql = """INSERT INTO bag1(
            zaid,catcoin,lastcmd,fly,inv,hl,creepy,celeb,flo,egg,randomColor,TNTBomb,setplayernum,swim,ctrlbot,punchtime,makebot,aiangry,punchpower,gm,unfreeze,freeze,shield,punch,sleep,cur,kill,speed,sm)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        info = (zaid,20,"None",0,0,0,0,0,0,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        c.execute(sql,info)
        send(str("恭喜"+name+"在扎卡拉注册成功✅成为我们的一员~喵呜"),cid)
        animater.animater("注册",name,zaid,None)
        newzaid = zaid +1
        sql = f"""UPDATE zaidnum
                  SET headMsg = '{newzaid}'"""
        c.execute(sql)
        conn.commit()
        conn.close()
    def getAccountHas(aid,cid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT *
                        from player 
                        WHERE PBID ='{aid}';""")
        inf = inf.fetchone()
        conn.close()
        if not inf:
            send("你还没注册喵~输入“/注册喵”注册吧~",cid)
            return False
        else:
            conn = sqlite3.connect(sqlfile)
            c = conn.cursor()
            inf = c.execute(f"""SELECT ac
                        from player 
                        WHERE PBID ='{aid}';""")
            inf = inf.fetchone()
            inf2 = c.execute(f"""SELECT QQ
                        from player 
                        WHERE PBID ='{aid}';""")
            inf2 = inf2.fetchone()
            print("aid:"+aid+" inf0:"+inf[0]+" inf2:"+str(inf2[0]))
            if "N" in inf[0]:
                if "None" in str(inf2[0]):
                    send("===============警告🚩🚩🚩===============",cid) 
                    send("系统检测到你的QQ号异常，你需要提交新的QQ号才能继续使用",cid)
                    send("发送“/QQ QQ号”即可更改QQ并进行安全验证",cid)
                    send("=============================================",cid)
                send("当前账户需要进行安全验证喵~😖",cid)
                send("请添加鲨鱼QQ群902867245，发送“注册”即可完成验证喵",cid)
                inf = c.execute(f"""SELECT QQ
                        from player 
                        WHERE PBID ='{aid}';""")
                inf = inf.fetchone()
                if "None" in inf[0]:
                    send("你的ID是“"+Getter.getzaid(aid)+"”,在QQ群请发送“注册 "+Getter.getzaid+"”即可验证成功喵⚽",cid)
                else:
                    send("你的QQ是"+str(inf[0])+",我们已经在群内@你了喵📨",cid)
                    zaqr.send("验证",str(inf[0]))
                conn.close()
                return False
            return True
class Store:
    def renewaltag(cmd,agu,cid,aid):
        price = 119
        zaid = Getter.getzaid(aid)
        ifornot = Account.gettag(zaid)
        if ifornot == "None":
            send("你还没有头衔喵",cid)
            send("输入“/购买头衔”可以设置你的头衔喵~",cid)
            return
        if agu ==[] or agu==['']:
            send("请输入续费多少月 || 当前续费价格："+str(price)+"+/30天/月🐱",cid)
            return
        month = int(agu[0][0])
        if month < 1:
            send("必须大于1个月才能续费喵😟",cid)
            return
        elif month > 6:
            send("单次续费不能大于5个月喵~😟",cid)
        month = int(month)
        if Coin.getcoin(zaid) < price*month:
            send("余额不足喵❌你只有"+str(Coin.getcoin(zaid))+"小鱼干喵",cid)
            send("当前续费价格："+str(price)+"+/30天/月，你需要"+str(price*month)+"小鱼干喵~",cid)
            return
        Account.renewaltag(zaid,month)
        send("续费成功✅花费掉"+str(price*month)+"块小鱼干喵🐱",cid)
    def settag(cmd,agu,cid,aid):
        tagMoney = 199
        if agu ==[] or agu==['']:
            send("请输入你要的头衔啊喂！例如“/购买头衔 四狗子”",cid)
            send("当前购买价：199小鱼干/30天/月，续费6折！（119/30天）",cid)
            return
        zaid = Getter.getzaid(aid)
        ifornot = Account.gettag(zaid)
        if ifornot != "None":
            send("你已经有一个头衔了喵",cid)
            send("输入“/更改头衔”可以更改你的头衔喵~",cid)
            return
        alltag = Account.gettag("all")
        tag = agu[0]
        if tag in alltag:
            send("头衔已经被占用了喵~换一个试试呗",cid)
            return
        coin = Coin.getcoin(zaid)
        if coin < tagMoney:
            send("头衔需要"+str(tagMoney)+"小鱼干喵呜~再攒攒喵",cid)
            return
        Coin.usecoin(zaid,tagMoney)
        r = Account.settag(zaid,tag)
        if r == True:
            send("头衔设置成功喵~有效期一个月喵✅",cid)
    def changetag(cmd,agu,cid,aid):
        changeMoney = 60
        if agu ==[] or agu==['']:
            send("请输入你要的头衔啊喂！例如“/更改头衔 四狗子”",cid)
            send("当前更改价："+str(changeMoney)+"小鱼干/30天/月",cid)
            return
        zaid = Getter.getzaid(aid)
        ifornot = Account.gettag(zaid)
        if ifornot == "None":
            send("你还没有头衔喵",cid)
            send("输入“/购买头衔”可以设置你的头衔喵~",cid)
            return
        alltag = Account.gettag("all")
        tag = agu[0]
        if tag in alltag:
            send("头衔已经被占用了喵~换一个试试呗",cid)
            return
        coin = Coin.getcoin(zaid)
        if coin < changeMoney:
            send("修改头衔需要"+str(changeMoney)+"小鱼干喵呜~再攒攒喵",cid)
            return
        Coin.usecoin(zaid,changeMoney)
        Account.changetag(zaid,agu[0])
        send("头衔修改成功喵~✅",cid)
    def renewaleffect(cmd,agu,cid,aid):
  #      try:
        price=Getter.getprice(Getter.getthingname(Account.geteffect(Getter.getzaid(aid))))
     #   except:
           # send("你还没有购买特效喵~输入“/购买特效”吧喵💫",cid)
         #   return
        if agu ==[] or agu==['']:
            send("请输入续费多少月 || 当前续费价格6折🐱",cid)
            return
        zaid = Getter.getzaid(aid)
        month = int(agu[0][0])
        if month < 1:
            send("必须大于1个月才能续费喵😟",cid)
            return
        elif month > 6:
            send("单次续费不能大于5个月喵~😟",cid)
        month = int(month)
        if Coin.getcoin(zaid) < price*month:
            send("余额不足喵❌你只有"+str(Coin.getcoin(zaid))+"小鱼干喵",cid)
            send("当前续费价格："+str(price)+"+/30天/月，你需要"+str(price*month)+"小鱼干喵~",cid)
            return
        Coin.usecoin(zaid,price*month)
        Account.renewaleffect(zaid,month)
        send("续费成功✅花费掉"+str(price*month)+"块小鱼干喵🐱",cid)
    def seteffect(cmd,agu,cid,aid):
        if agu ==[] or agu==['']:
            send("==========特效商城=============",cid)
            things = {"冰粒特效":"ice","火焰特效":"sweat","发光特效":"glow","闪光特效":"scorch","粘弹碎屑":"slime","烟雾特效":"distortion","金属碎屑":"metal","兔几附身":"surrounder","神":"spark"}
            for i in things:
                send("=="+str(i)+"========"+str(Getter.getprice(Getter.getthingname(i)))+"小鱼干/30天===",cid)
            send("请输入你要的特效啊喂！例如“/购买特效 神”",cid)
            send("发送“/商店 特效”获取可用特效喵🐱",cid)
            return
        try:
            thing = Getter.getprice(Getter.getthingname(agu[0]))
        except:
            send("特效名字错误喵！发送“/购买特效”获取可用特效喵🐱",cid)
            return
        tagMoney = thing
        zaid = Getter.getzaid(aid)
        ifornot = Account.geteffect(zaid)
        if ifornot != "None":
            send("你已经有一个特效了喵",cid)
            send("到期后才能更改特效喵~",cid)
            return
        coin = Coin.getcoin(zaid)
        if coin < tagMoney:
            send("余额不足❌特效需要"+str(tagMoney)+"小鱼干喵呜~再攒攒喵",cid)
            return
        Coin.usecoin(zaid,tagMoney)
        if Account.seteffect(zaid,Getter.getthingname(agu[0])):
            send("特效设置成功喵~有效期一个月喵✅",cid)

    def sendRedPacket(cmd,agu,cid,aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        zaid = Getter.getzaid(aid)
        coin = Coin.getcoin(zaid)
        name = Getter.getname(zaid)
        if agu ==[] or agu==['']:
            send("发送红包请输入/发红包 金额 数量 留言(可选)",cid)
            conn.close()
            return
        sql = f"""SELECT Name
                        from redbag ;"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        Name = inf[0]
        if Name != "None":
            send("还有另一个红包没有领完喵~输入/领红包 领取吧！",cid)
            conn.close()
            return
        money = int(agu[0])
        num = int(agu[1])
        if num < 1:
            send("不要那么小气啦🤜🤜至少发三个嘛喵",cid)
            conn.close()
            return
        elif num > 9:
            send("红包太多啦，扎卡拉发不过来喵😖",cid)
            conn.close()
            return
        try:
            msg = agu[2]
        except:
            msg = "None"
        if money < 10:
            send("额，不要那么小气啦喂~😣")
            conn.close()
            return
        if coin < money:
            send("啊哦，你没有那么多钱了啦😣你只有"+str(coin)+"小鱼干喵",cid)
            conn.close()
            return
        Coin.usecoin(zaid,money)
        sql = f"""UPDATE redbag
                  SET Name = '{name}';"""
        c.execute(sql)
        conn.commit()
        sql = f"""UPDATE redbag
                  SET Money = '{money}';"""
        c.execute(sql)
        conn.commit()
        sql = f"""UPDATE redbag
                  SET Num = '{num}';"""
        c.execute(sql)
        conn.commit()
        sql = f"""UPDATE redbag
                  SET Msg = '{msg}';"""
        c.execute(sql)
        conn.commit()
        send("红包发送成功🤑输入“/领红包”领取红包吧！",cid)
        ba.internal.chatmessage(str("|=======================|"))
        ba.internal.chatmessage(str("|    =          恭喜发财          =     |"))
        ba.internal.chatmessage(str("|        =      大吉大利      =         |"))
        ba.internal.chatmessage(str("|           ===========             |"))
        ba.internal.chatmessage(str("|                                              |"))
        ba.internal.chatmessage(str("|                                              |"))
        ba.internal.chatmessage(str("|           发送“/领红包”            |"))
        ba.internal.chatmessage(str("|              领取红包吧                |"))
        ba.internal.chatmessage(str(name+" 刚刚发了"+str(num)+"个红包🤑🧧"))
        animater.animater("红包来了🚩",name,coin,None)
        conn.close()
        
    def getRedPacket(cmd,agu,cid,aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        zaid = Getter.getzaid(aid)
        selfname = Getter.getname(zaid)
        sql = f"""SELECT rp
                        from player 
                        WHERE zaid ='{zaid}';"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        inf = inf[0]
        if inf == "Yes":
            send("你已经领取过红包了喂😟",cid)
            c = conn.cursor()
            return
        sql = f"""SELECT Name
                        from redbag ;"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        inf = inf[0]
        if inf == "None":
            send("当前没有红包噢😣输入“/发红包”发一个吧喵~",cid)
            conn.close()
            return
        sql = f"""SELECT Money
                        from redbag ;"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        money = inf[0]
        sql = f"""SELECT Num
                        from redbag ;"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        num = int(inf[0])
        sql = f"""SELECT Name
                        from redbag ;"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        name = inf[0]
        sql = f"""SELECT Msg
                        from redbag ;"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        msg = inf[0]
        if num == 1:
            coin = money
            newmoney = 0
        else:
            while True:
                coin = random.randint(0,money)
                newmoney = money-coin
                if coin == newmoney:
                    continue
                else:
                    newnum = num - 1
                    if newmoney/newnum < 1:
                        continue
                    break
        Coin.addcoin(zaid,coin)
        newnum = num - 1
        sql = f"""UPDATE redbag
                  SET Num = '{newnum}';"""
        c.execute(sql)
        conn.commit()
        if newmoney == 0:
            sql = f"""UPDATE redbag
                  SET Name = 'None';"""
            c.execute(sql)
            conn.commit()
            sql = f"""UPDATE redbag
                  SET Money = '0';"""
            c.execute(sql)
            conn.commit()
        else:
            sql = f"""UPDATE redbag
                  SET Money = '{newmoney}';"""
            c.execute(sql)
            conn.commit()
        sql = f"""UPDATE player
                  SET rp = 'Yes'
                  WHERE zaid = '{zaid}';"""
        c.execute(sql)
        conn.commit()
        send("你领取了 "+name+" 的红包🤑",cid)
        if msg == "None":
            msg = ""
        else:
            send(msg,cid)
        send("你获得了"+str(coin)+"个小鱼干喵🤤",cid)
        animater.animater(name +" 领取了红包",Getter.getname(zaid),coin,msg)
        if newnum == 0:
            ba.internal.chatmessage(str(name+"的红包被领完啦喵🚩"))
        else:
            ba.internal.chatmessage(str(selfname+"领取了"+name+"的红包喵🚩"))
        if newnum == 0:
            sql = f"""UPDATE player
                  SET rp = 'No';"""
            c.execute(sql)
            conn.commit()
            sql = f"""UPDATE redbag
                  SET Name = 'None';"""
        conn.close()
            
    def NewStoreThings(aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        global flyNum,invNum,hlNum,creepyNum,celebNum,floNum,speedNum,randomColorNum,TNTBombNum,swimNum,ctrlbotNum,punchtimeNum,makebotNum,aiangryNum,punchpowerNum,killNum,curNum,sleepNum,punchNum,shieldNum,gmNum,unfreezeNum,freezeNum
        T = c.execute("SELECT heagMsg  from StoreLog")
        T = c.fetchone()
        T = T[0]
        nowT = Getter.gettime(3)
        if aid == "pb-IF4XV3oqVw==":
            pass
        elif T == nowT:
            if storeNum == 1:
                ba.internal.chatmessage(str("商店刷新失败！每天只能刷新一次哦"))
                conn.close()
                return
        list = random.choices(storeList,weights=storeListR,k=10)
        if "fly" in list:
            flyNum = 1
        else:
            flyNum=0
        if "inv"in list:
            invNum = 1
        else:
            invNum=0
        if "hl"in list:
            hlNum = 1
        else:
            hlNum=0
        if "creepy"in list:
            creepyNum = 1
        else:
            creepyNum=0
        if "celeb"in list:
            celebNum = 1
        else:
            celebNum=0
        if "flo"in list:
            floNum = 1
        else:
            floNum=0
        if "speed" in list:
            speedNum = 1
        else:
            speedNum = 0
        if "aiangry" in list:
            aiangryNum = 1
        else:
            aiangryNum = 0
        if "randomColor" in list:
            randomColorNum = 1
        else:
            randomColorNum = 0
        if "TNTBomb" in list:
            TNTBombNum = 1
        else:
            TNTBombNum = 0
        if "swim" in list:
            swimNum = 1
        else:
            swimNum = 0
        if "ctrlbot" in list:
            ctrlbotNum = 1
        else:
            ctrlbotNum = 0
        if "punchtime" in list:
            punchtimeNum = 1
        else:
            punchtimeNum = 0
        if "punchpower" in list:
            punchpowerNum = 1
        else:
            punchpowerNum = 0
        if "makebot" in list:
            makebotNum = 1
        else:
            makebotNum = 0
        if "kill" in list:
            killNum = 1
        else:
            killNum = 0
        if "cur" in list:
            curNum = 1
        else:
            curNum = 0
        if "shield" in list:
            shieldNum = 1
        else:
            shieldNum = 0
        if "unfreeze" in list:
            unfreezeNum = 1
        else:
            unfreezeNum = 0
        if "sleep" in list:
            speedNum = 1
        else:
            speedNum = 0
        if "gm" in list:
            gmNum = 1
        else:
            gmNum = 0
        if "freeze" in list:
            freezeNum = 1
        else:
            freezeNum = 0
        if "punch" in list:
            punchNum = 1
        else:
            punchNum = 0
        if "sleep" in list:
            sleepNum = 1
        else:
            sleepNum = 0
        sql2 = f"""UPDATE StoreLog
                  SET heagMsg = '{nowT}';"""
        c.execute(sql2)
        conn.commit()
        animater.animater("刷新商店",None,None,None)
        conn.close()
    def usething(zaid,thing,cid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT {thing}
                        from bag1 
                        WHERE zaid ='{zaid}';"""
        inf = c.execute(sql)
        thingNum = inf.fetchone()
        thingNum = thingNum[0]
        if thingNum == 0:
            send("emm，背包好像没有这个东西噢🐵",cid)
            send("使用“/商店”购买ta吧o(*≧▽≦)ツ┏━┓",cid)
            conn.close()
            return False
        else:
            newThing = int(thingNum)-1
            sql = f"""UPDATE bag1
                  SET '{thing}' = '{newThing}'
                  WHERE zaid ='{zaid}';"""
            c.execute(sql)
            conn.commit()
            conn.close()
            return True
    def egger(cmd,agu,cid,aid):
        zaid = Getter.getzaid(aid)
        thing = ["1000coin","500coin","200coin","flo3","flo","fly10","inv10","again2","again","funnymonkey","TNTBomb10","swim10","punchtime5","sm20","sm10","randomColor10","sleep5","randomColor20"]
        chothing = [1,3,5,6,7,6,6,5,6,5,5,4,5,5,5,6,5,5]
        choicething = random.choices(thing,weights=chothing,k=1)
        choicething = choicething[0]
        if choicething == "1000coin":
            Coin.addcoin(zaid,1000)
            send("手气真不错，获得：1000个小鱼干喵🐱",cid)
        elif choicething == "500coin":
            Coin.addcoin(zaid,500)
            send("手气真不错，获得500个小鱼干喵🐱",cid)
        elif choicething == "200coin":
            Coin.addcoin(zaid,200)
            send("手气真不错，获得200个小鱼干喵🐱",cid)
        elif choicething == "flo3":
            send("手气真不错，获得无人机x3喵🐱",cid)
            for i in range(3):
                Store.buyer(zaid,"flo",0,cid)
        elif choicething == "flo":
            Store.buyer(zaid,"flo",0,cid)
            send("手气真不错，获得无人机x1喵🐱",cid)
        elif choicething == "fly10":
            for i in range(10):
                Store.buyer(zaid,"fly",0,cid)
            send("手气真不错，获得飞行指令x10喵🐱",cid)
        elif choicething == "inv10":
            for i in range(10):
                Store.buyer(zaid,"inv",0,cid)
            send("手气真不错，获得隐身指令x10喵🐱",cid)
        elif choicething == "again2":
            for i in range(2):
                Store.buyer(zaid,"egg",0,cid)
            send("手气真不错，获得再来两次唔🐱",cid)
        elif choicething == "egg":
            for i in range(1):
                Store.buyer(zaid,"fly",0,cid)
            send("手气真不错，获得再来一次喵~🐱",cid)
        elif choicething == "TNTBomb10":
            for i in range(10):
                Store.buyer(zaid,"TNTBomb",0,cid)
            send("手气真不错，获得TNT炸弹x10喵~🐱",cid)
        elif choicething == "swim10":
            for i in range(10):
                Store.buyer(zaid,"swim",0,cid)
            send("手气真不错，获得游泳指令x10喵~🐱",cid)
        elif choicething == "punchtime5":
            for i in range(5):
                Store.buyer(zaid,"punchtime",0,cid)
            send("手气真不错，获得出拳间隔x5喵~🐱",cid)
        elif choicething == "sm20":
            for i in range(20):
                Store.buyer(zaid,"sm",0,cid)
            send("手气真不错，获得史诗指令x20喵~🐱",cid)
        elif choicething == "sm10":
            for i in range(10):
                Store.buyer(zaid,"sm",0,cid)
            send("手气真不错，获得史诗指令x10喵~🐱",cid)
        elif choicething == "randomColor10":
            for i in range(10):
                Store.buyer(zaid,"randomColor",0,cid)
            send("手气真不错，获得闪光色x10喵~🐱",cid)
        elif choicething == "sleep5":
            for i in range(5):
                Store.buyer(zaid,"sleep",0,cid)
            send("手气真不错，获得昏迷指令x10喵~🐱",cid)
        elif choicething == "randomColor20":
            for i in range(20):
                Store.buyer(zaid,"randomColor",0,cid)
            send("手气真不错，获得闪光色x20喵~🐱",cid)
        elif choicething == "funnymonkey":
            send("彩蛋已开启，啥也没有www",cid)
            send("啊噢，别灰心，换个姿势试试看喵🐱",cid)
    def buyer(zaid,thing,money,cid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        sql = f"""SELECT {thing}
                        from bag1 
                        WHERE zaid ='{zaid}';"""
        inf = c.execute(sql)
        inf = inf.fetchone()
        cat = "catcoin"
        coin = c.execute(f"""SELECT {cat}
                        from bag1 
                        WHERE zaid ='{zaid}';""")
        coin = coin.fetchone()
        thingnum = int(inf[0])
        coin = coin[0]
        money = int(money)
        coin = int(coin)
        if money > coin:
            send("余额不足喵！你还需"+str(money-coin)+"小鱼干喵❌",cid)
            conn.close()
            return
        thingnum = thingnum+1
        sql = f"""UPDATE bag1
                  SET '{thing}' = '{thingnum}'
                  WHERE zaid ='{zaid}';"""
        c.execute(sql)
        conn.commit()
        newcatcoin = coin-money
        sql = f"""UPDATE bag1
                  SET catcoin = '{newcatcoin}'
                  WHERE zaid ='{zaid}';"""
        c.execute(sql)
        conn.commit()
        send("购买成功喵✅~",cid)
        send("花费了你"+str(money)+"块小鱼干；物品已存放在背包，输入“/背包”查看喵🎒",cid)
        conn.close()

class Coin:
    def addcoin(zaid,addcoin):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT catcoin
                    from bag1 
                    WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        catcoin = int(inf[0])
        catcoin = catcoin + addcoin
        sql2 = f"""UPDATE bag1
              SET catcoin = '{catcoin}'
              WHERE zaid ='{zaid}';"""
        c.execute(sql2)
        conn.commit()
        conn.close()
    def usecoin(zaid,usecoin):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT catcoin
                    from bag1 
                    WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        catcoin = int(inf[0])
        catcoin = catcoin - usecoin
        sql2 = f"""UPDATE bag1
              SET catcoin = '{catcoin}'
              WHERE zaid ='{zaid}';"""
        c.execute(sql2)
        conn.commit()
        conn.close()
    def getcoin(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT catcoin
                        from bag1 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        catcoin = int(inf[0])
        conn.close()
        return catcoin






