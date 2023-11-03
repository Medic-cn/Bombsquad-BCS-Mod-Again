import _ba
import random
#汉化by edMedic
#QQ2091341667
#Email：medic163@163.com/edmedic@outlook.com
#禁止未经授权用于开服
#授权id：82B51274EA94336EB3D7DDEA4D1E738D
def decorate_map():
    try:
        activity = _ba.get_foreground_host_activity()
        activity.fireflies_generator(20,True)
        activity.map.node.reflection = "powerup"
        activity.map.node.reflection_scale = [4]
        # activity.map.node.color = random.choices([(0.8,0.3,0.3),(0.6,0.5,0.7),(0.3,0.8,0.5)])[0]
        m = 5
        s = 5000
        ba.animate_array(activity.globalsnode, 'ambient_color', 3, {0: (1*m,0,0), s: (0,1*m,0),s*2:(0,0,1*m),s*3:(1*m,0,0)},True)
        activity.map.background.reflection = "soft"
    except:
        pass
