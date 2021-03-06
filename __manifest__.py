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
        # CSS
        'views/web_views/assert_backend.xml',

        # Main Menu
        'menu/menu.xml',

        # Sequence
        'sequence/base_pack.xml',
        'sequence/account.xml',
        'sequence/product.xml',
        'sequence/stores.xml',
        'sequence/purchase.xml',
        'sequence/invoice.xml',
        'sequence/asserts.xml',

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
            'data/account/journal.xml',

            # Base Pack
            'data/base_pack/base_pack.xml',

        # Views

            # Base Pack
            'views/web_views/base_pack/company.xml',
            'views/web_views/base_pack/users.xml',
            'views/web_views/base_pack/person.xml',
            'views/web_views/base_pack/employee.xml',
            'views/web_views/base_pack/patient.xml',

            # Account
            'views/web_views/account/account.xml',
            'views/web_views/account/year.xml',
            'views/web_views/account/period.xml',
            'views/web_views/account/journal_entries.xml',
            'views/web_views/account/journal_items.xml',
            'views/web_views/account/customer_payments.xml',
            'views/web_views/account/vendor_payments.xml',

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
            'views/web_views/stores/store_configuration.xml',

            # Batch
            'views/web_views/batch/dummy.xml',
            'views/web_views/batch/batch.xml',

            # Asserts
            'views/web_views/asserts/asserts_capitalisation.xml',
            'views/web_views/asserts/asserts.xml',
            'views/web_views/asserts/service.xml',
            'views/web_views/asserts/reminder.xml',

            # Hr
            'views/web_views/hr/hr_category.xml',
            'views/web_views/hr/hr_contact.xml',
            'views/web_views/hr/hr_department.xml',
            'views/web_views/hr/hr_designation.xml',
            'views/web_views/hr/hr_experience.xml',
            'views/web_views/hr/hr_qualification.xml',

            # Recruitment
            'views/web_views/recruitment/resume_bank.xml',
            'views/web_views/recruitment/vacancy_position.xml',
            'views/web_views/recruitment/interview_schedule.xml',
            'views/web_views/recruitment/appointment_order.xml',

            # Time Management
            'views/web_views/time_management/shift.xml',
            'views/web_views/time_management/time_configuration.xml',
            'views/web_views/time_management/monthly_attendance.xml',
            'views/web_views/time_management/monthly_attendance_wiz.xml',
            'views/web_views/time_management/week_schedule.xml',
            'views/web_views/time_management/attendance.xml',
            'views/web_views/time_management/time_sheet.xml',
            'views/web_views/time_management/time_sheet_application.xml',
            'views/web_views/time_management/shift_change.xml',
            'views/web_views/time_management/holiday_change.xml',
            'views/web_views/time_management/add_employee.xml',

            # Leave Management
            'views/web_views/leave_management/leave.xml',
            'views/web_views/leave_management/comp_off.xml',
            'views/web_views/leave_management/permission.xml',
            'views/web_views/leave_management/leave_account.xml',
            'views/web_views/leave_management/leave_level.xml',
            'views/web_views/leave_management/leave_type.xml',
            'views/web_views/leave_management/leave_configuration.xml',

            # Payroll
            'views/web_views/payroll/hr_pay_update_wiz.xml',
            'views/web_views/payroll/hr_pay.xml',
            'views/web_views/payroll/payroll_generation.xml',
            'views/web_views/payroll/payslip.xml',
            'views/web_views/payroll/salary_rule.xml',
            'views/web_views/payroll/salary_rule_slab.xml',
            'views/web_views/payroll/salary_structure.xml',

            # Purchase
            'views/web_views/purchase/indent.xml',
            'views/web_views/purchase/quotation.xml',
            'views/web_views/purchase/purchase_order.xml',
            'views/web_views/purchase/material_receipt.xml',
            'views/web_views/purchase/purchase_invoice.xml',
            'views/web_views/purchase/direct_material_receipt.xml',
            'views/web_views/purchase/purchase_return.xml',
            'views/web_views/purchase/material_return.xml',

            # Pharmacy
            'views/web_views/pharmacy/sale_order.xml',
            'views/web_views/pharmacy/material_delivery.xml',
            'views/web_views/pharmacy/sale_return.xml',
            'views/web_views/pharmacy/material_intake.xml',

            # Hospital
            'views/web_views/hospital/ambulance.xml',
            'views/web_views/hospital/ward.xml',
            'views/web_views/hospital/bed.xml',
            'views/web_views/hospital/bed_shifting.xml',
            'views/web_views/hospital/notes.xml',
            'views/web_views/hospital/reminders.xml',
            'views/web_views/hospital/notification.xml',
            'views/web_views/hospital/admission.xml',
            'views/web_views/hospital/discharge.xml',
            'views/web_views/hospital/doctor_availability.xml',

            # Schedule
            'views/web_views/schedule/opt.xml',
            'views/web_views/schedule/ot.xml',
            'views/web_views/schedule/others.xml',

            # Operation
            'views/web_views/operation/procedure.xml',

            # Patient
            'views/web_views/patient/symptoms.xml',
            'views/web_views/patient/diagnosis.xml',
            'views/web_views/patient/prescription.xml',
            'views/web_views/patient/ipt_treatment.xml',
            'views/web_views/patient/opt_treatment.xml',

        # Menu
        'menu/base_pack.xml',
        'menu/account.xml',
        'menu/hr.xml',
        # 'menu/contact.xml',
        'menu/product.xml',
        'menu/stores.xml',
        'menu/time_management.xml',
        'menu/leave_management.xml',
        'menu/payroll.xml',
        'menu/recruitment.xml',
        'menu/purchase.xml',
        # 'menu/pharmacy.xml',
        'menu/hospital.xml',
        'menu/asserts.xml',

    ],
    "demo": [

    ],
    "qweb": [

    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
