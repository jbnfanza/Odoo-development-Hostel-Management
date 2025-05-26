from odoo import models, fields
from odoo.exceptions import UserError

class StudentReportWizard(models.TransientModel):
    _name = 'student.report.wizard'
    _description = 'Student Report Wizard'

    room_id = fields.Many2one('room.management', string='Room')
    student_id = fields.Many2one('student.information', string='Student')
    filter_by = fields.Selection([('new', 'Room'), ('students', 'Students')], string="Filter By")

    def print_report(self):
        domain = []

        if self.filter_by == 'students' and self.student_id:
            domain = [('id', '=', self.student_id.id)]
        elif self.filter_by == 'new' and self.room_id:
            domain = [('name_id', '=', self.room_id.id)]

        students = self.env['student.information'].search(domain)

        if not students:
            raise UserError("No student records found for the selected filter.")

        return self.env.ref('hostel_management.action_report_temp_stud').report_action(students)

