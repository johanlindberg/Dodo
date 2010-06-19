from __future__ import division 
import logging
import pyglet
import os

## To be put in config file:
image_extensions = ['jpg']
#image_extensions = ['JPG']
start_directory = r'c:\pics'
#start_directory = r'/home/johanlindberg/Pictures'
back_img = r'c:\pics\dodo_default\back.jpg'
#back_img = r'/home/johanlindberg/Pictures/Dodo/back.jpg'

class Dodo(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, width=800, height=600, resizable=True)

        self.click_handlers = {}
        self.load_back_sprite()
        self.load_all_images()
        pic=pyglet.image.load(back_img)
        logging.basicConfig(filename = '/home/johanlindberg/Projects/Dodo/log.txt',
                            level = logging.DEBUG)

    def load_all_images(self):
    	print("working directory is",os.curdir)
        """loads all images in current directory if they have a file extension
        included in <image_extensions>."""
        logging.debug("Load_all_images_start")
        self.sprites = []
        """next level exists if there is a directory with the same name as 
        the filename without the file extenstion"""
        for filename in os.listdir(os.curdir):        
            # only load images with supported extensions
            for ext in image_extensions:
#                if filename.lower().endswith(ext.lower()):
                if filename.endswith(ext):
                    fname,extens=os.path.splitext(filename)
                    pic = pyglet.image.load('%s/%s' % (os.curdir, filename))
                    spr = pyglet.sprite.Sprite(pic)
                    spr.filename = fname
                    print(os.path.join(os.curdir,fname))
                    if os.path.isdir(os.path.join(os.curdir,fname)):
                        spr.nextlevelexists=1                 
                    else:
                        spr.nextlevelexists=0                                        
                    self.sprites.append(spr)       
    	self.position_and_scale_all_images()
        logging.debug("Load_all_images_end")
    
    def load_back_sprite(self):
    	self.back_sprite = pyglet.sprite.Sprite(pyglet.image.load(back_img))
        self.position_back_sprite()            

    
    
    def position_back_sprite(self):
    	self.back_sprite_x_pos = self.width - self.back_sprite.width
    	self.back_sprite_y_pos = self.height - self.back_sprite.height    
    	self.back_sprite.position = (self.back_sprite_x_pos , self.back_sprite_y_pos)
    
    
    
    def position_and_scale_all_images(self):	
    	logging.debug("position_and_scale_start")
    	for i in range(len(self.sprites)):
           self.sprites[i].scale=1
           print(self.sprites[i].nextlevelexists)		
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
   
   
   
    def back_image_clicked(self,x,y):
   	print("back_pressed")
   	print(os.curdir,start_directory)
   	print("len")
   	print(len(self.sprites))
   	print(self.sprites[0].nextlevelexists)	
        if os.curdir != start_directory:
            if self.sprites[0].nextlevelexists != -1: 
                (head,tail)=os.path.split(os.curdir)
	        os.curdir=head
	self.load_all_images()
   
              
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
        self.back_sprite.draw()

    def on_mouse_press(self, x, y, button, modifiers):
    	#if the clicked img is the back img. If it is, go back one step
        if x > self.back_sprite_x_pos and y > self.back_sprite_y_pos:
            self.back_image_clicked(x,y)
	    self.load_all_images()
	    return 1
	#Go through the sprites to se which one was clicked    
        for i in xrange(len(self.sprites)):
            sprite = self.sprites[i]
            if x > sprite.x and \
               x < sprite.x + sprite.width and \
               y > sprite.y and \
               y < sprite.y + sprite.height:
             #   self.click_handlers[i](self, x, y, button, modifiers)                 
                 #if the clicked img is a sub-menu, go to next level
                 if self.sprites[i].nextlevelexists==1:
                     os.curdir=os.path.join(os.curdir,self.sprites[i].filename)
		     self.load_all_images()
		     break
		     
		 #if the clicked img is not a sub-meny it should be be fullscreen
		 if self.sprites[i].nextlevelexists==0:
                     self.sprites = [self.sprites[i],]
                     self.sprites[0].nextlevelexists = -1
                     self.position_and_scale_all_images()
                     break

    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.position_back_sprite()
        self.position_and_scale_all_images()

if __name__ == '__main__':
    	
    os.curdir=start_directory
    dodo = Dodo()
    pyglet.app.run()
    
