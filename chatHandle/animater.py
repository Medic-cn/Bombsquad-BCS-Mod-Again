#Made by inkMedic
#Discord: Medic#3158
import _ba
import ba
activity = _ba.get_foreground_host_activity()
pos = (50,730)
post = (40,370)
def anime(x,msg,color):
    if _ba.get_foreground_host_activity().globalsnode.slow_motion:
            s = 0.27
    else:
            s = 1
    activity = _ba.get_foreground_host_activity()
    blackscale = (x,90)
    activity.button = ba.NodeActor(
        ba.newnode('image',
                attrs={
                    'texture': ba.gettexture('buttonSquare'),
                    'attach': 'bottomCenter',
                    'color': color
                }
            )
        )
    ba.animate_array(activity.button.node, 'position', 2, {
                0.0*s: (pos[0], pos[1]),
                0.05*s: (pos[0],pos[1]-50),
                0.1*s: (pos[0],pos[1]-70),
                0.15*s: (pos[0],pos[1]-85),
                0.2*s: (pos[0],pos[1]-95),
                0.25*s: (pos[0],pos[1]-98),
                0.3*s: (pos[0],pos[1]-100),
                0.35*s: (pos[0],pos[1]-101),
                0.4*s: (pos[0],pos[1]-102),
                4.9*s: (pos[0],pos[1]-103),
                4.95*s: (pos[0],pos[1]-90),
                5.0*s: (pos[0],pos[1]-70),
                5.1*s: (pos[0],pos[1]-1),
                5.15*s:(pos[0],pos[1]+999)
            })
    ba.animate(activity.button.node, 'opacity', {
                0.0*s: 0.0,
                0.07*s: 0.3,
                0.3*s: 0.7,
                4.9*s: 0.7,
                5.0*s: 0.2,
                5.1*s: 0
                            })
    ba.animate_array(activity.button.node, 'scale', 2,{
                0.0*s: (x, 90),
                4.4*s: (x, 90),
                4.5*s: (x-10, 80)
                            })
    activity = _ba.get_foreground_host_activity()
    activity.img = ba.NodeActor(
        ba.newnode('image',
                attrs={
                    'texture': ba.gettexture('usersButton'),
                    'attach': 'bottomCenter'
                }
            )
        )
    xp = x/2.2
    print(xp)
    posa = (-xp,730)
    ba.animate_array(activity.img.node, 'position', 2, {
                0.0*s: (posa[0], posa[1]),
                0.05*s: (posa[0],posa[1]-50),
                0.1*s: (posa[0],posa[1]-70),
                0.15*s: (posa[0],posa[1]-85),
                0.2*s: (posa[0],posa[1]-95),
                0.25*s: (posa[0],posa[1]-98),
                0.3*s: (posa[0],posa[1]-100),
                0.35*s: (posa[0],posa[1]-101),
                0.4*s: (posa[0],posa[1]-102),
                4.9*s: (posa[0],posa[1]-103),
                4.95*s: (posa[0],posa[1]-90),
                5.0*s: (posa[0],posa[1]-70),
                5.1*s: (posa[0],posa[1]-1),
                5.15*s:(posa[0],posa[1]+999)
            })
    ba.animate(activity.img.node, 'opacity', {
                0.0*s: 0.0,
                0.07*s: 0.3,
                0.3*s: 0.7,
                4.9*s: 0.7,
                5.0*s: 0.2,
                5.1*s: 0
                            })
    ba.animate_array(activity.img.node, 'scale', 2,{
                0.0*s: (60,60),
                4.4*s: (60,60),
                4.5*s: (50,50)
                            })
    msger = ba.newnode(
                'text',
                attrs={
                    'text': msg,
                    'color': (1-color[0],1-color[1],1-color[2]),
                    'h_align': 'center',
                    'shadow': 0.5,
                    'flatness': 0,             })
    ba.animate_array(msger, 'position', 2, {
                0.0*s: (post[0], post[1]),
                0.05*s: (post[0],post[1]-50),
                0.1*s: (post[0],post[1]-70),
                0.15*s: (post[0],post[1]-85),
                0.2*s: (post[0],post[1]-95),
                0.25*s: (post[0],post[1]-98),
                0.3*s: (post[0],post[1]-100),
                0.35*s: (post[0],post[1]-101),
                0.4*s: (post[0],post[1]-102),
                4.9*s: (post[0],post[1]-103),
                4.95*s: (post[0],post[1]-90),
                5.0*s: (post[0],post[1]-70),
                5.1*s: (post[0],post[1]-1),
                5.15*s:(post[0],post[1]+999)
            })
    ba.animate(msger, 'opacity', {
                0.0*s: 0.0,
                0.07*s: 0.3,
                0.3*s: 0.7,
                4.9*s: 0.7,
                5.0*s: 0.2,
                5.1*s: 0
                            })
    ba.animate(msger, 'scale', {
                0.0*s: (1.3),
                4.4*s: (1.3),
                4.5*s: (1.2)
                            })
def message(msg,aid):
    activity = _ba.get_foreground_host_activity()
    print(activity)
    ctps = [i for i in _ba.get_foreground_host_activity().players if (i.sessionplayer.get_v1_account_id() == aid)]
    if len(ctps) == 0:
            return
    mplayer = ctps[0]
    try:
        color = mplayer.color
    except:
        color = (0.1,0.9,0.1)
    tlen = len(msg)
    x = tlen*50
    with ba.Context(activity):
        anime(x,msg,color)