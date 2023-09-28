from asyncio.log import logger

from rest_framework.response import Response
from rest_framework.views import status

from apps.fyle.helpers import get_fyle_orgs, get_request, post_request


def test_post_request(mocker):
    mocker.patch(
        "apps.fyle.helpers.requests.post",
        return_value=Response({"message": "Post request"}, status=status.HTTP_200_OK),
    )
    try:
        post_request(url="sdfghjk", body={}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")

    mocker.patch(
        "apps.fyle.helpers.requests.post",
        return_value=Response(
            {"message": "Post request"}, status=status.HTTP_400_BAD_REQUEST
        ),
    )
    try:
        post_request(url="sdfghjk", body={}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")


def test_get_request(mocker):
    mocker.patch(
        "apps.fyle.helpers.requests.get",
        return_value=Response({"message": "Get request"}, status=status.HTTP_200_OK),
    )
    try:
        get_request(url="sdfghjk", params={"key": "sample"}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")

    mocker.patch(
        "apps.fyle.helpers.requests.get",
        return_value=Response(
            {"message": "Get request"}, status=status.HTTP_400_BAD_REQUEST
        ),
    )
    try:
        get_request(url="sdfghjk", params={"sample": True}, refresh_token="srtyu")
    except Exception:
        logger.info("Error in post request")


def test_get_fyle_orgs(mocker):
    mocker.patch(
        "apps.fyle.helpers.requests.get",
        return_value=Response({"message": "Get request"}, status=status.HTTP_200_OK),
    )
    try:
        get_fyle_orgs(refresh_token="srtyu", cluster_domain="erty")
    except Exception:
        logger.info("Error in post request")
