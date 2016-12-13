""" treegen v0.9 <github.com/fiedlr/treegen> | (c) 2016 Adam Fiedler | <opensource.org/licenses/MIT> """

from main import Forest, Tree
import random

def run(dimensions):
	""" Run the program with the chosen config - accessible through terminal """
	forest = Forest(dimensions)
	width, height = forest.get_size()

	# spawn a tree (iterations, breaking points, height, max thickness, forest, root height, roughness)
	tr1 = Tree(5, 9, 500, 10, forest, 1.5)
	# place in the middle
	tr1.grow((width // 2, height - 1))

	# create a forest (experimental)
	"""for i in range(100):
		# spawn another tree
		tr = Tree(4, random.randint(4, 10), random.randint(90, 110), 5, forest, random.uniform(1, 2))
		tr.grow((random.randint(20, width - 20), random.randint(20, height - 20)))"""

	# save the resulting image
	forest.render()
	forest.save_image('test.png')

run((800, 600))
