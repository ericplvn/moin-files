import os
import hashlib
from PIL import Image, ImageOps
from PIL.ImageFileIO import ImageFileIO

from MoinMoin import log
from MoinMoin import wikiutil
from MoinMoin.Page import Page
from MoinMoin.action import AttachFile
from MoinMoin.caching import CacheEntry


logging = log.getLogger(__name__)


def crop(img, width, height):
    src_width, src_height = img.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = int(width), int(height)
    dst_ratio = float(dst_width) / float(dst_height)

    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = float(src_height - crop_height) / 3

    return img.crop((
        x_offset,
        y_offset,
        x_offset + int(crop_width),
        y_offset + int(crop_height)
    ))


def thumbnail(img, long_side):
    long_side = int(long_side)
    width, height = [float(d) for d in img.size]

    if height > width:
        width = (width / height) * long_side
        height = long_side
    else:
        height = (height / width) * long_side
        width = long_side

    img.thumbnail((width, height), Image.ANTIALIAS)
    return img


def thumbnail_constrain(img, size, dimension):
    size = int(size)
    width, height = [float(d) for d in img.size]

    if dimension.lower() == "h":
        height, width = size, ((width * size) / height)
    elif dimension.lower() == "w":
        width, height = size, ((height * size) / width)
    else:
        raise Exception("Must contrain valid dimension")

    img.thumbnail((int(width), int(height)), Image.ANTIALIAS)
    return img


def get_cache_key(request, filename):
    ops = hashlib.md5(":".join(request.values.getlist("do")))

    key = filename.split(".")
    key.insert(0, "thumbnail")
    key.insert(-1, ops.hexdigest()[:8])

    return ".".join(key)


def execute(pagename, request):
    _ = request.getText

    if not request.user.may.read(pagename):
        return _('You are not allowed to view attachments of this page.')

    page = Page(request, pagename)
    pagename, filename, fpath = AttachFile._access_file(pagename, request)

    if not filename:
        request.status_code = 404
        return

    cache = CacheEntry(request, page,
        get_cache_key(request, filename), scope="item")

    if cache.exists() and (cache.mtime() >= os.path.getmtime(fpath)):
        logging.info("Using cache for %s", fpath)
        cache.open(mode="r")
        request.write(cache.read())
        cache.close()
        return

    action_map = {
        'ds': ImageOps.grayscale,
        'cr': crop,
        'th': thumbnail,
        'tc': thumbnail_constrain,
    }

    with open(fpath) as fp:
        img = Image.open(fp)

        for action in request.values.getlist("do"):
            action = action.split(":")
            args = action[1].split(",") if len(action) > 1 else []

            try:
                img = action_map[action[0]](img, *args)
            except Exception, e:
                request.status_code = 400
                request.write("Error: {}".format(e))
                return

    mt = wikiutil.MimeType(filename=filename)
    request.headers['Content-Type'] = mt.content_type()
    data = img.tostring('jpeg', img.mode)

    try:
        cache.lock("w")
        cache.open(mode="w")
        cache.write(data)
        cache.close()
    except Exception, e:
        request.status_code = 500
        request.write("Error: {}".format(e))
        return
    finally:
        cache.unlock()
        request.write(data)
