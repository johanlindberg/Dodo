from __future__ import division 

import pyglet
import os
import time

class Dodo(pyglet.window.Window):
    def __init__(self):
        self.load_configuration()
        os.curdir = self.params["start_directory"]
        self.time=time.time()
        self.click_handlers = {}
        self.exclude_folders_list = self.get_exclude_folder_list()
        pyglet.window.Window.__init__(self, resizable=True, fullscreen = True)
        self.sprites = self.load_all_images(os.curdir)
        self.load_back_sprite()
        self.current_path = []
        
    	self.position_and_scale_all_images()

    def get_exclude_folder_list(self):
    	""" In the dodo.conf file there is a exclude_folders_hash that contains a number of lists with folder names to be excluded from loading. 
    	   This function lets the user choose one of the lists at application startup"""
    	i=1
    	temparray=[]
    	print("Configurations:")
    	for key in self.params["exclude_folders_hash"].iterkeys():
    		print i,key
    		i += 1
    		temparray.append(key)    	    	
    	x = input ('Choose configuration number ')
    	return self.params["exclude_folders_hash"][temparray[x-1]] 

    def load_configuration(self):
        self.params = {}

        fin = open("dodo.conf")
        for line in fin.readlines():
            key, value = line.split("=")
            self.params[key.strip()] = eval(value) # NOTE! eval is probably not a
                                                   # good idea in the long run!

        fin.close()

    def load_all_images(self, directory):
        """loads all images in current directory if they have a file extension
        included in <image_extensions>.

        The result is a list of lists mapping the directory structure on disk.
        If an image is associated with a directory it's sprites are stored in
        a list accessed with sprite.contents."""

        result = {}

        for filename in os.listdir(directory):
            # only load images with supported extensions
            for ext in self.params["image_extensions"]:
                fname, extension = os.path.splitext(filename)
                #print(filename,extension.lower(), ext.lower())
                if extension.lower() == ext.lower():
                    if  ((fname in self.exclude_folders_list) and (os.path.isdir(os.path.join(directory,fname)))) :
                    	break #Do not load image and subfolder images if defined in the exclude_folder_list in dodo.conf
                    pic = pyglet.image.load('%s/%s' % (directory, filename))
                    spr = pyglet.sprite.Sprite(pic)
                    
                    # meta data
                    spr.contents = {}
                    #fname, extension = os.path.splitext(filename)
                    if os.path.isdir(os.path.join(directory,fname)):
                        spr.contents = self.load_all_images(os.path.join(directory,fname))

                    spr.filename = filename                    
                    result[filename] = spr

        return result

    def find_sprites(self):
        sprites = self.sprites
        for p in self.current_path:
            if len(sprites[p].contents.values()) == 0:
                sprites = { p : sprites[p] }
            else:
                sprites = sprites[p].contents

        return sprites

    def load_back_sprite(self):
    	self.back_sprite = pyglet.sprite.Sprite(pyglet.image.load(self.params["back_img"]))
        self.position_back_sprite()            
       
    def position_back_sprite(self):
    	self.back_sprite_x_pos = self.width - self.back_sprite.width
    	self.back_sprite_y_pos = 0   
    	self.back_sprite.position = (self.back_sprite_x_pos , self.back_sprite_y_pos)

    def position_and_scale_all_images(self):
        sprites = self.find_sprites().values()
        for s in sprites:
            s.scale = 1

        # c, r is the suggested matrix layout
        c, r = self.get_layout(len(sprites))
        # dx, dy is the maximum size of each image in the matrix
        dx, dy = (self.width - self.params["boarder_size"]*(c + 1)) / c, (self.height - self.params["boarder_size"]*(r + 1)) / r
        x = self.params["boarder_size"]
        y = self.height - dy - self.params["boarder_size"]
        i = 0
        for col in range(c):
           y = self.height - dy - self.params["boarder_size"]
           for row in range(r):
           	#break if all pictures already drawn
                if i == len(sprites):
                   break

                # Scale the image to fit the area.
	    	scale = float(dx / sprites[i].width)
	    	if scale > float(dy / sprites[i].height):
	    	     scale = float(dy / sprites[i].height)
	    	
                sprites[i].position=(x,y)
                sprites[i].scale = scale

                # attach an on_mouse_click handler to this sprite
                def handler(self, x, y, button, modifiers):
                    print "You clicked at pos %s,%s which contains sprite number: %s" % (x, y, i)
                self.click_handlers[i] = handler

                i += 1
                y = y - dy - self.params["boarder_size"]

           x += dx + self.params["boarder_size"]
              
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

    ## event handlers
    ## --------------	

    def on_draw(self):
        self.clear()
        for s in self.find_sprites().values():
            s.draw()

        if len(self.current_path) > 0:
            self.back_sprite.draw()

    def on_mouse_press(self, x, y, button, modifiers):
    	#toggel between fullscreen mode by holding alt-Gr (modifiers = 6 ) and clicking anywhere
    	if modifiers == 6:
    		if self.fullscreen == True:
    			self.set_fullscreen(fullscreen=False, screen=None) 
    		else:
    			self.set_fullscreen(fullscreen=True, screen=None)

        #check if params["min_time_between_clicks"] has gone since last click
        if time.time() - self.time < self.params["min_time_between_clicks"]:
        	return(1)
        self.time=time.time()

        # check back button first
        #print("modifiers value ",modifiers)
        if len(self.current_path) > 0 and \
           x > self.back_sprite.x and \
           x < self.back_sprite.x + self.back_sprite.width and \
           y > self.back_sprite.y and \
           y < self.back_sprite.y + self.back_sprite.height:
            self.current_path.pop()
            
        else:
            sprites = self.find_sprites().values()
            for i in xrange(len(sprites)):
                sprite = sprites[i]
                if x > sprite.x and \
                   x < sprite.x + sprite.width and \
                   y > sprite.y and \
                   y < sprite.y + sprite.height:
                    if modifiers != 2:
                    	#  Modifiers = 2 means that ctrl is pressed.
                    	#  Then sprite will be made almost invisible and not possible to click
                      #self.click_handlers[i](self, x, y, button, modifiers)
                      if sprites[i].opacity == self.params["max_opacity"] and len(sprites) > 1:
                      	self.current_path.append(sprite.filename)
                    
                    else:
                      if sprites[i].opacity == self.params["dim_opacity"]:
                      	sprites[i].opacity = self.params["max_opacity"]
                      else:
                     		sprites[i].opacity = self.params["dim_opacity"]
                    break

        self.position_and_scale_all_images()
        
        
    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.position_back_sprite()
        self.position_and_scale_all_images()

if __name__ == '__main__':
    dodo = Dodo()
    pyglet.app.run()
    
