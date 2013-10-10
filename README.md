PiLight
=======

Flexible LED controller designed to run on a Raspberry Pi, and drive WS2801 LED strings. Has a Django web-based interface for access anywhere.


Installation
------------

Install all prerequisites first:

* [Python](http://www.python.org/download/) - 2.7 recommended
* Database software - [PostgreSQL](http://www.postgresql.org/download/) recommended
* [RabbitMQ](http://www.rabbitmq.com/download.html) (requires [Erlang](http://www.erlang.org/download.html))
* [pip](https://pypi.python.org/pypi/pip/) strongly recommended to install extra Python dependencies

> Note: These instructions assume you're using a Raspberry Pi with Occidentalis for the most part - omit sudo if your flavor doesn't use it, for example. This is all tested working with a 512MB Raspberry Pi device, and Occidentalis v0.2.

Download the source to a desired location:

    hg clone https://bitbucket.org/tomnz/pilight

Install the Python dependencies:

    cd pilight
    sudo pip install -r requirements.txt

> Note: If you get an error message about available space on the device, it's likely your /tmp folder is too small. Run `sudo nano /etc/default/tmpfs`, change TMP_SIZE to 200M, then try `pip install -r requirements.txt` again. You may run into this when installing on a Raspberry Pi device.

Create a new database in your DBMS (e.g. PostgreSQL) to use for PiLight.

Copy the settings file and make required changes (particularly set up your light parameters, and database instance):

    cd pilight
    cp pilight/settings.py.default pilight/settings.py

> Note: Be sure to edit your new settings.py file!

Setup the database:

    python manage.py syncdb
    python manage.py migrate
    python manage.py loaddata fixtures/initial_data.json
    python manage.py createcachetable pilight_cache


Launch PiLight
--------------

Once you've gone through all the installation steps, you're ready to run PiLight!

First, ensure that RabbitMQ and your DBMS are running. Then, run the following commands in separate console windows (or use `screen`):

    sudo python manage.py lightdriver

And

    python manage.py runserver 0.0.0.0:8000

> Note: `lightdriver` and `runserver` are both blocking commands that run until stopped, which is why they must be in separate console windows. We bind `runserver` to 0.0.0.0:8000 so that it can be accessed from other devices on the network, not just localhost. This is useful for controlling PiLight from your phone or computer.

That's it! You should now be able to access the interface to control the lights by accessing [http://localhost:8000/](http://localhost:8000/).


Guide
-----

### Introduction

PiLight is designed around a simple "Colors" + "Transformations" system. You specify both parts in the configuration interface.

* Colors define the "initial" or "base" states for each individual LED. Using the PiLight interface, you can "paint" colors onto the LEDs. Specify a tool (solid/smooth), tool radius and opacity, and a color. Then, click individual lights to start painting. The lights will refresh after each click.
* Transformations get applied in real time when the light driver is running. They modify the base colors based on a variety of input parameters, and usually a "time" component. Typically they will produce an animation effect, such as flashing or scrolling. Transformations can be added to the "active" stack. Each transformation is applied in sequence, for each "frame" that gets sent to the LEDs. Multiple transformations of the same type can be stacked; for example, to have a slow flash, with faster small fluctuations.

> Note: Currently parameters for transforms are not editable via nice controls. However, when adding a transform, sensible defaults will be applied, and you can edit the parameter string by hand. This should be fairly self-explanatory.

You can view a 10-second preview of what the lights will look like after animations are applied (animated in-browser) by hitting the Preview button.

### Running the light driver

Changes in the configuration interface are instantly sent to the light driver if it's currently running. You can also use the buttons at the top right to control the driver:

* Refresh will force the light driver to reload its configuration (if it's started), as well as refresh the configuration page for any changes
* Start will start the light driver so that it powers the lights and runs transforms
* Stop will stop the light driver and power off the lights - then await a new Start command

> Note: These buttons all have no effect if the driver is not running. Remember to start it with `python manage.py lightdriver`.

### Loading and saving

You can save the current configuration by typing a name in the text box at top right, and hitting Save. You can also load past configurations with the Load button.

> Note: If you load a configuration, changes you make are NOT automatically saved back to that configuration. Make sure you hit Save again when you're done. This will overwrite previous settings, if a configuration already exists with the same name.