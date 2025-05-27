from odoo import models, fields
from odoo.exceptions import UserError

class StudentReportWizard(models.TransientModel):
    _name = 'student.report.wizard'
    _description = 'Student Report Wizard'

    room_id = fields.Many2one('room.management', string='Room')
    student_id = fields.Many2one('student.information', string='Student')

    def print_report(self):
        cr = self.env.cr

        if self.student_id:
            query = """
                SELECT id FROM student_information WHERE id = %s
            """
            cr.execute(query, (self.student_id.id,))

        elif self.room_id:
            query = """
                SELECT id FROM student_information WHERE name_id = %s
            """
            cr.execute(query, (self.room_id.id,))

        else:
            raise UserError("Please select either a student or a room to generate the report.")

        result = cr.fetchall()
        student_ids = [row[0] for row in result]

        if not student_ids:
            raise UserError("No student records found for the selected filter.")

        students = self.env['student.information'].browse(student_ids)

        return self.env.ref('hostel_management.action_report_temp_stud').report_action(students)


