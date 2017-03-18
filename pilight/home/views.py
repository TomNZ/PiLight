import json

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.middleware import csrf
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST

from home import client_queries
from home.models import Transform, Light, TransformInstance, Store
from pilight.classes import Color, PikaConnection
from pilight.driver import LightDriver


# Pika message passing setup
# Helper functions for controlling the light driver
def publish_message(msg, first=True):
    channel = PikaConnection.get_channel()
    if not channel:
        # Connection failed to open - fail silently
        return
    try:
        channel.basic_publish(exchange='', routing_key=settings.PIKA_QUEUE_NAME, body=msg)

    # Current version of Pika can be a little unstable - catch ANY exception
    except:
        print 'Pika channel publish failed - clearing objects to try again'
        # Force the channel to try reconnecting next time
        PikaConnection.clear_channel()

        # Someone closed our connection - attempt the publish again to refresh
        # (But only if it's the first time)
        if first:
            publish_message(msg, first=False)
        else:
            # Not the first time - there is something bigger going on - fail silently
            pass


def message_start_driver():
    publish_message('start')


def message_stop_driver():
    publish_message('stop')


def message_restart_driver():
    publish_message('restart')


def success_json(data_dict):
    data_dict['success'] = True
    return json.dumps(data_dict)


def fail_json(error):
    return json.dumps({
        'success': False,
        'error': error,
    })


def message_color_channel(channel, color):
    # Make sure we got a color
    if not isinstance(color, Color):
        return

    # Truncate the channel name so we don't have any possibility of
    # messiness with buffer overruns or the like
    channel = str(channel)[0:30]

    publish_message('color_%s_%s' % (channel, color.to_hex()))


def auth_check(user):
    # Should we restrict access?
    if not settings.LIGHTS_REQUIRE_AUTH:
        return True

    # Auth is really easy - you just need to be logged in
    if user.is_authenticated():
        return True
    else:
        return False


# Views
@ensure_csrf_cookie
@user_passes_test(auth_check)
def index(request):
    return render(
        request,
        'home/index.html',
    )


@ensure_csrf_cookie
@user_passes_test(auth_check)
def bootstrap_client(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    # Get objects that the page needs
    current_lights = Light.objects.get_current()

    # Find average light color to use as default for paintbrush
    tool_color = Color(0, 0, 0)
    base_colors = []
    for light in current_lights:
        tool_color += light.color
        base_colors.append(light.color.safe_dict())
    tool_color /= len(current_lights)

    return HttpResponse(success_json({
        'baseColors': base_colors,
        'activeTransforms': client_queries.active_transforms(),
        'availableTransforms': client_queries.available_transforms(),
        'configs': client_queries.configs(),
        'toolColor': tool_color.safe_dict(),
        'csrfToken': csrf.get_token(request),
    }), content_type='application/json')


@csrf_exempt
def post_auth(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    result = 'Failed'

    if user is not None:
        if user.is_active:
            login(request, user)
            result = 'Authenticated'
        else:
            result = 'Disabled'

    return HttpResponse(success_json({'result': result}), content_type='application/json')


@user_passes_test(auth_check)
def get_base_colors(request):
    # Always "reset" the lights - will fill out the correct number if it's wrong
    Light.objects.reset()

    return HttpResponse(success_json({
        'baseColors': client_queries.base_colors(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def save_config(request):
    req = json.loads(request.body)

    error = None
    if 'configName' in req:
        # First see if the store already exists
        store_name = (req['configName'])[0:29]
        stores = Store.objects.filter(name=store_name)
        if len(stores) >= 1:
            store = stores[0]
            # Remove existing lights/transforms
            store.light_set.all().delete()
            store.transforminstance_set.all().delete()
        else:
            # Create new store
            store = Store()
            store.name = store_name
            store.save()

        # Copy all of the current lights and transforms to the given store
        current_lights = Light.objects.get_current()
        current_transforms = TransformInstance.objects.get_current()

        for light in current_lights:
            # By setting primary key to none, we ensure a copy of
            # the object is made
            light.pk = None
            # Set the store to None so that it's part of the "current"
            # setup
            light.store = store
            light.save()

        for transforminstance in current_transforms:
            transforminstance.pk = None
            transforminstance.store = store
            transforminstance.save()

    else:
        error = 'Must specify a config name'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    return HttpResponse(success_json({
        'configs': client_queries.configs(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def load_config(request):
    req = json.loads(request.body)

    error = None
    if 'id' in req:
        store = Store.objects.get(id=req['id'])
        if store:
            # Found the store - load its lights and transforms
            # First clear out existing "current" items
            Light.objects.get_current().delete()
            TransformInstance.objects.get_current().delete()

            for light in store.light_set.all():
                # By setting primary key to none, we ensure a copy of
                # the object is made
                light.pk = None
                # Set the store to None so that it's part of the "current"
                # setup
                light.store = None
                light.save()

            for transforminstance in store.transforminstance_set.all():
                transforminstance.pk = None
                transforminstance.store = None
                transforminstance.save()

        else:
            error = 'Invalid config specified'
    else:
        error = 'Must specify a config'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    message_restart_driver()
    # Return an empty response - the client will re-bootstrap
    return HttpResponse(success_json({}), content_type='application/json')


@user_passes_test(auth_check)
def run_simulation(request):
    # To do this, we call into the driver class to simulate running
    # the actual driver
    driver = LightDriver()
    colors = driver.run_simulation(0.1, 100)
    hex_colors = []

    for color in colors:
        hex_colors.append([x.to_hex_web() for x in color])

    return HttpResponse(json.dumps(hex_colors), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def apply_light_tool(request):
    """
    Complex function that applies a "tool" across several lights
    """

    error = None
    if 'tool' in request.POST and \
            'index' in request.POST and \
            'radius' in request.POST and \
            'opacity' in request.POST and \
            'color' in request.POST:
        # Always "reset" the lights - will fill out the correct number if it's wrong
        Light.objects.reset()
        current_lights = list(Light.objects.get_current())

        tool = request.POST['tool']
        index = int(request.POST['index'])
        radius = int(request.POST['radius'])
        opacity = float(request.POST['opacity']) / 100
        color = Color.from_hex(request.POST['color'])

        if tool == 'solid':
            # Apply the color at the given opacity and radius
            min_idx = max(0, index - radius)
            max_idx = min(len(current_lights), index + radius + 1)

            for i in range(min_idx, max_idx):
                light = current_lights[i]
                light.color = (light.color * (1.0 - opacity)) + (color * opacity)
                light.save()

        elif tool == 'smooth':
            # Apply the color at the given opacity and radius, with falloff
            min_idx = max(0, index - radius)
            max_idx = min(len(current_lights), index + radius + 1)

            for i in range(min_idx, max_idx):
                distance = abs(index - i)
                # TODO: Better falloff function
                strength = (1.0 - (float(distance) / radius)) * opacity

                light = current_lights[i]
                light.color = (light.color * (1.0 - strength)) + (color * strength)
                light.save()

        else:
            error = 'Unknown tool %s' % tool
    else:
        error = 'No tool specified'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    message_restart_driver()
    return HttpResponse(success_json({'baseColors': client_queries.base_colors()}), content_type='application/json')


@user_passes_test(auth_check)
def fill_color(request):

    if request.method == 'POST':
        if 'color' in request.POST:
            color = Color.from_hex(request.POST['color'])

            for light in Light.objects.get_current():
                light.color = color
                light.save()

            result = True
        else:
            result = False
    else:
        result = False

    if result:
        message_restart_driver()

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@csrf_exempt
def update_color_channel(request):

    if request.method == 'POST':
        if 'color' in request.POST and 'channel' in request.POST:
            color = Color.from_hex(request.POST['color'])
            channel = request.POST['channel']

            message_color_channel(channel, color)

            result = True
        else:
            result = False
    else:
        result = False

    return HttpResponse(json.dumps({'success': result}), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def delete_transform(request):
    req = json.loads(request.body)

    error = None
    if 'id' in req:
        transform = TransformInstance.objects.get(id=req['id'])
        if transform:
            transform.delete()
        else:
            error = 'Invalid transform specified'
    else:
        error = 'No transform specified'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    message_restart_driver()
    return HttpResponse(success_json({
        'activeTransforms': client_queries.active_transforms(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def update_transform(request):
    req = json.loads(request.body)

    error = None
    result = None
    if 'id' in req and 'params' in req:
        transform = TransformInstance.objects.get(id=req['id'])
        if transform:
            transform.params = json.dumps(req['params'])
            transform.save()
            result = {
                'id': transform.id,
                'transformId': transform.transform.id,
                'name': transform.transform.name,
                'longName': transform.transform.long_name,
                'params': json.loads(transform.params),
            }
        else:
            error = 'Invalid transform specified'
    else:
        error = 'Must supply transform and params'

    print result
    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    message_restart_driver()
    return HttpResponse(success_json({
        'transform': result,
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def add_transform(request):
    req = json.loads(request.body)

    error = None
    if 'id' in req:
        transform = Transform.objects.filter(id=req['id'])
        if len(transform) == 1:
            transform_instance = TransformInstance()
            transform_instance.transform = transform[0]
            transform_instance.params = json.dumps(transform[0].default_params)
            transform_instance.order = 0
            transform_instance.save()
        else:
            error = 'Invalid transform specified'
    else:
        error = 'No transform specified'

    if error:
        return HttpResponse(fail_json(error), content_type='application/json')

    message_restart_driver()
    return HttpResponse(success_json({
        'activeTransforms': client_queries.active_transforms(),
    }), content_type='application/json')


@require_POST
@user_passes_test(auth_check)
def start_driver(request):
    message_start_driver()
    return HttpResponse()


@require_POST
@user_passes_test(auth_check)
def stop_driver(request):
    message_stop_driver()
    return HttpResponse()


@require_POST
@user_passes_test(auth_check)
def restart_driver(request):
    message_restart_driver()
    return HttpResponse()