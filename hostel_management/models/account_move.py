from odoo import models, fields, api
class AccountMove(models.Model):

    _inherit = 'account.move'

    student_id = fields.Many2one('student.information', string="Student")


    def action_post(self):
        result = super().action_post()
        template = self.env.ref('account.email_template_edi_invoice')
        if (
                self.move_type == 'out_invoice'
                and self.state == 'posted'
                and self.partner_id.email
                and template
        ):
            template.send_mail(self.id, force_send=True)
        return result
