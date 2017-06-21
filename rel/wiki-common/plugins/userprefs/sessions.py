from MoinMoin import user, wikiutil
from MoinMoin.widget import html
from MoinMoin.userprefs import UserPrefBase


class Settings(UserPrefBase):

    def __init__(self, request):
        UserPrefBase.__init__(self, request)
        self.request = request
        self.cfg = request.cfg
        self.title = "View sessions"
        self.name = 'sessions'

    def handle_form(self):
        request = self.request
        form = request.form
        ss = self.cfg.session_service

        if form.has_key('cancel'):
            return

        if request.method != 'POST':
            return

        if not wikiutil.checkTicket(request, form['ticket']):
            return

        deleted = 0
        for key in form.keys():
            if not key.startswith("session."):
                continue

            _, sid = key.split(".", 1)
            ss.destroy_session(request, ss.get_session(request, sid))
            deleted += 1

        return 'info', "%s Sessions deleted" % deleted

    def create_form(self, create_only=False, recover_only=False):
        r = self.request
        ss = self.cfg.session_service
        format_time = lambda x: self.request.user.getFormattedDateTime(x) if x else x

        form = self.make_form(html.Text("Active sessions for your account"))
        ticket = wikiutil.createTicket(self.request)
        form.append(html.INPUT(type="hidden", name="ticket", value="%s" % ticket))

        self._table.append(html.TR().extend([
            html.TD().extend([""]),
            html.TD().extend([html.B().append("From IP")]),
            html.TD().extend([html.B().append("Login Date")]),
            html.TD().extend([html.B().append("Expiration")]),
            html.TD().extend([html.B().append("User Agent")]),
        ]))

        for sid in ss.get_all_session_ids(r):
            session = ss.get_session(r, sid)

            if session.get("user.id") != r.user.id:
                continue

            self._table.append(html.TR().extend([
                html.TD().extend([html.INPUT(type="checkbox", name="session.%s" % sid)]),
                html.TD().extend([session.get("from_ip")]),
                html.TD().extend([format_time(session.get("started"))]),
                html.TD().extend([format_time(session.get("expires"))]),
                html.TD().extend([session.get("from_ua")]),
            ]))

        form.append(unicode(html.INPUT(type="submit", name='save', value="Delete Sessions")))
        form.append(unicode(html.INPUT(type="submit", name='cancel', value="Cancel")))

        #form.append(repr(r.in_headers))

        return unicode(form)
