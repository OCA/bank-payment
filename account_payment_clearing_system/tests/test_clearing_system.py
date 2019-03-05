# -*- coding: utf-8 -*-
# Copyright 2019 Braintec (https://www.braintec-group.com/)
# @author: Tobias Bächle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestClearingSystem(TransactionCase):

    def setUp(self):
        super(TestClearingSystem, self).setUp()
        self.bank_model = self.env['res.bank']

    def test_payment_file_generation(self):
        payment_method_id = self.env['account.payment.method'].search(
            [('code', '=', 'sepa_credit_transfer')])
        vals = {
            'name': 'Company Test Bank',
            'csmi': 'other',
            'bic': 'TESTBIC1',
            'street': 'Some Street 456',
            'city': 'Some Place',
            'zip': '12345',
            'country': self.env.ref('base.ch').id,
            'phone': '123456789'
        }
        company_bank_id = self.env['res.bank'].create(vals)

        vals = {
            'acc_number': '123456',
            'partner_id': self.env.user.company_id.partner_id.id,
            'bank_id': company_bank_id.id
        }
        partner_bank_id = self.env['res.partner.bank'].create(vals)

        vals = {
            'name': 'Bank',
            'type': 'bank',
            'code': 'BNKCL1',
            'bank_account_id': partner_bank_id.id,
        }
        journal_id = self.env['account.journal'].create(vals)

        vals = {
            'name': 'Test Payment Mode',
            'payment_method_id': payment_method_id.id,
            'bank_account_link': 'fixed',
            'fixed_journal_id': journal_id.id,
            'payment_order_ok': True,
            'move_option': 'date',
        }
        payment_mode_id = self.env['account.payment.mode'].create(vals)

        partner_id = self.env['res.partner'].create({'name': 'Test Partner'})
        vals = {
            'name': 'Test Bank',
            'csmi': 'ATBLZ',
            'csmi_number': '12345',
            'street': 'Some Street 123',
            'city': 'Some Place',
            'zip': '98745',
            'country': self.env.ref('base.ch').id,
            'phone': '123456789'
        }
        bank_id = self.env['res.bank'].create(vals)

        vals = {
            'acc_number': '654321',
            'partner_id': partner_id.id,
            'bank_id': bank_id.id
        }
        partner_bank_id = self.env['res.partner.bank'].create(vals)

        transact_vals = {
            'amount_currency': 100.0,
            'partner_id': partner_id.id,
            'partner_bank_id': partner_bank_id.id,
            'communication_type': 'normal',
            'communication': 'test_ref_123456'
        }
        vals = {
            'payment_mode_id': payment_mode_id.id,
            'journal_id': journal_id.id,
            'date_prefered': 'due',
            'payment_line_ids': [(0, 0, transact_vals)]
        }
        payment_order_id = self.env['account.payment.order'].create(vals)
        payment_order_id.draft2open()
        action = payment_order_id.open2generated()
        self.assertEquals(payment_order_id.state, 'generated')
        self.assertEquals(action['res_model'], 'ir.attachment')
        attachment = self.env['ir.attachment'].browse(action['res_id'])
        self.assertEquals(attachment.datas_fname[-4:], '.xml')
        xml_file = attachment.datas.decode('base64')
        xml_root = etree.fromstring(xml_file)
        namespaces = xml_root.nsmap
        namespaces['p'] = xml_root.nsmap[None]
        namespaces.pop(None)
        party_agent_csmi_identification_code = xml_root.xpath(
            '//p:FinInstnId/p:ClrSysMmbId/p:ClrSysId/p:Cd',
            namespaces=namespaces)
        self.assertEquals(party_agent_csmi_identification_code[0].text,
                          'ATBLZ')
        party_agent_csmi_identification_member_id = xml_root.xpath(
            '//p:FinInstnId/p:ClrSysMmbId/p:MmbId',
            namespaces=namespaces)
        self.assertEquals(party_agent_csmi_identification_member_id[0].text,
                          '12345')

    def test_csmi_number_ATBLZ(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'ATBLZ',
                'csmi_number': '1234',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'ATBLZ',
            'csmi_number': '12345',
        })
        self.assertEqual(bank.csmi_number, '12345')

    def test_csmi_number_AUBSB(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'AUBSB',
                'csmi_number': '12345',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'AUBSB',
            'csmi_number': '123456',
        })
        self.assertEqual(bank.csmi_number, '123456')

    def test_csmi_number_CACPA(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'CACPA',
                'csmi_number': '12345678',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'CACPA',
            'csmi_number': '123456789',
        })
        self.assertEqual(bank.csmi_number, '123456789')

    def test_csmi_number_CHBCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'CHBCC',
                'csmi_number': '123456',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'CHBCC',
            'csmi_number': '1234',
        })
        self.assertEqual(bank.csmi_number, '1234')

    def test_csmi_number_CHSIC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'CHSIC',
                'csmi_number': '12345',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'CHSIC',
            'csmi_number': '123456',
        })
        self.assertEqual(bank.csmi_number, '123456')

    def test_csmi_number_CNAPS(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'CNAPS',
                'csmi_number': '12345678',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'CNAPS',
            'csmi_number': '123456789012',
        })
        self.assertEqual(bank.csmi_number, '123456789012')

    def test_csmi_number_DEBLZ(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'DEBLZ',
                'csmi_number': '1234567',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'DEBLZ',
            'csmi_number': '12345678',
        })
        self.assertEqual(bank.csmi_number, '12345678')

    def test_csmi_number_ESNCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'ESNCC',
                'csmi_number': '1234567',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'ESNCC',
            'csmi_number': '12345678',
        })
        self.assertEqual(bank.csmi_number, '12345678')

    def test_csmi_number_GBDSC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'GBDSC',
                'csmi_number': '12345',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'GBDSC',
            'csmi_number': '123456',
        })
        self.assertEqual(bank.csmi_number, '123456')

    def test_csmi_number_GRBIC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'GRBIC',
                'csmi_number': '123456',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'GRBIC',
            'csmi_number': '1234567',
        })
        self.assertEqual(bank.csmi_number, '1234567')

    def test_csmi_number_HKNCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'HKNCC',
                'csmi_number': '1234',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'HKNCC',
            'csmi_number': '123',
        })
        self.assertEqual(bank.csmi_number, '123')

    def test_csmi_number_IENCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'IENCC',
                'csmi_number': '12345',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'IENCC',
            'csmi_number': '123456',
        })
        self.assertEqual(bank.csmi_number, '123456')

    def test_csmi_number_INFSC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'INFSC',
                'csmi_number': '12345678',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'INFSC',
            'csmi_number': '12345678901',
        })
        self.assertEqual(bank.csmi_number, '12345678901')

    def test_csmi_number_ITNCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'ITNCC',
                'csmi_number': '12345678',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'ITNCC',
            'csmi_number': '1234567890',
        })
        self.assertEqual(bank.csmi_number, '1234567890')

    def test_csmi_number_JPZGN(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'JPZGN',
                'csmi_number': '123456',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'JPZGN',
            'csmi_number': '1234567',
        })
        self.assertEqual(bank.csmi_number, '1234567')

    def test_csmi_number_NZNCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'NZNCC',
                'csmi_number': '12345',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'NZNCC',
            'csmi_number': '123456',
        })
        self.assertEqual(bank.csmi_number, '123456')

    def test_csmi_number_PLKNR(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'PLKNR',
                'csmi_number': '1234567',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'PLKNR',
            'csmi_number': '12345678',
        })
        self.assertEqual(bank.csmi_number, '12345678')

    def test_csmi_number_PTNCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'PTNCC',
                'csmi_number': '1234567',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'PTNCC',
            'csmi_number': '12345678',
        })
        self.assertEqual(bank.csmi_number, '12345678')

    def test_csmi_number_RUCBC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'RUCBC',
                'csmi_number': '12345678',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'RUCBC',
            'csmi_number': '123456789',
        })
        self.assertEqual(bank.csmi_number, '123456789')

    def test_csmi_number_SESBA(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'SESBA',
                'csmi_number': '123',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'SESBA',
            'csmi_number': '1234',
        })
        self.assertEqual(bank.csmi_number, '1234')

    def test_csmi_number_SGIBG(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'SGIBG',
                'csmi_number': '12345',
            })

        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'SGIBG',
                'csmi_number': '12',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'SGIBG',
            'csmi_number': '1234',
        })
        self.assertEqual(bank.csmi_number, '1234')

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'SGIBG',
            'csmi_number': '1234567',
        })
        self.assertEqual(bank.csmi_number, '1234567')

    def test_csmi_number_THCBC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'THCBC',
                'csmi_number': '1234',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'THCBC',
            'csmi_number': '123',
        })
        self.assertEqual(bank.csmi_number, '123')

    def test_csmi_number_TWNCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'TWNCC',
                'csmi_number': '123456',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'TWNCC',
            'csmi_number': '1234567',
        })
        self.assertEqual(bank.csmi_number, '1234567')

    def test_csmi_number_USABA(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'USABA',
                'csmi_number': '12345678',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'USABA',
            'csmi_number': '123456789',
        })
        self.assertEqual(bank.csmi_number, '123456789')

    def test_csmi_number_USPID(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'USPID',
                'csmi_number': '123',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'USPID',
            'csmi_number': '1234',
        })
        self.assertEqual(bank.csmi_number, '1234')

    def test_csmi_number_ZANCC(self):
        with self.assertRaises(ValidationError):
            bank = self.bank_model.create({
                'name': "Test Bank",
                'csmi': 'ZANCC',
                'csmi_number': '12345',
            })

        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'ZANCC',
            'csmi_number': '123456',
        })
        self.assertEqual(bank.csmi_number, '123456')

    def test_csmi_number_other(self):
        bank = self.bank_model.create({
            'name': "Test Bank",
            'csmi': 'other',
            'csmi_number': False,
        })
        self.assertEqual(bank.csmi_number, False)
