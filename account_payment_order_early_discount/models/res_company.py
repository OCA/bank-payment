# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

import pytz

from odoo import models

# Days searched for a working day: a company calendar without any working day
# within a month is considered not maintained, the date is then left as it is
MAX_WORKDAY_SHIFT = 31


class ResCompany(models.Model):
    _inherit = "res.company"

    def _payment_order_is_workday(self, day):
        """Working day according to the company calendar (attendances minus global
        leaves such as public holidays); Monday to Friday without a calendar."""
        self.ensure_one()
        calendar = self.resource_calendar_id
        if not calendar:
            return day.weekday() < 5
        tz = pytz.timezone(calendar.tz or "UTC")
        start = tz.localize(datetime.combine(day, time.min))
        end = tz.localize(datetime.combine(day, time.max))
        return bool(list(calendar._work_intervals_batch(start, end)[False]))

    def _payment_order_shift_to_workday(self, day, step):
        """First working day from `day` on, forward (step 1) or backward (-1)."""
        self.ensure_one()
        for _i in range(MAX_WORKDAY_SHIFT):
            if self._payment_order_is_workday(day):
                return day
            day += timedelta(days=step)
        return day
