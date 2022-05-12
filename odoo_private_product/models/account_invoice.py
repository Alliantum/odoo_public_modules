from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """If there are private products added, check that the partner is attached to them,
        otherwise display an error mentioning the partners that are attached to those products"""
        errors = []
        for line in self.invoice_line_ids.filtered(lambda r: len(r.product_id.restricted_partner_ids) >= 1):
            if line.invoice_id.partner_id not in line.product_id.restricted_partner_ids:
                limited_partners = line.product_id.restricted_partner_ids
                more = (_(' and {} more').format(str(len(limited_partners) - 1)) if len(limited_partners) > 1 else '')
                errors.append(_("{} is a private product, and can just be sold to {}{}").
                              format(line.product_id.name, limited_partners[0].name, more))
        if errors:
            raise ValidationError('\n'.join(errors))
        return super(AccountInvoice, self)._onchange_partner_id()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """If the product is private, check that it is attached to the selected partner,
        otherwise display an error"""
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id.restricted_partner_ids and self.invoice_id.partner_id not in self.product_id.restricted_partner_ids:
            raise ValidationError(_("{} is a private product, and can't be sold to {}").format(self.product_id.name, self.invoice_id.partner_id.name))
        return res
