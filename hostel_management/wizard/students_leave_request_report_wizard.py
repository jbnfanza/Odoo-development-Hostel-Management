from odoo import models, fields
from odoo.exceptions import UserError

class StudentLeaveReportWizard(models.TransientModel):
    _name = 'students.leave.request.report.wizard'
    filter_by = fields.Selection([('student', 'Student'), ('room', 'Room'),('start','Start Date'),('arrival','Arrival Date')], string="Filter By")
    def print_report(self):
        return