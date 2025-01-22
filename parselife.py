import os.path

from life import FileType, Coord, Grid, get_grid, bounding_box


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


def parse_cells(file):
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



def write_rle(file: FileType, live_cells: list[Coord]):
	x, y, width, height = bounding_box(live_cells)
	grid = get_grid(live_cells, x, y, width, height)
	with open(file, 'w') as f:

		def write_char():
			if count > 1:
				f.write(str(count))
			f.write('b' if not cell else 'o')
	
		f.write(f"x = {width}, y = {height}, rule = B3/S23\n")
		for row in grid:
			cell = row[0]
			count = 1
			for next_cell in row[1:]:
				if next_cell == cell:
					count += 1
				else:
					write_char()
					cell = next_cell
					count = 1

			write_char()
			f.write('$\n')

		f.write('!')


def write_cells(grid: Grid, symbols: str = '.O'):
	for row in grid:
		print(''.join(symbols[c] for c in row).rstrip(symbols[0]))


if __name__ == '__main__':
	cells, width, height = parse_rle('rle/gosper.rle')
	grid = get_grid(cells, 0, 0, width, height)
	write_rle('test.rle', grid, width, height)
	cells2, width2, height2 = parse_rle('test.rle')
	write_cells(get_grid(cells2, 0, 0, width2, height2))

