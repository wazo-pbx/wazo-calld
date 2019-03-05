# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from .schemas import fax_schema

logger = logging.getLogger(__name__)


class FaxesBusEventHandler:

    def __init__(self, notifier):
        self._notifier = notifier

    def subscribe(self, bus_consumer):
        bus_consumer.on_ami_event('UserEvent', self._fax_result)

    def _fax_result(self, event):
        if event['UserEvent'] != 'FaxProgress':
            return

        fax_infos = {
            'context': event['WAZO_FAX_DESTINATION_CONTEXT'],
            'extension': event['WAZO_FAX_DESTINATION_EXTENSION'],
            'caller_id': event['WAZO_FAX_CALLER_ID'],
            'call_id': event['Uniqueid'],
            'id': event['Uniqueid'],
        }
        fax = fax_schema.dump(fax_infos).data
        if event['STATUS'] == 'SUCCESS':
            self._notifier.notify_fax_succeeded(fax)
        elif event['STATUS'] == 'FAILED':
            fax['error'] = event['ERROR']
            self._notifier.notify_fax_failed(fax)
