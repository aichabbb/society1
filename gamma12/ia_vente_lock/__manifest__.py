# -*- coding: utf-8 -*-
{
    'name': "ia_vente_lock",

    'summary': """ cacher la bouton "Créer une facture" """,

    'description': """ Ce module permet de cacher la bouton "Créer une facture" en sate bloquer """,

    'author': "ItAdvisor Inc",
    'website': "www.itadvisor.ma",
    'category': 'Uncategorized',
    'version': '12.0.1.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
