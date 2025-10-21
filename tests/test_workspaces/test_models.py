"""
Tests for workspace models
"""
from unittest import mock

from django.core.cache import cache
from fyle_accounting_library.fyle_platform.enums import CacheKeyEnum

from apps.workspaces.models import FeatureConfig


def test_get_feature_config_cache_miss(add_feature_config):
    """
    Test get_feature_config method when cache miss occurs
    This tests lines 323, 328-330, 335-338 in apps/workspaces/models.py
    """
    workspace_id = 1
    cache.clear()
    result = FeatureConfig.get_feature_config(workspace_id, 'export_via_rabbitmq')
    assert result is True
    cache_key = CacheKeyEnum.FEATURE_CONFIG_EXPORT_VIA_RABBITMQ.value.format(workspace_id=workspace_id)
    cached_value = cache.get(cache_key)
    assert cached_value is True
    result = FeatureConfig.get_feature_config(workspace_id, 'fyle_webhook_sync_enabled')
    assert result is False
    cache_key = CacheKeyEnum.FEATURE_CONFIG_FYLE_WEBHOOK_SYNC_ENABLED.value.format(workspace_id=workspace_id)
    cached_value = cache.get(cache_key)
    assert cached_value is False


def test_get_feature_config_cache_hit(add_feature_config):
    """
    Test get_feature_config method when cache hit occurs
    This tests lines 323, 328-330, 332-333 in apps/workspaces/models.py
    """
    workspace_id = 1
    cache_key = CacheKeyEnum.FEATURE_CONFIG_EXPORT_VIA_RABBITMQ.value.format(workspace_id=workspace_id)
    cache.set(cache_key, False, 172800)
    with mock.patch.object(FeatureConfig.objects, 'get') as mock_get:
        result = FeatureConfig.get_feature_config(workspace_id, 'export_via_rabbitmq')
        assert result is False
        mock_get.assert_not_called()


def test_get_feature_config_cache_key_mapping(add_feature_config):
    """
    Test that cache key mapping works correctly for different keys
    This tests lines 323, 328-330 in apps/workspaces/models.py
    """
    workspace_id = 1
    cache.clear()
    FeatureConfig.get_feature_config(workspace_id, 'export_via_rabbitmq')
    FeatureConfig.get_feature_config(workspace_id, 'fyle_webhook_sync_enabled')
    export_cache_key = CacheKeyEnum.FEATURE_CONFIG_EXPORT_VIA_RABBITMQ.value.format(workspace_id=workspace_id)
    webhook_cache_key = CacheKeyEnum.FEATURE_CONFIG_FYLE_WEBHOOK_SYNC_ENABLED.value.format(workspace_id=workspace_id)
    assert cache.get(export_cache_key) is True
    assert cache.get(webhook_cache_key) is False
