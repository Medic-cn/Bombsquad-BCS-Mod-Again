import _ba
import ba
def animater(mgs,name,coin,cmd):
        if mgs == "签到":
            tittle = "签到成功✅"
            msg = name + "获得" +str(coin) +" 个小鱼干🐱"
            img = "tickets"
            color = (0.1,0.9,0.1)
        elif mgs == "使用指令":
            tittle = "使用指令成功✅"
            msg = name + "使用了" + cmd
            img = "startButton"
            color = (0.1,0.9,0.1)
        elif "离开游戏" in mgs:
            tittle = "离开游戏"
            msg = name + "离开了游戏。\n欢迎下次再来喵~"
            img = "backIcon"
            color = (0.9,0.9,0.9)
        elif "加入游戏" in mgs:
            tittle = "加入单挑"
            msg = name + "加入了游戏\n和各位一决胜负喵~"
            img = "achievementBoxer"
            color = (0.9,0.9,0.1)
        elif "下一回合" in mgs:
            tittle = "下一回合进入"
            msg = name + " 将在下一回合加入游戏喵~🚩\nYou will enter at next round~"
            img = "controllerIcon"
            color = (0.1,0.9,0.1)
        elif "竞猜" in mgs:
            tittle = mgs
            if "成功" in mgs:
                msg = name +"竞猜成功🚩\n获得"+str(coin)+"块小鱼干🐱"
                color = (0.1,0.9,0.1)
            elif "中立" in mgs:
                msg = name+"没有竞猜成功\n没有获得小鱼干喵😖"
                color = (0.9,0.9,0.1)
            elif "失败" in mgs:
                msg = name +"竞猜失败😟\n扣除"+str(coin)+"块小鱼干💫"
                color = (0.9,0.1,0.1)
            img = "storeCharacter"
        elif "刷新商店" in mgs:
            tittle = "商店刷新成功✅"
            color = (0.1,0.9,0.1)
            msg = "商店已刷新最新商品\n输入“/商店”购买商品吧"
            img = "storeIcon"
        elif "注册" in mgs:
           tittle = "注册成功✅"
           color = (0.1,0.9,0.1)
           msg = name + "注册成功喵🎉编号:"+str(coin)+"\n以后就是大家族一员了喔"
           img = "usersButton"
        elif "红包来了" in mgs:
            tittle = mgs
            color = (0.2,1,1)
            msg = name +"刚刚发了"+str(coin)+"个红包\n发送“/领红包”领取吧✨"
            img = "chestIcon"
        elif "领取了红包" in mgs:
            tittle = mgs 
            color = (0.1,0.6,0.1)
            msg = name+"领取了红包\n获得"+str(coin)+"个小鱼干🐱\n"+cmd
            img = "chestOpenIcon"
            
        if _ba.get_foreground_host_activity().globalsnode.slow_motion:
            s = 0.27
        else:
            s = 1
        activity = _ba.get_foreground_host_activity()
        pos = (850,450)
        posi = (650,450)
        post = (825,110)
        poste = (825,80)
        with ba.Context(activity):
            activity.black = ba.NodeActor(
            ba.newnode('image',
                attrs={
                    'texture': ba.gettexture('bg'),
                    'scale': (400, 130),
                    'attach': 'bottomCenter',
                    'opacity': 0.5
                }
            )
        )
        with ba.Context(activity):
            ba.animate_array(activity.black.node, 'position', 2, {
                0.0*s: (pos[0], pos[1]),
                0.05*s: (pos[0]-280,pos[1]),
                0.1*s: (pos[0]-320,pos[1]),
                0.15*s: (pos[0]-340,pos[1]),
                0.2*s: (pos[0]-355,pos[1]),
                0.25*s: (pos[0]-365,pos[1]),
                0.3*s: (pos[0]-370,pos[1]),
                0.35*s: (pos[0]-373,pos[1]),
                0.4*s: (pos[0]-375,pos[1]),
                4.9*s: (pos[0]-390,pos[1]),
                4.95*s: (pos[0]-378,pos[1]),
                5.0*s: (pos[0]-330,pos[1]),
                5.1*s: (pos[0]-200,pos[1]),
                5.15*s:(pos[0]+999,pos[1])
            })
        with ba.Context(activity):
            activity.image = ba.NodeActor(
            ba.newnode('image',
                attrs={
                    'texture': ba.gettexture(img),
                    'scale': (80, 80),
                    'attach': 'bottomCenter',
                    'opacity': 0.8
                }
            )
        )
        with ba.Context(activity):
            ba.animate_array(activity.image.node, 'position', 2, {
                0.0*s: (posi[0], posi[1]),
                0.05*s: (posi[0]-280,posi[1]),
                0.1*s: (posi[0]-320,posi[1]),
                0.15*s: (posi[0]-340,posi[1]),
                0.2*s: (posi[0]-355,posi[1]),
                0.25*s: (posi[0]-365,posi[1]),
                0.3*s: (posi[0]-370,posi[1]),
                0.35*s: (posi[0]-373,posi[1]),
                0.4*s: (posi[0]-375,posi[1]),
                4.9*s: (posi[0]-390,posi[1]),
                4.95*s: (posi[0]-378,posi[1]),
                5.0*s: (posi[0]-330,posi[1]),
                5.1*s: (posi[0]-200,posi[1]),
                5.15*s:(posi[0]+999,posi[1])
            })
        with ba.Context(activity):
            tittle = ba.newnode(
                'text',
                attrs={
                    'text': tittle,
                    'color': color,
                    'h_align': 'center',
                    'shadow': 0.3,
                    'flatness': 0,
                    'opacity': 0.9,
                    'scale': 1.8                })
        with ba.Context(activity):
            ba.animate_array(tittle, 'position', 2, {
                0.0*s: (post[0], post[1]),
                0.05*s: (post[0]-280,post[1]),
                0.1*s: (post[0]-320,post[1]),
                0.15*s: (post[0]-340,post[1]),
                0.2*s: (post[0]-355,post[1]),
                0.25*s: (post[0]-365,post[1]),
                0.3*s: (post[0]-370,post[1]),
                0.35*s: (post[0]-373,post[1]),
                0.4*s: (post[0]-375,post[1]),
                4.9*s: (post[0]-390,post[1]),
                4.95*s: (post[0]-378,post[1]),
                5.0*s: (post[0]-330,post[1]),
                5.1*s: (post[0]-200,post[1]),
                5.15*s:(post[0]+999,post[1])
            })
        with ba.Context(activity):
            text = ba.newnode(
                'text',
                attrs={
                    'text': msg,
                    'color': color,
                    'h_align': 'center',
                    'shadow': 0.3,
                    'flatness': 0,
                    'opacity': 0.9,
                    'scale': 1                })
        with ba.Context(activity):
            ba.animate_array(text, 'position', 2, {
                0.0*s: (poste[0], poste[1]),
                0.05*s: (poste[0]-280,poste[1]),
                0.1*s: (poste[0]-320,poste[1]),
                0.15*s: (poste[0]-340,poste[1]),
                0.2*s: (poste[0]-355,poste[1]),
                0.25*s: (poste[0]-365,poste[1]),
                0.3*s: (poste[0]-370,poste[1]),
                0.35*s: (poste[0]-373,poste[1]),
                0.4*s: (poste[0]-375,poste[1]),
                4.9*s: (poste[0]-390,poste[1]),
                4.95*s: (poste[0]-378,poste[1]),
                5.0*s: (poste[0]-330,poste[1]),
                5.1*s: (poste[0]-200,poste[1]),
                5.15*s:(poste[0]+999,poste[1])
            })