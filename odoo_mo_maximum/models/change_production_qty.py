
from odoo import api, fields, models, _


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    # Here is created the message that appears when ONCE you have a MO
    # and you want to update the quantity to produce
    warning_message = fields.Html(compute="_get_warning_message")

    @api.depends('product_qty')
    def _get_warning_message(self):
        for wiz in self:
            if wiz.mo_id.product_id.max_production and wiz.mo_id.product_id.max_production > 0 and not wiz.mo_id.allow_exceed_max:
                wiz.warning_message = _("<p>This product has a limit on the quantities you can produce for a single MO."
                                        " Maximum is {}, so be aware, that if you overpass this limit a new MO will be created"
                                        " with the exceeded amounts.</p>").format(wiz.mo_id.product_id.max_production)

    @api.model
    def create(self, vals):
        # Checks if allow_exceed_max is checked and quantity is greater than allowed
        mo_id = self.env['mrp.production'].browse(vals.get('mo_id'))
        if not mo_id.allow_exceed_max:
            reference = mo_id.product_id and mo_id.product_id.max_production
            if reference and reference > 0:
                qty = mo_id.product_uom_id._compute_quantity(vals.get('product_qty'), mo_id.product_id.uom_id)
                if reference and qty > reference:
                    vals['product_qty'] = reference
                    # Here is where the rest of the quantity gets converted into a new MO
                    updated_qty = qty - reference
                    mo_id.copy(default={'product_qty': updated_qty})
        return super(ChangeProductionQty, self).create(vals)

    @api.onchange('product_qty')
    def onchange_check_max_raise(self):
        for wiz in self:
            if not wiz.mo_id.allow_exceed_max and wiz.mo_id.product_id and wiz.mo_id.product_id.max_production and wiz.mo_id.product_uom_id and wiz.product_qty:
                if wiz.mo_id.product_uom_id._compute_quantity(wiz.product_qty, wiz.mo_id.product_id.uom_id) > wiz.mo_id.product_id.max_production:
                    return {'warning': {
                        'title': 'Confirm Max Exceeded',
                        'message': "Producing {} {} exceeds the limit of {} per a single Manufacturing Order, which is {} {}.\n\n"
                                "If you still want to allow exceeding that maximum amount for this MO, please check the field 'Allow Exceed Max'."
                                " Otherwise a new MO will be created with the exceeded amounts.".format(
                    wiz.product_qty, wiz.mo_id.product_uom_id.name, wiz.mo_id.product_id.name, wiz.mo_id.product_id.max_production, wiz.mo_id.product_id.uom_id.name),
                            }}
