from odoo import models, fields, api
from odoo.exceptions import UserError

class LeaveReportWizard(models.TransientModel):
    _name = 'leave.request.report.wizard'
    _description = 'Leave Request Report Wizard'

    filter_by = fields.Selection([
        ('student', 'Student'),
        ('room', 'Room'),
        ('start', 'Start Date'),
        ('arrival', 'Arrival Date')
    ], string="Filter By", required=True)

    student_id = fields.Many2one('student.information', string="Student")
    room_id = fields.Many2one('room.management', string="Room")
    start_date = fields.Date(string="Start Date")
    arrival_date = fields.Date(string="Arrival Date")

    def print_report(self):
        where_clauses = []
        params = []
        join_clause = ""

        if self.filter_by == 'student' and self.student_id:
            where_clauses.append("lr.student_name_id = %s")
            params.append(self.student_id.id)

        elif self.filter_by == 'room' and self.room_id:
            join_clause = "JOIN student_information si ON lr.student_name_id = si.id"
            where_clauses.append("si.name_id = %s")
            params.append(self.room_id.id)

        elif self.filter_by == 'start' and self.start_date:
            where_clauses.append("lr.name = %s")
            params.append(self.start_date)

        elif self.filter_by == 'arrival' and self.arrival_date:
            where_clauses.append("lr.arrival_date = %s")
            params.append(self.arrival_date)

        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT lr.id
            FROM leave_request lr
            {join_clause}
            {where_clause}
        """

        self.env.cr.execute(query, tuple(params))
        result = self.env.cr.fetchall()
        ids = [row[0] for row in result]

        records = self.env['leave.request'].browse(ids)

        if not records:
            raise UserError("No leave requests found for the selected criteria.")

        return self.env.ref('hostel_management.leave_request_report_action').report_action(
            records
        )
