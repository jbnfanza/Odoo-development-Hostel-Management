from odoo import fields,models
class LeaveRequest(models.Model):
    _name='leave.request'
    name=fields.Date(string="Date",required="1")
    arrival_date=fields.Date(required="1")
    state=fields.Selection(selection=[('new', 'NEW'), ('approved', 'APPROVED') ] ,string='State', default='new')
    student_name_id=fields.Many2one('student_information',string="Name",required="1")
    reason=fields.Char(string="Reason for Leave",required="1")



    def action_approval(self):
         self.state = 'approved'

