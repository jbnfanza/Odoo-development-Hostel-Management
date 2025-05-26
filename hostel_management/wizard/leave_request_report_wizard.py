from odoo import models, fields
from odoo.exceptions import UserError

class StudentReportWizard(models.TransientModel):
    _name = 'leave.request.report.wizard'
    filter_by = fields.Selection([('student', 'Student'), ('room', 'Room'),('start','Start Date'),('arrival','Arrival Date')], string="Filter By")
    def print_report(self):
        return