# -*- coding: utf-8 -*-
# Part of Ptest. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class Res_config_(models.TransientModel):
    _inherit = 'res.config.settings'

    chatbot_selection_1 = fields.Selection(
        [
            ('chatbot', 'Chatbot'),
            ('agent', 'agent')
        ],
        string="ChatBot Setting 1",
        config_parameter="p_qssot_chatbot.chatbot_selection_1"
    )
    chatbot_selection_2 = fields.Selection(
        [
            ('chatbot', 'Chatbot'),
            ('agent', 'agent')
        ],
        string="ChatBot Setting 2",
        config_parameter="p_qssot_chatbot.chatbot_selection_2"
    )
    chatbot_selection_3 = fields.Selection(
        [
            ('chatbot', 'Chatbot'),
            ('agent', 'agent')
        ],
        string="ChatBot Setting 3",
        config_parameter="p_qssot_chatbot.chatbot_selection_3"
    )
    chatbot_end_str_1 = fields.Char(
        "ChatBot End String",
        placeholder="ChatBot End String 1",
        config_parameter="p_qssot_chatbot.chatbot_end_str_1"
    )
    chatbot_end_str_2 = fields.Char(
        "ChatBot End String",
        placeholder="ChatBot End String 2",
        config_parameter="p_qssot_chatbot.chatbot_end_str_2"
    )
    chatbot_end_str_3 = fields.Char(
        "ChatBot End String",
        placeholder="ChatBot End String 3",
        config_parameter="p_qssot_chatbot.chatbot_end_str_3"
    )
    algorithm_1 = fields.Selection(
        [
            ('ntlk', 'NTLK')
        ]
    )
    algorithm_2 = fields.Selection(
        [
            ('ntlk', 'NTLK')
        ]
    )
    algorithm_3 = fields.Selection(
        [
            ('ntlk', 'NTLK')
        ]
    )

    def set_values(self):
        super(Res_config_, self).set_values()
        self.env['ir.config_parameter'].set_param("p_qssot_chatbot.chatbot_end_str_1", self.chatbot_end_str_1 or '')
        self.env['ir.config_parameter'].set_param("p_qssot_chatbot.chatbot_end_str_2", self.chatbot_end_str_2 or '')
        self.env['ir.config_parameter'].set_param("p_qssot_chatbot.chatbot_end_str_3", self.chatbot_end_str_3 or '')
