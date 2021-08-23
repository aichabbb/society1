# -*- coding: utf-8 -*-
{
    'name': "ia_jawaz",

    'summary': """ Ajouter l'onglet jawaz """,

    'description': """ Ce module permet d'ajouter l'onglet jawaz """,

    'author': "ItAdvisor Inc",
    'maintainer': 'FBK',
    'website': "http://www.itadvisor.ma",
    'category': 'Custom',
    'version': '12.0.1.0.2',
    'sequence': '1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'gestion_parc_automobile'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
