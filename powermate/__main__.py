import argparse
import asyncio

from powermate import PowerMate


def main(args=None):
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-p', '--path', help='Path to the PowerMate device')
  group.add_argument('-i', '--index', type=int, default=None,
                     help='Index of which PowerMate to open')
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-b', '--brightness', type=int,
                     help='Set constant brightness [0 to 255]')
  group.add_argument('-s', '--pulse-speed', type=int,
                     help='Set pulse speed [-255 to 255]')
  args = parser.parse_args(args)

  if not args.path:
    paths = PowerMate.enumerate()

    if not paths:
      print('No PowerMates detected')
      return 1

    if args.index is not None:
      args.path = paths[args.index]
    elif len(paths) == 1:
      args.path = paths[0]
    else:
      for i, path in enumerate(paths):
        print(f'{i}\t{path}')
      print()
      index = input(f'Select Device [0-{len(paths) - 1}]: ')
      args.path = paths[int(index)]

  def on_turn(amount):
    print(f'Turned: {amount}')

  def on_button(pressed):
    print(f'Button: {pressed}')

  device = PowerMate(args.path, turn_callback=on_turn,
                     button_callback=on_button)

  if args.brightness is not None:
    device.set_led_solid(args.brightness)
  elif args.pulse_speed is not None:
    device.set_led_pulse(args.pulse_speed)

  try:
    asyncio.get_event_loop().run_forever()
  except KeyboardInterrupt:
    pass

  return 0


raise SystemExit(main())
