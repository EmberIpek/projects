# Author: Ember Ipek
# Date: 4/21/2025
# Fun little project with HC_SR04 sensor, maps the distance to an RGB value
# to create a smooth rainbow gradient 

import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0x6F00D2, 0xFF5809]
colors_table = {"RED": ["0110000", 0xFF0000],
				"ORANGE": ["1101101", 0xFF8000],
				"WHITE": ["1111001", 0xFFFFFF],
				"YELLOW": ["0110011", 0xFFFF00],
				"DARK BLUE": ["1011011", 0x0000FF],
				"LIGHT BLUE": ["1011111", 0x0020FF],
				"PURPLE": ["1110000", 0x0A00FF],
				"PINK": ["1111111", 0xFF50B4],
				"TURQUOISE": ["1111011", 0x00FF30],
				"MAGENTA": ["1110111", 0xFF00FF],
				"CYAN": ["0011111", 0x00FFFF],
				"LIME": ["1001110", 0x30FF00],
				"GREEN": ["0111101", 0x00FF00]}
rainbow_keys = ["RED", "ORANGE", "YELLOW", "LIME", "GREEN",
                "TURQUOISE", "CYAN", "LIGHT BLUE", "DARK BLUE",
                "PURPLE", "MAGENTA", "PINK"]
rainbow_colors = [colors_table[key][1] for key in rainbow_keys]

segments_pins = [16, 18, 22, 24, 26, 15, 19]
R = 11
G = 12
B = 13
trigger = 23
echo = 21

def setup(Rpin, Gpin, Bpin):
	global pins
	global p_R, p_G, p_B
	pins = {'pin_R': Rpin, 'pin_G': Gpin, 'pin_B': Bpin}
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	for i in pins:
		GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode as output
		GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to turn LED off
	for i in segments_pins:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, GPIO.LOW)
	GPIO.setup(trigger,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(echo,GPIO.IN)
	
	p_R = GPIO.PWM(pins['pin_R'], 2000)  # set PWM frequency to 2KHz
	p_G = GPIO.PWM(pins['pin_G'], 2000)
	p_B = GPIO.PWM(pins['pin_B'], 2000)
	
	p_R.start(100)      # Initial duty Cycle = 100 (All LEDs off)
	p_G.start(100)
	p_B.start(100)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def off():
	for i in pins:
		GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds
  
def interpolate_color(c1, c2, t):
	r1, g1, b1 = (c1 >> 16) & 0xFF, (c1 >> 8) & 0xFF, c1 & 0xFF
	r2, g2, b2 = (c2 >> 16) & 0xFF, (c2 >> 8) & 0xFF, c2 & 0xFF

	r = int(r1 + (r2 - r1) * t)
	g = int(g1 + (g2 - g1) * t)
	b = int(b1 + (b2 - b1) * t)

	return (r << 16) + (g << 8) + b
  
def distance_to_color(distance, max_distance):
	normalized = max(0, min(distance / max_distance, 1))

	segment_count = len(rainbow_colors) - 1
	segment_length = 1.0 / segment_count

	index = int(normalized / segment_length)
	t = (normalized - index * segment_length) / segment_length

	if index >= segment_count:
		return rainbow_colors[-1]

	return interpolate_color(rainbow_colors[index], rainbow_colors[index + 1], t)
	

def setColor(col):
	R_val = (col & 0xff0000) >> 16 # extract each R,G,B color component from list of colors
	G_val = (col & 0x00ff00) >> 8
	B_val = (col & 0x0000ff) >> 0

	R_val = map(R_val, 0, 255, 0, 100)  # map each RGB color component from 0-255 levels to 0-100
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)
	
	p_R.ChangeDutyCycle(100-R_val)     # Change duty cycle
	p_G.ChangeDutyCycle(100-G_val)
	p_B.ChangeDutyCycle(100-B_val)

def segments(seg):
	i = 0
	for char in seg:
		if (char == '1'):
			GPIO.output(segments_pins[i], GPIO.HIGH)
		elif (char == '0'):
			GPIO.output(segments_pins[i], GPIO.LOW)
		i += 1
  
def checkdist():
	GPIO.output(trigger, GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(trigger, GPIO.LOW)
	while not GPIO.input(echo):
		pass
	t1 = time.time()
	while GPIO.input(echo):
		pass
	t2 = time.time()
	# print("t1: ", t1, "t2: ", t2)
	return (t2-t1)*340/2

def loop():
	while True:
		distance = checkdist()
		color = distance_to_color(distance, 1)
		#color_displayed = colors_table.get(color)[1]
		#hex_code = colors_table.get(color)[0]
		setColor(color)
		#segments(hex_code)
		time.sleep(0.1)

def destroy():
	p_R.stop()
	p_G.stop()
	p_B.stop()
	off()
	GPIO.cleanup()

if __name__ == "__main__":
	try:
		setup(R, G, B)
		loop()
	except KeyboardInterrupt:
		destroy()