from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    mail_attachment_line_ids = fields.One2many(comodel_name='mail.attachment.line', inverse_name='company_id', string="Dynamic Mail Attachments")
