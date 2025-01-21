import os
import sys
from collections import defaultdict
from collections.abc import Iterable, Collection
from dataclasses import dataclass
from itertools import chain

from PIL import Image, ImageDraw, ImageFont

import parselife

Coord = tuple[int, int]
Grid = list[list[bool]]
FileType = str | bytes | os.PathLike

NEIGHBORHOOD = [
	(-1,  1), (0,  1), (1,  1),
	(-1,  0),          (1,  0),
	(-1, -1), (0, -1), (1, -1),
]
FIXEDSYS = ImageFont.truetype('FSEX300.ttf', 16)

@dataclass
class Cell:
	live: bool = False
	neighbors: int = 0


def get_cell_table(live_cells: Iterable[Coord]):
	cells = defaultdict(Cell)
	for x, y in live_cells:
		cells[(x, y)].live = True
		for dx, dy in NEIGHBORHOOD:
			cells[(x + dx, y + dy)].neighbors += 1
	return cells


def generate(live_cells: Iterable[Coord]):
	for coord, cell in get_cell_table(live_cells).items():
		if cell.neighbors == 3 or (cell.neighbors == 2 and cell.live):
			yield coord


def advance(live_cells: Iterable[Coord], steps: int):
	for _ in range(steps):
		live_cells = list(generate(live_cells))
	return live_cells


def bounding_box(live_cells: Iterable[Coord]):
	min_x = sys.maxsize
	min_y = sys.maxsize
	max_x = ~sys.maxsize
	max_y = ~sys.maxsize
	for x, y in live_cells:
		min_x = min(x, min_x)
		min_y = min(y, min_y)
		max_x = max(x, max_x)
		max_y = max(y, max_y)
	if min_x == sys.maxsize:
		raise ValueError
	return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1


def get_grid(
		live_cells: Iterable[Coord], 
		grid_x: int,
		grid_y: int,
		width: int,
		height: int):
			
	grid = [[False] * width for _ in range(height)]
	for x, y in live_cells:
		x -= grid_x
		y -= grid_y
		if 0 <= x < width and 0 <= y < height:
			grid[y][x] = True
	return grid


def write_cells_txt(grid: Grid, symbols: str = '.O'):
	for row in grid:
		print(''.join(symbols[c] for c in row).rstrip(symbols[0]))


def test():
	import os
	file = 'rle/rpentomino.rle'
	# -50, -24, 100, 48
	live_cells, width, height = parselife.parse(file)
	gen = 0
	while True:
		os.system('cls')
		write_cells_txt(get_grid(live_cells, -50, -24, 100, 48), ['  ', '()'])
		try:
			if input(f"Generation {gen:<6} Population: {len(live_cells):<6}"):
				break
		except KeyboardInterrupt:
			break
		live_cells = list(generate(live_cells))
		gen += 1


def life_generator(live_cells, gen=0):
	yield live_cells, gen
	while True:
		live_cells = list(generate(live_cells))
		gen += 1
		yield live_cells, gen


def get_frames(
		life: Iterable[tuple[Iterable[Coord], int]],
		grid_x: int,
		grid_y: int,
		width: int,
		height: int,
		frame_count: int,
		frame_duration: int,
		scale: int,
		grid: int = 0,
		live_color: str = 'lime',
		dead_color: str = 'black',
		grid_color: str = '#222',
		generations_per_frame=1,
		info=False,
		still_life_duration=None):
	
	if info is True:
		info = 'red'

	def create_image(gen):
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

		if info:
			draw.text((2, height * scale - 16), f"Generation {gen}", info, font=FIXEDSYS)

		return image

	live_cells, gen = next(life)
	live_cells = set(live_cells)
	image = create_image(gen)
	for f in range(frame_count - 1):
		prev = live_cells
		for _ in range(generations_per_frame - 1):
			next(life)
		live_cells, gen = next(life)
		live_cells = set(live_cells)
		if live_cells == prev:
			frame_duration = still_life_duration or frame_duration * (frame_count - f)
			break
		yield image, frame_duration
		image = create_image(gen)

	yield image, frame_duration


def create_animated_gif(file, *frame_generators):
	frames = chain.from_iterable(frame_generators)
	head, duration0 = next(frames)
	durations = [duration0]
	images = []

	for image, duration in frames:
		images.append(image)
		durations.append(duration)

	# print(durations)

	head.save(
		file,
		save_all=True,
		append_images=images,
		duration=durations,
		loop=0)


def bounds(width, height, pad_width, pad_height):
	return -pad_width, -pad_height, width + 2 * pad_width, height + 2 * pad_height


if __name__ == '__main__':
	file = 'rle/p144bigagun.rle'
	live_cells, width, height = parselife.parse(file)
	live_cells = advance(live_cells, 144 * 4)
	life = life_generator(live_cells)
	create_animated_gif('output.gif', get_frames(
		life,
		218 - 25, 246 - 25, 15 + 50, 10 + 50,
		144,  # steps
		50,  # interval
		8,  # scale
		1,  # grid
	))
