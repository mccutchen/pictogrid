#!/usr/bin/env python

__doc__ = """pictogrid.py

Provides a function, pictogrid, that will take a list of images and arrange
them into a grid.

The module can also be executed directly from the command line."""

import glob
import logging
import optparse
import sys

import Image, ImageDraw

usage = """Usage: %prog -c COLUMNS [options] image1 [image2 ... imageN]"""
description = """Arranges images into a grid."""

logging.getLogger().setLevel(logging.ERROR)


def pictogrid(images, cols, tile_width, tile_height, padding=0,
              background='white', border=None, outpath=None):
    """Generates a, uh, "pictogrid" by arranging the given images into the
    given number of columns. Each image will be resized to tile_width x
    tile_height if it is not already that size.

    The images will be arranged on the grid in the order in which they are
    received, so any sorting should be done before this function is called.

    The grid's apperance can be tweaked by giving each tile padding and by
    setting the output image's background color and each tile's border color,
    which may be any colors recognized by PIL.

    If outpath is given, it is the path to which the resulting image should be
    saved.
    """

    # Figure out how many rows we will need based on the number of images and
    # the number of columns.
    n = len(images)
    rows = (n / cols) + min(1, n % cols)

    # Calculate the output image's size
    output_width = (tile_width + padding) * cols + padding
    output_height = (tile_height + padding) * rows + padding

    result = Image.new('RGB', (output_width, output_height), background)
    draw = ImageDraw.Draw(result)

    for i, path in enumerate(images):
        col = i % cols
        row = (i / cols)
        logging.info('Processing %s: %3d @ (%2d, %2d)', path, i, col, row)

        img = open_and_size(path, tile_width, tile_height)
        offset = make_offset(img, col, row, tile_width, tile_height, padding)
        logging.debug('Offset: %r', offset)

        result.paste(img, offset)

        if border:
            x1, y1 = offset
            box = (x1, y1, x1 + tile_width, y1 + tile_height)
            draw.rectangle(box, outline=border)

    if outpath:
        result.save(outpath)

    return result

def make_offset(img, col, row, tw, th, padding):
    """Calculates the appropriate offset to place the given image at the given
    column and row on a grid with cells with the given target width and height
    and padding."""

    # Calculate the offset of this image's grid panel
    x = tw * col + padding * (col + 1)
    y = th * row + padding * (row + 1)

    # Calculate the offset required to center the image in the panel
    w, h = img.size
    dx = (tw - w) / 2
    dy = (th - h) / 2

    return (x + dx, y + dy)

def open_and_size(img_or_path, tw, th):
    """Opens the image at the given path (unless it's already an Image object)
    and ensures that it fits into the given target width and height."""

    if isinstance(img_or_path, Image.Image):
        img = img_or_path
    else:
        img = Image.open(img_or_path)

    if img.size == (tw, th):
        return img

    w, h = img.size
    ratio = min(tw / float(w), th / float(h))
    nw = int(w * ratio)
    nh = int(h * ratio)

    logging.debug('Resizing %r => %r', (w,h), (tw,th))
    logging.debug('Ratio: %s', ratio)
    logging.debug('New size: %r', (nw, nh))

    return img.resize((nw, nh), Image.ANTIALIAS)

def main(argv):
    parser = optparse.OptionParser(usage=usage, description=description)
    parser.add_option('-c', '--cols', help='Number of columns in the grid',
                      dest='cols', type='int')
    parser.add_option('-d', '--dimensions',
                      help='Dimensions of each image [100 100]',
                      dest='dimensions', metavar='WIDTH HEIGHT', nargs=2,
                      type='int', default=(100,100))
    parser.add_option('-p', '--padding',
                      help='Padding between images [%default]',
                      dest='padding', type='int', default=0)
    parser.add_option('-b', '--background',
                      help='Background color [%default]',
                      dest='background', default='white')
    parser.add_option('-v', '--border', help='Border color', dest='border',
                      default=None)
    parser.add_option('-o', '--output', help='Output path', dest='output',
                      default='pictogrid.jpg')

    opts, args = parser.parse_args(argv)

    try:
        if not opts.cols:
            raise RuntimeError('Required option missing: cols')
        if len(args) == 1:
            raise RuntimeError('Required arguments missing: images')
    except RuntimeError, e:
        print '%s\n' % e
        parser.print_help()
        sys.exit(-1)
    else:
        paths = args[1:]
        w, h = opts.dimensions
        pictogrid(paths, opts.cols, w, h, opts.padding, opts.background,
                  opts.border, opts.output)

if __name__ == '__main__':
    main(sys.argv)
