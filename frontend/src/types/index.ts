export interface Project {
  id: string;
  title: string;
  threads_url: string;
  status: string; // draft, crawled, synthesized, rendered, published
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
  post?: ThreadsPost;
  selections: CommentSelection[];
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
}

export interface ThreadsComment {
  id: string;
  post_id: string;
  parent_comment_id?: string;
  author_username: string;
  author_display_name?: string;
  author_avatar_url?: string;
  content: string;
  like_count?: number;
  reply_count?: number;
  nesting_depth: number;
  published_at?: string;
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
