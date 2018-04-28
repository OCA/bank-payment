# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
Parser for HSBC UK MT940 format files
Based on fi_patu's parser
"""
import re
from datetime import datetime
import logging


_logger = logging.getLogger(__name__)


class HSBCParser(object):

    def __init__(self):
        recparse = dict()
        # Allowed characters. The list was originally taken from HSBC's
        # spec, but the ampersand character was found out in the wild in
        # the customer account name
        patterns = {'ebcdic': r"\w/\?:\(\).,'+{} &-"}

        # MT940 header
        recparse["20"] = r":(?P<recordid>20):(?P<transref>.{1,16})"
        recparse["25"] = (r":(?P<recordid>25):(?P<sortcode>\d{6})"
                          r"(?P<accnum>\d{1,29})")
        recparse["28"] = r":(?P<recordid>28C?):(?P<statementnr>.{1,8})"

        # Opening balance 60F
        recparse["60F"] = (r":(?P<recordid>60F):(?P<creditmarker>[CD])"
                           r"(?P<prevstmtdate>\d{6})(?P<currencycode>.{3})"
                           r"(?P<startingbalance>[\d,]{1,15})")

        # Transaction
        recparse["61"] = (r"""
:(?P<recordid>61):
(?P<valuedate>\d{6})(?P<bookingdate>\d{4})?
(?P<creditmarker>R?[CD])
(?P<currency>[A-Z])?
(?P<amount>[\d,]{1,15})
(?P<bookingcode>[A-Z][A-Z0-9]{3})
(?P<custrefno>[%(ebcdic)s]{1,16})
(?://)
(?P<bankref>[%(ebcdic)s]{1,16})?
(?:\n(?P<furtherinfo>[%(ebcdic)s]))?
""" % (patterns)).replace('\n', '')

        # Further info
        recparse["86"] = (r":(?P<recordid>86):"
                          r"(?P<infoline1>.{1,80})?"
                          r"(?:\n(?P<infoline2>.{1,80}))?"
                          r"(?:\n(?P<infoline3>.{1,80}))?"
                          r"(?:\n(?P<infoline4>.{1,80}))?"
                          r"(?:\n(?P<infoline5>.{1,80}))?")

        # Forward available balance (64) /  Closing balance (62F)
        # / Interim balance (62M)
        recparse["64"] = (r":(?P<recordid>64|62[FM]):"
                          r"(?P<creditmarker>[CD])"
                          r"(?P<bookingdate>\d{6})(?P<currencycode>.{3})"
                          r"(?P<endingbalance>[\d,]{1,15})")

        for record in recparse:
            recparse[record] = re.compile(recparse[record])
        self.recparse = recparse

    def parse_record(self, line):
        """
        Parse record using regexps and apply post processing
        """
        for matcher in self.recparse:
            matchobj = self.recparse[matcher].match(line)
            if matchobj:
                break
        if not matchobj:
            _logger.warning("failed to match line %r", line)
            return
        # Strip strings
        matchdict = matchobj.groupdict()

        # Remove members set to None
        matchdict = dict([(k, v) for k, v in matchdict.iteritems() if v])

        matchkeys = set(matchdict.keys())
        needstrip = set([
            "transref", "accnum", "statementnr", "custrefno",
            "bankref", "furtherinfo", "infoline1", "infoline2", "infoline3",
            "infoline4", "infoline5", "startingbalance", "endingbalance"
        ])
        for field in matchkeys & needstrip:
            matchdict[field] = matchdict[field].strip()

        # Convert to float. Comma is decimal separator
        needsfloat = set(["startingbalance", "endingbalance", "amount"])
        for field in matchkeys & needsfloat:
            matchdict[field] = float(matchdict[field].replace(',', '.'))

        # Convert date fields
        needdate = set(["prevstmtdate", "valuedate", "bookingdate"])
        for field in matchkeys & needdate:
            datestring = matchdict[field]

            post_check = False
            if (len(datestring) == 4 and
                    field == "bookingdate" and
                    "valuedate" in matchdict):
                # Get year from valuedate
                datestring = matchdict['valuedate'].strftime('%y') + datestring
                post_check = True
            try:
                matchdict[field] = datetime.strptime(datestring, '%y%m%d')
                if post_check and matchdict[field] > matchdict["valuedate"]:
                    matchdict[field] = matchdict[field].replace(
                        year=matchdict[field].year - 1
                    )
            except ValueError:
                matchdict[field] = None

        return matchdict

    def parse(self, cr, data):
        records = []
        # Some records are multiline
        for line in data:
            if len(line) <= 1:
                continue
            if line[0] == ':' and len(line) > 1:
                records.append(line)
            else:
                records[-1] = '\n'.join([records[-1], line])

        output = []
        for rec in records:
            output.append(self.parse_record(rec))

        return output


def parse_file(filename):
    with open(filename, "r") as hsbcfile:
        HSBCParser().parse(None, hsbcfile.readlines())


def main():
    """The main function, currently just calls a dummy filename

    :returns: description
    """
    parse_file("testfile")


if __name__ == '__main__':
    main()
