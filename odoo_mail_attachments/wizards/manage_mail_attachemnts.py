from odoo import _, api, fields, models


class ManageMailAttachemnts(models.TransientModel):
    _name = 'manage.mail.attachments'
    _description = 'Manage Mail Attachments'

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    mail_attachment_line_ids = fields.One2many(related="company_id.mail_attachment_line_ids", readonly=False, string="Dynamic Attachment Lines")
