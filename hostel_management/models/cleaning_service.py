from odoo import fields, models, api


class CleaningService(models.Model):
    _name = 'cleaning.service'
    _description = 'Cleaning Service'

    name = fields.Many2one('room.management', string='Room Number', required=True)
    start_time = fields.Datetime(required=True)
    state = fields.Selection([ ('new', 'NEW'),    ('assigned', 'ASSIGNED'), ('done', 'DONE')   ], default='new', string='Status')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,  default=lambda self: self.env.user.company_id)
    staff_id = fields.Many2one('res.users', string="Cleaning Staff", readonly=True)

    @api.model
    def create(self, vals):
        room_id = vals.get('name')
        if room_id:
            room_model = self.env['room.management']
            room = room_model.search([('id', '=', room_id)], limit=1)
            if room:
                room.previous_state = room.state
                room.state = 'cleaning'
        return super().create(vals)

    def action_assign(self):
        self.staff_id = self.env.uid
        self.state = 'assigned'

    def action_complete(self):
        self.state = 'done'
        room = self.name
        room.state = room.previous_state or 'empty'
        room.previous_state = False
        room._compute_bed_booked_and_state()