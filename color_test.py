from pixels import set_all_values, get_pixels
import Adafruit_WS2801


try:
    pixels = get_pixels()
    while True:
        s = raw_input("Input RGB separated by space: ")
        r, g, b = s.split()
        color = Adafruit_WS2801.RGB_to_color( int(r), int(g), int(b) )
        set_all_values(pixels, color)
        pixels.show()

except KeyboardInterrupt:
    turn_off(pixels)