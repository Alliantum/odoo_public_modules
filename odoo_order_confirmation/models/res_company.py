# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    stock_warning_notify = fields.Many2many('res.users', string='Notify Stock Managers Warn')

    @api.multi
    def write(self, vals):
        """Add the users in `stock_warning_notify` to `group_sale_stock_approval`"""
        if 'stock_warning_notify' in vals:
            self.env.ref('odoo_order_confirmation.group_sale_stock_approval').users = vals['stock_warning_notify']
        return super(ResCompany, self).write(vals)
