
import requests
import json
import inspect
import sys
import xml.etree.ElementTree as ET
import ast

def _clean_server_name(server_name):
    # strip whitespace from beginning and ending
    cleaned_server_name = server_name.strip()
    # make sure last character is a '/'
    if (cleaned_server_name[-1] != '/'):
        cleaned_server_name = cleaned_server_name + '/'
    # make sure the server name string is prefaced with an 'https://'
    # if not already otherwise prefaced
    if (cleaned_server_name.find('http') == -1):
        cleaned_server_name = 'https://' + cleaned_server_name

    return cleaned_server_name

class XnatAccess(object):
    """Class for interacting with XNAT DB"""
    def __init__(self, server, user, password):
        super(XnatAccess, self).__init__()
        self._server = _clean_server_name(server)
        self._user = user
        self._password = password

    def get_new_tokens(self):
        request_url = self.server + 'data/services/tokens/issue'
        response = requests.get(request_url, auth=(self.user, self.password))
        token = json.loads(response.text)
        token_username = token['alias']
        token_password = token['secret']
        return token_username, token_password

    def _get_catalog_response_list(self, request_url, attrib_id):
        response_list = list()
        
        response = requests.get(request_url, auth=(self.user, self.password))
        
        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get response from request: " + request_url)
            sys.exit(1)

        if not 'text/xml' in response.headers['content-type']:
            print(inspect.stack()[0][3] + ": Unexpected response content-type: " + response.headers['content-type'] + " from " + request_url)
            sys.exit(1)

        root = ET.fromstring(response.text)

        for child in root:
            if child.tag == "{http://nrg.wustl.edu/catalog}entries":
                entries = child
                for entry in child:
                    entry_dict = ast.literal_eval(str(entry.attrib))
                    response_list.append(entry_dict[attrib_id])

        return response_list

    def _get_json_response_list(self, request_url, key):
        response_list = list()

        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get response from request: " + request_url)
            sys.exit(1)

        if not 'application/json' in response.headers['content-type']:
            print(inspect.stack()[0][3] + ": Unexpected response content-type: " + response.headers['content-type'] + " from " + request_url)
            sys.exit(1)

        json_response = json.loads(response.text)
        json_result_set = json_response['ResultSet']
        json_record_count = int(json_result_set['totalRecords'])
        json_result = json_result_set['Result']

        for i in xrange(0, json_record_count):
            item = str(json_result[i][key])
            response_list.append(item)

        return response_list

    def _get_json_response_list_of_lists(self, request_url, keys):
        response_list = list()
        
        response = requests.get(request_url, auth=(self.user, self.password))
        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get response from request: " + request_url)
            sys.exit(1)

        if not 'application/json' in response.headers['content-type']:
            print(inspect.stack()[0][3] + ": Unexpected response content-type: " + response.headers['content-type'] + " from " + request_url)
            sys.exit(1)

        json_response = json.loads(response.text)
        json_result_set = json_response['ResultSet']
        json_record_count = int(json_result_set['totalRecords'])
        json_result = json_result_set['Result']

        for i in xrange(0, json_record_count):
            item_list = list()
            for key in keys:
                item_list.append(str(json_result[i][key]))
            response_list.append(item_list)

        return response_list

    def get_server(self):
        return self._server

    server=property(get_server)

    def get_user(self):
        return self._user

    user=property(get_user)

    def get_password(self):
        return self._password

    password=property(get_password)

    def get_jsession_id(self):
        request_url = self._server + 'data/JSESSION'

        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get response from request: " + request_url)
            sys.exit(1)

        return response.text

    def get_project_id_list(self):
        """Get the list of valid project ids for the XNAT server."""
        request_url = self._server + 'data/projects'

        try:
            project_id_list = self._get_json_response_list(request_url, 'id')
        except KeyError:
            project_id_list = self._get_json_response_list(request_url, 'ID')
			
        return project_id_list

    def get_project(self):
        if (not self._project):
            print(inspect.stack()[0][3] + ": Cannot retrieve project because it is unset")
            sys.exit(1)
        return self._project
    
    def set_project(self, new_project):
        project_id_list = self.get_project_id_list()
        if not new_project in project_id_list:
            print(inspect.stack()[0][3] + ": Specified project: " + new_project + " not in valid project list for server: " + self.server)
            sys.exit(1)
        self._project = new_project

    project=property(get_project, set_project, doc="Current XNAT Project")

    def get_subject_label_list(self):
        """Get the list of valid subject labels for the current project."""
        request_url = self.server + 'data/projects/' + self.project + '/subjects'
        subject_label_list = self._get_json_response_list(request_url, 'label')
        return subject_label_list

    def get_subject(self):
        if (not self._subject):
            print(inspect.stack()[0][3] + ": Cannot retrieve subject because it is unset")
            sys.exit(1)
        return self._subject

    def set_subject(self, new_subject):
        subject_label_list = self.get_subject_label_list()
        if not new_subject in subject_label_list:
            print(inspect.stack()[0][3] + ": Specified subject: " + new_subject + " not in valid subject list for project: " + self._project)
            sys.exit(1)
        self._subject = new_subject

    subject=property(get_subject, set_subject, doc="Current XNAT Subject within Project")

    def get_session_label_list(self):
        """Get the list of valid session labels for the current subject."""
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments'
        session_label_list = self._get_json_response_list(request_url, 'label')
        return session_label_list

    def get_session_type(self, session_label):
        session_and_type_list = list()
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments'
        session_and_type_list = self._get_json_response_list_of_lists(request_url, ['label', 'xsiType'])

        for session_and_type in session_and_type_list:
            if session_label == session_and_type[0]:
                return session_and_type[1]

        print(inspect.stack()[0][3] + ": Specified session_label: " + session_label + " not found")
        sys.exit(1)

    def get_session(self):
        if (not self._session):
            print(inspect.stack()[0][3] + ": Cannot retrieve session because it is unset")
            sys.exit(1)
        return self._session

    def set_session(self, new_session):
        session_label_list = self.get_session_label_list()
        if not new_session in session_label_list:
            print(inspect.stack()[0][3] + ": Specified session: " + new_session + " not in valid session label list for subject: " + self._subject)
            sys.exit(1)
        self._session = new_session

    session=property(get_session, set_session, doc="Current Session/Experiment for the Subject")

    def get_xnat_session_id(self):
        session_and_session_id_list = list()
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/'
        session_and_session_id_list = self._get_json_response_list_of_lists(request_url, ['label', 'ID'])

        for session_and_session_id in session_and_session_id_list:
            if self.session == session_and_session_id[0]:
                return session_and_session_id[1]

        print(inspect.stack()[0][3] + ": Current session: " + self.session + " not found")
        sys.exit(1)


    xnat_session_id=property(get_xnat_session_id)

    def get_scan_id_list(self):
        """Get the list of valid scan ids for the session."""
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/scans'
        scan_id_list = self._get_json_response_list(request_url, 'ID')
        return scan_id_list

    def get_scan(self):
        if (not self._scan):
            print(inspect.stack()[0][3] + ": Cannot retrieve scan because it is unset")
            sys.exit(1)
        return self._scan

    def set_scan(self, new_scan):
        scan_id_list = self.get_scan_id_list()
        if not new_scan in scan_id_list:
            print(inspect.stack()[0][3] + ": Specified scan: " + new_scan + " not in valid scan id list for session: " + self._session)
            sys.exit(1)
        self._scan = new_scan

    scan=property(get_scan, set_scan, doc="Current Scan for the Session")

    def get_resource_label_list(self):
        """Get a list of valid resource ids for the session."""
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/resources'
        resource_label_list = self._get_json_response_list(request_url, 'label')
        return resource_label_list

    def does_resource_exist(self, resource_label):
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/resources'
        resource_label_list = self._get_json_response_list(request_url, 'label')
        if resource_label in resource_label_list :
            return True
        else :
            return False

    def get_resource(self):
        if (not self._resource):
            print(inspect.stack()[0][3] + ": Cannot retrieve resource because it is unset")
            sys.exit(1)
        return self._resource

    def set_resource(self, new_resource):
        resource_label_list = self.get_resource_label_list()
        if not new_resource in resource_label_list:
            print(inspect.stack()[0][3] + ": Specified resource: " + new_resource + " not in valid resource list for session: " + self._session)
            sys.exit(1)
        self._resource = new_resource

    resource=property(get_resource, set_resource, doc="Current Resource for the Session")

    def get_resource_file_name_list(self):
        """Get a list of file names for the Resource."""
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/resources/' + self.resource
        resource_file_name_list = self._get_catalog_response_list(request_url, 'name')
        return resource_file_name_list
    
    def get_named_resource_file_content(self, file_name):
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/resources/' + self.resource + '/files/' + file_name
        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get file: " + file_name + " from resource: " + self.resource)
            sys.exit(1)

        return response.text

    def get_scan_data_field_value(self, scan_number, data_field_name):
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/scans/' + str(scan_number) + "?format=json"
        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get scan data for scan number: " + scan_number)
            sys.exit(1)

        json_response = json.loads(response.text)
        # json_response is a dict with one entry under the key 'items'
        json_items = json_response['items']
        # json_items is a list with one item in it
        json_item = json_items[0]
        # json_item is a dict, we find the data we want under the key 'data_fields'
        data_fields = json_item['data_fields']

        # data_fields is a dict, we find the value we want under the specified data_field_name
        return data_fields[data_field_name]

    def show_scan_data_fields(self, scan_number):
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/scans/' + str(scan_number) + "?format=json"
        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get scan data for scan number: " + scan_number)
            sys.exit(1)

        json_response = json.loads(response.text)
        # json_response is a dict with one entry under the key 'items'
        json_items = json_response['items']
        # json_items is a list with one item in it
        json_item = json_items[0]
        # json_item is a dict, we find the data we want under the key 'data_fields'
        data_fields = json_item['data_fields']
        # data_fields is a dict, we cycle through the dict
        print("data_fields for scan number: " + scan_number)
        for key in data_fields.keys():
            print("key: " + key + "\tval: " + str(data_fields[key]))

    def get_scan_meta_value(self, scan_number, meta_value_name):
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/scans/' + str(scan_number) + "?format=json"
        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get scan data for scan number: " + scan_number)
            sys.exit(1)

        json_response = json.loads(response.text)
        # json_response is a dict with one entry under the key 'items'
        json_items = json_response['items']
        # json_items is a list with one item in it
        json_item = json_items[0]
        # json_item is a dict, we find the data we want under the key 'meta'
        meta = json_item['meta']
        # meta is a dict, we find the value we want under the specified meta_value_name
        return meta[meta_value_name]

    def show_scan_meta(self, scan_number):
        request_url = self.server + 'data/projects/' + self.project + '/subjects/' + self.subject + '/experiments/' \
            + self.session + '/scans/' + str(scan_number) + "?format=json"
        response = requests.get(request_url, auth=(self.user, self.password))

        if (response.status_code != 200):
            print(inspect.stack()[0][3] + ": Cannot get scan data for scan number: " + scan_number)
            sys.exit(1)

        json_response = json.loads(response.text)
        # json_response is a dict with one entry under the key 'items'
        json_items = json_response['items']
        # json_items is a list with one item in it
        json_item = json_items[0]
        # json_item is a dict, we find the data we want under the key 'meta'
        meta = json_item['meta']
        # meta is a dict, we cycle through the dict
        print("meta for scan number: " + scan_number)
        for key in meta.keys():
            print("key: " + key + "\tval: " + str(meta[key]))
