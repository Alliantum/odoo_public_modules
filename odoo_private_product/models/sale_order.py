from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """If there are private products added, check that the partner is attached to them,
        otherwise return an error mentioning the partners attached to those products"""
        errors = []
        for line in self.order_line.filtered(lambda r: len(r.product_id.restricted_partner_ids) >= 1):
            if line.order_id.partner_id not in line.product_id.restricted_partner_ids:
                limited_partners = line.product_id.restricted_partner_ids
                more = (_(' and {} more').format(str(len(limited_partners) - 1)) if len(limited_partners) > 1 else '')
                errors.append(_("{} is a private product, and can just be sold to {}{}").
                              format(line.product_id.name, limited_partners[0].name, more))
        if errors:
            raise ValidationError('\n'.join(errors))
        return super(SaleOrder, self).onchange_partner_id()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        """If the product is private, check that it is attached to the selected partner,
        otherwise display an error"""
        if not self.order_id.partner_id:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a partner.'),
            }
            return {'warning': warning}
        if self.product_id.restricted_partner_ids and self.order_id.partner_id not in self.product_id.restricted_partner_ids:
            raise ValidationError(_("{} is a private product, and can't be sold to {}").format(self.product_id.name, self.order_id.partner_id.name))
        return super(SaleOrderLine, self).product_id_change()
