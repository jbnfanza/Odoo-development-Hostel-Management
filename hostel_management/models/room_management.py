from odoo import fields, models, api


class RoomManagement(models.Model):
    _name = "room.management"
    _description = "room management"
    _inherit = ['mail.thread']

    name = fields.Char(string="Room Number", copy=False, readonly=True)
    room_type = fields.Selection(string="Room Type : ", selection=[("double", "Single"), ("single", "Connecting")], )
    number_of_bed = fields.Integer(string="Number of Bed", required="1")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    rent = fields.Float(string="Rent : ", required="1")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    facility_ids = fields.Many2many('facility')
    student_ids = fields.One2many('student.information', 'name_id', string="Students", readonly=True)
    total_rent = fields.Float(string='Total Rent', compute='_compute_total_rent', store=True)
    rent_product_id = fields.Many2one('product.template', string="Rent Product")
    pending_amount = fields.Float(string="Pending Amount", compute="_compute_pending_amount",currency_field='currency_id')
    previous_state = fields.Selection( selection=[('empty', 'EMPTY'), ('partial', 'PARTIAL'), ('full', 'FULL'), ('cleaning', 'CLEANING')])
    bed_booked = fields.Integer(compute='_compute_bed_booked_and_state', store=True)
    state = fields.Selection( selection=[('empty', 'EMPTY'), ('partial', 'PARTIAL'), ('full', 'FULL'), ('cleaning', 'CLEANING')], string='State', compute='_compute_bed_booked_and_state', store=True, default='empty')


    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('room.management')
        return super(RoomManagement, self).create(vals)



    @api.depends('rent', 'facility_ids')
    def _compute_total_rent(self):
        facility_charge = sum(self.facility_ids.mapped('charge'))
        self.total_rent = self.rent + facility_charge



    def action_monthly_invoice(self):
        rent_product = self.env['product.product'].search([('name', '=', 'Rental Product')], limit=1)
        invoices = self.env['account.move']
        for student in self.student_ids:
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': student.partner_id.id,
                'invoice_date': fields.Date.today(),
                'student_id': student.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': rent_product.id,
                    'quantity': 1,
                    'price_unit': float(self.total_rent),
                    'name': f'Rent for room {self.name}',
                })]
            })
            invoices += invoice
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoices.ids)],
        }



    def _compute_pending_amount(self):
        total_pending = 0.0
        for student in self.student_ids:
            invoices = self.env['account.move'].search([
                ('student_id', '=', student.id),
                ('state', 'in', ['draft', 'posted']),
                ('payment_state', '!=', 'paid')
            ])
            total_pending += sum(inv.amount_residual for inv in invoices)
        self.pending_amount = total_pending

    @api.depends('student_ids', 'number_of_bed')
    def _compute_bed_booked_and_state(self):
        for record in self:
            record.bed_booked = len(record.student_ids)
            if record.state == 'cleaning':
                continue
            if record.bed_booked == 0:
                record.state = 'empty'
            elif record.bed_booked < record.number_of_bed:
                record.state = 'partial'
            else:
                record.state = 'full'
