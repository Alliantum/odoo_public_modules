# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    percentage_warning = fields.Boolean(string='Warning Percent on Sale',
                                        config_parameter='odoo_order_confirmation.percentage_warning')
    kg_onsale_warning = fields.Float(string='Limit Kg',
                                     config_parameter='odoo_order_confirmation.kg_onsale_warning',
                                     default=200)
    units_onsale_warning = fields.Float(string='Limit Units',
                                        config_parameter='odoo_order_confirmation.units_onsale_warning',
                                        default=100)
    stock_warning_notify = fields.Many2many('res.users',
                                            related="company_id.stock_warning_notify",
                                            string="Users to notify",
                                            readonly=False)
