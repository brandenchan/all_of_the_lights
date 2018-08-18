
import pyglet
import numpy as np


colors = np.random.randint(0, 255, (50, 3))
# colors = np.full((50, 3), 1)

class Animation:
	def __init__(self):
		self.width = 1000
		self.height = 100
		self.screen = pyglet.window.Window(self.width, self.height, "All of the Lights", False, "tool")
		# self.screen.fill(100, 100, 100)
		self.border = 10
		self.n_shapes = 50
		self.circles = []
		makeCircle(100, 10, 10)
		# self.screen.update()
		pyglet.app.run()


	def draw_lights(self):
		available_width = self.width - (2*self.border)
		radius = available_width / self.n_shapes / 2
		diam = 2 * radius
		x_coords = np.linspace(0, available_width, self.n_shapes + 1)[:-1]
		x_coords = x_coords + self.border
		y_coord = self.border

		for i in range(self.n_shapes):
			x_curr = x_coords[i]
			circ_curr = self.canvas.create_oval(x_curr, y_coord, x_curr + diam, y_coord + diam)
			self.circles.append(circ_curr)

	def show_frame(self, colors):
		self.color_circles(colors)
		# self.canvas.pack()
		# self.canvas.update()


	def color_circles(self, colors):
		for i, c_rgb in enumerate(colors):
			c_hex = rgb_to_hex(c_rgb)
			tag = self.circles[i]
			self.canvas.itemconfigure(tag, fill=c_hex)

	def show(self):
		self.canvas.pack()
		self.gui.mainloop()

def rgb_to_hex(rgb):
	return '#%02x%02x%02x' % tuple(rgb)


def animate(x):
	for i in range(100):
		x.color_circles(np.random.randint(0, 255, (50,3)))
		x.canvas.update()

def makeCircle(numPoints, x_center, y_center):
    verts = []
    for i in range(numPoints):
        angle = radians(float(i)/numPoints * 360.0)
        x = 100*cos(angle) + 300
        y = 100*sin(angle) + 200
        verts += [x,y]
    return pyglet.graphics.vertex_list(numPoints, ('v2f', verts))


x = Animation()
# x.draw_lights()
# x.canvas.pack()
# x.gui.after(0, animate(x))
# x.gui.mainloop()


# for i in range(100):
# 	x.show_frame(np.random.randint(0, 255, (50,3)))
# 	x.gui.pack()
# x.show()


