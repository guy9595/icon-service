# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

from iconservice import IconServiceFlag
from iconservice.base.address import ZERO_SCORE_ADDRESS, GOVERNANCE_SCORE_ADDRESS
from iconservice.base.exception import InvalidParamsException, ScoreErrorException, ExceptionCode
from iconservice.icon_constant import REVISION_3
from tests import raise_exception_start_tag, raise_exception_end_tag
from tests.integrate_test.test_integrate_base import TestIntegrateBase


class TestIntegrateScores(TestIntegrateBase):

    def test_db_returns(self):
        tx1 = self._make_deploy_tx("test_scores",
                                   "test_db_returns",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS,
                                   deploy_params={"value": str(self._addr_array[1]),
                                                  "value1": str(self._addr_array[1])})

        prev_block, tx_results = self._make_and_req_block([tx1])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))
        score_addr1 = tx_results[0].score_address

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "get_value1",
                "params": {}
            }
        }
        response = self._query(query_request)
        self.assertEqual(response, 0)

        value = 1 * self._icx_factor
        tx2 = self._make_score_call_tx(self._addr_array[0], score_addr1, 'set_value1', {"value": hex(value)})

        prev_block, tx_results = self._make_and_req_block([tx2])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))

        response = self._query(query_request)
        self.assertEqual(response, value)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "get_value2",
                "params": {}
            }
        }
        response = self._query(query_request)
        self.assertEqual(response, "")

        value = "a"
        tx3 = self._make_score_call_tx(self._addr_array[0], score_addr1, 'set_value2', {"value": value})

        prev_block, tx_results = self._make_and_req_block([tx3])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))

        response = self._query(query_request)
        self.assertEqual(response, value)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "get_value3",
                "params": {}
            }
        }
        response = self._query(query_request)
        self.assertEqual(response, None)

        value = self._prev_block_hash
        tx4 = self._make_score_call_tx(self._addr_array[0], score_addr1, 'set_value3', {"value": bytes.hex(value)})

        prev_block, tx_results = self._make_and_req_block([tx4])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))

        response = self._query(query_request)
        self.assertEqual(response, value)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "get_value4",
                "params": {}
            }
        }
        response = self._query(query_request)
        self.assertEqual(response, self._addr_array[1])

        value = self._genesis
        tx5 = self._make_score_call_tx(self._addr_array[0], score_addr1, 'set_value4', {"value": str(value)})

        prev_block, tx_results = self._make_and_req_block([tx5])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))

        response = self._query(query_request)
        self.assertEqual(response, value)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "get_value5",
                "params": {}
            }
        }
        response = self._query(query_request)
        self.assertEqual(response, False)

        value = True
        tx6 = self._make_score_call_tx(self._addr_array[0], score_addr1, 'set_value5', {"value": hex(int(value))})

        prev_block, tx_results = self._make_and_req_block([tx6])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))

        response = self._query(query_request)
        self.assertEqual(response, value)

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "get_value6",
                "params": {}
            }
        }
        response = self._query(query_request)
        self.assertEqual(response, self._addr_array[1])

        value = self._genesis
        tx7 = self._make_score_call_tx(self._addr_array[0], score_addr1, 'set_value6', {"value": str(value)})

        prev_block, tx_results = self._make_and_req_block([tx7])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))

        response = self._query(query_request)
        self.assertEqual(response, value)

    def test_default_value_fail_install(self):
        tx1 = self._make_deploy_tx("test_scores",
                                   "test_default_value_fail1",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS)

        raise_exception_start_tag("test_default_value_fail_install")
        prev_block, tx_results = self._make_and_req_block([tx1])
        raise_exception_end_tag("test_default_value_fail_install")

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(False))
        score_addr1 = tx_results[0].score_address

    def test_default_value_fail_update(self):
        tx1 = self._make_deploy_tx("test_scores",
                                   "test_default_value_fail2",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS)

        raise_exception_start_tag("test_default_value_fail_update")
        prev_block, tx_results = self._make_and_req_block([tx1])
        raise_exception_end_tag("test_default_value_fail_update")

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(False))
        score_addr1 = tx_results[0].score_address

    def test_default_value_fail_external(self):
        tx1 = self._make_deploy_tx("test_scores",
                                   "test_default_value_fail3",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS)

        raise_exception_start_tag("test_default_value_fail_external")
        prev_block, tx_results = self._make_and_req_block([tx1])
        raise_exception_end_tag("test_default_value_fail_external")

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(False))
        score_addr1 = tx_results[0].score_address

    def test_service_flag(self):
        tx1 = self._make_deploy_tx("test_builtin",
                                   "latest_version/governance",
                                   self._admin,
                                   GOVERNANCE_SCORE_ADDRESS)

        prev_block, tx_results = self._make_and_req_block([tx1])
        self._write_precommit_state(prev_block)
        self.assertEqual(tx_results[0].status, int(True))

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": GOVERNANCE_SCORE_ADDRESS,
            "dataType": "call",
            "data": {
                "method": "getServiceConfig",
                "params": {}
            }
        }
        response = self._query(query_request)

        tx2 = self._make_deploy_tx("test_deploy_scores/install",
                                   "test_score",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS)

        table = {}
        for flag in IconServiceFlag:
            if flag.name is 'SCORE_PACKAGE_VALIDATOR':
                table[flag.name] = True
            else:
                table[flag.name] = False
        self.assertEqual(response, table)

        tx3 = self._make_score_call_tx(self._admin,
                                       GOVERNANCE_SCORE_ADDRESS,
                                       'updateServiceConfig',
                                       {"serviceFlag": hex(IconServiceFlag.AUDIT)})

        tx4 = self._make_deploy_tx("test_deploy_scores/install",
                                   "test_score",
                                   self._addr_array[1],
                                   ZERO_SCORE_ADDRESS)

        target_flag = IconServiceFlag.AUDIT | IconServiceFlag.FEE
        tx5 = self._make_score_call_tx(self._admin,
                                       GOVERNANCE_SCORE_ADDRESS,
                                       'updateServiceConfig',
                                       {"serviceFlag": hex(target_flag)})

        tx6 = self._make_deploy_tx("test_deploy_scores/install",
                                   "test_score",
                                   self._addr_array[1],
                                   ZERO_SCORE_ADDRESS)

        prev_block, tx_results = self._make_and_req_block([tx2, tx3, tx4, tx5, tx6])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))
        self.assertEqual(tx_results[1].status, int(True))
        self.assertEqual(tx_results[2].status, int(True))
        self.assertEqual(tx_results[3].status, int(True))
        self.assertEqual(tx_results[4].status, int(False))

        score_addr1 = tx_results[0].score_address
        score_addr2 = tx_results[2].score_address

        response = self._query(query_request)
        table = {}
        for flag in IconServiceFlag:
            if target_flag & flag == flag:
                table[flag.name] = True
            else:
                table[flag.name] = False
        self.assertEqual(response, table)

        query_request = {
            "address": score_addr1
        }
        self._query(query_request, 'icx_getScoreApi')

        query_request = {
            "address": score_addr2
        }
        with self.assertRaises(InvalidParamsException) as e:
            self._query(query_request, 'icx_getScoreApi')
        self.assertEqual(e.exception.args[0], f"SCORE is inactive: {score_addr2}")

    # case when readonly return type mismatched
    def test_return_type_revision_3(self):
        governance_update_tx = self._make_deploy_tx("test_builtin", "0_0_4/governance",
                                                    self._admin, GOVERNANCE_SCORE_ADDRESS)
        prev_block, tx_results = self._make_and_req_block([governance_update_tx])
        self._write_precommit_state(prev_block)
        self.assertEqual(tx_results[0].status, int(True))

        tx0 = self._make_score_call_tx(self._admin, GOVERNANCE_SCORE_ADDRESS,
                                       "setRevision", {"code": hex(REVISION_3), "name": "1.1.1"})
        prev_block, tx_results = self._make_and_req_block([tx0])
        self._write_precommit_state(prev_block)
        self.assertEqual(tx_results[0].status, int(True))

        tx1 = self._make_deploy_tx("test_scores",
                                   "test_db_returns_default_value",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS,
                                   deploy_params={})

        prev_block, tx_results = self._make_and_req_block([tx1])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))
        score_addr1 = tx_results[0].score_address

        method_format = "get_{}_value_{}_type"

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "",
                "params": {}
            }
        }

        type_list_for_int_value = ['str', 'bytes', 'address', 'bool', 'none']
        for t in type_list_for_int_value:
            query_request['data']['method'] = method_format.format('int', t)
            if t is 'bool':
                result = self._query(query_request)
                self.assertEqual(result, True)
            else:
                with self.assertRaises(ScoreErrorException)as e:
                    self._query(query_request)
                self.assertEqual(e.exception.code, ExceptionCode.SCORE_ERROR)

        type_list_for_bytes_value = ['int', 'str', 'address', 'bool', 'none']
        for t in type_list_for_bytes_value:
            query_request['data']['method'] = method_format.format('bytes', t)
            if t is 'none':
                result = self._query(query_request)
                self.assertEqual(result, None)
            else:
                with self.assertRaises(ScoreErrorException)as e:
                    self._query(query_request)
                self.assertEqual(e.exception.code, ExceptionCode.SCORE_ERROR)

        type_list_for_address_value = ['int', 'str', 'bytes', 'bool', 'none']
        for t in type_list_for_address_value:
            query_request['data']['method'] = method_format.format('address', t)
            if t is 'none':
                result = self._query(query_request)
                self.assertEqual(result, None)
            else:
                with self.assertRaises(ScoreErrorException)as e:
                    self._query(query_request)
                self.assertEqual(e.exception.code, ExceptionCode.SCORE_ERROR)

        for i in range(4, 6):
            type_list = ['int', 'bytes', 'none', 'address', 'str', 'bool']
            ret_type = type_list[i]
            del type_list[i]
            for t in type_list:
                method = method_format.format(ret_type, t)
                query_request['data']['method'] = method
                with self.assertRaises(ScoreErrorException) as e:
                    self._query(query_request)
                self.assertEqual(e.exception.code, ExceptionCode.SCORE_ERROR)

    # case when readonly return type mismatched
    def test_return_type_revision_lt_3(self):
        tx1 = self._make_deploy_tx("test_scores",
                                   "test_db_returns_default_value",
                                   self._addr_array[0],
                                   ZERO_SCORE_ADDRESS,
                                   deploy_params={})

        prev_block, tx_results = self._make_and_req_block([tx1])

        self._write_precommit_state(prev_block)

        self.assertEqual(tx_results[0].status, int(True))
        score_addr1 = tx_results[0].score_address

        method_format = "get_{}_value_{}_type"

        query_request = {
            "version": self._version,
            "from": self._admin,
            "to": score_addr1,
            "dataType": "call",
            "data": {
                "method": "",
                "params": {}
            }
        }

        for i in range(6):
            type_list = ['int', 'bytes', 'none', 'address', 'str', 'bool']
            ret_type = type_list[i]
            if i is 2: continue
            del type_list[i]
            for t in type_list:
                method = method_format.format(ret_type, t)
                query_request['data']['method'] = method
                self._query(query_request)


if __name__ == '__main__':
    unittest.main()
