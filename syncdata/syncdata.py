# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from .services import SyncDataService, ExecuteLogService


class SyncData(object):
    def __init__(self, session, redis, gid=0):
        self.session = session
        self.redis = redis
        self.gid = gid

    def sync(self, log_id, datas):
        """sync datas"""

        lock_key = 'hausir:syncdata:lock:{}'.format(self.gid)

        if self.redis.get(lock_key):
            return False

        try:
            self.redis.set(lock_key, True)
            send_data = self.get_send_data(log_id)
            if datas:
                self.execute_data(datas)
            max_log_id = self.get_max_log_id()

            if not send_data:
                sync_data_srv = SyncDataService(self.session, self.gid)
                sync_datas = sync_data_srv.get_all()
                send_data = {
                    'type': 'ALL',
                    'data': sync_datas,
                }
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.redis.delete(lock_key)

        self.redis.delete(lock_key)
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

        execute_log_srv = ExecuteLogService(self.session, self.gid)
        logs = execute_log_srv.get_unexecute_logs(log_id)

        return {
            'type': 'PART',
            'data': logs,
        }

    def execute_data(self, datas):
        """执行客户端发来的数据"""

        max_log_id_key = 'hausir:syncdata:maxlogid:{}'.format(self.gid)

        sync_data_srv = SyncDataService(self.session, self.gid)
        execute_log_srv = ExecuteLogService(self.session, self.gid)
        switcher = {
            'INSERT': sync_data_srv.add,
            'DELETE': sync_data_srv.delete,
            'UPDATE': sync_data_srv.update,
        }

        for data in datas:
            switcher.get(data.get('action'))(data.get('payload'))

        _id = execute_log_srv.add(datas)
        self.redis.set(max_log_id_key, _id)

        self.session.commit()

    def get_max_log_id(self):
        """获取最新的log_id"""

        max_log_id_key = 'hausir:syncdata:maxlogid:{}'.format(self.gid)

        max_log_id = self.redis.get(max_log_id_key)

        if not max_log_id:
            execute_log_srv = ExecuteLogService(self.session, self.gid)
            max_log_id = execute_log_srv.get_max_id()
            self.redis.set(max_log_id_key, max_log_id)

        return int(max_log_id)
