from odoo import fields, api, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    automatic_mailing_rule_ids = fields.One2many(comodel_name='automatic.mailing.rule', inverse_name='company_id')

    @api.model
    def get_automatic_mailing_template(self, model_name, record):
        for mailing_rule_id in self.automatic_mailing_rule_ids.filtered(lambda line: line.model_name == model_name):
            if mailing_rule_id._pass_filter(record):
                return mailing_rule_id.template_id
