from MoinMoin import wikiutil
from MoinMoin.action import AttachFile


def macro_Thumbnail(macro, attachment, height=200, width=None, link=True):
    _ = macro.request.getText
    formatter = macro.formatter

    pagename, filename = AttachFile.absoluteName(attachment, formatter.page.page_name)
    fname = wikiutil.taintfilename(filename)

    if not macro.request.user.may.read(pagename):
        return _('You are not allowed to view attachments of this page.')

    if width:
        size, dimension = width, "w"
    else:
        size, dimension = height, "h"

    if AttachFile.exists(macro.request, pagename, fname):
        url = AttachFile.getAttachUrl(pagename, fname, macro.request, do='get')

        output = [
            formatter.url(True, url) if link else "",
            formatter.image(
                macro.request.href(pagename, {
                     "target": fname,
                     "action": "Thumbnail",
                     "do": "tc:{},{}".format(size, dimension)
                })),
            formatter.url(False) if link else "",
        ]
    else:
        output = [
            formatter.span(True, style="color: red"),
            "No Image: {}".format(attachment),
            formatter.span(False),
        ]

    return "".join(output) 
