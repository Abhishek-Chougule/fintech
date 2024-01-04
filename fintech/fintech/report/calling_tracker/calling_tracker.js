

frappe.query_reports["Calling Tracker"] = {
    "filters":[

     {
                "fieldname": "report_option",
                "label": __("Report Option"),
                "fieldtype": "Select",
                "options": ["Last 30 days"],
//                    "default":"Last 30 days",
                "reqd" :1
            },
            {
                "fieldname": "call_status",
                "label": __("Call Status"),
                "fieldtype": "Select",
                "options": ["All","Answered","Busy","Failed","No Answer"],
                "default":"All",
                "reqd" :1
            },
            {
                    "fieldname": "clear_cache",
                    "label": __("Clear Cache"),
                    "fieldtype": "Button",
                    "onclick": function(report) {
                            frappe.ui.toolbar.clear_cache()
                    }
            }

    ]
}

