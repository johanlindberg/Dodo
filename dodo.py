from __future__ import division 
import logging
import pyglet
import os

## To be put in config file:
image_extensions = ['jpg']
#image_extensions = ['JPG']
#start_directory = r'c:\pics'
start_directory = r'/home/johanlindberg/Pictures'
#back_img = r'c:\pics\dodo_default\back.jpg'
back_img = r'/home/johanlindberg/Pictures/Dodo/back.jpg'

class Dodo(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, width=800, height=600, resizable=True)

        self.click_handlers = {}
        self.load_all_images()
        logging.basicConfig(filename = '/home/johanlindberg/Projects/Dodo/log.txt',
                            level = logging.DEBUG)

    def load_all_images(self):
    	print("working directory is",os.curdir)
        """loads all images in current directory if they have a file extension
        included in <image_extensions>."""
        logging.debug("Load_all_images_start")
        self.sprites = []
        self.filename = []
        """next level exists if there is a directory with the same name as 
        the filename without the file extenstion"""
        self.nextlevelexists=[]
        for filename in os.listdir(os.curdir):        
            for ext in image_extensions:
#                if filename.lower().endswith(ext.lower()):
                if filename.endswith(ext):
                    fname,extens=os.path.splitext(filename)
                    print(os.path.join(os.curdir,fname))
                    if os.path.isdir(os.path.join(os.curdir,fname)):
                        self.nextlevelexists.append(1)                 
                    else:
                        self.nextlevelexists.append(0)
                    # only load images with supported extensions
                    pic=pyglet.image.load('%s/%s' % (os.curdir, filename))
                    self.filename.append(fname)
                    self.sprites.append(pyglet.sprite.Sprite(pic))
        """Add back sprite if this is not the base diretory"""
        if os.curdir != start_directory:
            pic=pyglet.image.load(back_img)
            self.sprites.append(pyglet.sprite.Sprite(pic))
            self.filename.append('back')
            self.nextlevelexists.append(-1)        
    	self.position_and_scale_all_images()
        logging.debug("Load_all_images_end")            
    
    def position_and_scale_all_images(self):	
    	logging.debug("position_and_scale_start")
    	for i in range(len(self.sprites)):
           self.sprites[i].scale=1
           print(self.nextlevelexists[i])		
        # c, r is the suggested matrix layout
        c, r = self.get_layout(len(self.sprites))
        # dx, dy is the maximum size of each image in the matrix
        dx, dy = self.width/c, self.height/r
        logging.debug("dx=",dx,"dy=",dy)
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
	    	self.sprites[i].position=(x,y)
                self.sprites[i].scale = scale

                # attach an on_mouse_click handler to this sprite
                def handler(self, x, y, button, modifiers):
                    print "You clicked at pos %s,%s which contains sprite number: %s" % (x, y, i)
                self.click_handlers[i] = handler

                i += 1
                y += dy
           x += dx
        logging.debug("position_and_scale_end")
   
              
    def get_layout(self, n):
        """Returns a tuple with a suggested matrix size for displaying <n> images
        'optimized' for the current screen resolution. NOTE! This implementation
        assumes all images are square (width=height)."""
        logging.debug("get_layout_start")
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
 	logging.debug("Get_layout_end")                   
        return (w,h)

    ## event handlers
    ## --------------

    def on_draw(self):
    	logging.debug("on_draw")
        self.clear()
        for i in range(len(self.sprites)):
           self.sprites[i].draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for i in xrange(len(self.sprites)):
            sprite = self.sprites[i]
            if x > sprite.x and \
               x < sprite.x + sprite.width and \
               y > sprite.y and \
               y < sprite.y + sprite.height:
             #   self.click_handlers[i](self, x, y, button, modifiers)
                 
                 #if the clicked img is the back img, go up one level
                 if self.nextlevelexists[i]==-1:
                     (head,tail)=os.path.split(os.curdir)
                     os.curdir=head
                     self.load_all_images()
                     break	
                 
                 #if the clicked img is a sub-menu, go to next level
                 if self.nextlevelexists[i]==1:
                     os.curdir=os.path.join(os.curdir,self.filename[i])
		     self.load_all_images()
		     break
		     
		 #if the clicked img is not a sub-meny or back it should be be fullscreen
		 if self.nextlevelexists[i]==0:
                     self.sprites = [self.sprites[i],]
                     self.filename = [self.filename[i],]
                     self.nextlevelexists = [self.nextlevelexists[i],]

    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.position_and_scale_all_images()

if __name__ == '__main__':
    	
    os.curdir=start_directory
    dodo = Dodo()
    pyglet.app.run()
    
