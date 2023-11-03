import animater
color = (0.2,1,1)
def msg():
    global color
    if 1 > 0:
        msg = input("发送消息:--")
        if "/"in msg:
            if "color" in msg:
                if "green" in msg:
                    color = (0.1,0.9,0.1)
                elif "yellow" in msg:
                    color = (0.9,0.9,0.1)
                elif "red" in msg:
                    color = (0.9,0.1,0.1)
                elif "blue" in msg:
                    color = (0.2,1,1)
                elif "white" in msg:
                    color = (0.9,0.9,0.9)
                elif "black" in msg:
                    color = (0.1,0.1,0.1)
            elif "重启" in msg:
                animater.animater("重启",None,None,None)
        animater.animater("服主广播",msg,None,color)
