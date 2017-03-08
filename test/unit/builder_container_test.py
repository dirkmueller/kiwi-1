from mock import patch
from mock import call
import mock
import kiwi

from .test_helper import raises

from kiwi.builder.container import ContainerBuilder
from kiwi.exceptions import KiwiContainerBuilderError


class TestContainerBuilder(object):
    @patch('platform.machine')
    def setup(self, mock_machine):
        mock_machine.return_value = 'x86_64'
        self.xml_state = mock.Mock()
        self.xml_state.build_type.get_derived_from.return_value = None
        self.container_config = {
            'container_name': 'my-container',
            'entry_command': ["--config.cmd='/bin/bash'"]
        }
        self.xml_state.get_container_config = mock.Mock(
            return_value=self.container_config
        )
        self.xml_state.get_image_version = mock.Mock(
            return_value='1.2.3'
        )
        self.xml_state.get_build_type_name = mock.Mock(
            return_value='docker'
        )
        self.xml_state.xml_data.get_name = mock.Mock(
            return_value='image_name'
        )
        self.setup = mock.Mock()
        kiwi.builder.container.SystemSetup = mock.Mock(
            return_value=self.setup
        )
        self.container = ContainerBuilder(
            self.xml_state, 'target_dir', 'root_dir'
        )
        self.container.result = mock.Mock()

    @raises(KiwiContainerBuilderError)
    def test_init_remote_base_uri(self):
        self.xml_state.build_type.get_derived_from.return_value = \
            'http://example.org/image.tar.xz'
        ContainerBuilder(
            self.xml_state, 'target_dir', 'root_dir'
        )

    def test_init_derived(self):
        self.xml_state.build_type.get_derived_from.return_value = \
            'file:///image.tar.xz'
        builder = ContainerBuilder(
            self.xml_state, 'target_dir', 'root_dir'
        )
        assert builder.base_image == 'root_dir/image/image.tar.xz'

    @patch('kiwi.builder.container.ContainerSetup')
    @patch('kiwi.builder.container.ContainerImage')
    def test_create(self, mock_image, mock_setup):
        container_setup = mock.Mock()
        mock_setup.return_value = container_setup
        container_image = mock.Mock()
        mock_image.return_value = container_image
        self.setup.export_rpm_package_verification.return_value = '.verified'
        self.setup.export_rpm_package_list.return_value = '.packages'
        self.container.create()
        mock_setup.assert_called_once_with(
            'docker', 'root_dir', self.container_config
        )
        container_setup.setup.assert_called_once_with()
        mock_image.assert_called_once_with(
            'docker', 'root_dir', self.container_config
        )
        container_image.create.assert_called_once_with(
            'target_dir/image_name.x86_64-1.2.3.docker.tar.xz', None
        )
        assert self.container.result.add.call_args_list == [
            call(
                key='container',
                filename='target_dir/image_name.x86_64-1.2.3.docker.tar.xz',
                use_for_bundle=True,
                compress=False,
                shasum=True
            ),
            call(
                key='image_packages',
                filename='.packages',
                use_for_bundle=True,
                compress=False,
                shasum=False
            ),
            call(
                key='image_verified',
                filename='.verified',
                use_for_bundle=True,
                compress=False,
                shasum=False
            )
        ]
        self.setup.export_rpm_package_verification.assert_called_once_with(
            'target_dir'
        )
        self.setup.export_rpm_package_list.assert_called_once_with(
            'target_dir'
        )
