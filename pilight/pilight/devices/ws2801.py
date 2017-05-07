from pilight.devices import base


class Device(base.DeviceBase):
    def init(self):
        import Adafruit_WS2801
        from Adafruit_GPIO import SPI
        self.strip = Adafruit_WS2801.WS2801Pixels(
            self.num_leds * self.scale * self.repeat,
            spi=SPI.SpiDev(0, 0))
        self.strip.clear()
        self.strip.show()

    def set_color(self, index, color):
        self.strip.set_pixel(index, color.to_raw_corrected())

    def finish(self):
        self.strip.show()
