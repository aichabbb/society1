# -*- coding: utf-8 -*-
{
    'name': 'GammaRadTech Website',
    'version': '12.0.1.0.0',
    'summary': 'Website Theme For GammaRadTech',
    'category': 'Theme/Creative',
    'author': 'Rachdi Sami',
    'maintainer': 'ItAdvisor',
    'company': 'ItAdvisor',
    'website': 'https://www.itadvisor.ma',
    'depends': ['base', 'website', 'website_theme_install', 'sale'],
    'data': [
        'views/assets.xml',
        'views/layout.xml',
        # Snippets
        'views/snippets/banner_snippet.xml',
        'views/snippets/about_snippet.xml',
        'views/snippets/clients_snippet.xml',
        'views/snippets/features_snippet.xml',
        'views/snippets/work_left_snippet.xml',
        'views/snippets/work_right_snippet.xml',
        'views/snippets/testimonial_snippet.xml',
        'views/snippets/contact_snippet.xml',
        'views/snippets/footer_snippet.xml',
        'views/snippets/small_banner_snippet.xml',
        'views/snippets/generic_text_snippet.xml',
        # Snippets Bar
        'views/snippets/snippets_bar.xml',
        # Snippets Options
        'views/snippets/snippets_options.xml',
    ],
    'image': [
        'static/description/icon.png',
        'static/description/gammaradtech_website_screenshot.jpg',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
