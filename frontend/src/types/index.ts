export interface Project {
  id: string;
  title: string;
  threads_url: string;
  status: string; // draft, crawled, synthesized, rendered, published
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
  updated_at_human?: string;
  post?: ThreadsPost;
  selections: CommentSelection[];
}

export interface CrawlQualityReport {
  original_post_id: string;
  expected_reply_count?: number;
  retrieved_comment_count: number;
  retrieved_reply_count: number;
  duplicate_count: number;
  rejected_record_count: number;
  unresolved_relationship_count: number;
  data_source: string;
  crawl_status: string;
  completeness_warnings: string[];
}

export interface ThreadsPost {
  id: string;
  url: string;
  author_username: string;
  author_display_name?: string;
  author_avatar_url?: string;
  content: string;
  media_urls: string[];
  like_count?: number;
  reply_count?: number;
  repost_count?: number;
  published_at?: string;
  age_label?: string;
  is_youth_trend?: boolean;
}

export interface ThreadsComment {
  id: string;
  post_id: string;
  parent_comment_id?: string;
  parent_author_username?: string;
  author_username: string;
  author_display_name?: string;
  author_avatar_url?: string;
  content: string;
  like_count?: number;
  reply_count?: number;
  nesting_depth: number;
  published_at?: string;
  age_label?: string;
  is_youth_trend?: boolean;
}

export interface CommentSelection {
  id: string;
  project_id: string;
  comment_id: string;
  sequence_order: number;
  display_text: string;
  tts_text: string;
  voice_id?: string;
  voice_rate?: number;
  is_active: boolean;
  author_username?: string;
  author_display_name?: string;
  author_avatar_url?: string;
  like_count?: number;
  reply_count?: number;
  has_audio?: boolean;
  audio_duration_ms?: number;
}

export interface VoiceInfo {
  id: string;
  name: string;
  provider: string;
  gender: string;
  accent: string;
}

export interface MediaAsset {
  id: string;
  type: string;
  name: string;
  file_path: string;
  duration_ms?: number;
  file_size_bytes: number;
  created_at: string;
}

export interface JobStatus {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  error?: string;
  result?: any;
}

// Discovery Types
export interface TrendingTopic {
  id: string;
  name: string;
  category: string;
  source: string;
  source_label: string;
  traffic_hint?: string;
  updated_at: string;
  updated_at_human?: string;
}

export interface DiscoveredPost {
  id: string;
  threads_url: string;
  author_username: string;
  author_display_name: string;
  author_avatar_url: string;
  content: string;
  media_type: string;
  media_urls: string[];
  published_at?: string;
  age_label?: string;
  is_youth_trend?: boolean;
  like_count?: number;
  reply_count?: number;
  repost_count?: number;
  views_count?: number;
  hot_score: number;
  ranking_reason: string;
  discovery_source: string;
  topic?: string;
  is_vietnamese: boolean;
}

export interface DiscoveryResult {
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
}

export interface DiscoverySearchRequest {
  keyword?: string;
  category?: string;
  search_type?: 'TOP' | 'RECENT' | 'BOTH';
  media_type?: string;
  time_window?: '24h' | '3d' | '7d' | 'all';
  sort_by?: 'hot' | 'latest' | 'comments';
  limit?: number;
}

// AI Studio Types
export interface CuratedComment {
  comment_id: string;
  author_username: string;
  author_display_name: string;
  display_text: string;
  tts_text: string;
  like_count?: number;
  reply_count?: number;
  parent_comment_id?: string;
  nesting_depth: number;
  overall_score: number;
  humor_score: number;
  emotion_score: number;
  controversy_score: number;
  story_score: number;
  engagement_score: number;
  is_thread_dialog: boolean;
  selection_reason: string;
  suggested_sfx?: string;
  punchline_pause_sec: number;
}

export interface CurationResult {
  curated_comments: CuratedComment[];
  total_evaluated: number;
  total_filtered_spam: number;
  selection_mode: string;
  summary_insight: string;
}

export interface HookOption {
  id: string;
  style: 'curiosity' | 'conflict' | 'question' | 'custom';
  title_badge: string;
  hook_text: string;
  tts_text: string;
  reason: string;
  estimated_duration_sec: number;
  audio_path?: string;
}

export interface TimelineScene {
  id: string;
  scene_index: number;
  scene_type: 'hook' | 'post' | 'comment';
  author_username: string;
  author_display_name: string;
  display_text: string;
  tts_text: string;
  start_time_sec: number;
  duration_sec: number;
  end_time_sec: number;
  speech_duration_sec: number;
  pause_buffer_sec: number;
  card_image_path?: string;
  audio_path?: string;
  sfx_id?: string;
  sfx_offset_sec: number;
  sfx_volume: number;
  zoom_effect: boolean;
  zoom_factor: number;
  transition_style: string;
  is_punchline: boolean;
}

export interface TimelinePlan {
  scenes: TimelineScene[];
  total_duration_sec: number;
  caption_segments: any[];
  sfx_cues: any[];
  has_hook: boolean;
  video_pace: string;
}

export interface QualityIssue {
  code: string;
  severity: 'error' | 'warning';
  message: string;
  suggestion: string;
  field_target?: string;
  can_auto_fix: boolean;
}

export interface QualityCheckReport {
  is_passed: boolean;
  score: number;
  errors: QualityIssue[];
  warnings: QualityIssue[];
  suggestions: string[];
  video_duration_sec: number;
}

export interface SFXItem {
  id: string;
  name: string;
  category: string;
  description: string;
  file_path: string;
  duration_ms: number;
  default_volume: number;
}

