# -*- coding: utf-8 -*-

# Copyright 2016 by Avencall
# SPDX-License-Identifier: GPL-3.0+

import ari
import logging

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import contains_inanyorder
from hamcrest import is_in
from hamcrest import has_entry
from hamcrest import has_entries
from hamcrest import has_key
from hamcrest import not_

from xivo_test_helpers import until

from .test_api.base import IntegrationTest

RECIPIENT = {
    'context': 'local',
    'exten': 'answer',
}
ENDPOINT = 'Local/answer@local'
STASIS_APP = 'callcontrol'
STASIS_APP_INSTANCE = 'integration-tests'
ARI_CONFIG = {
    'base_url': 'http://localhost:5039',
    'username': 'xivo',
    'password': 'xivo',
}

logging.getLogger('swaggerpy.client').setLevel(logging.INFO)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)


class TestTransfers(IntegrationTest):

    asset = 'real_asterisk'

    def setUp(self):
        super(TestTransfers, self).setUp()
        self.ari = ari.connect(**ARI_CONFIG)

    def is_in_bridge(self, type_=None):
        bridges = self.ari.bridges.list()
        if type_:
            bridges = (bridge for bridge in bridges if bridge.json['bridge_type'] == type_)
        channel_ids = (channel_id for bridge in bridges for channel_id in bridge.json['channels'])
        return is_in(list(channel_ids))

    def is_talking_to(self, channel_id):
        bridges = self.ari.bridges.list()
        bridges = (bridge for bridge in bridges
                   if (channel_id in bridge.json['channels'] and
                       bridge.json['bridge_type'] == 'mixing'))
        channel_ids = (channel_id for bridge in bridges for channel_id in bridge.json['channels'])
        return is_in(channel_ids)

    def is_talking(self):
        channels = self.ari.channels.list()
        channel_ids = (channel.id for channel in channels if channel.json['state'] == 'Up')
        return is_in(list(channel_ids))

    def is_hungup(self):
        return not_(is_in(channel.id for channel in self.ari.channels.list()))

    def bridged_call_stasis(self):
        caller = self.ari.channels.originate(endpoint=ENDPOINT,
                                             app=STASIS_APP,
                                             variables={'variables': {'XIVO_STASIS_ARGS': STASIS_APP_INSTANCE}})
        callee = self.ari.channels.originate(endpoint=ENDPOINT,
                                             app=STASIS_APP,
                                             variables={'variables': {'XIVO_STASIS_ARGS': STASIS_APP_INSTANCE}})
        bridge = self.ari.bridges.create(type='mixing')

        def channel_is_up(channel_id):
            return self.ari.channels.get(channelId=channel_id).json['state'] == 'Up'

        until.true(channel_is_up, caller.id)
        bridge.addChannel(channel=caller.id)
        until.true(channel_is_up, callee.id)
        bridge.addChannel(channel=callee.id)
        return caller.id, callee.id

    def answered_transfer(self):
        transferred_channel_id, initiator_channel_id = self.bridged_call_stasis()
        response = self.ctid_ng.create_transfer(transferred_channel_id,
                                                initiator_channel_id,
                                                **RECIPIENT)

        transfer_id = response['id']
        recipient_channel_id = response['recipient_call']

        def channel_is_in_bridge(channel_id, bridge_id):
            return channel_id in self.ari.bridges.get(bridgeId=bridge_id).json['channels']

        until.true(channel_is_in_bridge, recipient_channel_id, transfer_id, tries=3)

        return (transferred_channel_id,
                initiator_channel_id,
                recipient_channel_id,
                transfer_id)

    def test_given_state_ready_when_transfer_start_and_answer_then_state_answered(self):
        transferred_channel_id, initiator_channel_id = self.bridged_call_stasis()

        response = self.ctid_ng.create_transfer(transferred_channel_id,
                                                initiator_channel_id,
                                                **RECIPIENT)

        assert_that(response, all_of(has_entries({'transferred_call': transferred_channel_id,
                                                  'initiator_call': initiator_channel_id}),
                                     has_key('id'),
                                     has_key('recipient_call')))

        transfer_bridge_id = response['id']
        recipient_channel_id = response['recipient_call']

        def transfer_is_answered():
            transfer_bridge = self.ari.bridges.get(bridgeId=transfer_bridge_id)
            assert_that(transfer_bridge.json,
                        has_entry('channels',
                                  contains_inanyorder(
                                      transferred_channel_id,
                                      initiator_channel_id,
                                      recipient_channel_id
                                  )))
            assert_that(transferred_channel_id, self.is_talking(), 'transferred channel not talking')
            assert_that(initiator_channel_id, self.is_talking(), 'initiator channel not talking')
            assert_that(recipient_channel_id, self.is_talking(), 'recipient channel not talking')

        until.assert_(transfer_is_answered, tries=3)

    def test_given_state_ready_when_transfer_start_and_complete_then_state_completed(self):
        (transferred_channel_id,
         initiator_channel_id,
         recipient_channel_id,
         transfer_id) = self.answered_transfer()

        self.ctid_ng.complete_transfer(transfer_id)

        def transfer_is_completed():
            transfer_bridge = self.ari.bridges.get(bridgeId=transfer_id)
            assert_that(transfer_bridge.json,
                        has_entry('channels',
                                  contains_inanyorder(
                                      transferred_channel_id,
                                      recipient_channel_id
                                  )))
            assert_that(transferred_channel_id, self.is_talking(), 'transferred channel not talking')
            assert_that(recipient_channel_id, self.is_talking(), 'recipient channel not talking')
            assert_that(initiator_channel_id, self.is_hungup(), 'initiator channel is still talking')

        until.assert_(transfer_is_completed, tries=3)

    def test_given_state_ready_when_transfer_start_and_cancel_then_state_completed(self):
        (transferred_channel_id,
         initiator_channel_id,
         recipient_channel_id,
         transfer_id) = self.answered_transfer()

        self.ctid_ng.cancel_transfer(transfer_id)

        def transfer_is_cancelled():
            transfer_bridge = self.ari.bridges.get(bridgeId=transfer_id)
            assert_that(transfer_bridge.json,
                        has_entry('channels',
                                  contains_inanyorder(
                                      transferred_channel_id,
                                      initiator_channel_id
                                  )))
            assert_that(transferred_channel_id, self.is_talking(), 'transferred channel not talking')
            assert_that(initiator_channel_id, self.is_talking(), 'initiator channel is not talking')
            assert_that(recipient_channel_id, self.is_hungup(), 'recipient channel is still talking')

        until.assert_(transfer_is_cancelled, tries=3)
