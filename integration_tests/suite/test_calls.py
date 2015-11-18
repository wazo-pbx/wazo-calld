# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that, contains, has_entries

from .base import IntegrationTest


class TestListCalls(IntegrationTest):

    asset = 'basic_rest'

    def test_given_no_calls_when_list_calls_then_empty_list(self):
        calls = self.list_calls()

        assert_that(calls, contains())

    def test_given_some_calls_and_no_user_id_when_list_calls_then_list_calls_with_no_user_uuid(self):
        self.set_ari_channels([{
            'id': 'first-id'
        }, {
            'id': 'second-id'
        }])

        calls = self.list_calls()

        assert_that(calls, contains(
            has_entries({'call_id': 'first-id',
                         'user_uuid': None}),
            has_entries({'call_id': 'second-id',
                         'user_uuid': None})))
