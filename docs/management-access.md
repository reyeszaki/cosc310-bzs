# Restaurant and menu access

Public visitors and customers can browse restaurants and menus. Management actions
require an active owner or admin account.

- Customers cannot create, update or delete restaurants or menu items.
- Owners can create restaurants, which are assigned to them automatically.
- Owners can edit/delete only their own restaurants and menu items.
- Admins can manage all restaurants and assign or remove an owner.
- An old restaurant without an owner_id can be managed only by an admin until assigned.

The frontend sends the bearer token with management requests and shows controls
based on the signed-in role and restaurant owner_id. The backend checks access too,
so calling the API directly cannot bypass these rules. The service also checks
permissions before saving changes.

## Assign an owner

Sign in as an admin and open a restaurant. Enter an existing active owner account's
ID in the owner form and select Save Owner. Leave the field blank to remove the owner.

The API is `PUT /restaurants/{restaurant_id}/owner`:

```json
{"owner_id": 2}
```

Only this endpoint can change ownership. Normal restaurant creation/update bodies
cannot set owner_id. A customer's profile update cannot change their role either.

## Set up a trusted manager account

Public registration still creates customers. There is no public role selector or
role-promotion endpoint. For this local project, a trusted maintainer can promote an
existing registered account using the repository from a Python shell in the project:

```python
from app.repository.users_repo import UserRepository

repository = UserRepository()
user = repository.get_by_email("your-registered-email@example.ca")
```

Check that `user` is the intended account and is not None. Then run one of these:

```python
repository.update(user["id"], {"role": "admin"})
```

or:

```python
repository.update(user["id"], {"role": "owner"})
```

Sign out and sign in again to refresh the frontend. Do not grant roles to accounts
you do not trust. No default manager passwords or manager accounts are added to the
project data. This manual setup is for the local course project; a deployed system
would need a controlled administration process.

## Responses and checks

- 401: missing/invalid token or deactivated account.
- 403: wrong role, another owner's restaurant, or invalid owner access.
- 404: restaurant or selected owner account does not exist.
- 409: the selected account is not an owner.
- 422: invalid input, or an attempt to set ownership through the normal item/details request.

Run `python -m pytest tests/test_management_permissions.py -q` for the access tests.
They use temporary storage and cover guests/customers, owners, admins, deactivated
accounts, ownership assignment, role/ownership injection and direct service calls.
Existing restaurant/menu CRUD tests run as an admin; they still check their original
success, validation and storage behavior.

All 66 tests passed locally. Separate Chrome checks with temporary accounts passed
customer restrictions, owner menu/restaurant edits, cross-owner restrictions and
admin assignment. Owner assignment was also read back through a fresh repository.
No full server restart was performed for this change.
