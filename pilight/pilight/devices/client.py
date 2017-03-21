import base64

from django.conf import settings

from pilight.classes import PikaConnection
from pilight.devices import base


class Device(base.DeviceBase):
    def __init__(self, num_leds, scale):
        super(Device, self).__init__(num_leds, scale)
        self.messages_since_last_queue_check = 0

    def set_colors(self, colors):
        """
        Publishes the color data to a Pika queue for ingestion
        by a client - usually pilight-client
        """
        channel = PikaConnection.get_channel()
        if not channel:
            # Failed to get the channel
            return

        # Check for excessive messages in queue - and drop them if
        # there are too many. This is useful if the light driver is
        # running but no client is taking the messages, to save
        # on memory.
        if self.messages_since_last_queue_check > 5000:
            self.messages_since_last_queue_check = 0
            result = channel.queue_declare(
                queue=settings.PIKA_QUEUE_NAME_COLORS,
                auto_delete=False,
                durable=True,
                passive=True
            )
            if result.method.message_count > 4000:
                channel.queue_purge(settings.PIKA_QUEUE_NAME_COLORS)

        # Encode the raw data to base64 for transmission
        data = base64.b64encode(self.to_data(colors))
        channel.basic_publish(exchange='', routing_key=settings.PIKA_QUEUE_NAME_COLORS, body=data)

        self.messages_since_last_queue_check += 1

    def to_data(self, colors):
        raw_data = bytearray(settings.LIGHTS_NUM_LEDS * 3)
        pos = 0
        for light in colors:
            raw_data[pos * 3:] = light.to_raw_corrected()
            pos += 1
        return raw_data