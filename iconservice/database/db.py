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

import plyvel

from iconservice.base.address import Address
from iconservice.base.exception import DatabaseException
from iconservice.iconscore.icon_score_context import ContextGetter
from iconservice.iconscore.icon_score_context import IconScoreContextType
from iconservice.utils import sha3_256
from iconservice.logger.logger import Logger
from iconservice.icon_config import *

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from iconservice.iconscore.icon_score_context import IconScoreContext


def _get_context_type(context: 'IconScoreContext') -> 'IconScoreContextType':
    if context is None:
        return IconScoreContextType.DIRECT
    else:
        return context.type


class PlyvelDatabase(object):
    """Plyvel database wrapper
    """

    @staticmethod
    def make_db(path: str, create_if_missing: bool=True) -> plyvel.DB:
        Logger.debug(f'make_db path : {path}')
        return plyvel.DB(path, create_if_missing=create_if_missing)

    def __init__(self, db: plyvel.DB) -> None:
        """Constructor

        :param path: db directory path
        """
        self._db = db

    def get(self, key: bytes) -> bytes:
        """Get value from db using key

        :param key: db key
        :return: value indicated by key otherwise None
        """
        return self._db.get(key)

    def put(self, key: bytes, value: bytes) -> None:
        """Put value into db using key.

        :param key: (bytes): db key
        :param value: (bytes): db에 저장할 데이터
        """
        self._db.put(key, value)

    def delete(self, key: bytes) -> None:
        """Delete a row

        :param key: delete the row indicated by key.
        """
        self._db.delete(key)

    def close(self) -> None:
        """Close db
        """
        if self._db:
            self._db.close()
            self._db = None

    def get_sub_db(self, key: bytes):
        """Get Prefixed db

        :param key: (bytes): prefixed_db key
        """

        return PlyvelDatabase(self._db.prefixed_db(key))

    def iterator(self) -> iter:
        return self._db.iterator()

    def write_batch(self, states: dict) -> None:
        """bulk data modification

        :param states: key:value pairs
            key and value should be bytes type
        """
        if states is None or len(states) == 0:
            return

        with self._db.write_batch() as wb:
            for key, value in states.items():
                if value:
                    wb.put(key, value)
                else:
                    wb.delete(key)


class DatabaseObserver(object):
    """ An abstract class of database observer.
    """

    def __init__(self, put_func: callable, delete_func: callable):
        self.__put_func = put_func
        self.__delete_func = delete_func

    def on_put(self,
               context: 'IconScoreContext',
               key: bytes,
               old_value: bytes,
               new_value: bytes):
        """Invoked when `put` is called in `ContextDatabase`.

        :param context: SCORE context
        :param key: key
        :param old_value: old value
        :param new_value: new value
        """
        if not self.__put_func:
            Logger.warning('__put_func is None', ICON_DB_LOG_TAG)
        self.__put_func(context, key, old_value, new_value)

    def on_delete(self,
                  context: 'IconScoreContext',
                  key: bytes,
                  old_value: bytes):
        """Invoked when `delete` is called in `ContextDatabase`.


        :param context: SCORE context
        :param key: key
        :param old_value:
        """
        if not self.__delete_func:
            Logger.warning('__delete_func is None', ICON_DB_LOG_TAG)
        self.__delete_func(context, key, old_value)


class ContextDatabase(PlyvelDatabase):
    """Database for an IconScore only used in the inside of iconservice.

    IconScore can't access this database directly.
    Cache + LevelDB
    """

    def __init__(self,
                 db: plyvel.DB,
                 address: Address) -> None:
        """Constructor

        :param plyvel_db:
        :param address: the address of IconScore 
        """
        super().__init__(db)
        self.address = address

    def get(self, context: 'IconScoreContext', key: bytes) -> bytes:
        """Returns value indicated by key from batch or StateDB

        :param context:
        :param key:
        :return: value
        """
        context_type = _get_context_type(context)

        if context_type == IconScoreContextType.INVOKE:
            return self.get_from_batch(context, key)
        else:
            return super().get(key)

    def get_from_batch(self,
                       context: 'IconScoreContext',
                       key: bytes) -> bytes:
        """Returns a value for a given key

        Search order
        1. TransactionBatch
        2. BlockBatch
        3. StateDB

        :param key:

        :return: a value for a given key
        """
        block_batch = context.block_batch
        tx_batch = context.tx_batch

        # get value from tx_batch
        icon_score_batch = tx_batch[self.address]
        if icon_score_batch:
            value = icon_score_batch.get(key, None)
            if value:
                return value

        # get value from block_batch
        icon_score_batch = block_batch[self.address]
        if icon_score_batch:
            value = icon_score_batch.get(key, None)
            if value:
                return value

        # get value from state_db
        return super().get(key)

    def put(self,
            context: 'IconScoreContext',
            key: bytes,
            value: bytes) -> None:
        """put value to StateDB or catch according to contex type

        :param context:
        :param key:
        :param value:
        """
        context_type = _get_context_type(context)

        if context_type == IconScoreContextType.QUERY:
            raise DatabaseException('put is not allowed')
        elif context_type == IconScoreContextType.INVOKE:
            self.put_to_batch(context, key, value)
        else:
            super().put(key, value)

    def put_to_batch(self, context: 'IconScoreContext', key: bytes, value: bytes):
        context.tx_batch.put(self.address, key, value)

    def delete(self, context: 'IconScoreContext', key: bytes):
        """Delete key from db

        :param context:
        :param key: key to delete from db
        """
        context_type = _get_context_type(context)

        if context_type == IconScoreContextType.QUERY:
            raise DatabaseException('delete is not allowed')
        elif context_type == IconScoreContextType.INVOKE:
            self.put_to_batch(context, key, None)
        else:
            super().delete(key)

    def close(self, context: 'IconScoreContext') -> None:
        """close db

        :param context:
        """
        context_type = _get_context_type(context)

        if context_type == IconScoreContextType.QUERY:
            raise DatabaseException(
                'close is not allowed on readonly context')

        return super().close()

    def write_batch(self,
                    context: 'IconScoreContext',
                    states: dict):
        context_type = _get_context_type(context)

        if context_type == IconScoreContextType.QUERY:
            raise DatabaseException(
                'write_batch is not allowed on readonly context')

        return super().write_batch(states)

    @staticmethod
    def from_address_and_path(
            address: Optional['Address'],
            path: str,
            create_if_missing=True) -> 'ContextDatabase':
        return ContextDatabase(
            PlyvelDatabase.make_db(path, create_if_missing),
            address)


class IconScoreDatabase(ContextGetter):
    """It is used in IconScore

    IconScore can access its states only through IconScoreDatabase
    """
    def __init__(self, context_db: 'ContextDatabase', prefix: bytes=b'') -> None:
        """Constructor

        :param context_db: ContextDatabase
        :param prefix:
        """
        self.__prefix = prefix
        self._context_db = context_db
        self.__observer: DatabaseObserver = None

    @property
    def address(self):
        return self._context_db.address

    def get(self, key: bytes) -> bytes:
        key = self.__hash_key(key)
        return self._context_db.get(self._context, key)

    def put(self, key: bytes, value: bytes):
        key = self.__hash_key(key)
        if self.__observer:
            old_value = self._context_db.get(self._context, key)
            self.__observer.on_put(self._context, key, old_value, value)
        self._context_db.put(self._context, key, value)

    def get_sub_db(self, prefix: bytes) -> 'IconScoreDatabase':
        icon_score_database = IconScoreDatabase(
            self._context_db, self.__prefix + prefix)
        icon_score_database.set_observer(self.__observer)
        return icon_score_database

    def delete(self, key: bytes):
        key = self.__hash_key(key)
        if self.__observer:
            old_value = self._context_db.get(self._context, key)
            self.__observer.on_delete(self._context, key, old_value)
        self._context_db.delete(self._context, key)

    def set_observer(self, observer: 'DatabaseObserver'):
        self.__observer = observer

    def __hash_key(self, key: bytes):
        """All key is hashed and stored to StateDB
        """
        return sha3_256(self.__prefix + key)
