/**
 * 数据源状态卡片组件
 */
import { useEffect, useState } from 'react';
import { Database, CheckCircle, Clock } from 'lucide-react';
import { api } from '@/services/api';
import type { DataSourceStatus } from '@/types/settings';

const SOURCE_NAMES: Record<string, string> = {
  akshare: 'AkShare',
  tushare: 'Tushare',
  baostock: 'BaoStock'
};

function formatTime(isoString: string | null): string {
  if (!isoString) return '-';
  const date = new Date(isoString);
  return date.toLocaleString('zh-CN');
}

export function DataSourceStatusCard() {
  const [statuses, setStatuses] = useState<DataSourceStatus[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const data = await api.getDataSourcesStatus();
      setStatuses(data.sources);
    } catch (error) {
      console.error('获取数据源状态失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // 每10秒刷新
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-blue-500" />
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">数据源状态</h2>
        </div>
        <div className="flex items-center justify-center py-8 text-slate-500 dark:text-slate-400">
          加载中...
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Database className="w-5 h-5 text-blue-500" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">数据源状态</h2>
      </div>

      <div className="space-y-3">
        {statuses.map((status) => (
          <div
            key={status.source_id}
            className={`
              rounded-xl border p-4
              ${
                status.enabled
                  ? 'bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700'
                  : 'bg-slate-50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-700 opacity-60'
              }
            `}
          >
            {/* 数据源名称和状态 */}
            <div className="flex items-center justify-between mb-3">
              <div className="font-semibold text-slate-900 dark:text-slate-100">
                {SOURCE_NAMES[status.source_id] || status.source_id}
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2.5 py-1 text-xs font-medium rounded-md ${
                    status.enabled
                      ? 'bg-green-50 dark:bg-green-500/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-500/30'
                      : 'bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-600/50'
                  }`}
                >
                  {status.enabled ? '已启用' : '已禁用'}
                </span>
                <span
                  className={`px-2.5 py-1 text-xs font-medium rounded-md ${
                    status.priority === 1
                      ? 'bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-500/30'
                      : 'bg-amber-50 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/30'
                  }`}
                >
                  {status.priority === 1 ? '主用' : '备用'}
                </span>
              </div>
            </div>

            {/* 详细信息 */}
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-slate-400 flex-shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">成功率：</span>
                <span
                  className={`font-medium ${
                    status.success_rate >= 80
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-orange-600 dark:text-orange-400'
                  }`}
                >
                  {status.success_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-slate-400 flex-shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">平均响应：</span>
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {status.avg_response_time.toFixed(0)}ms
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-500 dark:text-slate-400">最后请求：</span>
                <span className="text-slate-900 dark:text-slate-100">{formatTime(status.last_request_time)}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-500 dark:text-slate-400">最后成功：</span>
                <span
                  className={
                    status.last_success_time
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-slate-400 dark:text-slate-500'
                  }
                >
                  {formatTime(status.last_success_time)}
                </span>
              </div>
            </div>

            {/* 统计信息 */}
            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700/50 grid grid-cols-3 gap-3 text-xs">
              <div className="text-center">
                <div className="text-slate-500 dark:text-slate-400">总请求</div>
                <div className="font-semibold text-slate-900 dark:text-slate-100">
                  {status.total_requests}
                </div>
              </div>
              <div className="text-center">
                <div className="text-slate-500 dark:text-slate-400">成功</div>
                <div className="font-semibold text-green-600 dark:text-green-400">
                  {status.successful_requests}
                </div>
              </div>
              <div className="text-center">
                <div className="text-slate-500 dark:text-slate-400">失败</div>
                <div className="font-semibold text-red-600 dark:text-red-400">
                  {status.failed_requests}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
