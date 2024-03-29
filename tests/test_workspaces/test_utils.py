import json
from asyncio.log import logger
from unittest import mock

import jwt

from apps.workspaces.utils import generate_token, generate_xero_identity, generate_xero_refresh_token, revoke_token
from tests.test_xero.fixtures import data as xero_data


def test_generate_token(mocker, db):
    mocker.patch("apps.workspaces.utils.requests.post", return_value=None)

    generate_token(authorization_code="asdfgh")


def test_revoke_token(mocker, db):
    mocker.patch("apps.workspaces.utils.requests.post", return_value=None)

    revoke_token(refresh_token="asdfgh")


def test_generate_xero_identity(mocker, db):
    try:
        mocker.patch(
            "apps.workspaces.utils.generate_token",
            return_value=mock.MagicMock(
                status_code=200,
                text=json.dumps(
                    {
                        "refresh_token": "sdfgh",
                        "id_token": jwt.encode(
                            {
                                "given_name": "sdfgh",
                                "family_name": "dfgh",
                                "email": "sdfghj@ssdd.fgh",
                            },
                            key="secret",
                        ),
                    }
                ),
            ),
        )
        mocker.patch("xerosdk.XeroSDK.__init__", return_value=None)
        mocker.patch(
            "xerosdk.apis.Tenants.get_all", return_value=xero_data["get_all_tenants"]
        )
        mocker.patch("apps.workspaces.utils.revoke_token", return_value=None)

        generate_xero_identity(authorization_code="asdfgh", redirect_uri="sdfghj")
    except Exception:
        logger.info("Wrong client secret or/and refresh token")

    try:
        mocker.patch(
            "apps.workspaces.utils.generate_token",
            return_value=mock.MagicMock(
                status_code=400,
                text=json.dumps(
                    {
                        "refresh_token": "sdfgh",
                        "id_token": jwt.encode(
                            {
                                "given_name": "sdfgh",
                                "family_name": "dfgh",
                                "email": "sdfghj@ssdd.fgh",
                            },
                            key="secret",
                        ),
                    }
                ),
            ),
        )

        generate_xero_identity(authorization_code="asdfgh", redirect_uri="sdfghj")
    except Exception:
        logger.info("Wrong client secret or/and refresh token")

    try:
        mocker.patch(
            "apps.workspaces.utils.generate_token",
            return_value=mock.MagicMock(
                status_code=401,
                text=json.dumps(
                    {
                        "refresh_token": "sdfgh",
                        "id_token": jwt.encode(
                            {
                                "given_name": "sdfgh",
                                "family_name": "dfgh",
                                "email": "sdfghj@ssdd.fgh",
                            },
                            key="secret",
                        ),
                    }
                ),
            ),
        )

        generate_xero_identity(authorization_code="asdfgh", redirect_uri="sdfghj")
    except Exception:
        logger.info("Wrong client secret or/and refresh token")

    try:
        mocker.patch(
            "apps.workspaces.utils.generate_token",
            return_value=mock.MagicMock(
                status_code=500,
                text=json.dumps(
                    {
                        "refresh_token": "sdfgh",
                        "id_token": jwt.encode(
                            {
                                "given_name": "sdfgh",
                                "family_name": "dfgh",
                                "email": "sdfghj@ssdd.fgh",
                            },
                            key="secret",
                        ),
                    }
                ),
            ),
        )

        generate_xero_identity(authorization_code="asdfgh", redirect_uri="sdfghj")
    except Exception:
        logger.info("Wrong client secret or/and refresh token")


def test_generate_xero_refresh_token(mocker, db):
    mocker.patch(
        "apps.workspaces.utils.generate_token",
        return_value=mock.MagicMock(
            status_code=200, text=json.dumps({"refresh_token": "sdfgh"})
        ),
    )

    generate_xero_refresh_token(authorization_code="sdfgh")

    try:
        mocker.patch(
            "apps.workspaces.utils.generate_token",
            return_value=mock.MagicMock(
                status_code=401, text=json.dumps({"refresh_token": "sdfgh"})
            ),
        )

        generate_xero_refresh_token(authorization_code="sdfgh")
    except Exception:
        logger.info("Wrong client secret or/and refresh token")

    try:
        mocker.patch(
            "apps.workspaces.utils.generate_token",
            return_value=mock.MagicMock(
                status_code=500, text=json.dumps({"refresh_token": "sdfgh"})
            ),
        )

        generate_xero_refresh_token(authorization_code="sdfgh")
    except Exception:
        logger.info("Internal server error")
