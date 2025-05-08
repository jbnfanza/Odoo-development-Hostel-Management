from odoo import fields, models, api


class RoomManagement(models.Model):
    _name = "room_management"
    _description = "room management"
    _inherit = ['mail.thread']

    name = fields.Char(string="Room Number", copy=False, readonly=True)
    room_type = fields.Selection(string="Room Type : ", selection=[("double", "Single"), ("single", "Connecting")], )
    number_of_bed = fields.Integer(string="Number of Bed", required="1")
    state = fields.Selection(selection=[('empty', 'EMPTY'), ('partial', 'PARTIAL'), ('full', 'FULL')], string='State',
                             default='empty')
    company_id = fields.Many2one('res.company', string='Company', required="1")
    rent = fields.Float(string="Rent : ", required="1")
    bed_booked = fields.Integer()
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    facility_ids = fields.Many2many('facility')
    student_ids = fields.One2many('student_information', 'name_id', string="Students")
    total_rent = fields.Float(string='Total Rent', compute='_compute_total_rent', store=True)
    rent_product_id = fields.Many2one('product.template', string="Rent Product")


    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('room_management')
        return super(RoomManagement, self).create(vals)


    @api.depends('rent', 'facility_ids')
    def _compute_total_rent(self):
        for record in self:
            facility_charge = sum(record.facility_ids.mapped('charge'))
            record.total_rent = record.rent + facility_charge


    def action_monthly_invoice(self):
        rent_product = self.env['product.product'].search([('name', '=', 'Rental Product')], limit=1)
        invoices = self.env['account.move']
        for student in self.student_ids:
            if not student.partner_id:
                continue
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': student.partner_id.id,
                'invoice_date': fields.Date.today(),
                'student_id': student.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': rent_product.id,
                    'quantity': 1,
                    'price_unit': float(self.total_rent or 0.0),
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
