# -*- coding: iso-8859-1 -*-
from __future__ import division 

import pyglet
import os

import time

class Dodo_obj:
    def __init__(self, directory, filename):
	self.params = load_configuration()
	self.path = directory 
	self.name, extension = os.path.splitext(filename)
#	print(time.time()) 
	pic = pyglet.image.load('%s/%s' % (directory, filename))
#	print(time.time())
#	print(directory,filename) 
#	print("end")
	self.sprite = pyglet.sprite.Sprite(pic)
	print(self.name.decode('iso8859-1'))
	self.label=pyglet.text.Label(text=self.name.decode('iso8859-1'), color=(0, 0, 0, 255),font_size= 16, bold = True, font_name='Times New Roman',anchor_x = "center", anchor_y = "top" )
	self.label.set_style('color', (255,255,255,255))
	self.label.set_style('background_color', (0,0,0,255))

	
	#Check_for_video
	self.video_exist = False
	for ext in self.params["video_extensions"]:
	    #print(os.path.join(directory,self.name+ext))
            if os.path.isfile(os.path.join(directory,self.name+ext)):
                self.video_exist = True
                #print (os.path.join(directory,self.name+ext))
                self.video_source = pyglet.media.load(os.path.join(directory,self.name+ext))
        
        self.sound_exist = False
        #Check for sound
        for ext in self.params["sound_extensions"]:
	    #print(os.path.join(directory,self.name+ext))
            if os.path.isfile(os.path.join(directory,self.name+ext)):
                self.sound_exist = True
                #print (os.path.join(directory,self.name+ext))
                self.sound_source = pyglet.media.load(os.path.join(directory,self.name+ext), streaming=False)

        self.is_dir = os.path.isdir(os.path.join(directory,self.name))
        self.visible = True
        
    def togle_sprite_visible(self):
        if self.visible == False:
        	self.sprite.opacity = self.params["max_opacity"]
        	self.visible = True
        else:
                self.sprite.opacity = self.params["dim_opacity"]
                self.visible = False

        
class Dodo(pyglet.window.Window):
    def __init__(self):
        self.params = load_configuration()
        self.current_dodo = False
        os.curdir = self.params["start_directory"]
        self.time=time.time()
        self.click_handlers = {}
        #self.exclude_folders_list = self.get_exclude_folder_list()
        self.sprites = []
        self.sprites = self.load_all_images(os.curdir)
        pyglet.window.Window.__init__(self, resizable=True, fullscreen=True)        
        self.load_back_sprite()
        self.current_path = []
    	self.position_and_scale_all_images()

    def get_exclude_folder_list(self):
    	""" In the dodo.conf file there is a exclude_folders_hash that contains a number of lists with folder names to be excluded from loading. 
    	   This function lets the user choose one of the lists at application startup"""
    	
    	i=2
    	temparray=[]
    	temparray.append('Alla')
    	print("Configurations:")
    	print("1 Alla") 
    	for key in self.params["exclude_folders_hash"].iterkeys():
    		print i,key
    		i += 1
    		temparray.append(key)    	    	
    	x = input ('Choose configuration number: ')
    	if x == 1 :
    	   return []
    	return self.params["exclude_folders_hash"][temparray[x-1]] 

    
    def load_all_images(self, directory):
        """loads all images in current directory if they have a file extension
        included in <image_extensions>.

        The result is a list of lists mapping the directory structure on disk.
        If an image is associated with a directory it's sprites are stored in
        a list accessed with sprite.contents."""

        result = []

        for filename in os.listdir(directory):
            # only load images with supported extensions
            for ext in self.params["image_extensions"]:
                fname, extension = os.path.splitext(filename)
                #print(filename,extension.lower(), ext.lower())
                if extension.lower() == ext.lower():
                    temp = (Dodo_obj(directory,filename))
                    if temp.is_dir:
                       result.extend(self.load_all_images(os.path.join(directory,temp.name)))
                    result.append(temp)
        return result

    def find_dodos(self):
    	result = []
    	if self.current_dodo == False:
    	    for obj in self.sprites:
            	if obj.path == os.curdir:
               		result.append(obj)
        else:
        	result=[self.current_dodo]
        return result

    def load_back_sprite(self):
    	self.back_sprite = pyglet.sprite.Sprite(pyglet.image.load(self.params["back_img"]))
        self.position_back_sprite()            
       
    def position_back_sprite(self):
    	self.back_sprite_x_pos = self.width - self.back_sprite.width
    	self.back_sprite_y_pos = 0   
    	self.back_sprite.position = (self.back_sprite_x_pos , self.back_sprite_y_pos)

    def position_and_scale_all_images(self):
        dodos = self.find_dodos()
        for s in dodos:
            s.sprite.scale = 1

        # c, r is the suggested matrix layout
        c, r = self.get_layout(len(dodos))
        # dx, dy is the maximum size of each image in the matrix
        dx, dy = (self.width - self.params["boarder_size"]*(c + 1)) / c, (self.height - self.params["boarder_size"]*(r + 1)) / r
        x = self.params["boarder_size"]
        y = self.height - dy - self.params["boarder_size"]
        i = 0
        for col in range(c):
           y = self.height - dy - self.params["boarder_size"]
           for row in range(r):
           	#break if all pictures already drawn
                if i == len(dodos):
                   break

                # Scale the image to fit the area.
	    	scale = float(dx / dodos[i].sprite.width)
	    	if scale > float(dy / dodos[i].sprite.height):
	    	     scale = float(dy / dodos[i].sprite.height)
	    	
                dodos[i].sprite.position=(x,y)
                dodos[i].label.x=x+dodos[i].sprite.width*scale*0.5
                dodos[i].label.y=y+dodos[i].sprite.height*scale+5
                #pyglet.text.Label(dodos[i].name, color=(0, 100, 100, 133),
                 #         font_name='Times New Roman',width = 150, x=x, y=y+dodos[i].sprite.height*scale, anchor_x = "right", anchor_y = "top" )
                          
               # dodos[i].label.set_style(0, "color"=(0, 0, 0, 255))
                dodos[i].sprite.scale = scale

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
        
        
    def play_sound(self,sound_source):
        sound_source.play()

    ## event handlers
    ## --------------	

    def on_draw(self):
        self.clear()
        for s in self.find_dodos():
            s.sprite.draw()
            s.label.draw()

        if len(self.current_path) > 0:
            self.back_sprite.draw()
    
    def on_key_press(self,symbol, modifiers):
    	#Reload all images when key "i" is pressed 
        if symbol == 105:
          os.curdir = self.params["start_directory"]
          self.sprites = []
          self.sprites = self.load_all_images(self.params["start_directory"])
          self.current_dodo = False
          self.current_path = []
#          print(self.current_path)
#          print(len(self.sprites))
          self.position_and_scale_all_images()
                  

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
            if self.current_dodo != False:
            	self.current_dodo = False
           	
            else:
           	self.current_path.pop()
            	os.curdir,dummy = os.path.split(os.curdir)
            
        else:
            dodos = self.find_dodos()
            for i in xrange(len(dodos)):
                sprite = dodos[i].sprite
                if x > sprite.x and \
                   x < sprite.x + sprite.width and \
                   y > sprite.y and \
                   y < sprite.y + sprite.height:
                    if modifiers != 2:
                    	#  Modifiers = 2 means that ctrl is pressed.
                    	#  Then sprite will be made almost invisible and not possible to click
                      #self.click_handlers[i](self, x, y, button, modifiers)
                      if dodos[i].visible:
                      	if dodos[i].is_dir:
                      	   self.current_path.append(dodos[i].name)
                      	   os.curdir=os.path.join(os.curdir,dodos[i].name)
                      	else:
                      	     if self.current_dodo == False:
                      	         self.current_dodo = dodos[i]
                 	     if self.current_dodo.sound_exist:
                      	     	 self.play_sound(self.current_dodo.sound_source)
                    else:
                      dodos[i].togle_sprite_visible()
                    break

        self.position_and_scale_all_images()
        
        
    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.position_back_sprite()
        self.position_and_scale_all_images()

def load_configuration():
        params = {}

        fin = open("dodo.conf")
        for line in fin.readlines():
            key, value = line.split("=")
            params[key.strip()] = eval(value) # NOTE! eval is probably not a
                                                   # good idea in the long run!

        fin.close()
	return params

if __name__ == '__main__':
    dodo = Dodo()
    pyglet.app.run()
    
