"""
    MoinMoin - Parser for Markdown

    Syntax:

        To use in a code block:
    
            {{{{#!markdown
            <add markdown text here>
            }}}}

        To use for an entire page:

            #format markdown
            <add markdown text here>

    @copyright: 2009 by Jason Fruit (JasonFruit at g mail dot com)
    @license: GNU GPL, see http://www.gnu.org/licenses/gpl for details

"""


from markdown import util
from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern


class ToDoPattern(Pattern):

    def __init__(self):
        Pattern.__init__(self, "^\[([xX ])\]")
        self.counter = 0

    def handleMatch(self, m):
        node = util.etree.Element("input")

        node.attrib["type"] = "checkbox"
        node.attrib["id"] = "md_cbx_{0}".format(self.counter)
        self.counter += 1
        node.attrib["value"] = m.group(3).strip()

        if m.group(2).upper() == "X":
            node.attrib["checked"] = "checked"

        return node


class ToDoExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('todo', ToDoPattern(), "_begin")



Dependencies = ['user']

class Parser:
    """
    A thin wrapper around a Python implementation
    (http://www.freewisdom.org/projects/python-markdown/) of John
    Gruber's Markdown (http://daringfireball.net/projects/markdown/)
    to make it suitable for use with MoinMoin.
    """
    def __init__(self, raw, request, **kw):
        self.raw = raw
        self.request = request

    def format(self, formatter):
        todo = ToDoExtension(configs={})
        output_html = Markdown(extensions=[todo]).convert(self.raw)

        try:
            self.request.write(formatter.rawHTML(output_html))
        except:
            self.request.write(formatter.escapedText(output_html))
