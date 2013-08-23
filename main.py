#!/usr/bin/env python
"""
qr - Convert stdin (or the first argument) to a QR Code.

When stdout is a tty the QR Code is printed to the terminal and when stdout is
a pipe to a file an image is written. The default image format is PNG.
"""
import sys, os
import optparse
import qrcode

default_factories = {
	'pil': 'qrcode.image.pil.PilImage',
	'svg': 'qrcode.image.svg.SvgImage',
	'svg-fragment': 'qrcode.image.svg.SvgFragmentImage',
}


def main(*args):
	qr = qrcode.QRCode()

	parser = optparse.OptionParser(usage=__doc__.strip())
	parser.add_option(
		"--factory", help="Full python path to the image factory class to "
		"create the image with. You can use the following shortcuts to the "
		"built-in image factory classes: {0}.".format(
			", ".join(sorted(default_factories.keys()))))
	parser.add_option(
		"--optimize", type=int, help="Optimize the data by looking for chunks "
		"of at least this many characters that could use a more efficient "
		"encoding method. Use 0 to turn off chunk optimization.")
	opts, args = parser.parse_args(list(args))

	if opts.factory:
		module = default_factories.get(opts.factory, opts.factory)
		if '.' not in module:
			parser.error("The image factory is not a full python path")
		module, name = module.rsplit('.', 1)
		imp = __import__(module, {}, [], [name])
		image_factory = getattr(imp, name)
	else:
		image_factory = None

	#Get folders for public ssh keys
	if args:
		folder_name = args[0]
	else:
		folder_name = os.environ['HOME'] + "/.ssh/"

	public_keys = [basename for basename in os.listdir(folder_name) if basename.endswith('.pub')]

	for keys in public_keys:
		key_data = open(folder_name + keys)
		if opts.optimize is None:
			qr.add_data(key_data.read())
		else:
			qr.add_data(key_data.read(), optimize=opts.optimize)

		qr.make()

		img = qr.make_image(image_factory=image_factory)
		img.save(keys + ".png")


if __name__ == "__main__":
	main(*sys.argv[1:])
