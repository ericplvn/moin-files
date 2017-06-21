import csv
import time
from datetime import datetime
from cStringIO import StringIO

from MoinMoin.action import ActionBase
from MoinMoin.PageEditor import PageEditor


def moin_user_now(request):
    return datetime.fromtimestamp(time.mktime(
        request.user.getTime(time.time())))


class FormattedDateTime:

    def __init__(self, dt):
        self.dt = dt

    @property
    def time(self):
        return self.dt.strftime('%H:%M:%S')

    @property
    def date(self):
        return self.dt.strftime('%Y-%m-%d')


class DataRow(list):

    _attr_map = ['start_date', 'start_time', 'end_date', 'end_time', 'task']

    def __setattr__(self, attr, value):
        pos = self._attr_map.index(attr)
        self[pos] = value

    def __getattr__(self, attr):
        pos = self._attr_map.index(attr)
        return self[pos]

    def _make_datetime(self, date, time):
        if not date or not time:
            return None

        try:
            return datetime.strptime(' '.join((date, time)), '%Y-%m-%d %H:%M:%S')
        except ValueError as err:
            return datetime.strptime(' '.join((date, time)), '%Y-%m-%d %H:%M')

    @property
    def start_datetime(self):
        return self._make_datetime(self.start_date, self.start_time)

    @property
    def end_datetime(self):
        return self._make_datetime(self.end_date, self.end_time)

    @property
    def has_ended(self):
        return self.end_date != ''

    def mark_ended(self, now):
        if not self.has_ended:
            self.end_date = now.date
            self.end_time = now.time


def parse_rows(data):
    body = StringIO(data)

    if data.startswith('#'):
        body.readline()

    reader = csv.reader(body, quotechar='"')
    return [DataRow(r) for r in reader]


class ActivityAction(ActionBase):

    def __init__(self, pagename, request):
        ActionBase.__init__(self, pagename, request)

        self.page = PageEditor(request, pagename)
        self.use_ticket = True

    def get_user_now(self):
        return FormattedDateTime(moin_user_now(self.request))

    def get_rows(self):
        return parse_rows(self.page.body)

    def update_page(self, rows):
        out_page = StringIO()
        out_page.write('#format timecsv\n')
        csv.writer(out_page, quotechar='"').writerows(rows)

        return self.page.saveText(out_page.getvalue(), self.request.rev or 0)

    def start_activity(self, description):
        rows = self.get_rows()
        now = self.get_user_now()
    
        if len(rows) > 0:
            rows[-1].mark_ended(now)

        rows.append((now.date, now.time, '', '', description))

        return self.update_page(rows)

    def stop_activity(self):
        rows = self.get_rows()
        rows[-1].mark_ended(self.get_user_now())
        self.update_page(rows)

    @property
    def can_use_activity(self):
        return self.page.pi['format'] == 'timecsv'


class Analysis:

    def __init__(self, data, user_now):
        self.raw_data = data
        self.user_now = user_now
        self.data = {}
        self.order = []

    @staticmethod
    def _to_time(value):
        hours = value // 3600
        minutes = (value // 60) - (hours * 60)

        if hours == 0:
            return '{} minutes'.format(minutes)
        else:
            return '{} hours {} minutes'.format(hours, minutes)

    def process(self):
        self.raw_data.sort(key=lambda i: i.start_datetime, reverse=True)

        for row in self.raw_data:
            date = row.start_datetime.date()
            data = self.data.get(date, None)

            if date not in self.order:
                self.order.append(date)

            if data is None:
                data = self.data[date] = {}

            if not data.get(row.task):
                data[row.task] = [0, False]

            if row.end_datetime:
                data[row.task][0] += (
                        row.end_datetime - row.start_datetime).seconds
            else:
                data[row.task][0] += (
                        self.user_now - row.start_datetime).seconds

            if not row.has_ended:
                data[row.task][1] = True

    def __iter__(self):
        for key in self.order:
            yield key, dict((k, (self._to_time(v[0]), v[1])) for k, v in self.data[key].items())
