from odoo import fields, models, api


class LeaveRequest(models.Model):
    _name = 'leave.request'
    _description = 'Leave Request'

    name = fields.Date(string="Date", required=True)
    arrival_date = fields.Date(string="Arrival Date", required=True)
    state = fields.Selection(selection=[('new', 'NEW'), ('approved', 'APPROVED')], string='State', default='new')
    student_name_id = fields.Many2one('student.information', string="Student", required=True)
    reason = fields.Char(string="Reason for Leave", required=True)
    student_id = fields.Many2one('student.information', string="Student", required=True)
    company_id = fields.Many2one(  'res.company', string='Company',default=lambda self: self.env.company,required=True  )

    def action_approval(self):
        self.state = 'approved'
        student = self.student_name_id
        room = student.name_id
        if student:
            student.is_on_leave = True
        if room and not any(room_student for room_student in room.student_ids if not room_student.is_on_leave):
            room.previous_state = room.state
            self.env['cleaning.service'].create({
                'name': room.id,
                'start_time': fields.Datetime.now(),
                'company_id': room.company_id.id
            })
            room.state = 'cleaning'

    @api.model
    def create(self, vals):
        if 'student_id' not in vals:
            student = self.env['student.information'].search([('user_id', '=', self.env.uid)], limit=1)
            if student:
                vals['student_id'] = student.id
        return super().create(vals)
