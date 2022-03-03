from odoo import _, api, fields, models, modules, tools
import logging

_logger = logging.getLogger(__name__)


class Mail_Channel_inherit(models.Model):
    _inherit = 'mail.channel'

    channel_current_stage = fields.Selection(
        [
            ('setting_1', 'Setting 3'),
            ('setting_2', 'Setting 3'),
            ('setting_3', 'Setting 3'),
        ]
    )

    def write(self, vals):
        if vals.get('channel_current_stage') and self.channel_type == 'livechat':
            new_vals = self.get_update_channel_data(vals.get('channel_current_stage'))
            vals.update(new_vals)
        call_super = super(Mail_Channel_inherit, self).write(vals)
        return call_super

    def get_update_channel_data(self, chat_stage):
        chatbot_selection_1 = self.env['ir.config_parameter'].sudo().get_param('p_qssot_chatbot.chatbot_selection_1')
        chatbot_selection_2 = self.env['ir.config_parameter'].sudo().get_param('p_qssot_chatbot.chatbot_selection_2')
        operator_partner_id = False
        if chat_stage == 'setting_1':
            if chatbot_selection_1 == 'chatbot':
                operator_partner_id = 7
            elif chatbot_selection_1 == 'agent':
                operator_partner_id = 3
        elif chat_stage == 'setting_2':
            if chatbot_selection_2 == 'chatbot':
                operator_partner_id = 7
            elif chatbot_selection_2 == 'agent':
                operator_partner_id = 3
        if operator_partner_id:
            channel_partner_to_add = [(6, 0, []), (4, operator_partner_id)]
            user_id = self.env.user.id
            if user_id:
                visitor_user = self.env['res.users'].browse(user_id)
                if visitor_user and visitor_user.active:  # valid session user (not public)
                    channel_partner_to_add.append((4, visitor_user.partner_id.id))
            self._broadcast([operator_partner_id])
            return {
                'channel_partner_ids': channel_partner_to_add,
                'livechat_active': True,
                'livechat_operator_id': operator_partner_id,
            }
        else:
            return {}
