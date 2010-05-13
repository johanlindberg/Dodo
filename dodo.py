import pyglet
import os

image_extensions = ['jpg']

class Dodo(pyglet.window.Window):
    def __init__(self, directory):
        pyglet.window.Window.__init__(self, fullscreen = True)
        self.load_all_images(directory)

    def load_all_images(self, directory):
        """loads all images in <directory> if they have a file extension
        included in <image_extensions>."""
        self.images = []
        for filename in os.listdir(directory):
            for ext in image_extensions:
                if filename.endswith(ext):
                    # only load images with supported extensions
                    self.images.append(pyglet.image.load('%s/%s' % (directory, filename)))

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
        c, r = self.get_layout(len(self.images))

        # dx, dy is the maximum size of each image in the matrix
        dx, dy = self.width/c, self.height/r

        i, y = 0, 0
        for row in range(r):
            x = 0
            for col in range(c):
                # display image on screen by selecting the center region of the
                # image that fits into the matrix slot.

                # cx, cy is the center of the image
                cx, cy = self.images[i].width/2, self.images[i].height/2

                # xp, yp is the top left position of the image that fits into
                # the matrix slot.
                xp, yp = cx-(dx/2)+2, cy-(dy/2)+2

                # this is the border size around each image
                offset_x, offset_y = 2, 2
                if xp < 0 and yp > 0:
                    # if xp is outside of the image (negative value) we copy the
                    # whole width of the image and adjust the offset accordingly.
                    img = self.images[i].get_region(0,yp,self.images[i].width,dy-4)
                    offset_x = 2+ abs(xp)
                    
                elif xp > 0 and yp < 0:
                    # see above
                    img = self.images[i].get_region(xp,0,dx-4,self.images[i].height)
                    offset_y = 2+ abs(yp)
                    
                elif xp < 0 and yp < 0:
                    # see above
                    img = self.images[i].get_region(0,0,self.images[i].width,self.images[i].height)
                    offset_x, offset_y = 2+ abs(xp), 2+ abs(yp)
                    
                else:          
                    img = self.images[i].get_region(xp,yp,dx-4,dy-4)

                # copy image to screen
                img.blit(x+offset_x, y+offset_y)
                
                i += 1
                x += dx
                
            y += dy

if __name__ == '__main__':
    dodo = Dodo(directory = '/home/johanlindberg/Pictures/')
    pyglet.app.run()
    
