import os

from life import get_grid, generate
import parselife


file = 'rle/gosper.rle'
# -50, -24, 100, 48
live_cells, width, height = parselife.parse(file)
gen = 0
while True:
	os.system('cls')
	parselife.write_cells(get_grid(live_cells, -50, -24, 100, 48), ['  ', '()'])
	try:
		if input(f"Generation {gen:<6} Population: {len(live_cells):<6}"):
			break
	except KeyboardInterrupt:
		break
	live_cells = list(generate(live_cells))
	gen += 1
