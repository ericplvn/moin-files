from MoinMoin.theme.modernized import Theme as _Theme
from MoinMoin.Page import Page
from MoinMoin import wikiutil


class Theme(_Theme):

    # Hook to add an override stylesheet, favicon, iPhone icon, and viewport
    # tag
    def universal_edit_button(self, d, **k):
        return u'\n'.join([
            ('<meta name="viewport" content="width=device-width, '
                'initial-scale=1" />'),

            ('<link rel="shortcut icon" href="/WikiStatic?'
                'action=AttachFile&do=get&target=favicon.ico">'),

            ('<link rel="apple-touch-icon-precomposed" href="/WikiStatic?'
                'action=AttachFile&do=get&target=iphone-icon.png"/>'),

            ('<link rel="stylesheet" type="text/css" charset="utf-8" '
                'media="all" href="/WikiStatic?'
                'action=AttachFile&do=get&target=mcrute.css">'),

            ('<script type="text/javascript" src="/WikiStatic?'
                'action=AttachFile&do=get&target=dnd-upload.js">'
                '</script>'),

            ('<script type="text/javascript" src="/WikiStatic?'
                'action=AttachFile&do=get&target=features.js">'
                '</script>'),
        ]) + _Theme.universal_edit_button(self, d, **k)

    # Hook to add a Home link to the header links next to the logo
    def username(self, d):
        html = _Theme.username(self, d)
        first_tag = html.index('>') + 1

        page = wikiutil.getFrontPage(self.request)

        return u'{} {} <span class="sep"> | </span> {}'.format(
                html[:first_tag], page.link_to_raw(self.request, "Home"),
                html[first_tag:])

    def editbarItems(self, page):
        actions = _Theme.editbarItems(self, page)

        # Add quick link actions for starting/stopping activities
        if page.pi['format'] == 'timecsv':
            actions.insert(len(actions) - 1, page.link_to(
                self.request, text='Start Activity',
                querystr={ 'action': 'StartActivity' }, rel='nofollow'))

            actions.insert(len(actions) - 1, page.link_to(
                self.request, text='Stop Activity',
                querystr={ 'action': 'StopActivity' }, rel='nofollow'))

        return actions

    def send_title(self, text, **keywords):
        if 'editor_mode' in keywords:
            if 'body_attr' in keywords:
                keywords['body_attr'] += 'id="page-editor"'
            else:
                keywords['body_attr'] = 'id="page-editor"'

        return _Theme.send_title(self, text, **keywords)

    def searchform(self, d):
        _ = self.request.getText
        form = self.request.values
        updates = {
            'search_label': _('Search:'),
            'search_value': wikiutil.escape(form.get('value', ''), 1),
            'search_full_label': _('Text'),
            'search_title_label': _('Titles'),
            'url': self.request.href(d['page'].page_name)
            }
        d.update(updates)

        html = u'''
<form id="searchform" method="get" action="%(url)s">
<div>
<input type="hidden" name="action" value="fullsearch">
<input type="hidden" name="context" value="180">
<label for="searchinput">%(search_label)s</label>
<input id="searchinput" type="text" name="value" value="%(search_value)s" size="20"
    onfocus="searchFocus(this)" onblur="searchBlur(this)"
    onkeyup="searchChange(this)" onchange="searchChange(this)" alt="Search">
<input id="fullsearch" name="fullsearch" type="submit"
    value="%(search_full_label)s" alt="Search Full Text">
<input id="titlesearch" name="titlesearch" type="submit"
    value="%(search_title_label)s" alt="Search Titles">
</div>
</form>
<script type="text/javascript">
<!--// Initialize search form
var f = document.getElementById('searchform');
f.getElementsByTagName('label')[0].style.display = 'none';
var e = document.getElementById('searchinput');
searchChange(e);
searchBlur(e);
//-->
</script>
''' % d
        return html


def execute(request):
    return Theme(request)

