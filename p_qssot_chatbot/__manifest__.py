# -*- coding: utf-8 -*-
# Part of test. See LICENSE file for full copyright and licensing details.
{
    'name': "Chat Bot",
    'summary': "Chat Bot",
    'description': "Chat Bot",
    "version": "0.1",
    "category": "Other",
    'author': "Param Enterprice",
    'license': 'Other proprietary',
    # 'images': ['static/description/icon.png'],
    "depends": [
        'base','mail','im_livechat','website_livechat'
    ],
    'price': 20,
    'currency': 'USD',
    "data": [
        'views/res_config_view.xml'
    ],
    "application": False,
    'installable': True,
}
