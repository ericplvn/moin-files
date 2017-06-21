from cStringIO import StringIO
from .._activitybase import Analysis, parse_rows, moin_user_now


DAY_TEMPLATE_TOP = """
<h2>{day}</h2>
<table class="timecsv">
    <thead>
        <tr>
            <th>Project</th>
            <th>Time Spent</th>
        </tr>
    </thead>
    <tbody>
"""


DAY_TEMPLATE_BOTTOM = """\
    </tbody>
</table>
"""


ROW_TEMPLATE = '\t<tr class="{active}"><td>{task}</td><td>{time}</td></tr>\n'


class Parser:

    def __init__(self, raw, request, **kw):
        self.request = request
        self.analysis = Analysis(parse_rows(raw), moin_user_now(request))
        self.analysis.process()

    def format(self, formatter, **kw):
        output = StringIO()

        for day, rows in self.analysis:
            output.write(DAY_TEMPLATE_TOP.format(day=day.strftime('%A %B %d, %Y')))

            for task, (time, still_active) in rows.items():
                output.write(ROW_TEMPLATE.format(task=task, time=time,
                    active='active' if still_active else ''))

            output.write(DAY_TEMPLATE_BOTTOM)

        self.request.write(output.getvalue())
