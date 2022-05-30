# -*- encoding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _setup_fields(self):
        """Add the `Warning` state to the selection field if doesn't exist"""
        super(SaleOrder, self)._setup_fields()
        selection = self._fields['state'].selection
        exists = False
        for idx, (state, __) in enumerate(selection):
            if state == 'warning':
                exists = True
        if not exists:
            selection.append(('warning', _('Warning')))

    def action_remove_warning(self):
        """Check that there are no missing quantities in order to remove the `Warning` state"""
        picking_id = self.env['stock.picking'].search([('sale_id', '=', self.id)], limit=1)
        if picking_id:
            current_state = picking_id.check_amounts()
            if not current_state[0]:
                self.state = 'sale'
            else:
                raise ValidationError(_("It wasn't possible to remove the warning state.There're still some quantities missing in the Deliveries:") + "\n\n" + current_state[1])
