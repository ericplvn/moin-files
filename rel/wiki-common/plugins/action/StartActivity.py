from MoinMoin import wikiutil
from .._activitybase import ActivityAction, FormattedDateTime


TEMPLATE = '''
<table>
    <tr>
        <td class="label"><label>%(comment_label)s</label></td>
        <td class="content">
            <input type="text" name="activity" size="80" maxlength="200">
        </td>
    </tr>
    <tr>
        <td></td>
        <td class="buttons">
            %(buttons_html)s
        </td>
    </tr>
</table>
'''


class StartActivity(ActivityAction):

    def __init__(self, pagename, request):
        ActivityAction.__init__(self, pagename, request)

        self.form_trigger = 'start_activity'
        self.form_trigger_label = self._('Start Activity')

    def check_condition(self):
        if not self.can_use_activity:
            return 'This page does not support activities.'
        else:
            return None

    def do_action(self):
        description = wikiutil.clean_input(self.form.get('activity', u''))
        return True, self.start_activity(description) 

    def get_form_html(self, buttons_html):
       return TEMPLATE % {
           'pagename': self.pagename,
           'comment_label': self._("Activity to start"),
           'buttons_html': buttons_html,
       }


def execute(pagename, request):
    StartActivity(pagename, request).render()
