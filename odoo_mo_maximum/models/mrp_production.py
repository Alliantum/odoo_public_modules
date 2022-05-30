
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# Here we configure the creation and modification of Manufacturing Orders
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    allow_exceed_max = fields.Boolean('Allow Exceed Max', default=False)
    max_allowed_reached = fields.Boolean('Max Reached', default=False)

    @api.onchange('product_qty', 'product_id')
    def onchange_check_max_raise(self):
        if not self.allow_exceed_max and self.product_id and self.product_id.max_production and self.product_uom_id and self.product_qty:
            if self.product_uom_id._compute_quantity(self.product_qty, self.product_id.uom_id) > self.product_id.max_production:
                self.max_allowed_reached = True
                return {'warning': {
                    'title': 'Confirm Max Exceeded',
                    'message': "Producing {} {} exceeds the limit of {} per a single Manufacturing Order, which is {} {}.\n\n"
                               "If you steel want to allow exceed that maximum amount for this MO, please check the field 'Allow Exceed Max'."
                               " Otherwise a new MO will be created with the exceeded amounts.".format(
                self.product_qty, self.product_uom_id.name, self.product_id.name, self.product_id.max_production, self.product_id.uom_id.name),
                        }}
        self.max_allowed_reached = False

    def split_amount_create_mo(self, vals, product_id):
        next_vals = vals.copy()
        mo_uom_id = self.env['uom.uom'].browse(vals.get('product_uom_id'))
        qty = mo_uom_id._compute_quantity(vals.get('product_qty'), product_id.uom_id)
        if qty > product_id.max_production:
            res_qty = product_id.uom_id._compute_quantity(product_id.max_production, mo_uom_id)
            next_vals['product_qty'] = product_id.uom_id._compute_quantity(qty - product_id.max_production, mo_uom_id)
            return (res_qty, next_vals)
        return (vals['product_qty'], False)

    def check_max_raise(self, qty, uom_name, product_id):
        if qty > product_id.max_production:
            raise ValidationError(_(
            "Can't save this order. The amount for the MO ( {} {} ) exceeds the limit of {} per a single Manufacturing Order, which is {} {}.".format(
                qty, uom_name, product_id.name, product_id.max_production, product_id.uom_id.name)))

    def _find_grouping_target(self, vals, product_id=None):
        # Overriden from mrp_production_grouped_by_product module, it removes the limit on the search
        domain = self._get_grouping_target_domain(vals)
        if product_id:
            domain.append(('product_qty', '<', product_id.max_production))
        return self.env['mrp.production'].search(domain)

    @api.model
    def create(self, vals):
        product_id = self.env['product.product'].browse(vals.get('product_id'))
        if (self.env.context.get('group_mo_by_product') and
                (not self.env.context.get('test_enable') or self.env.context.get('test_group_mo'))):
            mo_ids = self._find_grouping_target(vals, product_id)
            product_qty = vals['product_qty']
            modified_mo_ids = self.env['mrp.production']
            for mo_id in mo_ids:
                if product_qty:
                    qty_available = product_id.max_production - mo_id.product_qty
                    if product_qty > qty_available:
                        vals['product_qty'] = qty_available
                        product_qty -= qty_available
                    else:
                        vals['product_qty'] = product_qty
                        product_qty = 0
                    mo_id.env['change.production.qty'].create({
                        'mo_id': mo_id.id,
                        'product_qty': mo_id.product_qty + vals['product_qty'],
                    }).change_prod_qty()
                    mo_id._post_mo_merging_adjustments(vals)
                    modified_mo_ids += mo_id
            # return one of the modified MO to keep consistency
            if not product_qty and modified_mo_ids:
                return modified_mo_ids[0]
            else: vals['product_qty'] = product_qty
        if product_id.max_production and product_id.max_production > 0 and (not vals.get('allow_exceed_max') or vals['allow_exceed_max'] == False):
            vals['product_qty'], next_values = self.split_amount_create_mo(vals, product_id)
            # If there are more units than the limit then the rest are created in a new MO
            if next_values:
                self.env['mrp.production'].create(next_values)
        return super(MrpProduction, self.with_context(group_mo_by_product=False)).create(vals)

    def write(self, vals):
        product_id = self.env['product.product'].search([('id', '=', vals.get('product_id'))]) if 'product_id' in vals else None
        for mo_id in self:
            if not mo_id.allow_exceed_max:
                if not product_id: product_id = mo_id.product_id
                allow_exceed = mo_id.allow_exceed_max
                if 'allow_exceed_max' in vals:
                    allow_exceed = True if vals.get('allow_exceed_max') == False else False
                if product_id.max_production and product_id.max_production > 0 and not allow_exceed:
                    if 'product_qty' in vals and 'product_uom_id' in vals:
                        new_uom_id = self.env['uom.uom'].browse(vals.get('product_uom_id'))
                        qty = new_uom_id._compute_quantity(vals.get('product_qty'), product_id.uom_id)
                        mo_id.check_max_raise(qty, new_uom_id.name, product_id)
                    elif 'product_qty' in vals:
                        qty = mo_id.product_uom_id._compute_quantity(vals.get('product_qty'), product_id.uom_id)
                        mo_id.check_max_raise(qty, mo_id.product_uom_id.name, product_id)
                    elif 'product_uom_id' in vals:
                        new_uom_id = self.env['uom.uom'].browse(vals.get('product_uom_id'))
                        qty = new_uom_id._compute_quantity(mo_id.product_qty, product_id.uom_id)
                        mo_id.check_max_raise(qty, new_uom_id.name, product_id)
        return super(MrpProduction, self).write(vals)
