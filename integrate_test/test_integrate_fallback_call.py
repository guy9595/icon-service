# -*- coding: utf-8 -*-

# Copyright 2017-2018 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""IconScoreEngine testcase
"""

import unittest

from iconcommons.icon_config import IconConfig
from iconservice.base.address import AddressPrefix, ZERO_SCORE_ADDRESS
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey
from iconservice.icon_inner_service import IconScoreInnerTask
from tests import create_address, raise_exception_start_tag, raise_exception_end_tag
from integrate_test.test_integrate_base import TestIntegrateBase


class TestIntegrateFallbackCall(TestIntegrateBase):
    def setUp(self):
        super().setUp()
        self.sample_root = "test_fallback_call_scores"

        conf = IconConfig("", default_icon_config)
        conf.load()
        conf.update_conf({ConfigKey.BUILTIN_SCORE_OWNER: str(self._admin_addr)})

        self._inner_task = IconScoreInnerTask(conf)
        self._inner_task._open()

        is_commit, tx_results = self._run_async(self._genesis_invoke())
        self.assertEqual(is_commit, True)
        self.assertEqual(tx_results[0]['status'], hex(1))

    def test_score_pass(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_pass", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        value = 1 * self._icx_factor
        validate_tx_response2, tx2 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx2]))
        tx_result2 = self._get_tx_result(tx_results2, tx2)
        self.assertEqual(tx_result2['status'], hex(True))

        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(value))

    def test_score_send_to_eoa(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_to_eoa", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        tmp_addr = str(create_address(AddressPrefix.EOA))
        value = 1 * self._icx_factor

        validate_tx_response2, tx2 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr1, 'set_addr_func', {"addr": tmp_addr}))
        self.assertEqual(validate_tx_response2, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx2, tx3]))
        tx_result2 = self._get_tx_result(tx_results2, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": tmp_addr
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(value))

    def test_score_revert(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_revert", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        value = 1 * self._icx_factor

        validate_tx_response2, tx2 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response2, hex(0))

        raise_exception_start_tag("test_score_revert")
        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx2]))
        tx_result2 = self._get_tx_result(tx_results2, tx2)
        self.assertEqual(tx_result2['status'], hex(False))
        raise_exception_end_tag("test_score_revert")

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

    def test_score_no_payable(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_no_payable", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        value = 1 * self._icx_factor

        validate_tx_response2, tx2 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response2, hex(0))

        raise_exception_start_tag("test_score_no_payable")
        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx2]))
        tx_result2 = self._get_tx_result(tx_results2, tx2)
        self.assertEqual(tx_result2['status'], hex(False))
        raise_exception_end_tag("test_score_no_payable")

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

    def test_score_pass_link_transfer(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_pass", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_transfer", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_score_func', {"score_addr": score_addr1}))
        self.assertEqual(validate_tx_response3, hex(0))

        value = 1 * 10 ** 18
        validate_tx_response4, tx4 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4]))
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(True))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(value))

    def test_score_pass_link_send(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_pass", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_send", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_score_func', {"score_addr": score_addr1}))
        self.assertEqual(validate_tx_response3, hex(0))

        value = 1 * 10 ** 18
        validate_tx_response4, tx4 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4]))
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(True))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(value))

    def test_score_no_payable_link_transfer(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_no_payable", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_transfer", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_score_func', {"score_addr": score_addr1}))
        self.assertEqual(validate_tx_response3, hex(0))

        value = 1 * 10 ** 18
        validate_tx_response4, tx4 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        raise_exception_start_tag("test_score_no_payable_link_transfer")
        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4]))
        raise_exception_end_tag("test_score_no_payable_link_transfer")
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(False))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

    def test_score_no_payable_link_send(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_no_payable", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_send", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_score_func', {"score_addr": score_addr1}))
        self.assertEqual(validate_tx_response3, hex(0))

        value = 1 * 10 ** 18
        validate_tx_response4, tx4 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        raise_exception_start_tag("test_score_no_payable_link_send")
        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4]))
        raise_exception_end_tag("test_score_no_payable_link_send")
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(False))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

    def test_score_revert_link_transfer(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_revert", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_transfer", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_score_func', {"score_addr": score_addr1}))
        self.assertEqual(validate_tx_response3, hex(0))

        value = 1 * 10 ** 18
        validate_tx_response4, tx4 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        raise_exception_start_tag("test_score_revert_link_transfer")
        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4]))
        raise_exception_end_tag("test_score_revert_link_transfer")
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(False))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

    def test_score_revert_link_send(self):
        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_score_revert", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_send", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_score_func', {"score_addr": score_addr1}))
        self.assertEqual(validate_tx_response3, hex(0))

        value = 1 * 10 ** 18
        validate_tx_response4, tx4 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response3, hex(0))

        raise_exception_start_tag("test_score_revert_link_send")
        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4]))
        raise_exception_end_tag("test_score_revert_link_send")
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(False))
        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

    def test_fallback(self):
        query_request = {
            "address": str(self._genesis_addr)
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(100 * self._icx_factor))

        addr1 = create_address(AddressPrefix.EOA)
        addr2 = create_address(AddressPrefix.EOA)

        validate_tx_response1, tx1 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_send_A", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response1, hex(0))

        validate_tx_response2, tx2 = self._run_async(
            self._make_deploy_tx(self.sample_root, "test_link_score_send_B", ZERO_SCORE_ADDRESS, self._admin_addr))
        self.assertEqual(validate_tx_response2, hex(0))

        precommit_req1, tx_results1 = self._run_async(self._make_and_req_block([tx1, tx2]))

        tx_result1 = self._get_tx_result(tx_results1, tx1)
        self.assertEqual(tx_result1['status'], hex(True))
        score_addr1 = tx_result1['scoreAddress']

        tx_result2 = self._get_tx_result(tx_results1, tx2)
        self.assertEqual(tx_result2['status'], hex(True))
        score_addr2 = tx_result2['scoreAddress']

        response = self._run_async(self._write_precommit_state(precommit_req1))
        self.assertEqual(response, hex(0))

        validate_tx_response3, tx3 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr1, 'add_score_addr', {"score_addr": score_addr2}))
        self.assertEqual(validate_tx_response3, hex(0))

        validate_tx_response4, tx4 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr1, 'add_user_addr', {"eoa_addr": str(addr1)}))
        self.assertEqual(validate_tx_response4, hex(0))

        validate_tx_response5, tx5 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_user_addr1', {"eoa_addr": str(addr2)}))
        self.assertEqual(validate_tx_response5, hex(0))

        validate_tx_response6, tx6 = self._run_async(
            self._make_score_call_tx(self._admin_addr, score_addr2, 'add_user_addr2', {"eoa_addr": str(addr1)}))
        self.assertEqual(validate_tx_response6, hex(0))

        value = 20 * self._icx_factor
        validate_tx_response7, tx7 = self._run_async(
            self._make_icx_send_tx(self._genesis_addr, score_addr1, value))
        self.assertEqual(validate_tx_response7, hex(0))

        precommit_req2, tx_results2 = self._run_async(self._make_and_req_block([tx3, tx4, tx5, tx6, tx7]))
        tx_result3 = self._get_tx_result(tx_results2, tx3)
        self.assertEqual(tx_result3['status'], hex(True))
        tx_result4 = self._get_tx_result(tx_results2, tx4)
        self.assertEqual(tx_result4['status'], hex(True))
        tx_result5 = self._get_tx_result(tx_results2, tx5)
        self.assertEqual(tx_result5['status'], hex(True))
        tx_result6 = self._get_tx_result(tx_results2, tx6)
        self.assertEqual(tx_result6['status'], hex(True))
        tx_result7 = self._get_tx_result(tx_results2, tx7)
        self.assertEqual(tx_result7['status'], hex(True))

        response = self._run_async(self._write_precommit_state(precommit_req2))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr1
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": score_addr2
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(0))

        query_request = {
            "address": str(addr1)
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(15 * self._icx_factor))
        query_request = {
            "address": str(addr2)
        }

        response = self._run_async(self._query(query_request, 'icx_getBalance'))
        self.assertEqual(response, hex(5 * self._icx_factor))


if __name__ == '__main__':
    unittest.main()
