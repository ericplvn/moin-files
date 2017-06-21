from MoinMoin.support.htmlmarkup import Markup
from HTMLParser import HTMLParseError

Dependencies = []

class Parser:

    extensions = ['.htm', '.html']
    Dependencies = Dependencies

    def __init__(self, raw, request, **kw):
        self.raw = raw
        self.request = request

    def format(self, formatter, **kw):
        try:
            self.request.write(formatter.rawHTML(Markup(self.raw)))
        except HTMLParseError, e:
            self.request.write(formatter.sysmsg(1) +
                formatter.text(u'HTML parsing error: %s in "%s"' % (e.msg,
                                  self.raw.splitlines()[e.lineno - 1].strip())) +
                formatter.sysmsg(0))
