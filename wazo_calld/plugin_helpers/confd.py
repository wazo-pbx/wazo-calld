# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from requests import HTTPError
from requests import RequestException

from .exceptions import (
    InvalidUserUUID,
    InvalidUserLine,
    NoSuchConferenceID,
    NoSuchUserVoicemail,
    NoSuchVoicemail,
    UserMissingMainLine,
    WazoConfdUnreachable,
)


def not_found(error):
    return error.response is not None and error.response.status_code == 404


class User:

    # TODO set tenant_uuid mandatory when calls plugin will be multi-tenant
    def __init__(self, user_uuid, confd_client, tenant_uuid=None):
        self.uuid = user_uuid
        self.tenant_uuid = tenant_uuid
        self._confd = confd_client

    def main_line(self):
        try:
            lines = self._confd.users.get(self.uuid, tenant_uuid=self.tenant_uuid)['lines']
        except HTTPError as e:
            if not_found(e):
                raise InvalidUserUUID(self.uuid)
            raise
        except RequestException as e:
            raise WazoConfdUnreachable(self._confd, e)

        try:
            main_line_id = lines[0]['id']
        except IndexError:
            raise UserMissingMainLine(self.uuid)
        return Line(main_line_id, self._confd, tenant_uuid=self.tenant_uuid)

    def line(self, line_id):
        try:
            lines = self._confd.users.get(self.uuid, tenant_uuid=self.tenant_uuid)['lines']
        except HTTPError as e:
            if not_found(e):
                raise InvalidUserUUID(self.uuid)
            raise
        except RequestException as e:
            raise WazoConfdUnreachable(self._confd, e)

        valid_line_ids = [line['id'] for line in lines]
        if line_id not in valid_line_ids:
            raise InvalidUserLine(self.uuid, line_id)

        return Line(line_id, self._confd, tenant_uuid=self.tenant_uuid)

    def mobile_phone_number(self):
        try:
            return self._confd.users.get(self.uuid, tenant_uuid=self.tenant_uuid)['mobile_phone_number']
        except HTTPError as e:
            if not_found(e):
                raise InvalidUserUUID(self.uuid)
            raise
        except RequestException as e:
            raise WazoConfdUnreachable(self._confd, e)


class Line:

    # TODO set tenant_uuid mandatory when calls plugin will be multi-tenant
    def __init__(self, line_id, confd_client, tenant_uuid=None):
        self.id = line_id
        self._confd = confd_client
        self.tenant_uuid = tenant_uuid

    def _get(self):
        try:
            return self._confd.lines.get(self.id, tenant_uuid=self.tenant_uuid)
        except HTTPError:
            raise
        except RequestException as e:
            raise WazoConfdUnreachable(self._confd, e)

    def context(self):
        line = self._get()
        return line['context']

    def interface(self):
        line = self._get()
        # TODO PJSIP clean after migration
        protocol = line['protocol'].replace('sip', 'pjsip')
        return "{}/{}".format(protocol, line['name'])

    def interface_autoanswer(self):
        interface = self.interface()
        if interface.startswith('sccp/'):
            interface = '{}/autoanswer'.format(interface)
        return interface


class Conference:

    def __init__(self, tenant_uuid, conference_id, confd_client):
        self.tenant_uuid = tenant_uuid
        self.conference_id = conference_id
        self._confd = confd_client

    def exists(self):
        try:
            conferences = self._confd.conferences.list(tenant_uuid=self.tenant_uuid, recurse=True)['items']
        except RequestException as e:
            raise WazoConfdUnreachable(self._confd, e)
        return self.conference_id in (conference['id'] for conference in conferences)

    @classmethod
    def from_id(cls, conference_id, confd_client):
        try:
            conference = confd_client.conferences.get(conference_id)
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise NoSuchConferenceID(conference_id)
            raise
        return cls(conference['tenant_uuid'],
                   conference['id'],
                   confd_client)


def get_user_voicemail(user_uuid, confd_client):
    try:
        voicemail = confd_client.users.get(user_uuid)['voicemail']
        if not voicemail:
            raise NoSuchUserVoicemail(user_uuid)
        return voicemail
    except HTTPError as e:
        if not_found(e):
            raise NoSuchUserVoicemail(user_uuid)
        raise
    except RequestException as e:
        raise WazoConfdUnreachable(confd_client, e)


def get_voicemail(voicemail_id, confd_client):
    try:
        return confd_client.voicemails.get(voicemail_id)
    except HTTPError as e:
        if not_found(e):
            raise NoSuchVoicemail(voicemail_id)
        raise
    except RequestException as e:
        raise WazoConfdUnreachable(confd_client, e)
