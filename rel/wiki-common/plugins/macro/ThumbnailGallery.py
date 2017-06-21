import re
from MoinMoin import wikiutil
from MoinMoin.action import AttachFile


def macro_ThumbnailGallery(macro, page=None, regex=None, height=200, width=None, link=True):
    _ = macro.request.getText
    formatter = macro.formatter
    pagename = page or macro.formatter.page.page_name
    output = []

    if not regex:
        regex = re.compile(".*\.(jpg|jpeg|png|gif)$")
    else:
        regex = re.compile(regex)

    if not macro.request.user.may.read(pagename):
        return _('You are not allowed to view attachments of this page.')

    for attachment in AttachFile._get_files(macro.request, pagename):
        if regex.match(attachment) is None:
            continue

        pagename, filename = AttachFile.absoluteName(attachment, pagename)
        fname = wikiutil.taintfilename(filename)

        if width:
            size, dimension = width, "w"
        else:
            size, dimension = height, "h"

        if AttachFile.exists(macro.request, pagename, fname):
            url = AttachFile.getAttachUrl(pagename, fname, macro.request, do='get')

            output.extend([
                macro.formatter.url(True, url) if link else "",
                macro.formatter.image(
                    macro.request.href(pagename, {
                         "target": fname,
                         "action": "Thumbnail",
                         "do": "tc:{},{}".format(size, dimension)
                    })),
                macro.formatter.url(False) if link else "",
                " ",
            ])

    return "".join(output) 
