import ba
import _ba
import bastd
#炸队绘制 by Wsdx233 & inkMedic
import picreader
#屏幕数据
width = 2
height = 2
size = (100,100)
fps = 0
#像素点
class Pix:
  def __init__(self,color,pos):
    global size,width,height
    self.color = color
    self.pos = pos
    self.size = (size[0]/width,size[1]/height)
    self.x = self.pos[0] * self.size[0]
    self.y = self.pos[1] * self.size[1]
    
    #原点
    opos = (
      -size[0]/2,
      -size[1]/2
    )
    
    self.img = bastd.actor.image.Image(
      ba.gettexture("white"),
      color = self.color,
      scale = (self.size[0],self.size[1]),
      position = (opos[0]+self.x,opos[1]+self.y)
    )

#保存像素点



#把颜色绘制出来

def reader(fps):
    colors = []
    xbit = []
    while True:
        x = 0
        y = 72
        color = picreader.reader(x,y,fps)
        xbit.append(color)
        x =+1
        if x == 97:
            x = 0
            y =+1
            colors.append(color)
            xbit = []
        if y == 720:
            break
        return colors
def painter():
    fps = 1
    while True:
        colors = reader(fps)
        fps =+1
        if fps == 2124:
            return
        for y,line in enumerate(colors):
            for x,e in enumerate(line):
                ba.pixes.append(Pix(e,(x,y)))
        ba.pixes = []
def running():
    ba.Timer(0.1,painter)




