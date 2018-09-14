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
        
        # Data
        'data/product/group.xml',
        'data/product/sub_group.xml',
        'data/product/uom.xml',
        'data/product/tax.xml',
        'data/product/category.xml',
        # 'data/product/product.xml',
        'data/product/location.xml',
        
        # Sequence
        'sequence/product.xml',
        

        # Base Pack

        # Product
        'views/web_views/product/group.xml',
        'views/web_views/product/sub_group.xml',
        'views/web_views/product/uom.xml',
        'views/web_views/product/tax.xml',
        'views/web_views/product/category.xml',
        # 'views/web_views/product/product.xml',
        'views/web_views/product/location.xml',
        'views/web_views/product/warehouse.xml',

        # Menu
        'menu/product.xml',
    ],
    "demo": [

    ],
    "qweb": [

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
