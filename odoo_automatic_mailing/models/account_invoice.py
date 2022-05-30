from odoo import models, api, _, fields



class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # Added here to make this module copatible with odoo_invoice_addresses
    partner_invoice_id = fields.Many2one('res.partner')

    def filter_recipients_mailing(self):
        # It returns the list of emails to be sent, it acts like a queue of pending mails. Filters whether the customer has allowed to send emails.
        recipients = []
        message = ''
        recipients.append(self.partner_invoice_id.email and self.partner_invoice_id or self.partner_id.email and self.partner_id)
        if self.user_id and self.user_id.os_enable_email_receivable is True and self.user_id.partner_id.email:
            formatted_emails = recipients[0].email.replace(';', ',')
            formatted_emails = [email.strip() for email in formatted_emails.split(',')]
            if not self.user_id.partner_id.email.strip() in formatted_emails:
                recipients.append(self.user_id.partner_id)
            else:
                if (self.user_id.partner_id != self.partner_invoice_id) and (
                        self.user_id.partner_id != self.partner_id):
                    formatted_emails.pop(formatted_emails.index(self.user_id.partner_id.email.strip()))
                    recipients[0].email = ", ".join(formatted_emails)
                    recipients.append(self.user_id.partner_id)
        elif self.user_id and self.user_id.os_enable_email_receivable is True and not self.user_id.partner_id.email:
            message = _(
                "{}, the Contact ({}) of this Order ({}) has received an email with this document in pdf attached to it.\n"
                " But, you couldn't receive a copy of that because you don't seem to have any email configured in your profile.\n\n"
                "Please, be sure to fulfill your email address if you would like to be able to receive copy of these automatic emails.".format(
                    self.user_id.name, self.partner_id.name, self.name))
        return recipients, message

    def notify_exception_automatic_mailing(self, message):
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        channel_id = self.env['mail.channel'].search([('name', '=', 'OdooBot')], limit=1)
        if not channel_id:
            channel_id = self.env['mail.channel'].with_context(
                {"mail_create_nosubscribe": True}).create({
                    'channel_partner_ids': [(4, self.env.user.id), (4, odoobot_id)],
                    'public': 'private',
                    'channel_type': 'chat',
                    'email_send': False,
                    'name': 'OdooBot'
                })
        channel_id.sudo().message_post(body=message, author_id=odoobot_id, message_type="comment",
                                       subtype_xmlid="mail.mt_comment")

    def _post(self, soft=True):
        res = super()._post(soft)
        # Whenever an invoice is created we need to send an email to the customer
        for invoice in self:
            
            if invoice.amount_total > 0 and invoice.move_type == 'out_invoice':
                if invoice.partner_id and invoice.partner_id.os_invoice_send_option == 'email':
                    if invoice.partner_id.email or invoice.partner_invoice_id.email:
                        to_notify, message = invoice.filter_recipients_mailing()
                        template_id = self.env.company.get_automatic_mailing_template('account.move', invoice)
                        if template_id:
                            for contact in to_notify:
                                post_params = dict(
                                    template_id=template_id.id,
                                    message_type='comment',
                                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id(
                                        'odoo_automatic_mailing.mt_automatic_mailing'),
                                    email_layout_xmlid='mail.mail_notification_paynow',
                                    attachment_ids=[],
                                    partner_ids=[(6, False, [contact.id])],
                                )
                                lang = contact.lang or invoice.partner_id.lang
                                invoice.sudo().with_context(lang=lang, default_type='binary').message_post_with_template(**post_params)
                                invoice.is_move_sent = True
                            if message:
                                self.notify_exception_automatic_mailing(message)
                        # else:
                        #     self.notify_exception_automatic_mailing(_("Automatic mailing at Invoice validation is not working because the template was not set in the settings."))
                    else:
                        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
                        channel_id = self.with_user(self.env.user.id).env['mail.channel'].search([('name', '=', 'OdooBot')], limit=1)
                        if not channel_id:
                            channel_id = self.env['mail.channel'].with_context({"mail_create_nosubscribe": True}).create({
                                'channel_partner_ids': [(4, self.env.user.id), (4, odoobot_id)],
                                'public': 'private',
                                'channel_type': 'chat',
                                'email_send': False,
                                'name': 'OdooBot'
                            })
                        name = False
                        if invoice.sequence_number_next_prefix and invoice.sequence_number_next:
                            name = invoice.sequence_number_next_prefix + invoice.sequence_number_next
                        message = _(
                            "The Contact of this Invoice{}couldn't automatically receive the email with the current document.\n\n"
                            " {} doesn't have any Email account assigned to it.".format(' ({}) '.format(name or invoice.name or ''), invoice.partner_id.name or ''))
                        channel_id.sudo().message_post(body=message, author_id=odoobot_id, message_type="comment",
                                                       subtype_xmlid="mail.mt_comment")
        return res
