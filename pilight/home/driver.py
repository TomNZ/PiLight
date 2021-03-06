import json

from django.conf import settings

from pilight.classes import Color, PikaConnection


# Pika message passing setup
# Helper functions for controlling the light driver
def publish_message(msg, first=True):
    channel = PikaConnection.get_channel()
    if not channel:
        # Connection failed to open
        print('Unable to connect to Pika channel')
        return
    try:
        channel.basic_publish(exchange='', routing_key=settings.PIKA_QUEUE_NAME, body=json.dumps(msg))

    # Current version of Pika can be a little unstable - catch ANY exception
    except:
        print('Pika channel publish failed - clearing objects to try again')
        # Force the channel to try reconnecting next time
        PikaConnection.clear_channel()

        # Someone closed our connection - attempt the publish again to refresh
        # (But only if it's the first time)
        if first:
            publish_message(msg, first=False)
        else:
            # Not the first time - there is something bigger going on - fail silently
            pass


def message_start():
    publish_message({
        'command': 'start',
    })


def message_start_playlist(playlist_id):
    publish_message({
        'command': 'start',
        'playlistId': playlist_id,
    })


def message_stop():
    publish_message({
        'command': 'stop',
    })


def message_restart():
    publish_message({
        'command': 'restart',
    })


def message_color_channel(channel, color):
    # Make sure we got a color
    if not isinstance(color, Color):
        return

    # Truncate the channel name so we don't have any possibility of
    # messiness with buffer overruns or the like
    channel = str(channel)[0:30]

    publish_message({
        'command': 'color',
        'channel': channel,
        'color': color.to_hex(),
    })
