"""
In this module a mapping is retained between the groups and the permissions.
"""

Groups = (
    "Admin",
    "Management",
    "Sales",
)

# Permission objects follow the logic codename="{'view', 'change', 'add', 'delete'}_{modelname}"
ADMINS_PERMS = (
    # ----------------------------------------------------------------
    # systemic models
    #
    ("session", ("view", "change", "delete", "add")),
    ("contenttype", ("view",)),
    ("permission", ("view",)),
    ("logentry", ("view",)),
    ("country", ("view", "change", "delete", "add")),
    ("city", ("view", "change", "delete", "add")),
    ("documenttype", ("view", "change", "delete", "add")),
    ("propertycategory", ("view", "change", "delete", "add")),
    ("propertytype", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    ("group", ("view", "change", "delete", "add")),
    ("user", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # archive
    #
    ("image", ("view", "change", "delete", "add")),
    ("file", ("view", "change", "delete", "add")),
    ("documentimage", ("view", "change", "delete", "add")),
    ("documentfile", ("view", "change", "delete", "add")),
    ("document", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # real_estate
    #
    # agreement
    ("agreement", ("view", "change", "delete", "add")),
    ("agreementcommission", ("view", "change", "delete", "add")),
    ("agreementdocument", ("view", "change", "delete", "add")),
    ("agreementparty", ("view", "change", "delete", "add")),
    ("agreementrelatedcontact", ("view", "change", "delete", "add")),
    # project
    ("project", ("view", "change", "delete", "add")),
    ("projectaddress", ("view", "change", "delete", "add")),
    ("projectcontact", ("view", "change", "delete", "add")),
    ("projectdocument", ("view", "change", "delete", "add")),
    ("projectfile", ("view", "change", "delete", "add")),
    ("projectimage", ("view", "change", "delete", "add")),
    ("relatedproject", ("view", "change", "delete", "add")),
    # property
    ("property", ("view", "change", "delete", "add")),
    ("propertyassociatedcontact", ("view", "change", "delete", "add")),
    ("propertydocument", ("view", "change", "delete", "add")),
    ("propertyfile", ("view", "change", "delete", "add")),
    ("propertyimage", ("view", "change", "delete", "add")),
    ("propertyowner", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # common
    #
    ("phone", ("view", "change", "delete", "add")),
    ("email", ("view", "change", "delete", "add")),
    ("address", ("view", "change", "delete", "add")),
    # contact
    ("contact", ("view", "change", "delete", "add")),
    ("contactemployee", ("view", "change", "delete", "add")),
    ("contactaddress", ("view", "change", "delete", "add")),
    ("contactdocument", ("view", "change", "delete", "add")),
    ("contactemail", ("view", "change", "delete", "add")),
    ("contactfile", ("view", "change", "delete", "add")),
    ("contactimage", ("view", "change", "delete", "add")),
    ("contactphone", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # organization
    #
    # user
    ("user", ("view", "change", "add")),
    # organization
    ("organization", ("view", "change", "delete", "add")),
)

MANAGEMENT_PERMS = (
    # ----------------------------------------------------------------
    # systemic models
    #
    ("session", ("view",)),
    ("contenttype", ("view",)),
    ("permission", ("view",)),
    ("logentry", ("view",)),
    ("country", ("view",)),
    ("city", ("view",)),
    ("documenttype", ("view",)),
    ("propertycategory", ("view",)),
    ("propertytype", ("view",)),
    # ----------------------------------------------------------------
    ("group", ("view",)),
    # ----------------------------------------------------------------
    # archive
    #
    ("image", ("view", "change", "delete", "add")),
    ("file", ("view", "change", "delete", "add")),
    ("documentimage", ("view", "change", "delete", "add")),
    ("documentfile", ("view", "change", "delete", "add")),
    ("document", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # real_estate
    #
    ("agent", ("view", "change", "delete", "add")),
    ("agentdocument", ("view", "change", "delete", "add")),
    # agreement
    ("agreement", ("view", "change", "delete", "add")),
    ("agreementcommission", ("view", "change", "delete", "add")),
    ("agreementdocument", ("view", "change", "delete", "add")),
    ("agreementparty", ("view", "change", "delete", "add")),
    ("agreementrelatedcontact", ("view", "change", "delete", "add")),
    # project
    ("project", ("view", "change", "delete", "add")),
    ("projectaddress", ("view", "change", "delete", "add")),
    ("projectcontact", ("view", "change", "delete", "add")),
    ("projectdocument", ("view", "change", "delete", "add")),
    ("projectfile", ("view", "change", "delete", "add")),
    ("projectimage", ("view", "change", "delete", "add")),
    ("relatedproject", ("view", "change", "delete", "add")),
    # property
    ("property", ("view", "change", "delete", "add")),
    ("propertyassociatedcontact", ("view", "change", "delete", "add")),
    ("propertydocument", ("view", "change", "delete", "add")),
    ("propertyfile", ("view", "change", "delete", "add")),
    ("propertyimage", ("view", "change", "delete", "add")),
    ("propertyowner", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # common
    #
    ("phone", ("view", "change", "delete", "add")),
    ("email", ("view", "change", "delete", "add")),
    ("address", ("view", "change", "delete", "add")),
    # contact
    ("contact", ("view", "change", "delete", "add")),
    ("contactemployee", ("view", "change", "delete", "add")),
    ("contactaddress", ("view", "change", "delete", "add")),
    ("contactdocument", ("view", "change", "delete", "add")),
    ("contactemail", ("view", "change", "delete", "add")),
    ("contactfile", ("view", "change", "delete", "add")),
    ("contactimage", ("view", "change", "delete", "add")),
    ("contactphone", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # organization
    #
    # user
    ("user", ("view", "change", "add", "delete")),
    # organization
    ("organization", ("view", "change", "add")),
    # department
)

SALES_PERMS = (
    # ----------------------------------------------------------------
    # systemic models
    #
    ("session", ("view",)),
    ("contenttype", ("view",)),
    ("permission", ("view",)),
    ("country", ("view",)),
    ("city", ("view",)),
    ("documenttype", ("view",)),
    ("propertycategory", ("view",)),
    ("propertytype", ("view",)),
    ("label", ("view",)),
    ("brochuretemplate", ("view",)),
    # ----------------------------------------------------------------
    ("group", ("view",)),
    ("user", ("view",)),
    # ----------------------------------------------------------------
    # archive
    #
    ("image", ("view", "change", "delete", "add")),
    ("file", ("view", "change", "delete", "add")),
    ("documentimage", ("view", "change", "delete", "add")),
    ("documentfile", ("view", "change", "delete", "add")),
    ("document", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # real_estate
    #
    # agreement
    ("agreement", ("view", "change", "add")),
    ("agreementcommission", ("view", "change", "delete", "add")),
    ("agreementdocument", ("view", "change", "add")),
    ("agreementparty", ("view", "change", "delete", "add")),
    ("agreementrelatedcontact", ("view", "change", "delete", "add")),
    # project
    ("project", ("view", "change", "add")),
    ("projectaddress", ("view", "change", "delete", "add")),
    ("projectcontact", ("view", "change", "delete", "add")),
    ("projectdocument", ("view", "change", "delete", "add")),
    ("projectfile", ("view", "change", "delete", "add")),
    ("projectimage", ("view", "change", "delete", "add")),
    ("relatedproject", ("view", "change", "delete", "add")),
    # property
    ("property", ("view", "change", "add")),
    ("propertyassociatedcontact", ("view", "change", "delete", "add")),
    ("propertydocument", ("view", "change", "delete", "add")),
    ("propertyfile", ("view", "change", "delete", "add")),
    ("propertyimage", ("view", "change", "delete", "add")),
    ("propertyowner", ("view", "add")),
    # ----------------------------------------------------------------
    # common
    #
    ("phone", ("view", "change", "delete", "add")),
    ("email", ("view", "change", "delete", "add")),
    ("address", ("view", "change", "delete", "add")),
    # contact
    ("contact", ("view", "change", "add")),
    ("contactemployee", ("view", "change", "delete", "add")),
    ("contactaddress", ("view", "change", "delete", "add")),
    ("contactdocument", ("view", "change", "delete", "add")),
    ("contactemail", ("view", "change", "delete", "add")),
    ("contactfile", ("view", "change", "delete", "add")),
    ("contactimage", ("view", "change", "delete", "add")),
    ("contactphone", ("view", "change", "delete", "add")),
    # ----------------------------------------------------------------
    # organization
    #
    # user
    ("user", ("view", "change")),
    # organization
    ("organization", ("view",)),
)
