# Copyright 2013-2016 Akretion - Alexis de Lattre
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2016 Tecnativa - Antonio Espinosa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def is_sepa_creditor_identifier_valid(sepa_creditor_identifier):
    """Check if SEPA Creditor Identifier is valid
    @param sepa_creditor_identifier: SEPA Creditor Identifier as str
        or unicode
    @return: True if valid, False otherwise
    """
    if not isinstance(sepa_creditor_identifier, str):
        return False
    try:
        sci = str(sepa_creditor_identifier).lower()
    except Exception:
        logger.warning("SEPA Creditor ID should contain only ASCII characters.")
        return False
    if len(sci) < 9:
        return False
    before_replacement = sci[7:] + sci[0:2] + "00"
    logger.debug("SEPA ID check before_replacement = %s" % before_replacement)
    after_replacement = ""
    for char in before_replacement:
        if char.isalpha():
            after_replacement += str(ord(char) - 87)
        else:
            after_replacement += char
    logger.debug("SEPA ID check after_replacement = %s" % after_replacement)
    return int(sci[2:4]) == (98 - (int(after_replacement) % 97))
