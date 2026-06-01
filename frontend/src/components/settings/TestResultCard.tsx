/**
 * 测试结果卡片组件
 */
import { CheckCircle, XCircle } from 'lucide-react'
import type { TestResult } from '@/types/settings'

interface TestResultCardProps {
  result: TestResult
}

export function TestResultCard({ result }: TestResultCardProps) {
  return (
    <div
      className={`card overflow-hidden ${
        result.success
          ? 'border-green-500 dark:border-green-500/50'
          : 'border-red-500 dark:border-red-500/50'
      }`}
    >
      <div className="space-y-3">
        {/* 状态消息 */}
        <div className="flex items-center gap-2">
          {result.success ? (
            <CheckCircle className="h-5 w-5 text-green-500 dark:text-green-400 flex-shrink-0" />
          ) : (
            <XCircle className="h-5 w-5 text-red-500 dark:text-red-400 flex-shrink-0" />
          )}
          <span className="text-slate-700 dark:text-slate-300">{result.message}</span>
        </div>

        {/* 账户积分 */}
        {result.account_points > 0 && (
          <div className="text-sm">
            <span className="text-slate-500 dark:text-slate-400">账户积分：</span>
            <span className="font-semibold text-slate-900 dark:text-slate-100">
              {result.account_points}
            </span>
          </div>
        )}

        {/* 可用接口列表 */}
        {result.api_list.length > 0 && (
          <div>
            <div className="text-sm font-medium mb-2 text-slate-700 dark:text-slate-300">
              可用接口：
            </div>
            <div className="flex flex-wrap gap-2">
              {result.api_list.map((api) => (
                <span
                  key={api}
                  className="px-2.5 py-1 text-xs font-medium rounded-md bg-blue-50 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-500/30"
                >
                  {api}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
