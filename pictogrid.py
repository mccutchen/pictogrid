from __future__ import with_statement

import os
import sys
import logging

import Image, ImageDraw

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

    output_img = Image.new('RGB', (output_width, output_height), background)
    draw = ImageDraw.Draw(output_img)

    for i, path in enumerate(images):
        col = i % cols
        row = (i / cols)
        logging.info('Processing %s: %3d @ (%2d, %2d)', path, i, col, row)

        img = open_and_size(path, tile_width, tile_height)
        offset = make_offset(img, col, row, tile_width, tile_height, padding)
        logging.debug('Offset: %r', offset)

        output_img.paste(img, offset)

        if border:
            x1, y1 = offset
            box = (x1, y1, x1 + tile_width, y1 + tile_height)
            draw.rectangle(box, outline=border)

    if outpath:
        output_img.save(outpath)

    return output_img


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


def open_and_size(path, tw, th):
    """Opens the image at the given path and ensures that it fits into the
    given target width and height."""

    img = Image.open(path)

    if img.size == (tw, th):
        return img

    w, h = img.size
    ratio = min(tw/float(w),
                th/float(h))
    nw = int(w * ratio)
    nh = int(h * ratio)

    logging.debug('Resizing %r => %r', (w,h), (tw,th))
    logging.debug('Ratio: %s', ratio)
    logging.debug('New size: %r', (nw, nh))

    return img.resize((nw, nh), Image.ANTIALIAS)
