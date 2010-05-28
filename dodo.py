from __future__ import division 
import pyglet
import os

image_extensions = ['jpg']
#image_extensions = ['JPG']

class Dodo(pyglet.window.Window):
    def __init__(self, directory):
        pyglet.window.Window.__init__(self, width=900, height=600)
        self.load_all_images(directory)

    def load_all_images(self, directory):
        """loads all images in <directory> if they have a file extension
        included in <image_extensions>."""
        self.sprites = []
        for filename in os.listdir(directory):
            for ext in image_extensions:
#                if filename.lower().endswith(ext.lower()):
                if filename.endswith(ext):
                    # only load images with supported extensions
                    pic=pyglet.image.load('%s/%s' % (directory, filename))
                    #pic=pyglet.image.load('c:\pics\dodo1.jpg')
                    self.sprites.append(pyglet.sprite.Sprite(pic))			

    def get_layout(self, n):
        """Returns a tuple with a suggested matrix size for displaying <n> images
        'optimized' for the current screen resolution. NOTE! This implementation
        assumes all images are square (width=height)."""
        ratio = float(self.width) / self.height

        # w, h is the suggested matrix size. it starts with 1 image and "grows"
        # into a size that fits all <n> images.
        w, h = 1, 1
        for i in xrange(n):
            if i >= w * h:
                # if the matrix can't hold <i> images we need to grow it
                # x, y are the ratios when the matrix grows in width and height
                # which ever differs the least from the 'optimal' ratio (screen
                # resolution) is chosen.
                x, y = float(w+1)/h, w/float(h+1)
                if abs(ratio-x) < abs(ratio-y):
                    w += 1 # grow in width
                else:
                    h += 1 # grow in height
                    
        return (w,h)
        
    def on_draw(self):
        self.clear()

        # c, r is the suggested matrix layout
        c, r = self.get_layout(len(self.sprites))
        print("cols",c)
        print("rows",r)
        # dx, dy is the maximum size of each image in the matrix
        dx, dy = self.width/c, self.height/r
        x = 0
        y = 0
        i = 0
        for col in range(c):
           y = 0
           for row in range(r):
           	#break if all pictures already drawn
                if i==len(self.sprites):
                   break
                # Scale the image to fit the area.
		scale=float(dx / (self.sprites[i].width))
		if scale > float(dy / self.sprites[i].height):
		     scale = float(dy / self.sprites[i].height)
		print("scale" ,scale)     
                self.sprites[i].position=(x,y)
                self.sprites[i].scale = scale
                self.sprites[i].draw()
                print("x",x)
                print("y",y)
                i += 1
                y += dy
                print("dy",dy)
                print("i",i)
           x += dx

if __name__ == '__main__':
#    dodo = Dodo(directory = r'c:\pics')
    dodo = Dodo(directory = r'/home/johanlindberg/Pictures/Dodo/')
    pyglet.app.run()
    
