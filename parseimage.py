from PIL import Image

def image_to_text(image_file, output_file):
	image = Image.open(image_file).convert('RGB')
	width, height = image.size
	with open(output_file, 'w') as file:
		for y in range(height):
			for x in range(width):
				file.write('.' if image.getpixel((x, y)) == (255, 255, 255) else 'O') 
			file.write('\n')

image_to_text('puffer.png', 'puffer.cells')
