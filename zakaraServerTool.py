import sqlite3
import time
import _ba
from Handlers import send
from playersData import pdata
sqlfile = "/bss/NewZakara.dmb"
class Getter:
    def getname(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT NAME
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        conn.commit()
        name = inf[0]
        conn.close()
        return name
    def getzaid(aid):
        print(aid)
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT zaid
                        from player 
                        WHERE PBID ='{aid}';""")
        inf = inf.fetchone()
        conn.commit()
        try:
            catcoin = inf[0]
        except:
            catcoin = None
        conn.close()
        return catcoin
    def getaid(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT PBID
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        conn.commit()
        catcoin = inf[0]
        conn.close()
        return catcoin
    def gettag(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT tag
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        conn.commit()
        catcoin = inf[0]
        conn.close()
        return catcoin
    def geteffect(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT effect
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        conn.commit()
        catcoin = inf[0]
        conn.close()
        return catcoin
    def gettagt(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT tagtime
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        conn.commit()
        catcoin = inf[0]
        conn.close()
        return catcoin
    def geteffectt(zaid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT effecttime
                        from player 
                        WHERE zaid ='{zaid}';""")
        inf = inf.fetchone()
        conn.commit()
        catcoin = inf[0]
        conn.close()
        return catcoin
 #   def getcid(aid):
  #      cid = -256
  #      for x in _ba.get_game_roster():
  #          if x["account_id"] == aid:
  #              cid = x["client_id"]
  #      return cid
    def gettimes():
        ntime = int(time.time())
        return ntime
def checkp(aid):
        import sqlite3
        conn = sqlite3.connect(sqlfile)
        c = conn.cursor()
        inf = c.execute(f"""SELECT *
                        from player 
                        WHERE PBID ='{aid}';""")
        inf = inf.fetchone()
        conn.close()
        if not inf:
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
                conn.close()
                return False
            else:
                conn.close()
                return True
def remove_tag(aid):
    try:
        pdata.remove_tag(aid)
    except:
        pass
def remove_effect(aid):
    try:
        pdata.remove_effect(aid)
    except:
        pass
def baner(aid):
    mute = False
    ban = False
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
            for i in inf:
                if "None" in i:
                    continue
                if int(i)>Getter.gettimes():
                    ban="ban"
            if ban == False:
                ban = "None"
    inf2 = c.execute(f"""SELECT mutet
                        from muter 
                        WHERE PBID ='{aid}';""")
    inf2 = inf2.fetchall()
    inf2 = list(map(lambda x:x[0],inf2))
    if not inf2:
        mute = "None"
    else:
        for i in inf2:
            if "None" in i:
                continue
            if int(i)>Getter.gettimes():
                mute="mute"
        if mute == False:
            mute = "None"
    conn.close()
    return ban+mute
def uuidbaner(uuid):
    import sqlite3
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    inf = c.execute(f"""SELECT bant
                        from baner 
                        WHERE device ='{uuid}';""")
    inf = inf.fetchall()
    inf = list(map(lambda x:x[0],inf))
    if not inf:
        ban = "None"
    else:
        for i in inf:
            if "None" in i:
                continue
            if int(i)>Getter.gettimes():
                ban="ban"
    return ban
#conn.commit() 把这个修了先
def deltag(zaid,cid):
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    aid = Getter.getaid(zaid)
    pdata.remove_tag(aid)
    sql = f"""UPDATE player
                  SET tag = 'None'
                  WHERE zaid = '{zaid}'"""
    c.execute(sql)
    conn.commit()
    sql = f"""UPDATE player
                  SET tagtime = 'None'
                  WHERE zaid = '{zaid}'"""
    c.execute(sql)
    conn.commit()
    conn.close()
    send("头衔已到期喵，已为你自动释放喵📨",cid)
def checktag(aid,cid):
    zaid = Getter.getzaid(aid)
    if zaid == None:
        return
    time = Getter.gettimes()
    tagt = Getter.gettagt(zaid)
    if Getter.gettag(zaid) == "None":
        remove_tag(aid)
        return
    if tagt == "None":
        remove_tag(aid)
        return
    elif tagt == "":
        remove_tag(aid)
        return
    elif tagt == None:
        remove_tag(aid)
        return
    remindt = int(tagt) - 604800
    if time > int(tagt):
        deltag(zaid,cid)
    elif remindt < time:
        day = int((tagt-time)/86400)
        if day == 0:
            send("你的头衔即将被释放，请及时续费📨",cid)
        else:
            send("你的头衔还有"+str(day)+"天被释放，请及时续费🐱",cid)
    try:
        pdata.remove_tag(aid)
        print("remove OK")
    except:
        pass
    pdata.set_tag(Getter.gettag(zaid),aid)
def deleffect(zaid,cid):
    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    aid = Getter.getaid(zaid)
    pdata.remove_effect(aid)
    sql = f"""UPDATE player
                  SET effect = 'None'
                  WHERE zaid = '{zaid}'"""
    c.execute(sql)
    conn.commit()
    sql = f"""UPDATE player
                  SET effecttime = 'None'
                  WHERE zaid = '{zaid}'"""
    c.execute(sql)
    conn.commit()
    conn.close()
    send("特效已到期喵，已为你自动释放喵📨",cid)
def checkeffect(aid,cid):
    zaid = Getter.getzaid(aid)
    if zaid == None:
        return
    time = Getter.gettimes()
    tagt = Getter.geteffectt(zaid)
    if tagt == "None":
        remove_effect(aid)
        return
    elif tagt == "":
        remove_effect(aid)
        return
    elif tagt == None:
        remove_effect(aid)
        return
    remindt = int(tagt) - 604800
    if time > int(tagt):
        deleffect(zaid,cid)
    elif remindt < time:
        day = int((tagt-time)/86400)
        if day == 0:
            send("你的特效即将被释放，请及时续费📨",cid)
        else:
            send("你的特效还有"+str(day)+"天被释放，请及时续费🐱",cid)
    try:
        pdata.remove_effect(aid)
        print("remove OK")
    except:
        pass
    pdata.set_effect(Getter.geteffect(zaid),aid)
