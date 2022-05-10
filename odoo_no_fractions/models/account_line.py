from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    uom_id = fields.Many2one('uom.uom',
        string='Unit of Measure',
        compute='_compute_uom_id'
    )

    @api.depends('product_uom_id')
    def _compute_uom_id(self):
        for record in self:
            record.uom_id = record.product_uom_id

    @api.onchange('product_id', 'product_uom_id')
    def _check_avoid_fractions(self):
        """If the uom category of a product has `avoid_sell_fractions` enabled, and the
        quantity is not an integer, display a warning"""
        for line in self:
            if line.uom_id.category_id.avoid_sell_fractions:
                #if int(line.quantity) != line.quantity:
                if not line.quantity.is_integer():
                    warning = {
                        'title': _('Invalid Product Quantity'),
                        'message': _("You're trying to sell {} {} of the product {}.\n"
                                     " However the UoM for that product ( {} ) doesn't allow to"
                                     " sell floating point amounts of it. Please enter a non-decimal Quantity.").format(line.quantity,
                                                                                                                        line.uom_id.name,
                                                                                                                        line.product_id.name,
                                                                                                                        line.uom_id.name),
                    }
                    return {'warning': warning}

    @api.model_create_multi
    def create(self, vals_list):
        """If the uom category of a product has `avoid_sell_fractions` enabled, and the
        quantity is not an integer, return an error that prevents the creation of the invoice"""
        lines = super(AccountInvoiceLine, self).create(vals_list)
        for line in lines:
            if line.uom_id.category_id.avoid_sell_fractions:
                #if int(line.quantity) != line.quantity:
                if not line.quantity.is_integer():
                    raise ValidationError(_("You're trying to sell {} {} of the product {}.\n"
                                            " However the UoM for that product ( {} ) doesn't allow to"
                                            " sell floating point amounts of it. Please enter a non-decimal Quantity.").format(line.quantity,
                                                                                                                               line.uom_id.name,
                                                                                                                               line.product_id.name,
                                                                                                                               line.uom_id.name))
        return lines

    def write(self, vals):
        """If the uom category of a product has `avoid_sell_fractions` enabled, and the
        quantity is not an integer, return an error that prevents saving the invoice when
        a change was made to the quantity or the uom"""
        res = super(AccountInvoiceLine, self).write(vals)
        if vals.get('uom_id'):
            uom_id = self.env['uom.uom'].browse(vals.get('uom_id'))
            if uom_id.category_id.avoid_sell_fractions:
                if vals.get('quantity') and (int(vals.get('quantity')) != vals.get('quantity')):
                    raise ValidationError(_("You're trying to sell {} {}.\n"
                                            " However the UoM for that product ( {} ) doesn't allow to"
                                            " sell floating point amounts of it. Please enter a non-decimal Ordered Quantity.").format(vals.get('quantity'),
                                                                                                                                       uom_id.name,
                                                                                                                                       uom_id.name))
                else:
                    for line in self:
                        #if int(line.quantity) != line.quantity:
                        if not line.quantity.is_integer():
                            raise ValidationError(_("You're trying to sell {} {} of the product {}.\n"
                                                    " However the UoM for that product ( {} ) doesn't allow to"
                                                    " sell floating point amounts of it. Please enter a non-decimal Ordered Quantity.").format(line.quantity,
                                                                                                                                               line.uom_id.name,
                                                                                                                                               line.product_id.name,
                                                                                                                                               line.uom_id.name))
        elif vals.get('quantity'):
            for line in self:
                if line.uom_id.category_id.avoid_sell_fractions:
                    #if int(vals.get('quantity')) != vals.get('quantity'):
                    if not float(vals.get('quantity')).is_integer():
                        raise ValidationError(_("You're trying to sell {} {} of the product {}.\n"
                                                " However the UoM for that product ( {} ) doesn't allow to"
                                                " sell floating point amounts of it. Please enter a non-decimal Ordered Quantity.").format(vals.get('quantity'),
                                                                                                                                           line.uom_id.name,
                                                                                                                                           line.product_id.name,
                                                                                                                                           line.uom_id.name))
        return res
