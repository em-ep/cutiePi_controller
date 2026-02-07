from gpiozero import LEDBoard
from time import sleep

leds = LEDBoard(22, 23, 24, 25)

leds[0].on()
sleep(1)