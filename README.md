Description
-----------

This is a cross-platform Python library for the USB
[Griffin PowerMate][powermate] (don't think it will work with the Bluetooth
version). It is tested to work on both Windows and Linux. While it is two
completely separate implementations, they have the same interface. Both rely on
[asyncio][].

[powermate]: https://en.wikipedia.org/wiki/Griffin_PowerMate
[asyncio]: https://docs.python.org/3/library/asyncio.html

Picking a Device
----------------

Multiple PowerMates can be used at once. The `PowerMate` class constructor
requires a path to the device. On Linux this will be something like
`/dev/input/event15`. On Windows it will be something horrible like
`\\?\hid#vid_077d&pid_0410#6&1c38037f&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}`.
Rather that type the path directly, you can use `PowerMate.enumerate()` which
returns a list of PowerMate device paths.

Callbacks
---------

This library works on a callback system. The `PowerMate` constructor takes
callback functions for when the knob is turned and when the button is pressed
(or released). These callback will be called on an asyncio event loop. The
`turn_callback` should take a single parameter that will be an integer number of
ticks the knob has turned. Postive means clockwise and negative means
counter-clockwise. The `button_callback` takes a boolean that is `True` when the
button is pressed and `False` when it is released.

Example
-------

```
from powermate import PowerMate

def on_turn(amount):
  print(f'Turned: {amount}')

def on_button(pressed):
  if pressed:
    print('Button pressed')
  else:
    print('Button released')

paths = PowerMate.enumerate()
if not paths:
  print('No PowerMates detected')
else:
  powermate = PowerMate(
      paths[0],
      turn_callback=on_turn,
      button_callback=on_button)
```

LED Control
-----------

The PowerMate has a somewhat controllable blue LED in it. It can either be solid
on or pulsing. When it is solid, you can adjust the brightness. When it is
pulsing, you can adjust the speed.

To turn it solid on, call `powermate.set_led_solid(brightness)` where the
brightness is 0-255 (default: 128).

To cause it to pulse, call
`powermate.set_led_pulse(speed, table, when_sleeping)`. Speed is from -255 to
255. 0 is its default speed (also 1 and -1). Positive numbers multiply its
default speed (2 is twice as fast, 3 is three times as fast, etc), and negative
numbers divide its default speed (-2 is half as fast, -3 is a third as fast,
etc). The `table` is 0-2, but I haven't noticed any difference. `when_sleeping`
is a boolean that controls if it should continue to pulse when the device is
suppose to be asleep (violating the USB power management standards) or whether
to go into low-power mode.

asyncio Event Loop
------------------

The `PowerMate` class requires an asyncio event loop to function. In the Linux
version, the events are polled on this event loop. In Windows the events are
polled on a thread, however in both versions the callbacks are called on the
event loop. By default PowerMate will use the current event loop when its
constructor is called. However, if you wish to specify another event loop
(perhaps one that is created but not started when PowerMate is constructed that
will be run on a separate thread), you can pass it to the `loop` parameter to
the contructor.

Shutting Down
-------------

Calling `powermate.close()` will disconnect from the device and prevent further
event callbacks from being called.
