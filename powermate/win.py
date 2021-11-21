import asyncio

import pywinusb.hid

from .base import *


class PowerMate:
  @classmethod
  def enumerate(cls):
    """Enumerates PowerMate devices.

    Returns:
      A list of device paths.
    """
    filter = pywinusb.hid.HidDeviceFilter(vendor_id=VENDOR_ID,
                                          product_id=PRODUCT_ID)
    return [device.device_path for device in filter.get_devices()]

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
    self._device = pywinusb.hid.HidDevice(path)
    self._device.open()
    self._button = False
    self._device.set_raw_data_handler(self._raw_data_handler)
    ## self._device.add_event_handler(0x10033, self._on_turn,
                                   ## pywinusb.hid.HID_EVT_SET)
    ## self._device.add_event_handler(0x90001, self._on_button,
                                   ## pywinusb.hid.HID_EVT_CHANGED)

  def close(self):
    """Closes this device."""
    self._device.close()

  def set_led_solid(self, brightness=128):
    """Sets the LED to constant brightness.

    Args:
      brightness: A brightness (0-255).
    """
    brightness = min(max(brightness, 0), 255)
    self._device.send_feature_report([0, 0x41, 1, 3, 0, 0, 0, 0, 0])
    self._device.send_feature_report([0, 0x41, 1, 1, 0, brightness, 0, 0, 0])

  def set_led_pulse(self, speed=0, table=0, when_sleeping=True):
    """Sets the LED to pulse.

    Args:
      speed: A speed (-255 to +255).
      table: A pulse table (0-2).
      when_sleeping: Whether to pulse when asleep.
    """
    speed = min(max(speed, -0xFF), 0xFF)
    speed_scale = 2 * (speed > 0) if speed else 1
    speed = abs(speed)
    table = min(max(table, 0), 2)
    when_sleeping = 1 if when_sleeping else 0
    self._device.send_feature_report([0, 0x41, 1, 2, 0, when_sleeping, 0, 0, 0])
    self._device.send_feature_report([0, 0x41, 1, 3, 0, 1, 0, 0, 0])
    self._device.send_feature_report(
        [0, 0x41, 1, 4, table, speed_scale, speed, 0, 0])

  def _raw_data_handler(self, data):
    button = data[1]
    turn = data[2]
    if button != self._button:
      self._button = button
      self._on_button(button)
    if turn:
      self._on_turn(turn)

  def _on_turn(self, value, event_type=None):
    if value > 128:
      value -= 256
    if self._turn_callback:
      self._loop.call_soon_threadsafe(self._turn_callback, value)

  def _on_button(self, value, event_type=None):
    if self._button_callback:
      self._loop.call_soon_threadsafe(self._button_callback, bool(value))
