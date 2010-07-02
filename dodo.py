from __future__ import division 

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
        self.sprites = self.load_all_images(os.curdir)
        
        self.current_path = []

        # load back image
        pic = pyglet.image.load(back_img)
        self.back = pyglet.sprite.Sprite(pic)
        self.back.filename = 'back'

    	self.position_and_scale_all_images()

    def load_all_images(self, directory):
        """loads all images in current directory if they have a file extension
        included in <image_extensions>.

        The result is a list of lists mapping the directory structure on disk.
        If an image is associated with a directory it's sprites are stored in
        a list accessed with sprite.contents."""

        result = {}

        for filename in os.listdir(directory):
            # only load images with supported extensions
            for ext in image_extensions:
                if filename.lower().endswith(ext.lower()):
                    pic = pyglet.image.load('%s/%s' % (directory, filename))
                    spr = pyglet.sprite.Sprite(pic)
                    
                    # meta data
                    spr.contents = {}
                    fname, extension = os.path.splitext(filename)
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

    def position_and_scale_all_images(self):
        sprites = self.find_sprites().values()
        for s in sprites:
            s.scale = 1

        # c, r is the suggested matrix layout
        c, r = self.get_layout(len(sprites))
        # dx, dy is the maximum size of each image in the matrix
        dx, dy = self.width/c, self.height/r
        x = 0
        y = 0
        i = 0
        for col in range(c):
           y = 0
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
                y += dy

           x += dx
              
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
            self.back.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        # check back button first
        if len(self.current_path) > 0 and \
           x > self.back.x and \
           x < self.back.x + self.back.width and \
           y > self.back.y and \
           y < self.back.y + self.back.height:
            self.current_path.pop()            

        else:
            sprites = self.find_sprites().values()
            for i in xrange(len(sprites)):
                sprite = sprites[i]
                if x > sprite.x and \
                   x < sprite.x + sprite.width and \
                   y > sprite.y and \
                   y < sprite.y + sprite.height:
                    #self.click_handlers[i](self, x, y, button, modifiers)
                    self.current_path.append(sprite.filename)
                    break

        self.position_and_scale_all_images()

    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.position_and_scale_all_images()

if __name__ == '__main__':
    	
    os.curdir=start_directory
    dodo = Dodo()
    pyglet.app.run()
    
