from __future__ import with_statement

import os
import sys
import logging

import Image, ImageDraw

logging.getLogger().setLevel(logging.INFO)


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

    # Used to compare & resize each individual image
    tile_size = (tile_width, tile_height)

    for i, path in enumerate(images):
        col = i % cols
        row = (i / cols)
        logging.info('Processing image %s: %s @ %r', i, path, (col, row))

        img = Image.open(path)

        if img.size != tile_size:
            img, extra_offset = resize(img, tile_size)
        else:
            extra_offset = (0, 0)

        offset = make_offset(
            col, row, tile_width, tile_height, padding, extra_offset)
        logging.debug('Offset: %r', offset)

        output_img.paste(img, offset)

        if border:
            x1, y1 = offset
            box = (x1, y1, x1 + tile_width, y1 + tile_height)
            draw.rectangle(box, outline=border)

    if outpath:
        output_img.save(outpath)

    return output_img


def make_offset(col, row, w, h, padding, extra_offset=(0,0)):
    x = w * col + padding * (col + 1)
    y = h * row + padding * (row + 1)
    dx, dy = extra_offset
    return (x + dx, y + dy)


def resize(img, (target_w, target_h)):
    w, h = img.size
    ratio = min(float(target_w)/float(w),
                float(target_h)/float(h))
    new_w = int(w * ratio)
    new_h = int(h * ratio)

    logging.debug('Resizing img %s: %r => %r', img,(w,h),(target_w,target_h))
    logging.debug('Ratio: %s', ratio)
    logging.debug('New size: %r', (new_w, new_h))

    # Update the offset to center the oddly-sized
    # image in its assigned space
    # if new_w > new_h:
    #     offset = (0, new_h / 2)
    # else:
    #     offset = (new_w / 2, 0)
    offset = (0, 0)

    logging.debug('Offset: %r', offset)
    return img.resize((new_w, new_h), Image.ANTIALIAS), offset
