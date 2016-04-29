# -*- coding: utf-8 -*-
# © 2013-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def is_sepa_creditor_identifier_valid(sepa_creditor_identifier):
    """Check if SEPA Creditor Identifier is valid
    @param sepa_creditor_identifier: SEPA Creditor Identifier as str
        or unicode
    @return: True if valid, False otherwise
    """
    if not isinstance(sepa_creditor_identifier, (str, unicode)):
        return False
    try:
        sci = str(sepa_creditor_identifier).lower()
    except:
        logger.warning(
            "SEPA Creditor ID should contain only ASCII characters.")
        return False
    if len(sci) < 9:
        return False
    before_replacement = sci[7:] + sci[0:2] + '00'
    logger.debug(
        "SEPA ID check before_replacement = %s" % before_replacement)
    after_replacement = ''
    for char in before_replacement:
        if char.isalpha():
            after_replacement += str(ord(char) - 87)
        else:
            after_replacement += char
    logger.debug(
        "SEPA ID check after_replacement = %s" % after_replacement)
    return int(sci[2:4]) == (98 - (int(after_replacement) % 97))
