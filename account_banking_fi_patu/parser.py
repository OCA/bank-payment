# -*- coding: utf-8 -*-
"""Parser for PATU format files"""
import re
import datetime
import logging

_logger = logging.getLogger(__name__)


def fixchars(line):
    """Fix the characters mangled in the input

    :param line: Line to rewrite

    :returns: string, fixed line
    """
    # Fix the umlauts int the input
    line = line.replace("{", u"ä")
    line = line.replace("}", u"ö")
    # XXX: There are a whole bunch of these, adding them later
    return line


class PatuParser(object):
    """Parse PATU lines in to structs"""

    def __init__(self):
        """ Initialize PATU parser """

        recparse = dict()
        recparse["00"] = (
            r"T(?P<recordid>00)(?P<record_len>\d{3})"
            r"(?P<version>\d{3})(?P<accountnr>\d{14})"
            r"(?P<statementnr>\d{3})(?P<startdate>\d{6})"
            r"(?P<enddate>\d{6})"
            r"(?P<creationdate>\d{6})(?P<creationtime>\d{4})"
            r"(?P<customerid>.{17})(?P<balancedate>\d{6})"
            r"(?P<startingbalance>.{19})"
            r"(?P<itemcount>\d{6})(?P<currency>.{3})"
            r"(?P<accountname>.{30})"
            r"(?P<accountlimit>\d{18})(?P<accountowner>.{35})"
            r"(?P<bankcontact1>.{40})(?P<bankcontact2>.{40})"
            r"(?P<bankcontact3>.{30})(?P<ibanswift>.{30})"
        )
        recparse["10"] = (
            r"T(?P<recordid>[18]0)(?P<record_len>\d{3})"
            r"(?P<eventid>\d{6})"
            r"(?P<archivalnr>.{18})(?P<recorddate>\d{6})"
            r"(?P<valuedate>\d{6})"
            r"(?P<paymentdate>\d{6})(?P<eventtype>\d)"
            r"(?P<eventcode>.{3})(?P<eventdesc>.{35})"
            r"(?P<amount>.{19})(?P<receiptcode>.)(?P<creationmethod>.)"
            r"(?P<recipientname>.{35})(?P<recipientsource>.)"
            r"(?P<recipientaccount>.{14})(?P<recipientaccountchanged>.)"
            r"(?P<refnr>.{20})"
            r"(?P<formnr>.{8})(?P<eventlevel>.)"
        )
        recparse["11"] = (
            r"T(?P<recordid>[18]1)(?P<record_len>\d{3})"
            r"(?P<infotype>.{2})"
            r"(?:(?# Match specific info)"
            r"(?<=00)(?P<message>.{35})+"
            r"|"
            r"(?<=01)(?P<transactioncount>\d{8})"
            r"|"
            r"(?<=02)(?P<customerid>.{10})\s(?P<invoicenr>.{15})\s"
            r"(?P<invoicedate>\d{6})"
            r"|"
            r"(?<=03)(?P<cardnumber>.{19})\s(?P<storereference>.{14})"
            r"|"
            r"(?<=04)(?P<origarchiveid>.{18})"
            r"|"
            r"(?<=05)(?P<destinationamount>.{19})\s(?P<currency>.{3})\s"
            r"(?P<exchangerate>.{11})(?P<rateref>.{6})"
            r"|"
            r"(?<=06)(?P<principalinfo1>.{35})(?P<principalinfo2>.{35})"
            r"|"
            r"(?<=07)(?P<bankinfo1>.{35})"
            r"(?P<bankinfo2>.{35})?"
            r"(?P<bankinfo3>.{35})?"
            r"(?P<bankinfo4>.{35})?"
            r"(?P<bankinfo5>.{35})?"
            r"(?P<bankinfo6>.{35})?"
            r"(?P<bankinfo7>.{35})?"
            r"(?P<bankinfo8>.{35})?"
            r"(?P<bankinfo9>.{35})?"
            r"(?P<bankinfo10>.{35})?"
            r"(?P<bankinfo11>.{35})?"
            r"(?P<bankinfo12>.{35})?"
            r"|"
            r"(?<=08)(?P<paymentcode>\d{3})\s(?P<paymentdesc>.{31})"
            r"|"
            r"(?<=09)(?P<recipientname2>.{35})"
            r"|"
            r"(?<=11)(?P<reference>.{35})(?P<recipientiban>.{35})"
            r"(?P<recipientbic>.{35})(?P<recipientnameiban>.{70})"
            r"(?P<sendername>.{70})(?P<senderid>.{35})"
            r"(?P<archivalid>.{70})"
            r")"
        )
        recparse["40"] = (
            r"T(?P<recordid>40)(?P<record_len>\d{3})"
            r"(?P<recorddate>\d{6})(?P<balance>.{19})"
            r"(?P<availablefunds>.{19})"
        )
        recparse["50"] = (
            r"T(?P<recordid>50)(?P<record_len>\d{3})"
            r"(?P<period>\d)(?P<perioddate>\d{6})"
            r"(?P<depositcount>\d{8})(?P<depositsum>.{19})"
            r"(?P<withdrawcount>\d{8})(?P<withdrawsum>.{19})"
        )
        recparse["60"] = (
            r"T(?P<recordid>60)(?P<record_len>\d{3})"
            r"(?P<bankid>.{3})(?P<specialid>01)"
            r"(?P<interestperiodstart>\d{6})-"
            r"(?P<interestperiodend>\d{6})"
            r"(?P<avgbalanceinfo>.)(?P<avgbalance>.{19})"
            r"(?P<interestinfo>.)(?P<interestrate>\d{7})"
            r"(?P<limitbalanceinfo>.)(?P<avglimitbalance>.{19})"
            r"(?P<limitinterestinfo>.)(?P<limitinterestrate>\d{7})"
            r"(?P<limitusageinfo>.)(?P<limitusage>\d{7})"
            r"(?P<permanentbalanceinfo>.)(?P<permanentbalance>.{19})"
            r"(?P<refinterestinfo>.)(?P<refinterestname>.{35})"
            r"(?P<refinterestrate>\d{7})"
            r"(?P<refcreditinfo>.)(?P<refcreditname>.{35})"
            r"(?P<refcreditrate>\d{7})"
        )
        recparse["70"] = (
            r"T(?P<recordid>70)(?P<record_len>\d{3})"
            r"(?P<bankid>\d{3})"
            r"(?P<infoline1>.{80})"
            r"(?P<infoline2>.{80})?"
            r"(?P<infoline3>.{80})?"
            r"(?P<infoline4>.{80})?"
            r"(?P<infoline5>.{80})?"
            r"(?P<infoline6>.{80})?"
        )
        for record in recparse:
            recparse[record] = re.compile(recparse[record])
        self.recparse = recparse

    def parse_record(self, line):
        """Docstring for parse_perus

        :param line: description

        :returns: description
        """
        line = fixchars(line)
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
        for field in matchdict.keys():
            if not matchdict[field]:
                del matchdict[field]

        matchkeys = set(matchdict.keys())
        needstrip = set([
            "bankcontact1", "bankcontact2", "bankcontact3",
            "customerid", "accountowner", "accountname", "refnr", "formnr",
            "recipientname", "eventdesc", "recipientaccount", "message",
            "principalinfo1", "bankinfo1", "bankinfo2", "bankinfo3",
            "bankinfo4", "bankinfo5", "bankinfo6", "bankinfo7", "bankinfo8",
            "bankinfo9", "bankinfo10", "bankinfo11", "bankinfo12",
            "principalinfo2", "paymentdesc", "infoline1", "infoline2",
            "infoline3", "infoline4", "infoline5", "infoline6",
            "recipientname2", "recipientnameiban", "sendername"])
        for field in matchkeys & needstrip:
            matchdict[field] = matchdict[field].strip()
        # Convert to int
        needsint = set([
            "itemcount", "eventid", "record_len",
            "depositcount", "withdrawcount"])
        for field in matchkeys & needsint:
            matchdict[field] = float(matchdict[field])
        # Convert to float
        needsfloat = set([
            "startingbalance", "accountlimit", "amount",
            "destinationamount", "balance", "availablefunds", "depositsum",
            "withdrawsum", "avgbalance", "avglimitbalance",
            "permanentbalance"])
        for field in matchkeys & needsfloat:
            matchdict[field] = float(matchdict[field])
        # convert sents to euros
        needseur = set([
            "startingbalance", "accountlimit", "amount",
            "destinationamount", "balance", "availablefunds", "depositsum",
            "withdrawsum", "avgbalance", "permanentbalance"])
        for field in matchkeys & needseur:
            matchdict[field] = matchdict[field] / 100
        # convert ibanswift to separate fields
        if "ibanswift" in matchdict:
            matchdict["iban"], matchdict["swift"] = (
                matchdict["ibanswift"].strip().split()
            )

        # Convert date fields
        needdate = set([
            "startdate", "enddate", "creationdate", "balancedate",
            "valuedate", "paymentdate", "recorddate", "perioddate"])
        for field in matchkeys & needdate:
            # Base all dates on the year 2000, since it's unlikely that this
            # starndard will survive to see 2020 due to SEPA
            datestring = matchdict[field]
            if datestring == '000000':
                matchdict[field] = None
                continue

            matchdict[field] = datetime.date(
                int("20" + datestring[0:2]),
                int(datestring[2:4]), int(datestring[4:6]))
        # convert time fields
        needtime = set(["creationtime"])
        for field in matchkeys & needtime:
            timestring = matchdict[field]
            matchdict[field] = datetime.time(
                int(timestring[0:2]),
                int(timestring[2:4]))

        return matchdict


def parse_file(filename):
    """Parse file with PATU format inside

    :param filename: description

    :returns: description
    """
    patufile = open(filename, "r")
    parser = PatuParser()
    for line in patufile:
        parser.parse_record(line)


def main():
    """The main function, currently just calls a dummy filename

    :returns: description
    """
    parse_file("myinput.nda")


if __name__ == '__main__':
    main()
