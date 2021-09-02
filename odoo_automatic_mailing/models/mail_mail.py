# -*- coding: utf-8 -*-

import re
# Intrapackage imports
from email.charset import Charset
from odoo import api, models
from odoo import tools


# Helpers
specialsre = re.compile(r'[][\\()<>@,:;".]')
escapesre = re.compile(r'[\\"]')


# We override here these methods to work properly with the email separated by , or ; in the email field in contacts (emulating more or less the behavior in erp5)
def extendedformataddr(pair, charset='utf-8'):
    name, address = pair
    # The address MUST (per RFC) be ascii, so raise a UnicodeError if it isn't.
    address.encode('ascii')
    address = address.replace(';', ',')
    addresses = address.split(',')

    if name:
        try:
            name.encode('ascii')
        except UnicodeEncodeError:
            if isinstance(charset, str):
                charset = Charset(charset)
            encoded_name = charset.header_encode(name)
            temp = ['%s <%s>' % (encoded_name, address.strip()) for address in addresses]
            return [', '.join(temp)]
        else:
            quotes = ''
            if specialsre.search(name):
                quotes = '"'
            name = escapesre.sub(r'\\\g<0>', name)
            temp = ['%s%s%s <%s>' % (quotes, name, quotes, address.strip()) for address in addresses]
            return [', '.join(temp)]
    return [address]


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def _send_prepare_values(self, partner=None):
        """Return a dictionary for specific email values, depending on a
        partner, or generic to the whole recipients given by mail.email_to.

            :param Model partner: specific recipient partner
        """

        self.ensure_one()
        body = self._send_prepare_body()
        body_alternative = tools.html2plaintext(body)
        if partner:
            email_to = extendedformataddr((partner.name or 'False', partner.email or 'False'))
        else:
            email_to = tools.email_split_and_format(self.email_to)
        res = {
            'body': body,
            'body_alternative': body_alternative,
            'email_to': email_to,
        }
        return res
