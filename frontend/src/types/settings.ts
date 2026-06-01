/**
 * 设置相关类型定义
 */

export interface TushareConfig {
  enabled: boolean;
  tushare_token: string;
  timeout: number;
  max_retries: number;
  tushare_url: string;
  rate_limit?: number;
}

export interface TestResult {
  success: boolean;
  message: string;
  api_list: string[];
  account_points: number;
}

export interface DataSourceStatus {
  source_id: string;
  enabled: boolean;
  priority: number;
  success_rate: number;
  avg_response_time: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  last_request_time: string | null;
  last_success_time: string | null;
  last_failure_time: string | null;
}

export interface DataSourcesStatusResponse {
  sources: DataSourceStatus[];
}
