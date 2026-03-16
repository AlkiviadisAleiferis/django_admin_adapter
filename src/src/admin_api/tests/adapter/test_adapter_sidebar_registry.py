import pytest
from django.contrib.admin import site as default_admin_site
from django_admin_adapter.adapter import (
    AdminAPIAdapter,
    AdminAPIAdapterError,
)
from backend.real_estate.models import Property, Project
from backend.common.models import Contact, Email
from admin_api.views import DummyExtraView


# ============================================================================
# SUCCESS CASES
# ============================================================================


# --- None/Empty sidebar_registry ---


def test_sidebar_registry_none():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        sidebar_registry=None,
    )
    assert adapter.sidebar_registry == []


def test_sidebar_registry_empty_list():
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        sidebar_registry=[],
    )
    assert adapter.sidebar_registry == []


# --- Valid View Entries ---


def test_sidebar_registry_valid_view_entry():
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "icon": "fa-regular fa-house",
            "view_name": "dummy_view",
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
        sidebar_registry=sidebar_registry,
    )
    assert len(adapter.sidebar_registry) == 1
    assert adapter.sidebar_registry[0]["type"] == "view"
    assert adapter.sidebar_registry[0]["label"] == "Dummy View"
    assert adapter.sidebar_registry[0]["icon"] == "fa-regular fa-house"
    assert adapter.sidebar_registry[0]["view_name"] == "dummy_view"
    assert adapter.sidebar_registry[0]["client_view_path"] == "client_dummy_view_path/"
    assert adapter.sidebar_registry[0]["view_class"] == DummyExtraView


# --- Valid Model Entries ---


def test_sidebar_registry_valid_model_entry():
    sidebar_registry = [
        {
            "type": "model",
            "label": "Properties",
            "icon": "fa-solid fa-building",
            "app_name": "real_estate",
            "model_name": "property",
        }
    ]
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        sidebar_registry=sidebar_registry,
    )
    assert len(adapter.sidebar_registry) == 1
    assert adapter.sidebar_registry[0]["type"] == "model"
    # Label is overridden by model's verbose_name_plural
    assert (
        adapter.sidebar_registry[0]["label"]
        == Property._meta.verbose_name_plural.capitalize()
    )
    assert adapter.sidebar_registry[0]["icon"] == "fa-solid fa-building"
    assert adapter.sidebar_registry[0]["app_name"] == "real_estate"
    assert adapter.sidebar_registry[0]["model_name"] == "property"
    assert adapter.sidebar_registry[0]["model"] == Property
    assert (
        adapter.sidebar_registry[0]["model_admin"]
        == default_admin_site._registry[Property]
    )


# --- Valid Dropdown Entries ---


def test_sidebar_registry_valid_dropdown_with_model_entries():
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Real Estate",
            "icon": "fa-solid fa-building",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Projects",
                    "icon": "fa-solid fa-building",
                    "app_name": "real_estate",
                    "model_name": "project",
                },
                {
                    "type": "model",
                    "label": "Properties",
                    "icon": "fa-regular fa-house",
                    "app_name": "real_estate",
                    "model_name": "property",
                },
            ],
        }
    ]
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        sidebar_registry=sidebar_registry,
    )
    assert len(adapter.sidebar_registry) == 1
    assert adapter.sidebar_registry[0]["type"] == "dropdown"
    assert adapter.sidebar_registry[0]["label"] == "Real Estate"
    assert adapter.sidebar_registry[0]["icon"] == "fa-solid fa-building"

    assert len(adapter.sidebar_registry[0]["dropdown_entries"]) == 2

    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["type"] == "model"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["label"] == "Projects"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][0]["icon"]
        == "fa-solid fa-building"
    )
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["app_name"] == "real_estate"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["model_name"] == "project"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][0]["model_admin"]
        == default_admin_site._registry[Project]
    )
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["model"] == Project

    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["type"] == "model"
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["label"] == "Properties"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][1]["icon"]
        == "fa-regular fa-house"
    )
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["app_name"] == "real_estate"
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["model_name"] == "property"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][1]["model_admin"]
        == default_admin_site._registry[Property]
    )
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["model"] == Property


def test_sidebar_registry_valid_dropdown_with_view_entries():
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Custom Views",
            "icon": "fa-solid fa-eye",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "icon": "fa-solid fa-eye",
                    "view_name": "dummy_view",
                    "client_view_path": "client_dummy_view_path/",
                },
            ],
        }
    ]
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
        sidebar_registry=sidebar_registry,
    )
    assert adapter.sidebar_registry[0]["type"] == "dropdown"
    assert adapter.sidebar_registry[0]["label"] == "Custom Views"
    assert adapter.sidebar_registry[0]["icon"] == "fa-solid fa-eye"

    assert len(adapter.sidebar_registry[0]["dropdown_entries"]) == 1

    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["type"] == "view"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["label"] == "Dummy View"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["icon"] == "fa-solid fa-eye"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["view_name"] == "dummy_view"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][0]["client_view_path"]
        == "client_dummy_view_path/"
    )
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][0]["view_class"] == DummyExtraView
    )


# --- Complex Valid Scenarios ---


def test_sidebar_registry_valid_dropdown_with_mixed_entries():
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Mixed",
            "icon": "fa-solid fa-eye",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Projects",
                    "icon": "fa-solid fa-building",
                    "app_name": "real_estate",
                    "model_name": "project",
                },
                {
                    "type": "view",
                    "label": "Dummy View",
                    "icon": "fa-solid fa-eye",
                    "view_name": "dummy_view",
                    "client_view_path": "client_dummy_view_path/",
                },
            ],
        },
        {
            "type": "model",
            "label": "Projects",
            "icon": "fa-solid fa-building",
            "app_name": "real_estate",
            "model_name": "project",
        },
        {
            "type": "view",
            "label": "Dummy View",
            "icon": "fa-solid fa-eye",
            "view_name": "dummy_view",
            "client_view_path": "client_dummy_view_path/",
        },
    ]
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
        sidebar_registry=sidebar_registry,
    )
    assert adapter.sidebar_registry[0]["type"] == "dropdown"
    assert adapter.sidebar_registry[0]["label"] == "Mixed"
    assert adapter.sidebar_registry[0]["icon"] == "fa-solid fa-eye"

    assert len(adapter.sidebar_registry[0]["dropdown_entries"]) == 2

    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["type"] == "model"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["label"] == "Projects"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][0]["icon"]
        == "fa-solid fa-building"
    )
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["app_name"] == "real_estate"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["model_name"] == "project"
    assert adapter.sidebar_registry[0]["dropdown_entries"][0]["model"] == Project
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][0]["model_admin"]
        == default_admin_site._registry[Project]
    )

    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["type"] == "view"
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["label"] == "Dummy View"
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["icon"] == "fa-solid fa-eye"
    assert adapter.sidebar_registry[0]["dropdown_entries"][1]["view_name"] == "dummy_view"
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][1]["client_view_path"]
        == "client_dummy_view_path/"
    )
    assert (
        adapter.sidebar_registry[0]["dropdown_entries"][1]["view_class"] == DummyExtraView
    )

    assert adapter.sidebar_registry[1]["type"] == "model"
    assert adapter.sidebar_registry[1]["label"] == "Projects"
    assert adapter.sidebar_registry[1]["icon"] == "fa-solid fa-building"
    assert adapter.sidebar_registry[1]["app_name"] == "real_estate"
    assert adapter.sidebar_registry[1]["model_name"] == "project"
    assert adapter.sidebar_registry[1]["model"] == Project
    assert (
        adapter.sidebar_registry[1]["model_admin"]
        == default_admin_site._registry[Project]
    )

    assert adapter.sidebar_registry[2]["type"] == "view"
    assert adapter.sidebar_registry[2]["label"] == "Dummy View"
    assert adapter.sidebar_registry[2]["icon"] == "fa-solid fa-eye"
    assert adapter.sidebar_registry[2]["view_name"] == "dummy_view"
    assert adapter.sidebar_registry[2]["client_view_path"] == "client_dummy_view_path/"
    assert adapter.sidebar_registry[2]["view_class"] == DummyExtraView


def test_sidebar_registry_from_urls_example():
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "client_view_path": "client_dummy_view_path/",
            "icon": "fa-regular fa-house",
            "view_name": "dummy_view",
        },
        {
            "type": "model",
            "label": "Properties",
            "app_name": "real_estate",
            "model_name": "property",
        },
        {
            "type": "model",
            "label": "Users",
            "app_name": "organization",
            "model_name": "user",
        },
        {
            "type": "dropdown",
            "label": "Real Estate",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Projects",
                    "icon": "fa-regular fa-house",
                    "app_name": "real_estate",
                    "model_name": "project",
                },
                {
                    "type": "model",
                    "label": "Contacts",
                    "icon": "fa-regular fa-address-book",
                    "app_name": "common",
                    "model_name": "contact",
                },
                {
                    "type": "model",
                    "label": "Emails",
                    "icon": "fa-solid fa-email",
                    "app_name": "common",
                    "model_name": "email",
                },
            ],
        },
    ]
    adapter = AdminAPIAdapter(
        admin_site=default_admin_site,
        extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
        sidebar_registry=sidebar_registry,
    )
    assert len(adapter.sidebar_registry) == 4
    assert adapter.sidebar_registry[3]["dropdown_entries"][0]["model"] == Project
    assert adapter.sidebar_registry[3]["dropdown_entries"][1]["model"] == Contact
    assert adapter.sidebar_registry[3]["dropdown_entries"][2]["model"] == Email


# ============================================================================
# ERROR CASES
# ============================================================================


# --- sidebar_registry data type Validation ---


@pytest.mark.parametrize("sidebar_registry", [123, 4.5, "notalist", {"a": 1}])
def test_sidebar_registry_not_list(sidebar_registry):
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry must be of type list"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


# --- sidebar entry data type Validation ---


@pytest.mark.parametrize("entry", [123, 4.5, "notadict", ["a", "b"]])
def test_sidebar_entry_not_dict(entry):
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entries must be of type dict"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=[entry],
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [entry],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entries must be of type dict"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


# --- "label" sidebar entry Validation ---


def test_sidebar_entry_missing_label():
    sidebar_registry = [
        {
            "type": "view",
            "view_name": "dummy_view",
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry label missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "view_name": "dummy_view",
                    "client_view_path": "client_dummy_view_path/",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry label missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("label", [123, 4.5, ["label"], {"label": "value"}])
def test_sidebar_entry_label_not_str(label):
    sidebar_registry = [
        {
            "type": "view",
            "label": label,
            "view_name": "dummy_view",
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry label must be of type str"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": label,
                    "view_name": "dummy_view",
                    "client_view_path": "client_dummy_view_path/",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry label must be of type str"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


# --- "icon" Validation ---


@pytest.mark.parametrize("icon", [123, 4.5, ["icon"], {"icon": "value"}])
def test_sidebar_entry_icon_not_str(icon):
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "icon": icon,
            "view_name": "dummy_view",
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry icon must be of type str"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "icon": icon,
                    "view_name": "dummy_view",
                    "client_view_path": "client_dummy_view_path/",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry icon must be of type str"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


# --- "type" Field Validation ---


def test_sidebar_entry_missing_type():
    sidebar_registry = [
        {
            "label": "Some Label",
        }
    ]
    with pytest.raises(AdminAPIAdapterError, match="sidebar_registry entry type missing"):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "label": "Some Label",
                }
            ],
        }
    ]
    with pytest.raises(AdminAPIAdapterError, match="sidebar_registry entry type missing"):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("invalid_type", [{"invalid"}, "models", "views", "dropdowns", 2])
def test_sidebar_entry_invalid_type(invalid_type):
    sidebar_registry = [
        {
            "type": invalid_type,
            "label": "Some Label",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match=f"sidebar_registry entry invalid type: '{invalid_type}'",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": invalid_type,
                    "label": "Some Label",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match=f"sidebar_registry entry invalid type: '{invalid_type}'",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


# --------------------------------------------------------
# --- "type" -> "view" sidebar entry Validation ---
# --------------------------------------------------------


def test_sidebar_view_entry_missing_view_name():
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry view entry view_name missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "client_view_path": "client_dummy_view_path/",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry view entry view_name missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("view_name", [123, 4.5, ["view"], {"view": "name"}])
def test_sidebar_view_entry_view_name_not_str(view_name):
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "view_name": view_name,
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry view_name must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "view_name": view_name,
                    "client_view_path": "client_dummy_view_path/",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry view_name must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_view_entry_view_name_not_in_views():
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "view_name": "non_existent_view",
            "client_view_path": "client_dummy_view_path/",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry view_name 'non_existent_view' not in provided views",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "view_name": "non_existent_view",
                    "client_view_path": "client_dummy_view_path/",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry view_name 'non_existent_view' not in provided views",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_view_entry_missing_client_view_path():
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "view_name": "dummy_view",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry 'dummy_view' client_view_path missing",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "view_name": "dummy_view",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry 'dummy_view' client_view_path missing",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("client_view_path", [123, 4.5, ["path"], {"path": "value"}])
def test_sidebar_view_entry_client_view_path_not_str(client_view_path):
    sidebar_registry = [
        {
            "type": "view",
            "label": "Dummy View",
            "view_name": "dummy_view",
            "client_view_path": client_view_path,
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry 'dummy_view' client_view_path must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "view",
                    "label": "Dummy View",
                    "view_name": "dummy_view",
                    "client_view_path": client_view_path,
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry view entry 'dummy_view' client_view_path must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            extra_views={"dummy_view": ("dummy_view/", DummyExtraView, None)},
            sidebar_registry=sidebar_registry,
        )


# --------------------------------------------------------
# --- "type" -> "model" sidebar entry Validation ---
# --------------------------------------------------------


def test_sidebar_model_entry_missing_app_name():
    sidebar_registry = [
        {
            "type": "model",
            "label": "Properties",
            "model_name": "property",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry model entry's app_name missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Properties",
                    "model_name": "property",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry model entry's app_name missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("app_name", [123, 4.5, ["app"], {"app": "name"}])
def test_sidebar_model_entry_app_name_not_str(app_name):
    sidebar_registry = [
        {
            "type": "model",
            "label": "Properties",
            "app_name": app_name,
            "model_name": "property",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry model entry's app_name must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Properties",
                    "app_name": app_name,
                    "model_name": "property",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry model entry's app_name must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_model_entry_missing_model_name():
    sidebar_registry = [
        {
            "type": "model",
            "label": "Properties",
            "app_name": "real_estate",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry model entry's model_name missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Properties",
                    "app_name": "real_estate",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry model entry's model_name missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("model_name", [123, 4.5, ["model"], {"model": "name"}])
def test_sidebar_model_entry_model_name_not_str(model_name):
    sidebar_registry = [
        {
            "type": "model",
            "label": "Properties",
            "app_name": "real_estate",
            "model_name": model_name,
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry model entry's model_name must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Properties",
                    "app_name": "real_estate",
                    "model_name": model_name,
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry model entry's model_name must be of type str",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_model_entry_non_existing_model():
    sidebar_registry = [
        {
            "type": "model",
            "label": "Fake Model",
            "app_name": "real_estate",
            "model_name": "nonexistentmodel",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="Non existing 'real_estate.nonexistentmodel' model entry",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Fake Model",
                    "app_name": "real_estate",
                    "model_name": "nonexistentmodel",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="Non existing 'real_estate.nonexistentmodel' model entry",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_model_entry_non_existing_app():
    sidebar_registry = [
        {
            "type": "model",
            "label": "Some Model",
            "app_name": "nonexistentapp",
            "model_name": "somemodel",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="Non existing 'nonexistentapp.somemodel' model entry"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Some Model",
                    "app_name": "nonexistentapp",
                    "model_name": "somemodel",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="Non existing 'nonexistentapp.somemodel' model entry"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_model_entry_model_not_registered_in_admin():
    sidebar_registry = [
        {
            "type": "model",
            "label": "Phone",
            "app_name": "common",
            "model_name": "phone",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="Non existing 'common.phone' model admin for model entry",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
    # and inside dropdown
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Dropdown example",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Phone",
                    "app_name": "common",
                    "model_name": "phone",
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="Non existing 'common.phone' model admin for model entry",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


# --------------------------------------------------------
# --- "type" -> "dropdown" Entry Validation ---
# --------------------------------------------------------


def test_sidebar_dropdown_entry_missing_dropdown_entries():
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Real Estate",
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry model entry's dropdown_entries missing",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


@pytest.mark.parametrize("dropdown_entries", [123, 4.5, "notalist", {"a": 1}])
def test_sidebar_dropdown_entry_dropdown_entries_not_list(dropdown_entries):
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Real Estate",
            "dropdown_entries": dropdown_entries,
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry dropdown entry's dropdown_entries must be of type list",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_dropdown_entry_label_missing():
    sidebar_registry = [
        {
            "type": "dropdown",
            "dropdown_entries": [
                {
                    "type": "dropdown",
                    "label": "Inner Dropdown",
                    "dropdown_entries": [],
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError, match="sidebar_registry entry label missing"
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )


def test_sidebar_dropdown_entry_nested_dropdown_not_allowed():
    sidebar_registry = [
        {
            "type": "dropdown",
            "label": "Outer Dropdown",
            "dropdown_entries": [
                {
                    "type": "dropdown",
                    "label": "Inner Dropdown",
                    "dropdown_entries": [],
                }
            ],
        }
    ]
    with pytest.raises(
        AdminAPIAdapterError,
        match="sidebar_registry dropdown does not support nested dropdowns",
    ):
        AdminAPIAdapter(
            admin_site=default_admin_site,
            sidebar_registry=sidebar_registry,
        )
