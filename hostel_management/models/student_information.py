from odoo import fields, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date


class StudentInformation(models.Model):
    _name = "student_information"
    _description = "Student Information"
    _inherit = ['mail.thread']


    student_id = fields.Char(string="Student ID", readonly=True, copy=False)
    name = fields.Char(string="Student Name", required="1")
    date_of_birth = fields.Date(string="DOB", required="1")
    age = fields.Char(string='Age')
    image = fields.Image()
    email = fields.Char(string="Email", required="1")
    receive_mail = fields.Boolean(string="Receive Mail")
    city = fields.Char(string="City")
    street = fields.Char(string="Street", required="1")
    street_two = fields.Char(string="Street 2")
    zip = fields.Char(string="ZIP")
    state_id = fields.Many2one('res.country.state', string="State", required="1")
    country_id = fields.Many2one('res.country', string="Country", required="1")
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id, )
    name_id = fields.Many2one('room_management', string="Room", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner", readonly=True)
    student_name_id = fields.Many2one('student_information', string="Name")
    invoice_count = fields.Integer(compute="_compute_invoice_count")


    @api.onchange('date_of_birth')
    def _change_birth_date(self):
        if self.date_of_birth:
            dob = self.date_of_birth
            thisday = date.today()
            self.age = relativedelta(thisday, dob).years

    def alot_button(self):
        available_room = self.env['room_management'].search([
            ('state', 'in', ['partial', 'empty']),
            ('number_of_bed', '>', 0),
        ], order='id asc', limit=1)
        if not available_room:
            raise ValidationError('No available rooms to allocate.')
        # name=room number
        self.name_id = available_room
        available_room.bed_booked += 1
        remaining_beds = available_room.number_of_bed - available_room.bed_booked
        if remaining_beds == 0:
            available_room.state = 'full'
        elif remaining_beds < available_room.number_of_bed:
            available_room.state = 'partial'
        else:
            available_room.state = 'empty'


    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].create({
            'name': vals.get('name')
        })
        vals['partner_id'] = partner.id
        if not vals.get('student_id'):
            vals['student_id'] = self.env['ir.sequence'].next_by_code('student_information')
        return super(StudentInformation, self).create(vals)


    def action_vacate(self):
        for rec in self:
            if rec.name_id:
                rec.name_id.bed_booked -= 1
                rec.name_id = False


    def unlink(self):
        for student in self:
            leave_requests = self.env['leave.request'].search([
                ('student_name_id', '=', student.id)
            ])
            leave_requests.unlink()
        return super(StudentInformation, self).unlink()


    def action_view_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'create': False}
        }


    @api.depends('partner_id')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([('student_id', '=', rec.id)])


