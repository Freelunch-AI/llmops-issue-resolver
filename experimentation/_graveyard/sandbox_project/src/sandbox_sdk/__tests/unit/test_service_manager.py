import unittest
from unittest.mock import patch, MagicMock, call
import asyncio
import subprocess
from pathlib import Path
import time
from sandbox_sdk.sdk.infra_management.service_manager import ServiceManager

class TestServiceManager(unittest.TestCase):
    def setUp(self):
        self.compose_file = "docker-compose.yml"
        self.service_manager = ServiceManager(self.compose_file)

    @patch('pathlib.Path.exists')
    def test_init_valid_file(self, mock_exists):
        mock_exists.return_value = True
        manager = ServiceManager(self.compose_file)
        self.assertEqual(manager.compose_file_path, Path(self.compose_file))
        self.assertEqual(manager.inactivity_timeout, 1800)

    @patch('pathlib.Path.exists')
    def test_init_invalid_file(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            ServiceManager(self.compose_file)

    @patch('subprocess.run')
    def test_start_services_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], 0)
        
        result = self.service_manager.start_services()
        self.assertTrue(result)
        mock_run.assert_called_with(
            ['docker-compose', '-f', self.compose_file, 'up', '-d'],
            check=True
        )

    @patch('subprocess.run')
    def test_start_specific_services(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], 0)
        services = ['service1', 'service2']
        
        result = self.service_manager.start_services(services)
        self.assertTrue(result)
        mock_run.assert_called_with(
            ['docker-compose', '-f', self.compose_file, 'up', '-d', 'service1', 'service2'],
            check=True
        )

    @patch('subprocess.run')
    def test_start_services_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, [])
        
        result = self.service_manager.start_services()
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_stop_services_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], 0)
        
        result = self.service_manager.stop_services()
        self.assertTrue(result)
        mock_run.assert_called_with(
            ['docker-compose', '-f', self.compose_file, 'down'],
            check=True
        )

    @patch('subprocess.run')
    def test_stop_specific_services(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], 0)
        services = ['service1', 'service2']
        
        result = self.service_manager.stop_services(services)
        self.assertTrue(result)
        mock_run.assert_called_with(
            ['docker-compose', '-f', self.compose_file, 'stop', 'service1', 'service2'],
            check=True
        )

    @patch('subprocess.run')
    def test_stop_services_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, [])
        
        result = self.service_manager.stop_services()
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_get_running_services(self, mock_run):
        mock_process = MagicMock()
        mock_process.stdout = "service1\nservice2\n"
        mock_run.return_value = mock_process
        
        services = self.service_manager.get_running_services()
        self.assertEqual(services, ['service1', 'service2'])
        mock_run.assert_called_with(
            ['docker-compose', '-f', self.compose_file, 'ps', '--services'],
            check=True,
            capture_output=True,
            text=True
        )

    @patch('subprocess.run')
    def test_get_running_services_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, [])
        
        services = self.service_manager.get_running_services()
        self.assertEqual(services, [])

    def test_update_activity(self):
        service = 'test_service'
        self.service_manager.update_activity(service)
        self.assertIn(service, self.service_manager.last_activity_time)
        self.assertIsInstance(self.service_manager.last_activity_time[service], float)

    @patch('sandbox_sdk.service_manager.ServiceManager.get_running_services')
    def test_is_service_running(self, mock_get_running):
        mock_get_running.return_value = ['service1', 'service2']
        
        self.assertTrue(self.service_manager.is_service_running('service1'))
        self.assertFalse(self.service_manager.is_service_running('service3'))

    @patch('asyncio.create_task')
    @patch('sandbox_sdk.service_manager.ServiceManager.get_running_services')
    def test_start_inactivity_monitoring(self, mock_get_running, mock_create_task):
        mock_get_running.return_value = ['service1', 'service2']
        mock_task = MagicMock()
        mock_create_task.return_value = mock_task
        
        self.service_manager._start_inactivity_monitoring()
        
        self.assertEqual(mock_create_task.call_count, 2)
        self.assertEqual(len(self.service_manager.shutdown_tasks), 2)
        self.assertIn('service1', self.service_manager.shutdown_tasks)
        self.assertIn('service2', self.service_manager.shutdown_tasks)

    @patch('time.time')
    @patch('sandbox_sdk.service_manager.ServiceManager.stop_services')
    async def test_monitor_inactivity(self, mock_stop, mock_time):
        service = 'test_service'
        self.service_manager.last_activity_time[service] = 100
        mock_time.return_value = 2000  # Well past the inactivity timeout
        
        # Run the monitoring for a short time
        task = asyncio.create_task(self.service_manager._monitor_inactivity(service))
        await asyncio.sleep(0.1)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        mock_stop.assert_called_with([service])

if __name__ == '__main__':
    unittest.main()