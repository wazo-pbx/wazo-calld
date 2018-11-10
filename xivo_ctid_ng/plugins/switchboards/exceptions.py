# Copyright 2017 The Wazo Authors  (see AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_ctid_ng.exceptions import APIException


class NoSuchSwitchboard(APIException):

    def __init__(self, switchboard_uuid):
        super(NoSuchSwitchboard, self).__init__(
            status_code=404,
            message='No such switchboard',
            error_id='no-such-switchboard',
            details={
                'switchboard_uuid': switchboard_uuid
            }
        )


class NoSuchCall(APIException):

    def __init__(self, call_id):
        super(NoSuchCall, self).__init__(
            status_code=404,
            message='No such call',
            error_id='no-such-call',
            details={
                'call_id': call_id
            }
        )
