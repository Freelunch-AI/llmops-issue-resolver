import pytest
from datetime import datetime
from pydantic import ValidationError
from sandbox_sdk.sdk.models.resources import (
    ResourceLimits,
    ComputeResources,
    ResourceUsage,
    ResourceHistory,
    ResourceStatus
)

class TestResourceLimits:
    def test_default_values(self):
        limits = ResourceLimits()
        assert limits.max_cpu_cores == 8
        assert limits.max_ram_gb == 32
        assert limits.max_disk_gb == 100
        assert limits.max_sandboxes == 10

    def test_custom_values(self):
        limits = ResourceLimits(
            max_cpu_cores=4,
            max_ram_gb=16,
            max_disk_gb=50,
            max_sandboxes=5
        )
        assert limits.max_cpu_cores == 4
        assert limits.max_ram_gb == 16
        assert limits.max_disk_gb == 50
        assert limits.max_sandboxes == 5

class TestComputeResources:
    def test_valid_resources(self):
        resources = ComputeResources(
            cpu_cores=4.0,
            ram_gb=16,
            disk_gb=50
        )
        assert resources.cpu_cores == 4.0
        assert resources.ram_gb == 16
        assert resources.disk_gb == 50
        assert resources.memory_bandwidth_gbps is None
        assert resources.network_bandwidth_mbps is None

    def test_optional_fields(self):
        resources = ComputeResources(
            cpu_cores=4.0,
            ram_gb=16,
            disk_gb=50,
            memory_bandwidth_gbps=100.0,
            network_bandwidth_mbps=1000.0
        )
        assert resources.memory_bandwidth_gbps == 100.0
        assert resources.network_bandwidth_mbps == 1000.0

    def test_cpu_validation(self):
        with pytest.raises(ValueError, match="CPU cores cannot exceed 8"):
            ComputeResources(cpu_cores=10, ram_gb=16, disk_gb=50)

    def test_ram_validation(self):
        with pytest.raises(ValueError, match="RAM cannot exceed 32GB"):
            ComputeResources(cpu_cores=4, ram_gb=64, disk_gb=50)

    def test_disk_validation(self):
        with pytest.raises(ValueError, match="Disk space cannot exceed 100GB"):
            ComputeResources(cpu_cores=4, ram_gb=16, disk_gb=200)

class TestResourceUsage:
    def test_valid_usage(self):
        usage = ResourceUsage(
            cpu_usage_percent=75.5,
            ram_usage_gb=14.5,
            disk_usage_gb=45.2
        )
        assert usage.cpu_usage_percent == 75.5
        assert usage.ram_usage_gb == 14.5
        assert usage.disk_usage_gb == 45.2
        assert isinstance(usage.timestamp, datetime)

    def test_optional_bandwidth_fields(self):
        usage = ResourceUsage(
            cpu_usage_percent=75.5,
            ram_usage_gb=14.5,
            disk_usage_gb=45.2,
            memory_bandwidth_usage_gbps=80.0,
            network_bandwidth_usage_mbps=900.0
        )
        assert usage.memory_bandwidth_usage_gbps == 80.0
        assert usage.network_bandwidth_usage_mbps == 900.0

class TestResourceHistory:
    def test_valid_history(self):
        measurements = [
            ResourceUsage(cpu_usage_percent=75.5, ram_usage_gb=14.5, disk_usage_gb=45.2),
            ResourceUsage(cpu_usage_percent=80.0, ram_usage_gb=15.0, disk_usage_gb=46.0)
        ]
        history = ResourceHistory(
            sandbox_id="test-sandbox",
            measurements=measurements,
            max_cpu_usage=80.0,
            max_ram_usage=15.0,
            max_disk_usage=46.0
        )
        assert history.sandbox_id == "test-sandbox"
        assert len(history.measurements) == 2
        assert history.max_cpu_usage == 80.0

    def test_measurements_length_validation(self):
        measurements = [
            ResourceUsage(cpu_usage_percent=i, ram_usage_gb=i, disk_usage_gb=i)
            for i in range(1, 8)
        ]
        history = ResourceHistory(
            sandbox_id="test-sandbox",
            measurements=measurements,
            max_cpu_usage=7.0,
            max_ram_usage=7.0,
            max_disk_usage=7.0
        )
        assert len(history.measurements) == 5
        assert history.measurements[-1].cpu_usage_percent == 7.0

class TestResourceStatus:
    def test_valid_status(self):
        status = ResourceStatus(
            total_cpu_cores=8,
            total_ram_gb=32,
            total_disk_gb=100,
            available_cpu_cores=4.0,
            available_ram_gb=16,
            available_disk_gb=50,
            total_sandboxes=10,
            active_sandboxes=5
        )
        assert status.total_cpu_cores == 8
        assert status.available_cpu_cores == 4.0
        assert isinstance(status.timestamp, datetime)

    def test_available_sandboxes_property(self):
        status = ResourceStatus(
            total_cpu_cores=8,
            total_ram_gb=32,
            total_disk_gb=100,
            available_cpu_cores=4.0,
            available_ram_gb=16,
            available_disk_gb=50,
            total_sandboxes=10,
            active_sandboxes=7
        )
        assert status.available_sandboxes == 3

    def test_is_capacity_available_property(self):
        # Test when capacity is available
        status = ResourceStatus(
            total_cpu_cores=8,
            total_ram_gb=32,
            total_disk_gb=100,
            available_cpu_cores=4.0,
            available_ram_gb=16,
            available_disk_gb=50,
            total_sandboxes=10,
            active_sandboxes=5
        )
        assert status.is_capacity_available is True

        # Test when capacity is not available
        status_no_capacity = ResourceStatus(
            total_cpu_cores=8,
            total_ram_gb=32,
            total_disk_gb=100,
            available_cpu_cores=0,
            available_ram_gb=16,
            available_disk_gb=50,
            total_sandboxes=10,
            active_sandboxes=10
        )
        assert status_no_capacity.is_capacity_available is False