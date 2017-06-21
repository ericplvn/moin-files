from .._activitybase import ActivityAction


def execute(pagename, request):
    action = ActivityAction(pagename, request)

    if not action.can_use_activity:
        request.theme.add_msg('This page does not support activities.', 'error')
        return action.page.send_page()

    action.stop_activity()
    action.page.send_page()
