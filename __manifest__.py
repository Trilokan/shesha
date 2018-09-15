# -*- coding: utf-8 -GPK*-

{
    "name": "Shesha",
    "version": "1.0",
    "author": "La Mars",
    "website": "http://",
    "category": "Naga Kanni",
    "sequence": 1,
    "summary": "Hospital Management System",
    "description": """
    
    Hospital Management System
    
    Patient Management
    Employee Management
    Purchase Management
    Pharmacy Management
    Assert Management
    Accounts Management
    
    """,
    "depends": ["base", "mail"],
    "data": [
        # Main Menu
        'menu/menu.xml',

        # Sequence
        'sequence/base_pack.xml',
        'sequence/account.xml',
        'sequence/product.xml',
        'sequence/stores.xml',

        # Data

            # Product
            'data/product/group.xml',
            'data/product/sub_group.xml',
            'data/product/uom.xml',
            'data/product/tax.xml',
            'data/product/category.xml',
            'data/product/location.xml',

            # Account
            'data/account/account.xml',

            # Base Pack
            'data/base_pack/base_pack.xml',

        # Views

            # Product
            'views/web_views/product/group.xml',
            'views/web_views/product/sub_group.xml',
            'views/web_views/product/uom.xml',
            'views/web_views/product/tax.xml',
            'views/web_views/product/category.xml',
            'views/web_views/product/product.xml',
            'views/web_views/product/location.xml',
            'views/web_views/product/warehouse.xml',

            # Stores
            'views/web_views/stores/stock_adjustment.xml',
            'views/web_views/stores/store_request.xml',
            'views/web_views/stores/store_issue.xml',
            'views/web_views/stores/store_return.xml',
            'views/web_views/stores/store_intake.xml',
            'views/web_views/stores/stock_move.xml',
            'views/web_views/stores/asserts_capitalisation.xml',

            # Asserts
            'views/web_views/asserts/asserts.xml',
            'views/web_views/asserts/service.xml',
            'views/web_views/asserts/reminder.xml',

            # Base Pack
            'views/web_views/base_pack/company.xml',
            'views/web_views/base_pack/users.xml',
            'views/web_views/person/person.xml',


        # Menu
        'menu/contact.xml',
        'menu/product.xml',
        'menu/stores.xml',
    ],
    "demo": [

    ],
    "qweb": [

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
