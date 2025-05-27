from odoo import fields, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date


class StudentInformation(models.Model):
    _name = "student.information"
    _description = "Student Information"
    _inherit = ['mail.thread']

    student_id = fields.Char(string="Student ID", readonly=True, copy=False)
    name = fields.Char(string="Student Name", required=True)
    date_of_birth = fields.Date(string="DOB", required=True)
    age = fields.Char(string='Age')
    image = fields.Image()
    email = fields.Char(string="Email", required=True)
    receive_mail = fields.Boolean(string="Receive Mail")
    city = fields.Char(string="City")
    street = fields.Char(string="Street", required=True)
    street_two = fields.Char(string="Street 2")
    zip = fields.Char(string="ZIP")
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=', country_id)]", string="State")

    country_id = fields.Many2one('res.country', string="Country", required=True)


    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    name_id = fields.Many2one('room.management', string="Room", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner", readonly=True)
    student_name_id = fields.Many2one('student_information', string="Name")
    invoice_count = fields.Integer(compute="_compute_invoice_count", store=False)
    active = fields.Boolean(default=True)
    monthly_amount = fields.Float(related='name_id.total_rent', string="Monthly Amount")
    user_id = fields.Many2one('res.users', string="User", readonly=True)
    invoice_status = fields.Selection([('pending', 'Pending'), ('done', 'Done')], string='Invoice Status',
                                      compute='_compute_invoice_status', store=True)
    invoice_ids = fields.One2many('account.move', 'student_id', string="Invoices")
    is_on_leave = fields.Boolean(default=False)
    pending_amount = fields.Float(string="Pending Amount", compute="_compute_pending_amount")

    @api.onchange('date_of_birth')
    def _onchange_birth_date(self):
        if self.date_of_birth:
            self.age = relativedelta(date.today(), self.date_of_birth).years


    def alot_button(self):
        self.active = True

        available_rooms = self.env['room.management'].search([
            ('state', 'in', ['partial', 'empty', 'cleaning']),
            ('number_of_bed', '>', 0),
        ], order='id asc')

        for room in available_rooms:

            if len(room.student_ids) < room.number_of_bed:
                self.name_id = room
                return
        raise ValidationError('No available rooms to allocate.')


    def action_vacate(self):
        self.active = False
        room = self.name_id
        room.bed_booked -= 1
        self.name_id = False
        if room.bed_booked == 0:
            room.state = 'empty'
            self.env['cleaning.service'].create({
                'name': room.id,
                'start_time': fields.Datetime.now(),
                'company_id': room.company_id.id
            })
            room.state = 'cleaning'
        elif room.bed_booked < room.number_of_bed:
            room.state = 'partial'
        else:
            room.state = 'full'


    def unlink(self):
        leave_requests = self.env['leave.request'].search([
            ('student_name_id', '=', self.id)
        ])
        leave_requests.unlink()
        if self.name_id:
            room = self.name_id
            room.bed_booked -= 1
            self.name_id = False
            if room.bed_booked == 0:
                room.state = 'empty'
            elif room.bed_booked < room.number_of_bed:
                room.state = 'partial'
            else:
                room.state = 'full'
        return super().unlink()


    def action_view_invoices(self):
        invoice_ids = self.env['account.move'].search([('student_id', '=', self.id)]).ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('id', 'in', invoice_ids)],
        }
        if len(invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': invoice_ids[0],
            })
        else:
            action.update({
                'view_mode': 'list,form',
            })
        return action


    def _compute_invoice_count(self):
        self.invoice_count = self.env['account.move'].search_count([('student_id', '=', self.id)])


    def generate_monthly_invoices(self):
        product_template = self.env.ref('hostel_management.hostel_product_rent_template')
        product = product_template.product_variant_id
        for student in self.search([('active', '=', True)]):
            if student.name_id and student.partner_id:
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': student.partner_id.id,
                    'invoice_date': fields.Date.today(),
                    'student_id': student.id,
                    'invoice_line_ids': [(0, 0, {
                        'product_id': product.id,
                        'quantity': 1,
                        'price_unit': student.monthly_amount,
                        'name': f'Rent for room {student.name_id.name}',
                    })]
                }
                invoice = self.env['account.move'].create(invoice_vals)
                invoice.action_post()


    @api.depends('invoice_ids.state', 'invoice_ids.payment_state')
    def _compute_invoice_status(self):
        invoices = self.invoice_ids.filtered(lambda inv: inv.state in ['draft', 'posted'])
        if any(inv.payment_state != 'paid' for inv in invoices):
            self.invoice_status = 'pending'
        else:
            self.invoice_status = 'done'


    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].create({
            'name': vals.get('name'),
            'email': vals.get('email'),
            'company_id': self.env.company.id,
        })
        vals['partner_id'] = partner.id
        email = vals.get('email')
        if email:
            existing_user = self.env['res.users'].search([('login', '=', email)], limit=1)
            if existing_user:
                vals['user_id'] = existing_user.id
            else:
                new_user = self.env['res.users'].create({
                    'name': vals.get('name'),
                    'login': email,
                    'email': email,
                    'partner_id': partner.id,
                    'company_id': self.env.company.id,
                })
                vals['user_id'] = new_user.id
        if not vals.get('student_id'):
            vals['student_id'] = self.env['ir.sequence'].next_by_code('student.information')
        return super().create(vals)


    def _compute_pending_amount(self):
        for student in self:

            student.pending_amount = sum(
                student.invoice_ids.filtered(lambda inv: inv.state in ['draft','posted']).mapped(
                    'amount_residual'))
