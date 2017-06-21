import xmlrpclib
from .._activitybase import ActivityAction


def execute(self, pagename):
    action = ActivityAction(self._instr(pagename), self.request)

    if not action.page.exists():
        return self.noSuchPageFault()

    if not self.request.user.may.write(pagename):
        return self.notAllowedFault()

    if not action.can_use_activity:
        return xmlrpclib.Fault(1, "This page does not support activities.")

    action.stop_activity()

    return self._outstr('OK')
