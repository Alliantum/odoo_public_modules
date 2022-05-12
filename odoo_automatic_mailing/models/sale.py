from odoo import models, api, _, SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def filter_recipients_mailing(self):
        # It returns the list of emails to be sent, it acts like a queue of pending mails. Filters whether the customer has allowed to send emails.
        trigger = False
        recipients = []
        message = ''
        if self.partner_id and self.partner_id.email:
            recipients.append(self.partner_id)
            trigger = True
            if self.user_id and self.user_id.os_enable_email_receivable is True and self.user_id.partner_id.email:
                if recipients:
                    formatted_emails = recipients[0].email.replace(';', ',')
                    formatted_emails = [email.strip() for email in formatted_emails.split(',')]
                    if not self.user_id.partner_id.email.strip() in formatted_emails:
                        recipients.append(self.user_id.partner_id)
                    else:
                        if (self.user_id.partner_id != self.partner_invoice_id) and (self.user_id.partner_id != self.partner_id):
                            formatted_emails.pop(formatted_emails.index(self.user_id.partner_id.email.strip()))
                            recipients[0].email = ", ".join(formatted_emails)
                            recipients.append(self.user_id.partner_id)
            elif self.user_id and self.user_id.os_enable_email_receivable is True and not self.user_id.partner_id.email:
                message = _(
                    "{}, the Contact ({}) of this Order ({}) has received an email with this document in pdf attached to it.\n"
                    " But, you couldn't receive a copy of that because you don't seem to have any email configured in your profile.\n\n"
                    "Please, be sure to fulfill your email address if you would like to be able to receive copy of these automatic emails.".format(
                        self.user_id.name, self.partner_id.name, self.name))
        else:
            message = _(
                "The Contact of this Order ({}) couldn't automatically receive the email with the current document.\n\n"
                " {} doesn't have any Email account assigned to it.".format(self.name, self.partner_id.name))
        return trigger, recipients, message

    def notify_exception_automatic_mailing(self, message):
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        channel_id = self.sudo(self.env.user.id).env['mail.channel'].search([('name', '=', 'OdooBot')], limit=1)
        if not channel_id:
            channel_id = self.env['mail.channel'].with_context({"mail_create_nosubscribe": True}).create({
                'channel_partner_ids': [(4, self.env.user.id), (4, odoobot_id)],
                'public': 'private',
                'channel_type': 'chat',
                'email_send': False,
                'name': 'OdooBot'
            })
        channel_id.sudo().message_post(body=message, author_id=odoobot_id, message_type="comment",
                                        subtype="mail.mt_comment")

    def action_confirm(self):
        for order in self:
            confirm = super(SaleOrder, order).action_confirm()
            trigger, recipients, message = order.filter_recipients_mailing()
            if trigger:
                template_id = self.env.user.company_id.get_automatic_mailing_template('sale.order', order)
                if template_id:
                    for contact in recipients:
                        post_params = dict(
                            template_id=template_id.id,
                            message_type='comment',
                            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('odoo_automatic_mailing.mt_automatic_mailing'),
                            notif_layout='mail.mail_notification_paynow',
                            attachment_ids=[],
                            partner_ids=[(6, False, [contact.id])],
                            )
                        order.sudo(SUPERUSER_ID).with_context(lang=contact.lang, body_to_lang=contact.lang or 'en_US').message_post_with_template(**post_params)
                # else:
                #     message = _("Automatic mailing at Sale Order confirmation is not working because the template was not set in the settings.")
            if message:
                self.notify_exception_automatic_mailing(message)
            return confirm
