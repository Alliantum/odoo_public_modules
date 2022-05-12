# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherited(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        """
        Prepare the dict of values that will create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        res = super(SaleOrderInherited, self)._prepare_invoice()
        res['partner_id'] = self.partner_id.id
        res['partner_invoice_id'] = self.partner_invoice_id.id
        return res
