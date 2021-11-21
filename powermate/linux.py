import asyncio

import evdev
from evdev import ecodes

from .base import *


class PowerMate:
  @classmethod
  def enumerate(cls):
    """Enumerates PowerMate devices.

    Returns:
      A list of device paths.
    """
    devices = []
    for path in evdev.list_devices():
      device = evdev.InputDevice(path)
      if device.info.vendor == VENDOR_ID and device.info.product == PRODUCT_ID:
        devices.append(path)
      device.close()
    return devices

  def __init__(self, path, *, turn_callback=None, button_callback=None,
               loop=None):
    """
    Args:
      path: A path to a PowerMate device to open.
      turn_callback: A callback that will be passed a turn amount.
      button_callback: A callback that will be called when the button is pressed
          or released.
      loop: The asyncio event loop on which to call the callbacks.
    """
    if loop is None:
      loop = asyncio.get_event_loop()
    self._loop = loop
    self._turn_callback = turn_callback
    self._button_callback = button_callback
    self._device = evdev.InputDevice(path)
    self._task = asyncio.ensure_future(self._run(), loop=self._loop)

  def __del__(self):
    if getattr(self, '_device', None):
      self.close()

  def close(self):
    """Closes this device."""
    if getattr(self, '_task', None):
      self._task.cancel()
    self._device.close()

  async def _run(self):
    async for event in self._device.async_read_loop():
      if event.type == ecodes.EV_REL and event.code == ecodes.REL_DIAL:
        if self._turn_callback:
          self._loop.call_soon(self._turn_callback, event.value)
      elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_0:
        if self._button_callback:
          self._loop.call_soon(self._button_callback, bool(event.value))

  def set_led_solid(self, brightness=128):
    """Sets the LED to constant brightness.

    Args:
      brightness: A brightness (0-255).
    """
    brightness = min(max(brightness, 0), 255)
    self._device.write(ecodes.EV_MSC, ecodes.MSC_PULSELED, brightness)

  def set_led_pulse(self, speed=0, table=0, when_sleeping=True):
    """Sets the LED to pulse.

    Args:
      speed: A speed (-255 to +255).
      table: A pulse table (0-2).
      when_sleeping: Whether to pulse when asleep.
    """
    speed = min(max(speed, -0xFF), 0xFF) + 0xFF
    table = min(max(table, 0), 2)
    enable = 3 if when_sleeping else 2
    self._device.write(ecodes.EV_MSC, ecodes.MSC_PULSELED,
                       (speed << 8) | (table << 17) | (enable << 19))
