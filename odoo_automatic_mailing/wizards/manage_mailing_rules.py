from odoo import _, api, fields, models


class ManageMailingRules(models.TransientModel):
    _name = 'manage.mailing.rules'
    _description = 'Manage Mailing Rules'

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    automatic_mailing_rule_ids = fields.One2many(related="company_id.automatic_mailing_rule_ids", readonly=False)
