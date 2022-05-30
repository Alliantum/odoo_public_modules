# -*- encoding: utf-8 -*-

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    is_stock_confirmation = fields.Boolean('Stock Confirmation')
