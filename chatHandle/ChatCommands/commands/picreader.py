import cv2
def reader(x,y,fps):
    image = cv2.imread("video/v"+fps+".bmp")#读取图像  
    (b,g,r) = image[x,y]#读取(0,0)像素，Python中图像像素是按B,G,R顺序存储的
    (r,b,g) = (r/255,b/255,g/255)
    return (r,b,g)
