import random
import ba
import _ba
#import gc
import os
import sys
from bastd.ui.party import *
from efro.error import CleanError
import urllib
import json
#以下为常规导入部分
from bastd.actor.spazbot import *
from bastd.actor.spaz import *
from bastd.actor.playerspaz import *
from bastd.actor.bomb import *
from bastd.game import *
import bastd

if TYPE_CHECKING:
    from typing import List, Sequence, Optional, Dict, Any
class D:
    import ba
    commands = {
        
    }
    
    opened = True
    
    
    version_code = 1

    #Activity
    #获取当前Activity
    def a():
        return _ba.get_foreground_host_activity()
    #AddCommand
    #新增命令
    def ac(name,handler,info = None):
        if isinstance(name,list):
            for e in name:
                D.ac(e,handler)
            return
        D.commands[name] = handler
    #Foreground Session
    #获取当前Session
    def fs():
        return _ba.get_foreground_host_session()
    #Screen Message
    #弹出屏幕消息
    def s(*s,**kwargs):
        if not isinstance(s[0],str):
            s = list(s)
            s[0] = str(s[0])
        ba.screenmessage(*s,**kwargs)
    
    #Class
    def cls(pack,name):
        exec("from "+pack+" import "+name+" as p\nD.tempp = p")
        return D.tempp
    
    #For Do
    #循环执行
    def f(i,f,l):
        for id in range(i) :
            if l:
                f(id)
            else:
                f()
    #with Context Execute
    #在上下文环境中执行
    def ce(c):
        with ba.Context(D.a()):
          D.te(c)
    
    #Load Function
    #加载函数到Debbuger类
    def lf(n,c):
        D.te("def MT():\n "+c.replace("\n","\n ")+"\nD."+n+"=MT")
    
    #For Execute
    #循环执行
    def fe(i,s):
        for id in range(i):
            D.alp(eval(s))
    #Print
    #在聊天框打印（输出）信息
    def p(s):
        with ba.Context('ui'):
            if isinstance(s,list):
                for i in s:
                    ba._hooks.local_chat_message(i)
                return
            ba._hooks.local_chat_message(str(s))
    
    #Lines Print
    #聊天框打印多行消息
    def lp(s):
        for ls in str(s).split('\n'):
            D.p(ls)
    
    #Auto Lines Print
    #打印自动换行消息
    def alp(s,n = 80):
    
        D.lp(D.mls(s,n))
    
    
    #Send Internet Message
    #发送信息（联网）
    def si(s):
        _ba.chatmessage(str(s))
    #Mod Method
    #（在原方法执行前）修改/MOD方法
    def mm(pack,name,old,code):
        
        INDEX = str(random.randint(1,100000000))
        
        exec("from "+pack+" import *\n"+
              "def NMT(self):\n"+
              "    "+code+"\n"+
              "    self.YMT"+INDEX+"()\n"+
              +name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #Mod Method Behind
    #在原方法执行后附加修改/MOD方法（执行顺序不同）
    def mmb(pack,name,old,code):
        INDEX = str(random.randint(1,100000000))
        exec("from "+pack+" import *\ndef NMT(self):\n    self.YMT"+INDEX+"()\n    "+code+"\n"+name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #Mod Method with Any Argument
    #任意参数修改方法（原方法前）
    def mmaa(pack,name,old,code):
        INDEX = str(random.randint(1,100000000))
        exec("from "+pack+" import *\ndef NMT(self,*args,**kargs):\n    "+code+"\n    self.YMT"+INDEX+"(*args,**kargs)\n"+name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #Set Method with Any Argument
    #任意参数修改方法（原方法前）
    def smaa(pack,name,old,code):
        INDEX = str(random.randint(1,100000000))
        exec("from "+pack+" import *\ndef NMT(self,*args,**kargs):\n    "+code+"\n"+name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #mod Behind Method with Any Argument
    #任意参数修改方法（原方法前）
    def bmaa(pack,name,old,code):
        INDEX = str(random.randint(1,100000000))
        exec("from "+pack+" import *\ndef NMT(self,*args,**kargs):\n"+"    self.YMT"+INDEX+"(*args,**kargs)\n    "+code+"\n"+name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #Set Method with Arguments
    #带参数设置方法
    def sma(pack,name,old,arg,code):
        INDEX = str(random.randint(1,100000000))
        exec("from "+pack+" import *\ndef NMT(self,"+arg+"):\n    "+code+"\n"+name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #Set Method
    #设置方法
    def sm(pack,name,old,code):
        INDEX = str(random.randint(1,100000000))
        exec("from "+pack+" import *\ndef NMT(self):\n    "+code+"\n"+name+".YMT"+INDEX+" = "+name+"."+old+"\n"+name+"."+old+" = NMT")
    #Set Attribute
    #设置属性
    def sa(pack,name,attr,new):
        exec("from "+pack+" import *\n"+name+"."+attr+"="+new)
    #Cast Dir To
    #输出转换Dir结果到文件
    def cdt(obj,to):
        open(to,'w').write(str(dir(obj)).replace(",","\n"))
    
    #mod
    #修改方法
    def mod(obj,name,_by):
        _old = getattr(obj,name)
        def doit(*a,**ka):
            _by(_old,*a,**ka)
        
        setattr(obj,name,doit)
    
    #log
    #输出日志
    def log(path,str):
        with open(path,"a") as f:
            f.write("\n")
            f.write(str)
    
    #Import To Debugger
    #导入类到Debugger类
    def itd(package,name):
        D.te("from "+package+" import "+name+"\nD.p"+name+"="+name)
    
    #Try Execute Code
    #尝试运行代码
    def te(code):
        try:
            exec(code)
        except BaseException as err:
            re = str(repr(err))
            D.s("运行异常："+re)
    def fr(a):
        return a
    
    #Test MOD
    #运行mod（带报错）
    def tm(p):
        try:
            exec(open(p,'r').read())
        except Exception as e:
            D.alp(D.mls(str(e)))
    
    #Mult Lines String
    #转为多行字符串
    def mls(s,n = 20):
    
        if not isinstance(s,str):
            s = str(s)
    
        r = ""
        for i in range(0,len(s)-n,n):
            r += s[i:i+n]
            r += "\n"
        r+=s[-(len(s)%n):]
        
        
        return r
    
 
#Current game FirstPlayer
    #当前游戏第一个玩家
    def cfp(aid):
        ctps = [i for i in _ba.get_foreground_host_activity().players if (i.sessionplayer.get_v1_account_id() == aid)]
        if len(ctps) == 0:
            #没有获取到
            return

        #获取到了至少一个，选择第一个
        mplayer = ctps[0]
        return mplayer
    #玩家节点对象
    def pn(aid):
        return D.pa(aid).node
    
    #Player Actor
    #玩家演员对象
    def pa(aid):
        return D.cfp(aid).actor
    
    #Current game First Bot
    #当前游戏第一个机器人
    def cfb():
        return d.cb().get_living_bots()[0]
    
    #Current game Bots
    #当前游戏机器人
    def cb():
        return d.a()._bots if hasattr(d.a(),'_bots') else d.a()._bots
    
    #id方法读取activity(垃圾回收器调用，已过时）
    """
    def sac(ac):
        D.acs = id(ac)
    """
    
    #已过时，使用D.a()代替
    """
    def gas():
        for obj in gc.get_objects():
            if id(obj) == D.acs:
                return obj
    """
    
    def g():
        return D.a().globalsnode
    
    #Command
    #发送指令
    def cc():
        pass
    
    #Update
    #刷新检查未处理事件
    def u():
        #如果有待处理事件
        if ("DS" in dir(ba)) and len(ba.DS) > 0:
            #D.si("加载"+len(ba.DS)+"个插件!")
            for e in ba.DS:
                if "name" in e:
                    D.si("DEBUG:关联插件启动成功:"+e["name"])
                if "event" in e:
                    try:
                        e["event"](D)
                    except Exception as e:
                        D.s("加载异常:"+str(e),(1,0,0))
            ba.DS = []
    
    #Reload
    #重新加载某个模组
    def reload(mname):
        if not "." in mname:
            d.p("错误：没有包名！")
        name = mname.split(".")[0]
        cls = mname.split(".")[1]
        try:
            exec(f"import {name}\nimport importlib\nimportlib.reload({name})\nx={name}.{cls}()\nif hasattr(x,\"on_app_launch\"):\n  x.on_app_launch()")
        except Exception as e:
            d.p("加载错误："+str(e))

    #Save
    #保存指令列表
    def save():
        data = {}
        for k in D.commands:
            v = D.commands[k]
            
            if isinstance(v,str):
                data[k] = v
        
        con = json.dumps(data)
        _env = _ba.env()
        pdir = _env["python_directory_user"]
        with open(os.path.join(pdir,"chatExecConfig.json"),"w") as f:
            f.write(con)
    
    #Load
    #加载指令列表
    def load():
        _env = _ba.env()
        pdir = _env["python_directory_user"]
        if not os.path.exists(os.path.join(pdir,"chatExecConfig.json")):
            return
        
        with open(os.path.join(pdir,"chatExecConfig.json"),"r") as f:
            es = json.loads(f.read())
            for e in es:
                D.commands[e] = es[e]
    

#别名
d = D
ba.D = D
def getplayerpos(player):
    return player.actor.node.position
def getplayer(pid):
    player = d.a().players[pid]
    return player
def commandCheck(cmd,agu,cid,aid):
    if cmd in ["ai内杠","AI内杠","Ai内杠"]:
        with ba.Context(_ba.get_foreground_host_activity()):
            return CommandsRun.aiangry()
    elif cmd in ["闪光色"]:
        with ba.Context(_ba.get_foreground_host_activity()):
            return CommandsRun.randomColor()
    elif cmd in ["TNT炸弹"]: 
        if agu ==[] or agu==['']:
            player = D.cfp(aid)
            with ba.Context(_ba.get_foreground_host_activity()):
                return CommandsRun.TNTbomb(player)
    elif cmd in ["设置玩家人数","setplayernum","sp"]:
        if aid !="pb-IF4XV3oqVw==":
            return False
        pnum = int(agu[0])
        with ba.Context(_ba.get_foreground_host_activity()):
                return CommandsRun.setplayer(pnum)
    elif cmd in ["游泳指令","swim"]:
        with ba.Context(_ba.get_foreground_host_activity()):
            return CommandsRun.swim()
    elif cmd in ["控制机器人","ctrlbot","cb"]:
        if agu ==[] or agu==['']:
            player = D.cfp(aid)
            print(player)
            with ba.Context(_ba.get_foreground_host_activity()):
                return CommandsRun.flybomb(player)
#        elif isinstance(agu[0],int):
#            player = d.a().players[agu[0]]
#            with ba.Context(_ba.get_foreground_host_activity()):
#                return CommandsRun.flybomb(player)
#        else:
#            ctps = [i for i in _ba.get_foreground_host_activity().players if (agu[0] in i.sessionplayer().getName())]
#            if len(ctps) == 0:
#                return False
#            mplayer = ctps[0]
 #           player = mplayer
 #           with ba.Context(_ba.get_foreground_host_activity()):
 #               return CommandsRun.ctrlbot(player)
    elif cmd in ["出拳间隔","punchtime","pt"]:
        ctime = agu[0]
        ctime = int(ctime)
        player = D.cfp(aid)
        with ba.Context(_ba.get_foreground_host_activity()):
                return CommandsRun.setPunchTime(ctime,player)
    elif cmd in ["出拳力量","punchpower","pp"]:
        ctime = int(agu[0])
        player = D.cfp(aid)
        with ba.Context(_ba.get_foreground_host_activity()):
            return CommandsRun.setPunchPower(ctime,player)
    elif cmd in ["生成机器人","makebot","mb"]:
        if len(agu) != 2:
            if agu ==[] or agu==['']:
                print(_ba.get_foreground_host_activity().players)
                print(_ba.get_foreground_host_activity().players[0])
                player = D.cfp(aid)
                print("print(player.actor)的结果是")
                print(player.actor)
                print(player.position)
                print(player._postinited)
                print(player)
                spaz = "BomberBot"
                spaz = eval(spaz)
            elif agu[0] not in ["BomberBot","BrawlerBot","TriggerBot","ChargerBot","BomberBotPro","BrawlerBotPro","TriggerBotPro","BomberBotProShielded","ExplodeyBot","ChargerBotProShielded","StickyBot","BrawlerBotProShielded","TriggerBotProShielded"]:
                try:
                    pnum = int(agu[0])
                    player = d.a().players[pnum]
                    spaz = "BomberBot"
                    spaz = eval(spaz)
                except:
                    ctps = [i for i in _ba.get_foreground_host_activity().players if (agu[0] in i.sessionplayer().getName())]
                    if len(ctps) == 0:
                        return False
                    mplayer = ctps[0]
                    player = mplayer
                    spaz = "BomberBot"
                    spaz = eval(spaz)
            else:
                spaz = agu[0]
                spaz = eval(spaz)
                player = D.cfp(aid)
        else:
            spaz = agu[1]
            spaz = eval(spaz)
            player = d.a().players[agu[0]]
        with ba.Context(_ba.get_foreground_host_activity()):
            return CommandsRun.makeBot(spaz,player)

class CommandsRun:
    def swim():
        for p in _ba.get_foreground_host_activity().players:
            p.actor.node.roller_materials =()
            p.actor.node.materials =()
            return True
    def aiangry():
        def xx():
          bots = d.a()._bots
          lbs = bots.get_living_bots()
          def gbp(self):
            lbs = d.a()._bots.get_living_bots()
            if len(lbs) <= 0:
              return None,None
            hb = lbs[0] 
            if len(lbs) >= 2 and hb==self:
              hb = lbs[1]  
            hb.node.color = (0,1,0)
            if hb == self:
              if not hasattr(self,'ttt'):
                self.ttt = 0
                return None,None  
              self.ttt += 1
              if self.ttt > 4:
                self.node.handlemessage('celebrate', 2000)
              if self.ttt > 7:
                self.curse()
                self.curse_explode()
            return (
             ba.Vec3(hb.node.position[0],
              hb.node.position[1],
              hb.node.position[2]),
             ba.Vec3(hb.node.velocity[0],
              hb.node.velocity[1],
              hb.node.velocity[2])
            )
          SpazBot._get_target_player_pt = gbp
        d.cxk = xx
        xx()
        return True
    def TNTbomb(player):
        def nb():
            self=player
            b = Bomb(
                bomb_type="tnt",
                position = self.node.position,
                blast_radius = 5,
                bomb_scale=0.3
            ).autoretain()
            player.actor.node.hold_node = b.node
            b.node.sticky = True
            b.node.gravity_scale = 4
            
            b.bt = ba.Timer(5,b.explode)
    
            return b
        player.actor.drop_bomb = nb
        return True
    def setplayer(playernum):
        d.fs().max_players = playernum
        return True
    def celebforbot(t):
        d.a()._bots.celebrate(t)
        return True
    def ctrlbot(player):
        player.actor.node = d.a()._bots.get_living_bots()[0].node
        return True
    def setPunchTime(t,player):
        player.actor._punch_cooldown = t
        return True
    def setPunchPower(t,player):
        player.actor._punch_power_scale = t
        return True
    def randomColor():
        from random import random as ra
        ba.ra = ra
        def x():
            ba.D.g().tint = (0.5+ba.ra(),0.5+ba.ra(),0.5+ba.ra())
        ba.timer(0.2,x,repeat=True)
        return True
    def makeBot(bot,player):
        pos = getplayerpos(player)
        d.a()._bots.spawn_bot(bot,pos)
        return True