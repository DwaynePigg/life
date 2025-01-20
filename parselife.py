import os.path

def parse(file):
	_, ext = os.path.splitext(file)
	if ext == '.rle':
		return parse_rle(file)
	return parse_cells_txt(file)
	

def parse_rle(file):
	coords = []
	width = None
	height = None

	with open(file) as f:
		for line in f:
			line = line.strip()
			if not line.startswith('#'):
				header = {}
				for part in line.split(','):
					key, _, value = part.partition('=')
					header[key.strip()] = value.strip()
				width = int(header['x'])
				height = int(header['y'])
				break

		x = 0
		y = 0
		run = 0

		for line in f:
			for c in line.strip():
				if c.isdigit():
					run = run * 10 + int(c)
				else:
					run = max(run, 1)
					if c == 'b':
						x += run
					elif c == 'o':
						for _ in range(run):
							coords.append((x, y))
							x += 1
					elif c == '$':
						y += run
						x = 0
					elif c == '!':
						break
					run = 0

	return coords, width, height


def parse_cells_txt(file):
	coords = []
	max_x = 0
	y = 0
	
	def parse_line(line):
		nonlocal max_x
		line = line.strip()
		max_x = max(max_x, len(line))
		for x, c in enumerate(line):
			if c == 'O':
				coords.append((x, y))
	
	with open(file) as f:
		for line in f:
			if not line.startswith('!'):
				break
		parse_line(line)
		for y, line in enumerate(f, start=1):
			parse_line(line)
			
	return coords, max_x, y + 1
