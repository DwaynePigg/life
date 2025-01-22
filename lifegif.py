from collections.abc import Iterable
from itertools import chain

from PIL import Image, ImageDraw, ImageFont

from life import Coord, life_generator, advance
import parselife

FIXEDSYS = ImageFont.truetype('FSEX300.ttf', 16)


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


########################

file = 'p416gun-adv.rle'
live_cells, width, height = parselife.parse(file)
width, height = 990, 979
# live_cells = advance(live_cells, 416)
# parselife.write_rle('p416gun-close-adv.rle', live_cells)
life = life_generator(live_cells)
create_animated_gif('output.gif', get_frames(
	life,
	*bounds(width, height, 1, 1),
	# 471 - 35, 447 - 30, 11 + 70, 20 + 60,
	416,  # frames
	20,  # duration
	1,  # scale
	0,  # grid
	# info=True,
))

# https://conwaylife.com/wiki/60P5H2V0
# 218 - 25, 246 - 25, 15 + 50, 10 + 50,