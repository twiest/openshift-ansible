# pylint: skip-file

class OCSecretAdd(OpenShiftCLI):
    ''' Class to wrap the oc command line tools '''

    kind = 'sa'
    # pylint allows 5. we need 6
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config,
                 verbose=False):
        ''' Constructor for OpenshiftOC '''
        super(OCSecretAdd, self).__init__(config.namespace, config.kubeconfig)
        self.config = config
        self.verbose = verbose
        self._service_account = None

    @property
    def service_account(self):
        ''' Property for the yed var '''
        if not self._service_account:
            self.get()
        return self._service_account

    @service_account.setter
    def service_account(self, data):
        ''' setter for the yed var '''
        self._service_account = data

    def exists(self, in_secret):
        ''' return whether a key, value  pair exists '''
        result = self.service_account.find_secret(in_secret)
        if not result:
            return False
        return True

    def get(self):
        '''return a environment variables '''
        env = self._get(OCSecretAdd.kind, self.config.name)
        if env['returncode'] == 0:
            self.service_account = ServiceAccount(content=env['results'][0])
            env['results'] = self.service_account.get('secrets')
        return env

    def delete(self):
        '''delete secrets '''

        modified = []
        for rem_secret in self.service_account.secrets:
            modified.append(self.service_account.delete_secret(rem_secret))

        if any(modified):
            return self._replace_content(OCSecretAdd.kind, self.config.name, self.service_account.yaml_dict)

        return {'returncode': 0, 'changed': False}

    def put(self):
        '''place secrets into sa '''
        modified = False
        for add_secret in self.config.secrets:
            if not self.service_account.find_secret(add_secret):
                self.service_account.add_secret(add_secret)
                modified = True

        if modified:
            return self._replace_content(OCSecretAdd.kind, self.config.name, self.service_account.yaml_dict)

        return {'returncode': 0, 'changed': False}


    @staticmethod
    # pylint: disable=too-many-return-statements,too-many-branches
    # TODO: This function should be refactored into its individual parts.
    def run_ansible(params, check_mode):
        '''run the ansible idempotent code'''

        sconfig = ServiceAccountConfig(params['service_account'],
                                       params['namespace'],
                                       params['kubeconfig'],
                                       params['secrets'],
                                       None)

        oc_secret_add = OCSecretAdd(sconfig,
                                    verbose=params['debug'])

        state = params['state']

        api_rval = oc_secret_add.get()

        #####
        # Get
        #####
        if state == 'list':
            return {'changed': False, 'results': api_rval['results'], 'state': "list"}

        ########
        # Delete
        ########
        if state == 'absent':
            for secret in params.get('secrets', []):
                if oc_secret_add.exists(secret):

                    if check_mode:
                        return {'changed': True, 'msg': 'Would have performed a delete.'}

                    api_rval = oc_secret_add.delete()

                    return {'changed': True, 'results': api_rval, 'state': "absent"}

            return {'changed': False, 'state': "absent"}

        if state == 'present':
            ########
            # Create
            ########
            for secret in params.get('secrets', []):
                if not oc_secret_add.exists(secret):

                    if check_mode:
                        return {'changed': True, 'msg': 'Would have performed a create.'}

                    # Create it here
                    api_rval = oc_secret_add.put()
                    if api_rval['returncode'] != 0:
                        return {'failed': True, 'msg': api_rval}

                    # return the created object
                    api_rval = oc_secret_add.get()

                    if api_rval['returncode'] != 0:
                        return {'failed': True, 'msg': api_rval}

                    return {'changed': True, 'results': api_rval, 'state': "present"}


            return {'changed': False, 'results': api_rval, 'state': "present"}


        return {'failed': True,
                'changed': False,
                'msg': 'Unknown state passed. %s' % state,
                'state': 'unknown'}
