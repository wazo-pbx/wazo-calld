# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_calld.exceptions import APIException


class CalldUninitializedError(APIException):

    def __init__(self):
        super().__init__(
            status_code=503,
            message='wazo-calld is not ready to handle this request',
            error_id='wazo-calld-uninitialized',
        )


class TooManyChannels(Exception):
    def __init__(self, channels):
        self.channels = channels


class NotEnoughChannels(Exception):
    pass


class NoSuchConferenceID(Exception):
    def __init__(self, conference_id):
        self.conference_id = conference_id
        super().__init__('No such conference ID "{}"'.format(conference_id))


class UserMissingMainLine(APIException):

    def __init__(self, user_uuid):
        super().__init__(
            status_code=400,
            message='User has no main line',
            error_id='user-missing-main-line',
            details={
                'user_uuid': user_uuid
            }
        )


class UserPermissionDenied(APIException):

    def __init__(self, user_uuid, details):
        details = dict(details)
        details['user'] = user_uuid
        super().__init__(
            status_code=403,
            message='User does not have permission to handle objects of other users',
            error_id='user-permission-denied',
            details=details
        )


class InvalidExtension(APIException):

    def __init__(self, context, exten):
        super().__init__(
            status_code=400,
            message='Invalid extension',
            error_id='invalid-extension',
            details={
                'context': context,
                'exten': exten,
            }
        )


class InvalidUserUUID(APIException):

    def __init__(self, user_uuid):
        super().__init__(
            status_code=400,
            message='Invalid user: not found',
            error_id='invalid-user',
            details={
                'user_uuid': user_uuid
            }
        )


class InvalidUserLine(APIException):

    def __init__(self, user_id, line_id):
        super().__init__(
            status_code=400,
            message='User has no such line',
            error_id='invalid-user-line',
            details={
                'user_id': user_id,
                'line_id': line_id,
            }
        )


class NoSuchUserVoicemail(APIException):

    def __init__(self, user_uuid):
        super().__init__(
            status_code=404,
            message='No such user voicemail',
            error_id='no-such-user-voicemail',
            details={
                'user_uuid': user_uuid,
            }
        )


class NoSuchVoicemail(APIException):

    def __init__(self, voicemail_id):
        super().__init__(
            status_code=404,
            message='No such voicemail',
            error_id='no-such-voicemail',
            details={
                'voicemail_id': voicemail_id,
            }
        )


class WazoAmidError(APIException):

    def __init__(self, wazo_amid_client, error):
        super().__init__(
            status_code=503,
            message='wazo-amid request error',
            error_id='wazo-amid-error',
            details={
                'wazo_amid_config': {'host': wazo_amid_client.host,
                                     'port': wazo_amid_client.port,
                                     'timeout': wazo_amid_client.timeout},
                'original_error': str(error),
            }
        )


class WazoConfdUnreachable(APIException):

    def __init__(self, confd_client, error):
        super().__init__(
            status_code=503,
            message='wazo-confd server unreachable',
            error_id='wazo-confd-unreachable',
            details={
                'wazo_confd_config': {'host': confd_client.host,
                                      'port': confd_client.port,
                                      'timeout': confd_client.timeout},
                'original_error': str(error),
            }
        )
