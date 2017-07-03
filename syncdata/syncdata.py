# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from .services import SyncDataService, ExecuteLogService

LOCK_KEY = 'hausir:syncdata:lock'
MAX_LOG_ID_KEY = 'hausir:syncdata:maxlogid'


class SyncData(object):
    def __init__(self, session, redis):
        self.session = session
        self.redis = redis

    def sync(self, log_id, datas):
        """sync datas"""

        if self.redis.get(LOCK_KEY):
            return False

        try:
            self.redis.set(LOCK_KEY, True)
            send_data = self.get_send_data(log_id)
            if datas:
                self.execute_data(datas)
            max_log_id = self.get_max_log_id()

            if not send_data:
                sync_data_srv = SyncDataService(self.session)
                sync_datas = sync_data_srv.get_all()
                send_data = {
                    'type': 'ALL',
                    'data': sync_datas,
                }
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.redis.delete(LOCK_KEY)

        self.redis.delete(LOCK_KEY)
        return {
            'log_id': max_log_id,
            'data': send_data,
        }

    def get_send_data(self, log_id):
        """获取要返回给客户端的数据"""

        max_log_id = self.get_max_log_id()
        res = max_log_id - log_id

        if res > 100:
            return False

        execute_log_srv = ExecuteLogService(self.session)
        logs = execute_log_srv.get_unexecute_logs(log_id)

        return {
            'type': 'PART',
            'data': logs,
        }

    def execute_data(self, datas):
        """执行客户端发来的数据"""

        sync_data_srv = SyncDataService(self.session)
        execute_log_srv = ExecuteLogService(self.session)
        switcher = {
            'INSERT': sync_data_srv.add,
            'DELETE': sync_data_srv.delete,
            'UPDATE': sync_data_srv.update,
        }

        for data in datas:
            switcher.get(data.get('action'))(data.get('payload'))

        _id = execute_log_srv.add(datas)
        self.redis.set(MAX_LOG_ID_KEY, _id)

        self.session.commit()

    def get_max_log_id(self):
        """获取最新的log_id"""

        max_log_id = self.redis.get(MAX_LOG_ID_KEY)

        if not max_log_id:
            execute_log_srv = ExecuteLogService(self.session)
            max_log_id = execute_log_srv.get_max_id()
            self.redis.set(MAX_LOG_ID_KEY, max_log_id)

        return int(max_log_id)
