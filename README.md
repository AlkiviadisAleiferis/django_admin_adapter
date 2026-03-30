![Alt image](https://github.com/AlkiviadisAleiferis/django_admin_adapter/blob/main/docs/source/_static/official_logo.svg)

## Welcome

See the [live demo here](https://django-admin-adapter-demo.com)!

user: demo \
pass: demo

Django Admin Adapter is a package aiming to convert almost instantly an Admin Site,
to a series of battle ready API endpoints, with minimum effort.

There is also a [React Front-End](https://github.com/AlkiviadisAleiferis/react_django_admin)
to base your entire admin projects on.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Front end](#front-end)
  - [OpenAPI 3 Specification](#openapi-3-specification)
  - [React Based Front-end implementation](#react-based-front-end-implementation)
- [Quickstart](#quickstart)
- [Authentication](#authentication)
- [History View](#history-view)
- [Extra Views (and overriding existing)](#extra-views-and-overriding-existing)
  - [Overview](#overview)
  - [Structure](#structure)
  - [Adding Custom Views](#adding-custom-views)
  - [Overriding Built-in Views](#overriding-built-in-views)
  - [Available View Names](#available-view-names)
  - [Throttle Classes Configuration](#throttle-classes-configuration)
  - [Complete Example](#complete-example)
  - [Accessing Adapter and AdminSite Context](#accessing-adapter-and-adminsite-context)
  - [Authentication and Permissions](#authentication-and-permissions)
  - [Validation](#validation)
  - [URL Patterns](#url-patterns)
- [Sidebar Registry](#sidebar-registry)
  - [Overview](#overview-1)
  - [Basic Structure](#basic-structure)
  - [Entry Types](#entry-types)
    - [Model Entry](#model-entry)
    - [View Entry](#view-entry)
    - [Dropdown Entry](#dropdown-entry)
    - [Complete Example](#complete-example-1)
    - [Validation](#validation-1)
- [Actions](#actions)
  - [Overview](#overview-2)
  - [Available Endpoints](#available-endpoints)
  - [Request Format](#request-format)
  - [Response Format](#response-format)
  - [Built-in Actions](#built-in-actions)
  - [Creating Custom Actions](#creating-custom-actions)
  - [Error Handling](#error-handling-1)
  - [Complete Workflow Example](#complete-workflow-example)
- [List Filters](#list-filters)
  - [Overview](#overview-3)
  - [InputFilter](#inputfilter)
  - [AutocompleteFilter](#autocompletefilter)
  - [Building Input Filters](#building-input-filters)
  - [Range Filters](#range-filters)
  - [Complete Examples](#complete-examples)
  - [Filter Data from the API](#filter-data-from-the-api)
  - [Using Filters in API Requests](#using-filters-in-api-requests)
- [Throttling](#throttling)
  - [Default Throttle Classes](#default-throttle-classes)
  - [Configuring Rate Limits](#configuring-rate-limits)
  - [Customizing Throttle Classes](#customizing-throttle-classes)
  - [Per-View Throttle Classes](#per-view-throttle-classes)
  - [Complete Example](#complete-example-2)
  - [Disabling Throttling](#disabling-throttling)
  - [Validation](#validation-2)
- [Customizing Object/List Serializers](#customizing-objectlist-serializers)
  - [Default Serializer Classes](#default-serializer-classes)
  - [Overriding Serializer Classes](#overriding-serializer-classes)
- [Base Permission Class](#base-permission-class)
  - [Overview](#overview-4)
  - [Default Permission Class](#default-permission-class)
  - [Customizing the Permission Class](#customizing-the-permission-class)
  - [Complete Examples](#complete-examples-1)
  - [Important Notes](#important-notes)
- [Providing Extra Data](#providing-extra-data)
  - [Overview](#overview-5)
  - [Available Extra Data Methods](#available-extra-data-methods)
    - [From ModelAdmin Classes](#from-modeladmin-classes)
    - [From AdminAPIAdapter Class](#from-adminapiadapter-class)
  - [Error Handling](#error-handling)
- [Development and testing](#development-and-testing)
  - [Testing locally](#testing-locally)
  - [Future development](#future-development)
  - [Helping](#helping)

## Description

**Django Admin Adapter is a project aiming at converting, with minimum effort, an existing (or new) Django admin project, to a series of battle ready API endpoints.**

Imagine having the versatillity and rapid development capabilities of the Django Admin framework,
but not the slow template response cycle.

Here is where django admin adapter comes in place.

Create Django Admin projects and expose all the API endpoints of the project instantly,
decoupling the front end, and decreasing drastically the response times.
It needs almost no customization, and works out of the box
with the provided `django.contrib.admin.sites.AdminSite` class instance
( by default the `django.contrib.admin.sites.site` ).

Uses [Django Rest Framework](https://www.django-rest-framework.org/)
and [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/),
although the authentication system can be overriden and **is not a hard dependency**.

> [!IMPORTANT]
> If the endpoints are consumed by a dettached front-end \
> e.g. React (see [React Django Admin](https://github.com/AlkiviadisAleiferis/react_django_admin/) client) \
> then proper CORS package (e.g. [django-cors-headers](https://pypi.org/project/django-cors-headers/)) must be used, \
> with proper `CORS_ALLOWED_ORIGINS` and `ALLOWED_HOSTS` settings

> [!IMPORTANT]
> The object change and add views in order to maintain most of the django admin \
> functionallity, use multipart data, so make sure the `rest_framework.parsers.MultiPartParser` is used \
> in `REST_FRAMEWORK` settings

## Installation

Install using pip:

```bash
pip install django_admin_adapter
```

## Front end

### OpenAPI 3 Specification

An OpenAPI 3 specification is provided in `adapter_openapi3.yaml` in the base directory of the repository.
Browse the [Swagger](https://alkiviadisaleiferis.github.io/django_admin_adapter_swagger/#/) API freely.

### React Based Front-end implementation

There is a [React](https://github.com/AlkiviadisAleiferis/react_django_admin) project available for Admin API adapter projects.
Instructions are provided there for using the app.

## Quickstart

Inside your project's base `urls.py`:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin

admin_adapter = AdminAPIAdapter(
    admin.site,
    sidebar_registry = [
        {
            "type": "model",
            "label": "Users",
            "icon": "user-icon",
            "app_name": "auth",
            "model_name": "user",
        },
        {
            "type": "view",
            "label": "Dashboard",
            "icon": "dashboard-icon",
            "view_name": "custom_dashboard",
            "client_view_path": "/dashboard",
        },
        {
            "type": "dropdown",
            "label": "Settings",
            "icon": "settings-icon",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Groups",
                    "app_name": "auth",
                    "model_name": "group",
                },
            ],
        },
    ],
)

urlpatterns = [
    path("api/", include(admin_adapter.get_urls())),
]
```

Congrats! Now the endpoints needed to interact with the admin panel
are available.

See the [OpenAPI specification](https://alkiviadisaleiferis.github.io/admin_api_adapter_swagger/#/) to learn more about the instantly exposed endpoints.

Also customization and additions as seen later is possible.

## Authentication

> [!IMPORTANT]
> The Simple JWT is not a hard dependency, and can be overriden.
> If not, the adapter will raise an error at instantiation,
> in case the `rest_framework_simplejwt` is not installed.

> [!IMPORTANT]
> To control the throttling to the authentication views
> use the `authentication_throttle_class` argument at initialization.

> [!NOTE]
> For best compatibility use a subclass of `AbstractBaseUser`
> for your user model.

The exposed endpoints form the adapter are using the [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
package's token authentication system.

You do not need to add the `DEFAULT_AUTHENTICATION_CLASSES` to your project's settings.
For each View the `authentication_classes` are set automatically
when retrieving the adapter's urls.

Any settings provided for the JWT from `django.conf.settings` is used.

You can customize the tokens' lifetime through the settings of your project `ACCESS_TOKEN_LIFETIME` , `REFRESH_TOKEN_LIFETIME`

In case you want to override the `TokenObtainPairView` and
`TokenRefreshView` authentication views
you should pass the below arguments when instantiating the adapter:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin

admin_adapter = AdminAPIAdapter(
    admin.site,
    extra_views={
        "token_obtain_pair": (
            "token/", # or your own path
            CustomAdminTokenObtainPairView,
            None, # or your throttle classes [AnonRateThrottle, UserRateThrottle]
        ),
        "token_refresh": (
            "token/refresh/", # or your own path
            CustomAdminTokenRefreshView,
            None, # or your throttle classes [AnonRateThrottle, UserRateThrottle]
        ),
    },
)
```

that way the authentication views are changed to your preference.
Also this way the `CustomTokenObtainPairSerializer` of the Tokens returned can be overriden.


> [!NOTE]
> The default token obtain pair serializer has been changed to
> provide in the token 2 new fields, the `username` and the `identifier` fields.
> The first is the username field value (`USERNAME_FIELD` field)
> and the latter is the string representation of the user object.
> If you want to change the obtain pair serializer you should pass
> the `token_obtain_pair_serializer` argument to the constructor
> **as kwarg** with the value of your serializer class.


> **IN CASE YOU NEED TO CHANGE THE TOTAL AUTHENTICATION SYSTEM:**
> 1. At Adapter instantiation, pass `authentication_views_names` argument to the constructor
> as kwarg with the tuple of your auth views names.
> 2. At Adapter instantiation, pass the `authentication_class` argument to the constructor.
> 3. Make sure the two authentication views are overriden or deleted from the VIEWMAP of the adapter.
> 4. If `token_obtain_pair_serializer` is used, make sure you provide yours or else an error will be raised at instantiation.


## History View

The history view is exposed by default, but an option to restrict
the access to the history page per model and object is provided.

To control the access to the history view per model and object,
the `has_history_permission` method of the `ModelAdmin` class is used.

Create the following method on your model admin to control behavior:

```python
def has_history_permission(self, request, obj=None):
    ...
    return your_evaluated_boolean
```

If no method is provided, the history view is accessible to all
authenticated and permitted users.

## Extra Views (and overriding existing)

The `extra_views` parameter allows you to add custom API views to your admin adapter
or override the default built-in views. This provides flexibility to extend the adapter's
functionality with your own endpoints while maintaining consistent authentication,
permissions, and throttling behavior.

> [!IMPORTANT]
> If your custom view class does not define `permission_classes`, but
> ingerits from `APIView`, the `permission_classes` are set as the `settings.DEFAULT_PERMISSION_CLASSES`
> of the Django Rest Framework, which by default is `'rest_framework.permissions.AllowAny'`.
> The base permission of the adapter will be appended on those permissions.

> [!WARNING]
> The Views provided from the `get_urls` of the `ModelAdmin` are not added to the adapter's urls.
> If you want to add them, you should add them manually to the `extra_views` parameter.

### Overview

The `extra_views` parameter accepts a dictionary where:

- **Key**: A unique view name (string)
- **Value**: A tuple containing three elements:
  1. URL path (string)
  2. View class (subclass of `rest_framework.views.APIView`)
  3. Throttle classes list (list/tuple of two throttle classes, or `None`)

### Structure

```python
extra_views = {
    "view_name": (
        "path/to/view/<str:and_a_parameter>/",           # URL path
        CustomAPIView,              # View class
        [AnonThrottle, UserThrottle] # Throttle classes or None
    ),
}
```

### Adding Custom Views

You can add completely new endpoints to your admin API:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from rest_framework.views import APIView
from rest_framework.response import Response

class DashboardStatsView(APIView):
    def get(self, request):
        # Your custom logic here
        stats = {
            "total_users": 100,
            "active_sessions": 25,
        }
        return Response(stats)

admin_adapter = AdminAPIAdapter(
    admin.site,
    extra_views={
        "dashboard_stats": (
            "dashboard/stats/",
            DashboardStatsView,
            None,  # Use default throttle classes
        ),
    },
)
```

The new endpoint will be available at: `/api/dashboard/stats/`

### Overriding Built-in Views

You can override any of the adapter's default views by using the same view name:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from django_admin_adapter.views import AdminBaseInfoAPIView

class CustomBaseInfoView(AdminBaseInfoAPIView):
    def get_extra_data(self, request):
        # Add custom data to base_info response
        return {
            "company_name": "My Company",
            "version": "2.0.0",
        }

admin_adapter = AdminAPIAdapter(
    admin.site,
    extra_views={
        "base_info": (
            "base_info/",  # Keep the same path
            CustomBaseInfoView,
            None,
        ),
    },
)
```

### Available View Names

The following view names can be overridden:

**Authentication:**
- `password_change`
- `token_obtain_pair`
- `token_refresh`

**Autocomplete:**
- `filter_autocomplete`
- `filter_autocomplete_retrieve_label`
- `field_autocomplete`

**Base Information:**
- `base_info`

**List Operations:**
- `admin_list_create`
- `admin_list_info`
- `admin_list_action_preview`
- `admin_list_action_execute`

**Object Operations:**
- `admin_object_view`
- `admin_object_add`
- `admin_object_edit`
- `admin_object_delete_confirm`
- `admin_object_history`
- `admin_object`

### Throttle Classes Configuration

Each view in `extra_views` can have custom throttle classes:

**Using Default Throttles:**

```python
extra_views={
    "my_view": (
        "my-view/",
        MyView,
        None,  # Uses adapter's default throttle classes
    ),
}
```

**Custom Throttles:**

```python
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class MyViewAnonThrottle(AnonRateThrottle):
    rate = '10/hour'

class MyViewUserThrottle(UserRateThrottle):
    rate = '100/hour'

extra_views={
    "my_view": (
        "my-view/",
        MyView,
        [MyViewAnonThrottle, MyViewUserThrottle],  # Must be exactly 2 classes
    ),
}
```

The throttle classes list must contain exactly two classes:
1. **First class**: Applied to anonymous (unauthenticated) requests
2. **Second class**: Applied to authenticated user requests

### Complete Example

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_admin_adapter.views import AdminTokenObtainPairView

# Custom view with custom logic
class AnalyticsView(APIView):
    def get(self, request):
        return Response({"analytics": "data"})

# Custom throttles for analytics
class AnalyticsAnonThrottle(AnonRateThrottle):
    rate = '5/hour'

class AnalyticsUserThrottle(UserRateThrottle):
    rate = '50/hour'

# Override authentication view
class CustomTokenObtainView(AdminTokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Add custom logging or validation
        response = super().post(request, *args, **kwargs)
        # Custom post-processing
        return response

admin_adapter = AdminAPIAdapter(
    admin.site,
    extra_views={
        # New custom view
        "analytics": (
            "analytics/",
            AnalyticsView,
            [AnalyticsAnonThrottle, AnalyticsUserThrottle],
        ),
        "token_obtain_pair": (
            "token/",
            CustomTokenObtainView,
            None,  # Use default throttles
        ),
    },
)
```

### Accessing Adapter and AdminSite Context

Views defined in `extra_views` automatically receive access to the adapter context
through class attributes:

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class MyCustomView(APIView):
    # These attributes are automatically set by the adapter
    # _admin_site: The Django admin site instance
    # _adapter_instance: The AdminAPIAdapter instance
    # _admin_view_name: The view name string

    def get(self, request):
        # Access the admin site
        admin_site = self._admin_site

        # Access registered models
        registered_models = admin_site._registry.keys()

        # Access adapter instance
        adapter = self._adapter_instance

        return Response({
            "view_name": self._admin_view_name,
            "models_count": len(registered_models),
        })
```

### Authentication and Permissions

By default, all views except authentication views (`token_obtain_pair`, `token_refresh`)
automatically receive:

- **Authentication**: JWT authentication (or custom if specified)
- **Permissions**: `AdminSiteBasePermission` (result of your `AdminSite`'s `has_permission` method)

> [!IMPORTANT]
> If your custom view class already defines `permission_classes`, the adapter will
> append `AdminSiteBasePermission` to the existing list.

### Validation

The adapter validates `extra_views` during initialization and will raise
`AdminAPIAdapterError` if:

- `extra_views` is not a dictionary
- View data is not a tuple of exactly 3 elements
- URL path is not a string
- View class is not a subclass of `rest_framework.views.APIView`
- Throttle classes (if provided) is not a list or tuple
- Throttle classes list does not contain exactly 2 classes
- Any throttle class is not a subclass of `rest_framework.throttling.BaseThrottle`

### URL Patterns

All views defined in `extra_views` are registered with Django's URL patterns
when you call `adapter.get_urls()`. The full URL will be:

```
<your_base_path>/<view_path>
```

For example:

```python
urlpatterns = [
    path("api/", include(admin_adapter.get_urls())),
]
```

A view with path `"dashboard/"` will be accessible at: `/api/dashboard/`

## Sidebar Registry

The `sidebar_registry` parameter allows you to customize the navigation sidebar
structure of your admin API interface. This is particularly useful when you want
to organize your admin models and custom views in a specific way, different from
the default Django admin organization.

### Overview

The sidebar registry is a list of dictionaries, where each dictionary represents
a sidebar entry. There are three types of entries:

- **model**: Links to a Django model admin
- **view**: Links to a custom API view
- **dropdown**: A collapsible menu containing nested model or view entries

### Basic Structure

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin

sidebar_registry = [
    {
        "type": "model",
        "label": "Users",
        "icon": "user-icon",
        "app_name": "auth",
        "model_name": "user",
    },
    {
        "type": "view",
        "label": "Dashboard",
        "icon": "dashboard-icon",
        "view_name": "custom_dashboard",
        "client_view_path": "/dashboard",
    },
    {
        "type": "dropdown",
        "label": "Settings",
        "icon": "settings-icon",
        "dropdown_entries": [
            {
                "type": "model",
                "label": "Groups",
                "app_name": "auth",
                "model_name": "group",
            },
        ],
    },
]

admin_adapter = AdminAPIAdapter(
    admin.site,
    sidebar_registry=sidebar_registry,
)
```

### Entry Types

#### Model Entry

A model entry links to a registered Django model admin.

**Required fields:**

- `type`: Must be `"model"`
- `label`: Display name for the sidebar entry (string)
- `app_name`: Django app label (e.g., `Model._meta.app_label`)
- `model_name`: Model name (e.g., `Model._meta.model_name`)

**Optional fields:**

- `icon`: Icon identifier (string)

```python
{
    "type": "model",
    "label": "Blog Posts",
    "icon": "document",
    "app_name": "blog",
    "model_name": "post",
}
```

**Note:** The model must be registered with the admin site, otherwise a validation error will be raised.

#### View Entry

A view entry links to a custom API view defined in `extra_views`.

**Required fields:**

- `type`: Must be `"view"`
- `label`: Display name for the sidebar entry (string)
- `view_name`: Name of the view as defined in `extra_views` (string)
- `client_view_path`: Frontend route path for the view (string)

**Optional fields:**

- `icon`: Icon identifier (string)

```python
{
    "type": "view",
    "label": "Analytics",
    "icon": "chart",
    "view_name": "analytics_view",
    "client_view_path": "/analytics",
}
```

**Note:** The `view_name` must exist in the adapter's `extra_views` mapping.

#### Dropdown Entry

A dropdown entry creates a collapsible menu containing nested entries.

**Required fields:**

- `type`: Must be `"dropdown"`
- `label`: Display name for the dropdown (string)
- `dropdown_entries`: List of nested model or view entries

**Optional fields:**

- `icon`: Icon identifier (string)

```python
{
    "type": "dropdown",
    "label": "User Management",
    "icon": "users",
    "dropdown_entries": [
        {
            "type": "model",
            "label": "Users",
            "app_name": "auth",
            "model_name": "user",
        },
        {
            "type": "model",
            "label": "Groups",
            "app_name": "auth",
            "model_name": "group",
        },
    ],
}
```

**Note:** Nested dropdowns are not supported. Dropdown entries can only contain model or view types.

#### Complete Example

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from myapp.views import DashboardView, ReportsView

admin_adapter = AdminAPIAdapter(
    admin.site,
    sidebar_registry=[
        {
            "type": "view",
            "label": "Dashboard",
            "icon": "home",
            "view_name": "dashboard",
            "client_view_path": "/dashboard",
        },
        {
            "type": "dropdown",
            "label": "Content",
            "icon": "folder",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Articles",
                    "icon": "document",
                    "app_name": "blog",
                    "model_name": "article",
                },
                {
                    "type": "model",
                    "label": "Categories",
                    "icon": "tag",
                    "app_name": "blog",
                    "model_name": "category",
                },
            ],
        },
        {
            "type": "dropdown",
            "label": "User Management",
            "icon": "users",
            "dropdown_entries": [
                {
                    "type": "model",
                    "label": "Users",
                    "app_name": "auth",
                    "model_name": "user",
                },
                {
                    "type": "model",
                    "label": "Groups",
                    "app_name": "auth",
                    "model_name": "group",
                },
            ],
        },
        {
            "type": "view",
            "label": "Reports",
            "icon": "chart",
            "view_name": "reports",
            "client_view_path": "/reports",
        },
    ],
    extra_views={
        "dashboard": (
            "dashboard/",
            DashboardView,
            None,
        ),
        "reports": (
            "reports/",
            ReportsView,
            None,
        ),
    },
)
```

#### Validation

The adapter validates all sidebar entries during initialization and will raise
`AdminAPIAdapterError` if:

- Entry type is not one of: `"model"`, `"view"`, or `"dropdown"`
- Required fields are missing
- Field types are incorrect (e.g., non-string label)
- Model is not registered with the admin site
- View name is not defined in `extra_views`
- Nested dropdowns are attempted
- Model does not exist in Django apps

If `sidebar_registry` is `None` (default), an empty sidebar will be used.

## Actions

The Django Admin Adapter provides full support for Django admin actions
through two dedicated API endpoints.
Actions allow you to perform bulk operations on selected objects in the admin interface.

> [!IMPORTANT]
> All actions now must return a Django Rest Framework `Response` object
> and must accept a `confirm` parameter as the last argument, which
> differentiates flow between preview and execution.

### Overview

Actions in Django Admin are functions that can be performed on multiple selected objects at once.
The adapter exposes these actions through a two-step process:

1. **Preview** - Shows what will happen when the action is executed
2. **Execute** - Actually performs the action on the selected objects

This two-step approach ensures users can review the impact of an action before confirming it, preventing accidental bulk operations.

> [!NOTE]
> The preview combined with a proper fornt end client design
> and custom views endpoints, can be utilized for action
> logical multistep validation.

### Available Endpoints

#### Preview Action Endpoint

**URL Pattern:** `/api/<app_name>/<model_name>/action/<action_name>/preview/`

**Method:** `POST`

**View:** `AdminListActionPreviewAPIView`

**Purpose:** Previews what will happen when an action is executed without actually performing it.

#### Execute Action Endpoint

**URL Pattern:** `/api/<app_name>/<model_name>/action/<action_name>/execute/`

**Method:** `POST`

**View:** `AdminListActionExecuteAPIView`

**Purpose:** Executes the action on the selected objects.

### Request Format

Both preview and execute endpoints expect the same POST data format:

```json
{
  "select_across": 0,
  "selected_objects": [1, 2, 3, 4, 5]
}
```

> [!NOTE]
> Of course any other key, value pair can be provided to enhance the action procedure.
> Since the request is passed to the `ModelAdmin` action, the `request.data`
> can be accessed inside the action preview/execution block.

**Parameters:**

- **`select_across`** (integer):
  - `0` - Only selected objects (specified in `selected_objects`)
  - `1` - All objects matching the current filter (ignores `selected_objects`)

- **`selected_objects`** (array):
  - List of primary keys of the selected objects
  - Required when `select_across` is `0`
  - Ignored when `select_across` is `1`

### Response Format

#### Preview Response

The preview endpoint returns information about what will happen when the action is executed:

```json
{
  "name": "Action Name",
  "description": "Description of the action",
  // ... additional action-specific data
}
```

For the built-in `delete_selected` action:

```json
{
  "name": "Delete selected objects",
  "description": "Delete selected objects",
  "deletable_objects": ["Object 1", "Object 2", ["Related Object 1", "Related Object 2"]],
  "model_count": {
    "articles": "5",
    "comments": "12"
  },
  "perms_needed": [],
  "protected": []
}
```

**Fields:**

- **`name`**: Display name of the action
- **`description`**: Description of what the action does
- **`deletable_objects`**: Nested list of objects that will be deleted (for delete action)
- **`model_count`**: Dictionary mapping model names to count of objects affected
- **`perms_needed`**: List of required permissions that the user lacks
- **`protected`**: List of protected objects that cannot be deleted

#### Execute Response

The execute endpoint returns a success message after performing the action:

```json
{
  "messages": ["Successfully deleted 5 Articles."]
}
```

### Built-in Actions

#### Delete Selected

The adapter includes a built-in implementation of Django's `delete_selected` action.

**Preview Example:**

```bash
POST /api/blog/article/action/delete_selected/preview/
Content-Type: application/json

{
  "select_across": 0,
  "selected_objects": [1, 2, 3]
}
```

**Preview Response:**

```json
{
  "name": "Delete selected objects",
  "description": "Delete selected objects",
  "deletable_objects": [
    "Article: My First Post",
    "Article: Second Post",
    "Article: Third Post",
    [
      "Comment: Great article!",
      "Comment: Thanks for sharing"
    ]
  ],
  "model_count": {
    "articles": "3",
    "comments": "2"
  },
  "perms_needed": [],
  "protected": []
}
```

**Execute Example:**

```bash
POST /api/blog/article/action/delete_selected/execute/
Content-Type: application/json

{
  "select_across": 0,
  "selected_objects": [1, 2, 3]
}
```

**Execute Response:**

```json
{
  "messages": ["Successfully deleted 3 Articles."]
}
```

### Creating Custom Actions

To create custom actions that work with the adapter, you must follow a specific signature:

```python
from django.contrib import admin
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    actions = ['publish_articles', 'archive_articles']

    def publish_articles(self, request, queryset, confirm=False):
        """
        Custom action to publish selected articles.

        Args:
            request: The HTTP request object
            queryset: QuerySet of selected objects
            confirm: Boolean indicating preview (False) or execute (True)

        Returns:
            Response object with appropriate data
        """
        if not confirm:
            # Preview mode - return information about what will happen
            count = queryset.count()
            unpublished = queryset.filter(status='draft').count()

            return Response(
                data={
                    "name": "Publish Articles",
                    "description": f"Publish {unpublished} draft articles",
                    "total_selected": count,
                    "will_be_published": unpublished,
                    "already_published": count - unpublished,
                },
                status=status.HTTP_200_OK,
            )

        # Execute mode - perform the actual action
        updated = queryset.filter(status='draft').update(
            status='published',
            published_at=timezone.now()
        )

        return Response(
            data={
                "messages": [f"Successfully published {updated} articles."]
            },
            status=status.HTTP_200_OK,
        )

    publish_articles.short_description = "Publish selected articles"

    def archive_articles(self, request, queryset, confirm=False):
        """Archive selected articles."""
        if not confirm:
            return Response(
                data={
                    "name": "Archive Articles",
                    "description": "Move selected articles to archive",
                    "count": queryset.count(),
                    "warning": "Archived articles will not be visible to users",
                },
                status=status.HTTP_200_OK,
            )

        queryset.update(status='archived', archived_at=timezone.now())

        return Response(
            data={
                "messages": [f"Successfully archived {queryset.count()} articles."]
            },
            status=status.HTTP_200_OK,
        )

    archive_articles.short_description = "Archive selected articles"

admin.site.register(Article, ArticleAdmin)
```

> [!IMPORTANT]
> - All actions **must** accept a `confirm` parameter as the last argument
> - All actions **must** return a `rest_framework.response.Response` object
> - Preview mode (`confirm=False`) should return descriptive data without modifying objects
> - Execute mode (`confirm=True`) should perform the actual operation and return success messages

### Error Handling

The adapter handles various error conditions:

**No objects selected:**

```json
{
  "messages": ["No objects were selected."]
}
```
**Status:** `400 Bad Request`

---

**Action not found:**

**Status:** `404 Not Found`

---

**Permission denied:**

**Status:** `403 Forbidden`

---

**Malformed data:**

```json
{
  "messages": ["Malformed data provided (1)."]
}
```
**Status:** `400 Bad Request`

**Select Across Example:**

When `select_across` is set to `1`, the action applies to all objects matching the current filter:

```bash
POST /api/blog/article/action/publish_articles/preview/?status=draft
Content-Type: application/json

{
  "select_across": 1,
  "selected_objects": []
}
```

This will preview publishing **all** draft articles, not just selected ones.

### Complete Workflow Example

**Step 1: Get available actions**

```bash
GET /api/blog/article/info/
```

Response includes available actions:

```json
{
  "actions": [
    ["", "---------"],
    ["delete_selected", "Delete selected objects"],
    ["publish_articles", "Publish selected articles"],
    ["archive_articles", "Archive selected articles"]
  ],
  // ... other data
}
```

**Step 2: Preview the action**

```bash
POST /api/blog/article/action/publish_articles/preview/
Content-Type: application/json

{
  "select_across": 0,
  "selected_objects": [1, 2, 3, 4, 5]
}
```

**Step 3: Review the preview response**

```json
{
  "name": "Publish Articles",
  "description": "Publish 3 draft articles",
  "total_selected": 5,
  "will_be_published": 3,
  "already_published": 2
}
```

**Step 4: Execute the action**

```bash
POST /api/blog/article/action/publish_articles/execute/
Content-Type: application/json

{
  "select_across": 0,
  "selected_objects": [1, 2, 3, 4, 5]
}
```

**Step 5: Receive confirmation**

```json
{
  "messages": ["Successfully published 3 articles."]
}
```

## List Filters

The Django Admin Adapter provides custom list filter classes that extend Django's built-in filtering capabilities with API-friendly features. These filters enable advanced filtering options including text input, numeric ranges, date/datetime ranges, and autocomplete-based filtering.

Simple `ListFilter` classes still are working out of the box,
but Autocomplete and input filters (date, datetime, integer, float, str)
must be implemented from the package's ones.


### Overview

The adapter includes three main filter types:

1. **InputFilter** - Base class for text, number, date, and datetime input filters (better use helper functions)
2. **AutocompleteFilter** - Autocomplete-based filtering using related models
3. **Helper Functions** - `build_input_filter()` and `get_range_filters()` for easy filter creation

All filters work seamlessly with the Django admin list view and are automatically exposed through the API.

The `filter_autocomplete` and `filter_autocomplete_retrieve_label` views are used
for the `AutocompleteFilter`s.

### InputFilter

`InputFilter` is a base class that extends `admin.SimpleListFilter` to provide input-based filtering instead of predefined choices.

> [!WARNING]
> It is best to create input filters using the
> `build_input_filter` and `get_range_filters` helper functions.

**Key Features:**

- Supports multiple field types: `str`, `int`, `float`, `date`, `datetime`
- Configurable HTML input attributes (min, max, step, placeholder)
- Automatic type conversion and validation
- Custom lookup operators

**Supported Field Types:**

| Python Type | HTML Input Type | Example Use Case |
|-------------|----------------|------------------|
| `str` | `text` | Search by name, email, description |
| `int` | `number` | Filter by ID, count, quantity |
| `float` | `number` | Filter by price, rating, percentage |
| `date` | `date` | Filter by birth date, deadline |
| `datetime` | `datetime-local` | Filter by created_at, updated_at |

**Date/Datetime Formats:**

- **Date format:** `YYYY-MM-DD` (e.g., `2024-12-13`)
- **Datetime format:** `YYYY-MM-DDTHH:MM` (e.g., `2024-12-13T15:30`)

### AutocompleteFilter

`AutocompleteFilter` provides autocomplete-based filtering using related models. It leverages the adapter's autocomplete API endpoints to provide a searchable dropdown interface.

> [!IMPORTANT]
> - All filter parameter names must be unique within a ModelAdmin!
> - `AutocompleteFilter` requires the related model to have `search_fields` defined!
> - `AutocompleteFilter` requires the related model admin's view permission!

**Required Attributes:**

- **`title`**: Display title for the filter
- **`parameter_name`**: URL parameter name for the filter
- **`related_model`**: The Django model to search against
- **`relation_query_lookup`**: The lookup query connecting the related model to the current model

**Optional Attributes:**

- **`disabled_by_default`**: Whether the filter is disabled by default (default: `False`)
- **`filter_placeholder`**: Placeholder text for the autocomplete input

**Example:**

```python
from django.contrib import admin
from django_admin_adapter.filters import AutocompleteFilter
from myapp.models import Article, Author

class AuthorFilter(AutocompleteFilter):
    title = "Author"
    parameter_name = "author"
    related_model = Author
    relation_query_lookup = "author__id"
    filter_placeholder = "Search for author..."

class ArticleAdmin(admin.ModelAdmin):
    list_filter = [AuthorFilter]

admin.site.register(Article, ArticleAdmin)
```

**Requirements:**

- The `related_model` must be registered in the admin site
- The `related_model`'s ModelAdmin must have `search_fields` defined
- The user must have `view` permission on the `related_model`'s ModelAdmin/Model
- The `relation_query_lookup` must be a valid Django ORM lookup

**How It Works:**

1. The filter generates an autocomplete URL: `/api/autocomplete/<model_name>/`
2. When a user types, the API searches the related model using its `search_fields`
3. Selected values are used to filter the main queryset via the `relation_query_lookup`

### Building Input Filters

The `build_input_filter()` function creates custom `InputFilter` classes dynamically.

**Function Signature:**

```python
def build_input_filter(
    field_name: str,
    title: str,
    field_type: str | int | float | date | datetime,
    min_value = None,
    max_value = None,
    lookup_operator: str = "__icontains",
    parameter_name: str | None = None,
    disabled_by_default: bool = False,
    placeholder: str = "",
) -> InputFilter:
```

**Parameters:**

- **`field_name`**: Database field name to filter on
- **`title`**: Display title for the filter
- **`field_type`**: Python type (`str`, `int`, `float`, `date`, `datetime`)
- **`min_value`**: Minimum value/length for HTML input validation
- **`max_value`**: Maximum value/length for HTML input validation
- **`lookup_operator`**: Django ORM lookup operator (default: `__icontains`)
- **`parameter_name`**: Custom URL parameter name (default: same as `field_name`)
- **`disabled_by_default`**: Whether filter is disabled by default (relates to visibility in front-end not functionallity)
- **`placeholder`**: Placeholder text for the input field

**Examples:**

**Text Filter:**

```python
from django.contrib import admin
from django_admin_adapter.filters import build_input_filter
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_filter = [
        build_input_filter(
            field_name="title",
            title="Title Contains",
            field_type=str,
            lookup_operator="__icontains",
            placeholder="Search in title...",
        ),
    ]

admin.site.register(Article, ArticleAdmin)
```

**Number Filter:**

```python
class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        build_input_filter(
            field_name="price",
            title="Price Greater Than",
            field_type=float,
            min_value=0,
            max_value=10000,
            lookup_operator="__gte",
            placeholder="Minimum price",
        ),
    ]
```

**Date Filter:**

```python
class OrderAdmin(admin.ModelAdmin):
    list_filter = [
        build_input_filter(
            field_name="created_at",
            title="Created After",
            field_type=date,
            lookup_operator="__gte",
        ),
    ]
```

**Datetime Filter:**

```python
class LogEntryAdmin(admin.ModelAdmin):
    list_filter = [
        build_input_filter(
            field_name="timestamp",
            title="Timestamp After",
            field_type=datetime,
            lookup_operator="__gte",
        ),
    ]
```

### Range Filters

The `get_range_filters()` function creates a pair of filters for minimum and maximum values, perfect for numeric and date/datetime ranges.

**Function Signature:**

```python
def get_range_filters(
    field_name: str,
    title: str,
    field_type: int | float | date | datetime,
    min_value = None,
    max_value = None,
    parameter_name: str | None = None,
    disabled_by_default: bool = False,
    placeholder: str = "",
) -> tuple[InputFilter, InputFilter]:
```

> [!WARNING]
> for `parameter_name` do not use max/min prefix/suffix
> It will be appointed automatically.
> E.g. instead of `price__min` or `price__max` use `price`

**Returns:** A tuple of two `InputFilter` classes:
1. Minimum filter (uses `__gte` lookup)
2. Maximum filter (uses `__lte` lookup)

**Automatic Naming:**

- Minimum filter: `<title> Minimum` with parameter `<parameter_name>__min`
- Maximum filter: `<title> Maximum` with parameter `<parameter_name>__max`

**Examples:**

**Price Range:**

```python
from django.contrib import admin
from django_admin_adapter.filters import get_range_filters
from myapp.models import Product

class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        *get_range_filters(
            field_name="price",
            title="Price",
            field_type=float,
            min_value=0,
            max_value=10000,
            placeholder="Enter price",
        ),
    ]

admin.site.register(Product, ProductAdmin)
```

This creates two filters:
- "Price Minimum" - filters `price__gte`
- "Price Maximum" - filters `price__lte`

**Date Range:**

```python
class OrderAdmin(admin.ModelAdmin):
    list_filter = [
        *get_range_filters(
            field_name="order_date",
            title="Order Date",
            field_type=date,
        ),
    ]
```

This creates:
- "Order Date Minimum" - filters `order_date__gte`
- "Order Date Maximum" - filters `order_date__lte`

**Integer Range:**

```python
class ArticleAdmin(admin.ModelAdmin):
    list_filter = [
        *get_range_filters(
            field_name="view_count",
            title="View Count",
            field_type=int,
            min_value=0,
        ),
    ]
```

### Complete Examples

**E-commerce Product Admin:**

```python
from django.contrib import admin
from datetime import date, datetime
from django_admin_adapter.filters import (
    build_input_filter,
    get_range_filters,
    AutocompleteFilter,
)
from myapp.models import Product, Category, Manufacturer

class CategoryFilter(AutocompleteFilter):
    title = "Category"
    parameter_name = "category"
    related_model = Category
    relation_query_lookup = "category__id"
    filter_placeholder = "Search categories..."

class ManufacturerFilter(AutocompleteFilter):
    title = "Manufacturer"
    parameter_name = "manufacturer"
    related_model = Manufacturer
    relation_query_lookup = "manufacturer__id"

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock', 'category', 'created_at']
    search_fields = ['name', 'sku', 'description']

    list_filter = [
        # Autocomplete filters
        CategoryFilter,
        ManufacturerFilter,

        # Text search
        build_input_filter(
            field_name="sku",
            title="SKU",
            field_type=str,
            lookup_operator="__icontains",
            placeholder="Enter SKU...",
        ),

        # Price range
        *get_range_filters(
            field_name="price",
            title="Price",
            field_type=float,
            min_value=0,
            placeholder="Price",
        ),

        # Stock range
        *get_range_filters(
            field_name="stock",
            title="Stock Quantity",
            field_type=int,
            min_value=0,
        ),

        # Date range
        *get_range_filters(
            field_name="created_at",
            title="Created Date",
            field_type=date,
        ),
    ]

admin.site.register(Product, ProductAdmin)
```

**Blog Article Admin:**

```python
from django.contrib import admin
from datetime import datetime
from django_admin_adapter.filters import (
    build_input_filter,
    get_range_filters,
    AutocompleteFilter,
)
from myapp.models import Article, Author, Tag

class AuthorFilter(AutocompleteFilter):
    title = "Author"
    parameter_name = "author"
    related_model = Author
    relation_query_lookup = "author__id"

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'published_at', 'view_count']
    search_fields = ['title', 'content']

    list_filter = [
        'status',  # Standard Django choice filter
        AuthorFilter,

        # Title search
        build_input_filter(
            field_name="title",
            title="Title Contains",
            field_type=str,
            lookup_operator="__icontains",
        ),

        # View count range
        *get_range_filters(
            field_name="view_count",
            title="Views",
            field_type=int,
            min_value=0,
        ),

        # Published date range
        *get_range_filters(
            field_name="published_at",
            title="Published",
            field_type=datetime,
        ),

        # Word count filter
        build_input_filter(
            field_name="word_count",
            title="Minimum Words",
            field_type=int,
            lookup_operator="__gte",
            min_value=0,
        ),
    ]

admin.site.register(Article, ArticleAdmin)
```

### Filter Data from the API

When you call the list info endpoint, filters are included in the response.
See the swagger for the detailed response format.

### Using Filters in API Requests

```bash
# Filter by author
GET /api/blog/article/?author=5

# Filter by title
GET /api/blog/article/?title=django

# Filter by view count range
GET /api/blog/article/?view_count__min=100&view_count__max=1000

# Filter by published date range
GET /api/blog/article/?published_at__min=2024-01-01T00:00&published_at__max=2024-12-31T23:59

# Combine multiple filters
GET /api/blog/article/?author=5&status=published&view_count__min=100
```

## Throttling

The adapter provides built-in rate limiting (throttling) capabilities to protect your API
from abuse. By default, all endpoints use throttle classes that differentiate between
anonymous and authenticated users.

### Default Throttle Classes

The adapter uses two default throttle classes:

- **AdminAnonRateThrottle**: Applied to anonymous (unauthenticated) requests
- **AdminUserRateThrottle**: Applied to authenticated user requests

No throttling is provided for the authentication views. \
To configure throttling for the authentication endpoints \
provide your throttle class with the `authentication_throttle_class` argument.

These classes extend Django REST Framework's `AnonRateThrottle` and `UserRateThrottle`
respectively, and their rate limits can be configured in your Django settings.

### Configuring Rate Limits

To configure the default throttle rates, add the following to your Django settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Rate for AdminAnonRateThrottle
        'user': '1000/hour',  # Rate for AdminUserRateThrottle
    }
}
```

You can use different time periods: `second`, `minute`, `hour`, or `day`.

### Customizing Throttle Classes

> [!NOTE]
> By default Views of the default `django_admin_adapter.VIEWMAP` have no Throttles set,
> and they are set dynamically when building the site's urls. In that case the throttles
> are set if the viewmap's throttles classes list is `None`.
> That state is depended from the `extra_views` argument that overrides
> any viewmap with the same name.

You can override the default throttle classes globally for all adapter endpoints
and authentication's by passing custom throttle classes during adapter instantiation:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class CustomAnonThrottle(AnonRateThrottle):
    rate = '50/hour'

class CustomUserThrottle(UserRateThrottle):
    rate = '500/hour'

class CustomAuthThrottle(UserRateThrottle):
    rate = '500/hour'

admin_adapter = AdminAPIAdapter(
    admin.site,
    default_anon_throttle_class=CustomAnonThrottle,
    default_user_throttle_class=CustomUserThrottle,
    authentication_throttle_class=CustomAuthThrottle,
)
```

**Parameters:**

- `default_anon_throttle_class`: A subclass of `rest_framework.throttling.BaseThrottle`
  that will be applied to anonymous requests

- `default_user_throttle_class`: A subclass of `rest_framework.throttling.BaseThrottle`
  that will be applied to authenticated user requests

### Per-View Throttle Classes

You can also set custom throttle classes for specific views using the `extra_views`
parameter. This overrides the default throttle classes for that particular view:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from myapp.views import CustomDashboardView
from myapp.throttling import DashboardAnonThrottle, DashboardUserThrottle

admin_adapter = AdminAPIAdapter(
    admin.site,
    extra_views={
        "custom_dashboard": (
            "dashboard/",
            CustomDashboardView,
            [DashboardAnonThrottle, DashboardUserThrottle],  # Custom throttles
        ),
    },
)
```

The throttle classes list must contain exactly two classes:
1. First class: Applied to anonymous requests
2. Second class: Applied to authenticated user requests

If you pass `None` instead of a list, the view will use the default throttle classes.

### Complete Example

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from myapp.views import ReportsView
from myapp.throttling import ReportsAnonThrottle, ReportsUserThrottle

# Define custom global throttle classes
class StrictAnonThrottle(AnonRateThrottle):
    rate = '20/hour'

class StrictUserThrottle(UserRateThrottle):
    rate = '200/hour'

admin_adapter = AdminAPIAdapter(
    admin.site,
    # Set global default throttle classes
    default_anon_throttle_class=StrictAnonThrottle,
    default_user_throttle_class=StrictUserThrottle,
    # Override throttle classes for specific views
    extra_views={
        "reports": (
            "reports/",
            ReportsView,
            [ReportsAnonThrottle, ReportsUserThrottle],  # View-specific throttles
        ),
        # -------------------------------------------
        # override an adapter view throttles !!!
        "admin_list_create": (
            "<str:app_name>/<str:model_name>/",
            django_admin_adapter.views.list.AdminListCreateAPIView,
            [ReportsAnonThrottle, ReportsUserThrottle],  # View-specific throttles
        ),
    },
)
```

### Validation

The adapter validates throttle classes during initialization and will raise
`AdminAPIAdapterError` if:

- The provided class is not actually a class
- The class is not a subclass of `rest_framework.throttling.BaseThrottle`
- Per-view throttle classes are not provided as a list or tuple of exactly 2 classes

For more information on throttling in Django REST Framework, see the
[DRF Throttling documentation](https://www.django-rest-framework.org/api-guide/throttling/).

## Customizing Object/List Serializers

The adapter uses three main serializer classes to format data returned by the API endpoints.
You can customize these serializers freely.

### Default Serializer Classes

The adapter provides three default serializer classes:

- **object_serializer_class**: `AdminObjectViewSerializer` - Used for object detail views and readonly field rendering
- **list_serializer_class**: `AdminListSerializer` - Used for list views and object listings
- **history_serializer_class**: `AdminHistorySerializer` - Used for object history views

These serializers handle the conversion of Django model instances into JSON-serializable
data structures that the frontend can consume.

### Overriding Serializer Classes

To override the default serializer classes,
pass the corresponding serializer to the constructor **as kwarg**:

```python
from django_admin_adapter import AdminAPIAdapter
from django_admin_adapter.serializers import (
    AdminListSerializer,
    AdminObjectViewSerializer,
    AdminHistorySerializer,
)
from django.contrib import admin

# Create custom serializers
class CustomObjectSerializer(AdminObjectViewSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add custom field
        data['custom_field'] = 'custom_value'
        return data

class CustomListSerializer(AdminListSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Modify list representation
        data['display_name'] = str(instance).upper()
        return data

class CustomHistorySerializer(AdminHistorySerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add custom history formatting
        data['formatted_date'] = instance.action_time.strftime('%B %d, %Y')
        return data

# Use the custom adapter
admin_adapter = AdminAPIAdapter(
    admin.site,
    object_serializer_class=CustomObjectSerializer,
    list_serializer_class=CustomListSerializer,
    history_serializer_class=CustomHistorySerializer,
)

urlpatterns = [
    path("api/", include(admin_adapter.get_urls())),
]
```

## Base Permission Class

The `base_permission_class` class attribute controls the default permission checking mechanism for all API endpoints exposed by the adapter.

This allows you to customize who can access your admin API endpoints beyond the default staff-only requirement.

### Overview

By default, the adapter uses `AdminSiteBasePermission` as the base permission class for all non-authentication views. This permission class is automatically appended to any existing `permission_classes` defined in your custom views, ensuring consistent access control across your admin API.

The permission class is applied during URL pattern generation in the `build_view_path` method, which means:

- **Authentication views** (`token_obtain_pair`, `token_refresh`) do NOT receive the base permission class
- **All other views** automatically receive the base permission class in addition to any view-specific permissions

### Default Permission Class

The default `base_permission_class` is `AdminSiteBasePermission`, which is defined as:

```python
from rest_framework.permissions import BasePermission

class AdminSiteBasePermission(BasePermission):
    """
    Delegate basic permission handling to adapter's
    `AdminSite.has_permission`.
    """

    def has_permission(self, request, view):
        return view._admin_site.has_permission(request)
```

This class delegates permission checking to Django's admin site `has_permission` method,
which by default requires:

1. The user is authenticated
2. The user has `is_active=True`
3. The user has `is_staff=True`

### Customizing the Permission Class

You can pass the permission class as a keyword argument during instantiation:

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin

admin_adapter = AdminAPIAdapter(
    admin.site,
    base_permission_class=SuperuserOnlyPermission,
)
```

### Complete Examples

#### Example: Custom Permission Based on User Groups

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from rest_framework.permissions import BasePermission

class AdminGroupPermission(BasePermission):
    """
    Only allow users in the 'Admin' group to access the API.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_active and
            request.user.is_staff and
            request.user.groups.filter(name='Admin').exists()
        )

admin_adapter = AdminAPIAdapter(
    admin.site,
    base_permission_class=AdminGroupPermission,
)

urlpatterns = [
    path("api/", include(admin_adapter.get_urls())),
]
```

#### Example: IP-Based Permission

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin
from rest_framework.permissions import BasePermission

class InternalIPPermission(BasePermission):
    """
    Only allow requests from internal IP addresses.
    """
    ALLOWED_IPS = ['192.168.1.0/24', '10.0.0.0/8']

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user is authenticated and staff
        if not request.user.is_staff:
            return False

        # Additional IP check
        ip = self.get_client_ip(request)
        return self.is_ip_allowed(ip)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_ip_allowed(self, ip):
        # Implement IP checking logic
        # This is a simplified example
        return ip.startswith('192.168.') or ip.startswith('10.')

admin_adapter = AdminAPIAdapter(
    admin.site,
    base_permission_class=InternalIPPermission,
)
```

### Important Notes

> [!IMPORTANT]
> - The `base_permission_class` is **automatically appended** to existing `permission_classes` on views, not replaced
> - Authentication views (`token_obtain_pair`, `token_refresh`) **do not** receive the base permission class
> - If a custom view in `extra_views` already has `permission_classes` defined, the base permission will be added to that list
> - The permission class must be a subclass of `rest_framework.permissions.BasePermission`

> [!WARNING]
> - Changing the `base_permission_class` affects **all non-authentication endpoints** in your admin API
> - Make sure your custom permission class properly checks authentication status before performing additional checks


## Providing Extra Data

The adapter allows you to provide custom extra data in various API endpoints by implementing specific methods in your `ModelAdmin` classes or by overriding the adapter's method. This enables you to extend the default API responses with application-specific information.

### Overview

Extra data methods are called by the adapter's views when building API responses. These methods should return JSON-serializable data (dictionaries, lists, strings, numbers, etc.) that will be included in the response under the `extra_data` key.

### Available Extra Data Methods

#### From ModelAdmin Classes

You can add the following methods to your `ModelAdmin` subclasses to provide extra data for specific views:

##### `get_list_extra_data(request)`

Called by `AdminListInfoAPIView` when retrieving list view information (filters, actions, etc.).

**Parameters:**
- `request`: The current HTTP request object

**Returns:** JSON-serializable data or `None`

**Example:**

```python
from django.contrib import admin
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    def get_list_extra_data(self, request):
        return {
            "total_published": Article.objects.filter(status='published').count(),
            "total_drafts": Article.objects.filter(status='draft').count(),
            "categories": list(Article.objects.values_list('category', flat=True).distinct()),
        }

admin.site.register(Article, ArticleAdmin)
```

**Response location:** `/api/<app_name>/<model_name>/info/` → `extra_data`

---

##### `get_view_extra_data(request, obj)`

Called by `AdminObjectViewAPIView` when retrieving object view data.

**Parameters:**
- `request`: The current HTTP request object
- `obj`: The model instance being viewed

**Returns:** JSON-serializable data or `None`

**Example:**

```python
from django.contrib import admin
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    def get_view_extra_data(self, request, obj):
        return {
            "view_count": obj.views,
            "last_modified_by": str(obj.modified_by) if obj.modified_by else None,
            "related_articles": [
                {"id": a.id, "title": a.title}
                for a in Article.objects.filter(category=obj.category).exclude(id=obj.id)[:5]
            ],
        }

admin.site.register(Article, ArticleAdmin)
```

**Response location:** `/api/<app_name>/<model_name>/<pk>/view/` → `extra_data`

---

##### `get_add_extra_data(request)`

Called by `AdminObjectAddAPIView` when retrieving the add form data.

**Parameters:**
- `request`: The current HTTP request object

**Returns:** JSON-serializable data or `None`

**Example:**

```python
from django.contrib import admin
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    def get_add_extra_data(self, request):
        return {
            "default_author": request.user.id,
            "available_templates": ["standard", "featured", "news"],
            "suggested_tags": ["technology", "business", "lifestyle"],
        }

admin.site.register(Article, ArticleAdmin)
```

**Response location:** `/api/<app_name>/<model_name>/add/` → `extra_data`

---

##### `get_edit_extra_data(request, obj)`

Called by `AdminObjectEditAPIView` when retrieving the edit form data.

**Parameters:**
- `request`: The current HTTP request object
- `obj`: The model instance being edited

**Returns:** JSON-serializable data or `None`

**Example:**

```python
from django.contrib import admin
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    def get_edit_extra_data(self, request, obj):
        return {
            "edit_history_count": obj.revisions.count(),
            "last_editor": str(obj.modified_by) if obj.modified_by else None,
            "locked_by": str(obj.locked_by) if hasattr(obj, 'locked_by') and obj.locked_by else None,
            "word_count": len(obj.content.split()) if obj.content else 0,
        }

admin.site.register(Article, ArticleAdmin)
```

**Response location:** `/api/<app_name>/<model_name>/<pk>/edit/` → `extra_data`

---

##### `get_delete_extra_data(request, obj)`

Called by `AdminObjectConfirmDeleteAPIView` when retrieving delete confirmation data.

**Parameters:**
- `request`: The current HTTP request object
- `obj`: The model instance being deleted

**Returns:** JSON-serializable data or `None`

**Example:**

```python
from django.contrib import admin
from myapp.models import Article

class ArticleAdmin(admin.ModelAdmin):
    def get_delete_extra_data(self, request, obj):
        return {
            "warning": "This article has been published and has comments.",
            "comments_count": obj.comments.count(),
            "can_archive_instead": True,
            "archive_url": f"/archive/{obj.id}/",
        }

admin.site.register(Article, ArticleAdmin)
```

**Response location:** `/api/<app_name>/<model_name>/<pk>/delete/` → `extra_data`

---

#### From AdminAPIAdapter Class

##### `get_extra_base_info_data(request)`

Called by `AdminBaseInfoAPIView` when retrieving base information (sidebar, profile, etc.).

**Parameters:**
- `request`: The current HTTP request object

**Returns:** JSON-serializable data or `None`

**Example:**

```python
from django_admin_adapter import AdminAPIAdapter
from django.contrib import admin

class CustomAdminAPIAdapter(AdminAPIAdapter):
    def get_extra_base_info_data(self, request):
        return {
            "app_version": "2.1.0",
            "environment": "production",
            "company_name": "My Company",
            "support_email": "support@mycompany.com",
            "features": {
                "dark_mode": True,
                "notifications": True,
                "analytics": request.user.is_superuser,
            },
        }

admin_adapter = CustomAdminAPIAdapter(admin.site)
```

**Response location:** `/api/base_info/` → `extra`

---

### Error Handling

If an extra data method raises an exception, the adapter will not catch it, and the request will fail. Make sure to handle exceptions within your methods:

```python
def get_list_extra_data(self, request):
    try:
        # Your logic here
        return {"data": "value"}
    except Exception as e:
        # Log the error
        logger.error(f"Error in get_list_extra_data: {e}")
        # Return None or safe default
        return None
```

## Development and testing

### Testing locally

Follow the steps below, to run the project (admin + admin api)
ASSUMPTION: you are using a linux machine, don't know how it'll go on windows.
Before continuing, cd on the `/src` directory of the cloned repository and run the command below on terminal:

```bash
mkdir -p data/admin/media data/admin/static data/admin_api/static data/db data/redis
```

1. make sure you have docker properly installed on your machine
2. edit the `src/.env` file and change `DOCKER_USER` to your username and `DOCKER_USER_ID` to your user's system id ( run `cat /etc/group` in your terminal and `whomai` )
3. run `docker compose build`
4. run `docker compose up`
5. run `docker compose admin python3 manage.py init_db` to initialize the database

If all the steps went ok, then the old-school admin will be available in the `localhost:8000`
and the api will be available on `localhost:8888/api` base url.

You can log in the traditional admin with the credentials:
username: superuser (or pilot)
password: asd!@#123

If you cloned the [React](https://github.com/AlkiviadisAleiferis/react_django_admin) project, then running `npm start` will bring up the React app, and you will be able to log in
the API version of the admin from the `localhost:3000`

### Future development

Many ideas and concepts can be implemented in this library. The most propable depending on
the community's interest:

- Create mass edit action available from the library.
- Enable prepopulated fields in Add View, depending on GET query parameters.
- Implement more scrolling at autocomplete search.
- Create automatic swagger for all model admins.
- Create automatic swagger for all actions.

If interested with contribution and development with some of these features please contact me freely.

### Helping

Creating issues wherever bugs are found and giving suggestions for upcoming versions
can surely help in maintaining and growing this package.
