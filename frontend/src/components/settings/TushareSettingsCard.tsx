/**
 * Tushare 设置卡片组件
 */
import { useState, useEffect } from 'react';
import { Key, Loader2, Flame } from 'lucide-react';
import { api } from '@/services/api';
import type { TushareConfig, TestResult } from '@/types/settings';

export function TushareSettingsCard() {
  const [config, setConfig] = useState<TushareConfig>({
    enabled: false,
    tushare_token: '',
    timeout: 30,
    max_retries: 3,
    tushare_url: 'https://api.tushare.pro',
    rate_limit: 200
  });

  const [hasToken, setHasToken] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [saving, setSaving] = useState(false);

  // 加载已保存的配置
  useEffect(() => {
    const loadConfig = async () => {
      setLoading(true);
      try {
        const savedConfig = await api.getTushareConfig();
        setConfig({
          enabled: savedConfig.enabled,
          tushare_token: '',
          timeout: savedConfig.timeout,
          max_retries: savedConfig.max_retries,
          tushare_url: savedConfig.tushare_url,
          rate_limit: savedConfig.rate_limit
        });
        setHasToken(savedConfig.has_token || false);
      } catch (error) {
        console.error('加载 Tushare 配置失败:', error);
      } finally {
        setLoading(false);
      }
    };
    loadConfig();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.saveTushareConfig(config);
      alert('配置已保存');
    } catch (error) {
      alert('保存失败: ' + (error instanceof Error ? error.message : '未知错误'));
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    // 如果没有输入 token，且没有已保存的 token，则提示
    if (!config.tushare_token && !hasToken) {
      alert('请先输入 Tushare Token');
      return;
    }

    // 如果没有输入 token，但有已保存的，需要使用保存的配置测试
    if (!config.tushare_token && hasToken) {
      setTesting(true);
      setTestResult(null);
      try {
        // 使用已保存的配置测试（需要后端支持）
        const result = await api.testTushareConnection({
          ...config,
          tushare_token: '__SAVED__' // 后端会识别这个标记并使用已保存的 token
        });
        setTestResult(result);
        if (result.success) {
          alert('连接成功');
        } else {
          alert('连接失败: ' + (result.message || '未知错误'));
        }
      } catch (error) {
        alert('测试失败: ' + (error instanceof Error ? error.message : '未知错误'));
        console.error(error);
      } finally {
        setTesting(false);
      }
      return;
    }

    setTesting(true);
    setTestResult(null);
    try {
      const result = await api.testTushareConnection(config);
      setTestResult(result);
      if (result.success) {
        alert('连接成功');
      } else {
        alert('连接失败: ' + (result.message || '未知错误'));
      }
    } catch (error) {
      alert('测试失败: ' + (error instanceof Error ? error.message : '未知错误'));
      console.error(error);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2">
        <Key className="w-5 h-5 text-purple-500" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Tushare 数据源设置</h2>
      </div>

      <div className="text-sm text-slate-500 dark:text-slate-400">
        配置 Tushare Pro 数据源。访问{' '}
        <a
          href="https://tushare.pro"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 hover:underline"
        >
          Tushare Pro
        </a>
        {' '}获取 Token。
      </div>

      {/* 启用开关 */}
      <div className="rounded-xl border border-slate-200/80 bg-slate-50/80 px-4 py-3 dark:border-slate-700/80 dark:bg-slate-900/40">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-slate-700 dark:text-slate-200">启用 Tushare</div>
            <div className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              启用后将使用 Tushare 作为 A 股数据源
            </div>
          </div>
          <button
            type="button"
            onClick={() => setConfig({ ...config, enabled: !config.enabled })}
            className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${
              config.enabled ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                config.enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Token 输入 */}
      <div>
        <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
          Tushare Token
        </label>
        <div className="relative">
          <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="password"
            value={config.tushare_token}
            onChange={(e) => setConfig({ ...config, tushare_token: e.target.value })}
            className="input w-full pl-10"
            placeholder={hasToken ? '已保存，留空则保持不变' : '请输入 Tushare Token'}
            disabled={loading}
          />
        </div>
      </div>

      {/* 其他配置 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            超时时间（秒）
          </label>
          <input
            type="number"
            value={config.timeout}
            onChange={(e) => setConfig({ ...config, timeout: Number(e.target.value) })}
            className="input w-full"
            min={1}
            max={300}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            重试次数
          </label>
          <input
            type="number"
            value={config.max_retries}
            onChange={(e) => setConfig({ ...config, max_retries: Number(e.target.value) })}
            className="input w-full"
            min={0}
            max={10}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            API 端点
          </label>
          <input
            type="text"
            value={config.tushare_url}
            onChange={(e) => setConfig({ ...config, tushare_url: e.target.value })}
            className="input w-full"
            placeholder="https://api.tushare.pro"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            频率限制（次/分钟）
          </label>
          <input
            type="number"
            value={config.rate_limit || ''}
            onChange={(e) =>
              setConfig({ ...config, rate_limit: Number(e.target.value) || undefined })
            }
            className="input w-full"
            min={1}
            max={1000}
            placeholder="默认 200"
          />
        </div>
      </div>

      {/* 按钮组 */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleTest}
          disabled={testing || loading}
          className="btn-secondary inline-flex items-center gap-2"
        >
          {testing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Flame className="w-4 h-4" />}
          {testing ? '测试中...' : '测试连接'}
        </button>
        <button onClick={handleSave} disabled={saving || loading} className="btn-primary">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : '保存配置'}
        </button>
      </div>

      {/* 测试结果 */}
      {testResult && (
        <div
          className={`rounded-xl border px-4 py-3 ${
            testResult.success
              ? 'border-emerald-200 bg-emerald-50 dark:border-emerald-900/60 dark:bg-emerald-950/30'
              : 'border-rose-200 bg-rose-50 dark:border-rose-900/60 dark:bg-rose-950/30'
          }`}
        >
          <div
            className={`text-sm font-medium ${
              testResult.success
                ? 'text-emerald-800 dark:text-emerald-200'
                : 'text-rose-800 dark:text-rose-200'
            }`}
          >
            {testResult.success ? '✓ 连接成功' : '✗ 连接失败'}
          </div>
          {testResult.message && (
            <div
              className={`mt-2 text-sm ${
                testResult.success
                  ? 'text-emerald-700 dark:text-emerald-300'
                  : 'text-rose-700 dark:text-rose-300'
              }`}
            >
              {testResult.message}
            </div>
          )}
          {testResult.api_list && testResult.api_list.length > 0 && (
            <div className="mt-2 text-xs text-slate-600 dark:text-slate-300">
              <div>可用 API: {testResult.api_list.join(', ')}</div>
              <div>账户积分: {testResult.account_points}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
