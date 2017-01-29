#!/usr/bin/env python2
'''
 Unit tests for oc secret add
'''
# To run:
# ./oc_secret_add.py
#
# .
# Ran 1 test in 0.002s
#
# OK

import os
import sys
import unittest
import mock

# Removing invalid variable names for tests so that I can
# keep them brief
# pylint: disable=invalid-name,no-name-in-module
# Disable import-error b/c our libraries aren't loaded in jenkins
# pylint: disable=import-error,wrong-import-position
# place class in our python path
module_path = os.path.join('/'.join(os.path.realpath(__file__).split('/')[:-4]), 'library')  # noqa: E501
sys.path.insert(0, module_path)
from oc_secret_add import OCSecretAdd  # noqa: E402


class OCSecretAddTest(unittest.TestCase):
    '''
     Test class for OCSecretAdd
    '''

    def setUp(self):
        ''' setup method will create a file and set to known configuration '''
        pass

    @mock.patch('oc_secret_add.OCSecretAdd._run')
    def test_adding_a_secret(self, mock_cmd):
        ''' Testing adding a secret to a service account '''

        # Arrange

        # run_ansible input parameters
        params = {
            'state': 'present',
            'namespace': 'default',
            'secrets': ['builder-dockercfg-rsrua', 'builder-token-akqxi', 'newsecret'],
            'service_account': 'builder',
            'kubeconfig': '/etc/origin/master/admin.kubeconfig',
            'debug': False,
        }

        oc_get_sa_before = '''{
            "kind": "ServiceAccount",
            "apiVersion": "v1",
            "metadata": {
                "name": "builder",
                "namespace": "default",
                "selfLink": "/api/v1/namespaces/default/serviceaccounts/builder",
                "uid": "cf47bca7-ebc4-11e6-b041-0ed9df7abc38",
                "resourceVersion": "302879",
                "creationTimestamp": "2017-02-05T17:02:00Z"
            },
            "secrets": [
                {
                    "name": "builder-dockercfg-rsrua"
                },
                {
                    "name": "builder-token-akqxi"
                }

            ],
            "imagePullSecrets": [
                {
                    "name": "builder-dockercfg-rsrua"
                }
            ]
        }
        '''

        oc_get_sa_after = '''{
            "kind": "ServiceAccount",
            "apiVersion": "v1",
            "metadata": {
                "name": "builder",
                "namespace": "default",
                "selfLink": "/api/v1/namespaces/default/serviceaccounts/builder",
                "uid": "cf47bca7-ebc4-11e6-b041-0ed9df7abc38",
                "resourceVersion": "302879",
                "creationTimestamp": "2017-02-05T17:02:00Z"
            },
            "secrets": [
                {
                    "name": "builder-dockercfg-rsrua"
                },
                {
                    "name": "builder-token-akqxi"
                },
                {
                    "name": "newsecret"
                }

            ],
            "imagePullSecrets": [
                {
                    "name": "builder-dockercfg-rsrua"
                }
            ]
        }
        '''

        # Return values of our mocked function call. These get returned once per call.
        mock_cmd.side_effect = [
            (0, oc_get_sa_before, ''), # First call to the mock
            (0, oc_get_sa_before, ''), # Second call to the mock
            (0, 'serviceaccount "builder" replaced', ''), # Third call to the mock
            (0, oc_get_sa_after, ''), # Fourth call to the mock
        ]

        # Act
        results = OCSecretAdd.run_ansible(params, False)

        # Assert
        self.assertTrue(results['changed'])
        self.assertEqual(results['results']['returncode'], 0)
        self.assertEqual(results['state'], 'present')

        # Making sure our mock was called as we expected
        mock_cmd.assert_has_calls([
            mock.call(['oc', '-n', 'default', 'get', 'sa', 'builder', '-o', 'json'], None),
            mock.call(['oc', '-n', 'default', 'get', 'sa', 'builder', '-o', 'json'], None),
            mock.call(['oc', '-n', 'default', 'replace', '-f', '/tmp/builder'], None),
            mock.call(['oc', '-n', 'default', 'get', 'sa', 'builder', '-o', 'json'], None)
        ])

    def tearDown(self):
        '''TearDown method'''
        pass


if __name__ == "__main__":
    unittest.main()
