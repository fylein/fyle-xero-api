import logging

from apps.users.models import User

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def test_user_creation(db):
    """
    Test Post of User Profile
    """
    try:
        user = User.objects.create_user(email="", full_name="sample", password="samp")
    except Exception:
        logger.info("Users must have an email address")

    user = User.objects.create_user(
        email="sample@fyle.in", full_name="sample", password="samp"
    )
    assert user.email == "sample@fyle.in"


def test_create_staffuser(db):
    """
    Test Post of User Profile
    """
    user = User.objects.create_staffuser(
        email="sample@fyle.in", full_name="sample", password="samp"
    )
    assert user.email == "sample@fyle.in"


def test_create_superuser(db):
    """
    Test Post of User Profile
    """
    user = User.objects.create_superuser(
        email="sample@fyle.in", full_name="sample", password="samp"
    )
    assert user.email == "sample@fyle.in"


def test_get_of_user(db, add_users_to_database):
    """
    Test Get of User Profile
    """
    user = User.objects.filter(email="labhvam.s@fyle.in").first()
    assert user.user_id == "usqywo0f3nLY"


def test_user_funcs(db, add_users_to_database):
    user_object = User()
    user = user_object.has_module_perms(app_label="")
    assert user == True

    user = user_object.has_perm(perm="")
    assert user == True

    user = user_object.get_full_name()
    assert user == ""

    user = user_object.get_short_name()
    assert user == ""

    user = User.objects.create_user(
        email="sample@fyle.in", full_name="sample", password="samp"
    )
    assert user.is_staff is False
    assert user.is_admin is False
    assert user.is_active is True
