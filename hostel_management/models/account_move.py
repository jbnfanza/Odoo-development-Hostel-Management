from pycparser.ply.yacc import resultlimit

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    student_id = fields.Many2one('student_information', string="Student's name")

    def action_post(self):
        result = super().action_post()
        for invoice in self:
            if invoice.student_id and invoice.student_id.partner_id:
                invoice.message_post(
                    body=f"Invoice posted for student: {invoice.student_id.name}",
                    partner_ids=[invoice.student_id.partner_id.id]
                )
                invoice.student_id.message_post(
                    body=f"Invoice {invoice.name} has been confirmed.",
                    message_type='notification',
                )
            return result

    # def action_send_email(self):
    #     result = super().action_send_email()
    #     for template in self:
    #         if template.student_id:
    #             template.send_mail(
    #                 body=f"invoice", message_type='notification',
    #             )
    #     return result
