from collections import defaultdict
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from life import FileType, Coord, Cell, advance, NEIGHBORHOOD
import parselife

Color = str | tuple[int, int, int]


def create_png(
		file: FileType,
		live_cells: list[Coord],
		grid_x: int,
		grid_y: int,
		width: int,
		height: int,
		scale: int,
		grid: int = 0,
		live_color: str = 'white',
		dead_color: str = 'black',
		grid_color: str = '#222',
		neighbor_counter=None):
	
	font_size = 32
	font = ImageFont.truetype('FSEX300.ttf', 64)

	image = Image.new('RGB', (width * scale - grid, height * scale - grid), dead_color)
	draw = ImageDraw.Draw(image)
	for x, y in live_cells:
		x -= grid_x
		y -= grid_y
		draw.rectangle((
			x * scale, 
			y * scale,
			(x + 1) * scale - 1 - grid,
			(y + 1) * scale - 1 - grid), fill=live_color)
	if grid:
		for x in range(1, width):
			x = x * scale - 1
			draw.rectangle((x - grid + 1, 0, x, height * scale), fill=grid_color)
		for y in range(1, height):
			y = y * scale - 1
			draw.rectangle((0, y - grid + 1, width * scale, y), fill=grid_color)
	
	
	cells = defaultdict(Cell)
	for x, y in live_cells:
		cells[(x, y)].live = True
		for dx, dy in NEIGHBORHOOD:
			cells[(x + dx, y + dy)].neighbors += 1
	
	for y in range(height):
		for x in range(width):
			cell = cells[(x + grid_x, y + grid_y)]
			if cell.live:
				color = 'green' if cell.neighbors in {3, 2} else 'black'
			else:
				color = 'lime' if cell.neighbors == 3 else 'gray'
			if cell.neighbors:
				draw.text((x * scale + 22, y * scale + 6), str(cell.neighbors), color, font=font)

	image.save(file)


if __name__ == '__main__':
	file = 'rle/glider.rle'
	live_cells, width, height = parselife.parse(file)
	live_cells = advance(live_cells, 4)
	create_png(
		'life.png',
		live_cells,
		-2, -2,  # x, y
		width + 4, height + 4, # width, height
		80,  # scale
		4,  # grid
		'lime', 'black', '#222',
	)