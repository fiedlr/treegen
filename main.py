""" treegen v0.9 <github.com/fiedlr/treegen> | (c) 2016 Adam Fiedler | <opensource.org/licenses/MIT> """

import math
import random
from PIL import Image, ImageDraw, ImageColor

class Forest:
	""" The main class taking care of generating the whole picture, it can contain several trees """
	def __init__(self, dimensions):
		self.__image = Image.new("RGB", dimensions, (255, 255, 255))
		# Tree container
		self.__trees = []

	def get_image(self):
		""" Returns the current canvas """
		return self.__image

	def get_size(self):
		""" Returns the forest's size """
		return self.__image.size

	def add_tree(self, tree):
		""" Adds the tree instance into the forest """
		if isinstance(tree, Tree):
			self.__trees.append(tree)

	def render(self):
		""" Render itself """
		for tree in self.__trees:
			tree.draw()

	def save_image(self, filename):
		""" Saves the resulting canvas """
		self.__image.save(filename)

class Tree:
	""" The tree generator """
	def __init__(self, iterations, bpoints, tallness, thickness, forest, root_height=0, roughness=1):
		# Attribute containers
		self.__iterations = iterations
		self.__bpoints = bpoints
		self.__tallness = tallness
		self.__thickness = thickness
		self.__forest = forest
		self.__root_height = root_height # 0 for random
		self.__roughness = roughness # 0 for no roughness
		# Image container
		self.__image = ImageDraw.Draw(forest.get_image())
		# Shape containers
		self.__points = {}
		self.__polygons = {}
		# Add into forest
		self.__position = None # hasn't grown up yet
		forest.add_tree(self)

	def __get_angle(self, iteration, bpoint):
		""" Get the branch angle based on the iteration """
		if iteration == 0:
			return 0
		else:
			det_angle = math.pi / 3 if bpoint < self.__bpoints - iteration else math.pi / 6
			return det_angle / iteration

	def __get_new_vector(self, next_iteration, vector, bpoint):
		""" Return the det vector for the next iteration """
		# Rotate the current vector
		angle = (-1) ** bpoint * self.__get_angle(next_iteration, bpoint)
		x = math.cos(angle) * vector[0] - math.sin(angle) * vector[1]
		y = math.sin(angle) * vector[0] + math.cos(angle) * vector[1]
		# Shrink a little
		return (x / 1.61, y / 1.61) # no need for rounding it seems

	def __wrap_in_polygon(self, point, iteration, vector):
		""" Wraps the point in a polygon to create irregularity """
		quadrants = {1: [], 2: [], 3: [], 4: []}
		hspan = max(self.__thickness - 2, 1)
		wspan = hspan # turned out better
		randpoint = None
		for vertix in range(4, 17):
			# Place points regularly over the quadrants
			quadrant = 4 - vertix % 4
			if quadrant == 1:
				shift = (random.randint(0, wspan), random.randint(0, hspan))
			elif quadrant == 2:
				shift = (random.randint(-wspan, -1), random.randint(0, hspan))
			elif quadrant == 3:
				shift = (random.randint(-wspan, -1), random.randint(-hspan, -1))
			else:
				shift = (random.randint(0, wspan), random.randint(-hspan, -1))
			# Get a random point within the given span map
			randpoint = (point[0] + shift[0], point[1] + shift[1])
			quadrants[quadrant].append(randpoint)
		# Sort in order to avoid gaps (need a better solution)
		for q, quadrant in quadrants.items():
			quadrant.sort(key=lambda tup: tup[0], reverse=True if q < 3 else False)
		return quadrants[1] + quadrants[2] + quadrants[3] + quadrants[4]

	def __spawn_branch(self, pos, iteration, vector):
		""" Creates a new branch (made up of bpoints) """
		if iteration < self.__iterations:
			if iteration not in self.__points:
				self.__points[iteration] = []
			self.__points[iteration].append([]) # tree structure
			branch = self.__points[iteration][-1]
			if self.__roughness:
				if iteration not in self.__polygons:
					self.__polygons[iteration] = []
				self.__polygons[iteration].append([]) # tree roughness
				twig = self.__polygons[iteration][-1]
			prev_pos = pos
			for bpoint in range(self.__bpoints - iteration):
				if bpoint == 1 and iteration == 0 and self.__root_height > 0:
					# Extend the root
					dist = self.__root_height
				else:
					# Diversify the distances for non-zero bpoints
					dist = int(bool(bpoint)) * random.uniform(0.5, 1)
				new_point = (prev_pos[0] - dist * vector[0], prev_pos[1] - dist * vector[1])
				branch.append(new_point)
				# Build a body
				if self.__roughness:
					twig.append(self.__wrap_in_polygon(new_point, iteration, vector))
				# Add a branch only from intermediate bpoints
				if bpoint > 0:
					# Alternate branch directions
					new_vector = self.__get_new_vector(iteration + 1, vector, bpoint)
					self.__spawn_branch(new_point, iteration + 1, new_vector)
					if bpoint == self.__bpoints - iteration - 1:
						ad_vector = self.__get_new_vector(iteration + 1, vector, bpoint+1)
						self.__spawn_branch(new_point, iteration + 1, ad_vector)
				# Shift to new position
				prev_pos = new_point

	def __polysort(self, poly):
		""" Sorts the points so that they would be in right order for render """
		# Needs a better solution, too many loops
		left = []; right = []
		left.append(poly[0])
		for point in poly:
			if point[0] < self.__position[0]:
				left.append(point)
			elif point[0] > self.__position[0]:
				right.append(point)
		left.sort(key=lambda tup: tup[1], reverse=True)
		right.sort(key=lambda tup: tup[1])
		return left + right

	def get_random_brown(self):
		""" Returns a random shade of brown """
		r = random.randint(60, 80)
		g = b = random.randint(20, 30)
		return (r, g, b)

	def get_random_green(self):
		""" Returns a random shade of green """
		r = random.randint(0, 36)
		g = random.randint(100, 125)
		b = random.randint(32, 56)
		return (r, g, b)

	def get_size(self):
		""" Get approximate size of the tree """
		hitbox = self.get_hitbox()
		return (self.__tallness, abs(hitbox[1][0] - hitbox[-1][0]))

	def get_position(self):
		""" Return position """
		return self.__position

	def get_hitbox(self):
		""" Determine an approximate of hitbox (with minimum of points) """
		hitbox = []
		if len(self.__points):
			# Include main branch
			hitbox.append(self.__points[0][0][0]); hitbox.append(self.__points[0][0][-1])
			# Return last points of last 'real' branches
			if len(self.__points) > 1:
				boundary = min(2, self.__iterations-1)
				for br, branch in enumerate(self.__points[boundary]):
					if self.__roughness:
						hitbox.append(self.__polygons[boundary][br][-1][-1]);
					else:
						hitbox.append(branch[0]); hitbox.append(branch[-1])
			hitbox = self.__polysort(hitbox)
		return hitbox

	def grow(self, position):
		""" Starts the growth cycle """
		dist = round(self.__tallness / self.__bpoints)
		self.__position = position
		self.__spawn_branch(self.__position, 0, self.__get_new_vector(0, (0, dist), 0))

	def draw(self):
		""" Renders the tree onto the forest """
		for i, iteration in self.__points.items():
			for br, branch in enumerate(iteration):
				brown = self.get_random_brown(); green = self.get_random_green()
				# Connect with lines
				self.__image.line(branch, brown if i < 3 else green, width=self.__thickness - i * 2)
				# Add roughness
				if self.__roughness:
					for bpoint in range(len(branch)):
						self.__image.polygon(self.__polygons[i][br][bpoint], brown if i < 3 else green)
