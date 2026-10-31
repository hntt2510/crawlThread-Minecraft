import { Project, ThreadsComment, CommentSelection, VoiceInfo, MediaAsset, JobStatus } from '../types';

const API_BASE = '/api';

export const api = {
  // Projects
  async listProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`);
    if (!res.ok) throw new Error('Không thể tải danh sách dự án');
    return res.json();
  },

  async createProject(title: string, threads_url: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, threads_url }),
    });
    if (!res.ok) throw new Error('Không thể tạo dự án');
    return res.json();
  },

  async getProject(id: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`);
    if (!res.ok) throw new Error('Không tìm thấy dự án');
    return res.json();
  },

  async updateProject(id: string, data: { title?: string; settings?: Record<string, any> }): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Không thể cập nhật dự án');
    return res.json();
  },

  async deleteProject(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Không thể xóa dự án');
  },

  // Threads Crawler
  async startCrawl(threads_url: string, project_id?: string, max_comments: number = 50): Promise<{ job_id: string; project_id: string }> {
    const res = await fetch(`${API_BASE}/threads/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ threads_url, project_id, max_comments }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Lỗi khi bắt đầu cào Threads');
    }
    return res.json();
  },

  async getCrawlStatus(jobId: string): Promise<JobStatus> {
    const res = await fetch(`${API_BASE}/threads/crawl/${jobId}`);
    if (!res.ok) throw new Error('Không thể lấy trạng thái cào');
    return res.json();
  },

  // Comments & Selections
  async getProjectComments(projectId: string): Promise<ThreadsComment[]> {
    const res = await fetch(`${API_BASE}/comments/project/${projectId}`);
    if (!res.ok) throw new Error('Không thể tải bình luận');
    return res.json();
  },

  async getProjectSelections(projectId: string): Promise<CommentSelection[]> {
    const res = await fetch(`${API_BASE}/comments/project/${projectId}/selections`);
    if (!res.ok) throw new Error('Không thể tải danh sách chọn');
    return res.json();
  },

  async saveSelections(projectId: string, selections: any[]): Promise<void> {
    const res = await fetch(`${API_BASE}/comments/project/${projectId}/selections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selections),
    });
    if (!res.ok) throw new Error('Không thể lưu bình luận đã chọn');
  },

  async restoreComment(projectId: string, commentId: string): Promise<string> {
    const res = await fetch(`${API_BASE}/comments/project/${projectId}/restore/${commentId}`, { method: 'POST' });
    if (!res.ok) throw new Error('Không thể khôi phục bình luận gốc');
    const data = await res.json();
    return data.content;
  },

  // TTS
  async listVoices(): Promise<VoiceInfo[]> {
    const res = await fetch(`${API_BASE}/tts/voices`);
    if (!res.ok) throw new Error('Không thể tải danh sách giọng đọc');
    return res.json();
  },

  async previewVoice(text: string, voice: string, provider = 'edge_tts', rate = 1.0): Promise<string> {
    const res = await fetch(`${API_BASE}/tts/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice, provider, rate }),
    });
    if (!res.ok) throw new Error('Lỗi nghe thử giọng đọc');
    const blob = await res.blob();
    return URL.createObjectURL(blob);
  },

  async generateTTS(projectId: string, default_voice: string, default_rate = 1.0): Promise<{ job_id: string }> {
    const res = await fetch(`${API_BASE}/tts/generate/${projectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, default_voice, default_rate }),
    });
    if (!res.ok) throw new Error('Lỗi khi bắt đầu tạo giọng đọc');
    return res.json();
  },

  async getTTSStatus(jobId: string): Promise<JobStatus> {
    const res = await fetch(`${API_BASE}/tts/status/${jobId}`);
    if (!res.ok) throw new Error('Không thể lấy tiến trình giọng đọc');
    return res.json();
  },

  // Media
  async listMedia(type?: string): Promise<MediaAsset[]> {
    const url = type ? `${API_BASE}/media?type=${type}` : `${API_BASE}/media`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Không thể tải media');
    return res.json();
  },

  async uploadMedia(file: File, type: string): Promise<MediaAsset> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('media_type', type);
    const res = await fetch(`${API_BASE}/media/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Lỗi upload file media');
    return res.json();
  },

  // Video Render
  async startRender(data: {
    project_id: string;
    background_asset_id?: string;
    background_volume?: number;
    voice_volume?: number;
    card_theme?: string;
  }): Promise<{ job_id: string }> {
    const res = await fetch(`${API_BASE}/render/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Lỗi khi bắt đầu dựng video');
    return res.json();
  },

  async getRenderStatus(jobId: string): Promise<JobStatus> {
    const res = await fetch(`${API_BASE}/render/status/${jobId}`);
    if (!res.ok) throw new Error('Không thể lấy trạng thái dựng');
    return res.json();
  },

  // CapCut Exporter
  async exportCapCut(projectId: string, installToLocal: boolean = true): Promise<any> {
    const res = await fetch(`${API_BASE}/capcut/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, install_to_local: installToLocal }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Lỗi khi xuất CapCut');
    }
    return res.json();
  },

  // Publishing
  async publishVideo(data: {
    project_id: string;
    platforms: string[];
    youtube_metadata?: any;
    facebook_metadata?: any;
    tiktok_metadata?: any;
    confirm_publish: boolean;
  }): Promise<{ job_id: string }> {
    const res = await fetch(`${API_BASE}/publishing/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Lỗi khi xuất bản video');
    }
    return res.json();
  },

  async getPublishStatus(jobId: string): Promise<JobStatus> {
    const res = await fetch(`${API_BASE}/publishing/jobs/${jobId}`);
    if (!res.ok) throw new Error('Không thể lấy tiến trình xuất bản');
    return res.json();
  },

  // Settings
  async getSettings(): Promise<any> {
    const res = await fetch(`${API_BASE}/settings`);
    if (!res.ok) throw new Error('Không thể tải cài đặt');
    return res.json();
  },

  async updateSettings(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Không thể lưu cài đặt');
    return res.json();
  },

  async healthCheck(): Promise<any> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Server không phản hồi');
    return res.json();
  }
};
