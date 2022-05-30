from odoo import models, fields, _
from odoo.exceptions import ValidationError



class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[('warning', 'Warning')], ondelete={'warning': lambda recs: recs.write({'state': 'draft'})})

    def action_remove_warning(self):
        """Check that there are no missing quantities in order to remove the `Warning` state"""
        picking_id = self.env['stock.picking'].search([('sale_id', '=', self.id)], limit=1)
        if picking_id:
            current_state = picking_id.check_amounts()
            if not current_state[0]:
                self.state = 'sale'
            else:
                raise ValidationError(_("It wasn't possible to remove the warning state.There're still some quantities missing in the Deliveries:") + "\n\n" + current_state[1])
