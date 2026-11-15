# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

import pytz

from odoo import models

# Days searched for a working day: a company calendar without any working day
# within a month is considered not maintained, the date is then left as it is
MAX_WORKDAY_SHIFT = 31


class ResCompany(models.Model):
    _inherit = "res.company"

    def _payment_order_workdays(self, first, last):
        """Working days from `first` to `last` according to the company calendar
        (attendances minus global leaves of the company, such as public holidays);
        Monday to Friday without a calendar."""
        self.ensure_one()
        calendar = self.resource_calendar_id
        if not calendar:
            return {
                first + timedelta(days=i)
                for i in range((last - first).days + 1)
                if (first + timedelta(days=i)).weekday() < 5
            }
        tz = pytz.timezone(calendar.tz or "UTC")
        intervals = calendar._work_intervals_batch(
            tz.localize(datetime.combine(first, time.min)),
            tz.localize(datetime.combine(last, time.max)),
            # Leaves without calendar apply to all calendars: only those of this
            # company (the core does not filter them without a resource)
            domain=[
                ("time_type", "=", "leave"),
                ("company_id", "in", [False, self.id]),
            ],
        )[False]
        return {start.astimezone(tz).date() for start, _stop, _records in intervals}

    def _payment_order_is_workday(self, day):
        self.ensure_one()
        return day in self._payment_order_workdays(day, day)

    def _payment_order_shift_to_workday(self, day, step):
        """First working day from `day` on, forward (step 1) or backward (-1); `day`
        itself if there is none within MAX_WORKDAY_SHIFT days."""
        self.ensure_one()
        days = [day + timedelta(days=i * step) for i in range(MAX_WORKDAY_SHIFT)]
        workdays = self._payment_order_workdays(min(days), max(days))
        return next((d for d in days if d in workdays), day)
