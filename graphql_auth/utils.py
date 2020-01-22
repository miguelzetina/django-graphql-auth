from django.core import signing
from django.contrib.auth import get_user_model
from django.conf import settings as django_settings


def get_token(user, action, exp=None):
    username = user.get_username()
    if hasattr(username, "pk"):
        username = username.pk
    payload = {user.USERNAME_FIELD: username, "action": action}
    token = signing.dumps(payload)
    return token


def get_token_paylod(token, action, exp=None):
    payload = signing.loads(token, max_age=exp)
    _action = payload.pop("action")
    if _action != action:
        raise Exception("Invalid token.")
    return payload


def get_user_by_email(email):
    email_field_name = get_user_model().get_email_field_name()
    user = get_user_model()._default_manager.get(**{email_field_name: email})
    return user


def revoke_user_refresh_token(user):
    if (
        hasattr(django_settings, "GRAPHQL_JWT")
        and django_settings.GRAPHQL_JWT.get(
            "JWT_LONG_RUNNING_REFRESH_TOKEN", False
        )
        and "graphql_jwt.refresh_token.apps.RefreshTokenConfig"
        in django_settings.INSTALLED_APPS
    ):
        refresh_tokens = user.refresh_tokens.all()
        for refresh_token in refresh_tokens:
            try:
                refresh_token.revoke()
            except Exception:  # JSONWebTokenError
                pass


def flat_dict(dict_or_list):
    """
    if is dict, return list of dict keys,
    if is list, return the list
    """
    return (
        list(dict_or_list.keys())
        if isinstance(dict_or_list, dict)
        else dict_or_list
    )


def normalize_fields(dict_or_list, extra_list):
    """
    helper merge settings defined fileds and
    other fields on mutations
    """
    if isinstance(dict_or_list, dict):
        for i in extra_list:
            dict_or_list[i] = "String"
        return dict_or_list
    else:
        return dict_or_list + extra_list
