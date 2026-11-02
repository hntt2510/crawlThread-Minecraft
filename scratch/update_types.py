with open('frontend/src/types/index.ts', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """export interface DiscoveryResult {
  posts: DiscoveredPost[];
  total: number;
  topics: TrendingTopic[];
  api_status: {
    configured: boolean;
    status: string;
    username?: string;
    message?: string;
  };
  query: string;
  execution_time_ms: number;
}"""

new_block = """export interface DiscoveryResult {
  posts: DiscoveredPost[];
  total: number;
  topics: TrendingTopic[];
  api_status: {
    configured: boolean;
    status: string;
    username?: string;
    message?: string;
  };
  query: string;
  execution_time_ms: number;
  suggested_topics?: string[];
  matched_cluster?: string;
  original_keyword?: string;
}"""

content = content.replace(old_block.replace('\r\n', '\n'), new_block.replace('\r\n', '\n'))
with open('frontend/src/types/index.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated frontend/src/types/index.ts!')

