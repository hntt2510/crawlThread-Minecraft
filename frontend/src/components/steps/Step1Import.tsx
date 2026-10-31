import React, { useState } from 'react';
import {
  DownloadCloud,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Heart,
  MessageCircle,
  ExternalLink,
  Sparkles,
  RefreshCw,
  Repeat
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, DiscoveredPost } from '../../types';
import { DiscoveryPanel } from './DiscoveryPanel';

interface Step1Props {
  project: Project | null;
  onProjectUpdated: (project: Project) => void;
  onNext: () => void;
}

export const Step1Import: React.FC<Step1Props> = ({ project, onProjectUpdated, onNext }) => {
  const [loading, setLoading] = useState(false);
  const [progressMsg, setProgressMsg] = useState('');
  const [error, setError] = useState<string | null>(null);

  const startCrawlWorkflow = async (url: string, projectTitle: string) => {
    setError(null);
    setLoading(true);
    setProgressMsg('Đang khởi động cào dữ liệu Threads...');

    try {
      let activeProjectId = project?.id;
      if (!activeProjectId) {
        const newProj = await api.createProject(projectTitle, url);
        activeProjectId = newProj.id;
      } else {
        await api.updateProject(activeProjectId, {
          title: projectTitle,
          settings: { ...(project?.settings || {}), threads_url: url }
        });
      }

      const { job_id } = await api.startCrawl(url, activeProjectId, 50);

      // Poll crawl job
      const interval = setInterval(async () => {
        try {
          const status = await api.getCrawlStatus(job_id);
          setProgressMsg(status.message);

          if (status.status === 'completed') {
            clearInterval(interval);
            setLoading(false);
            const updated = await api.getProject(activeProjectId!);
            onProjectUpdated(updated);
            // Move directly to Step 2
            onNext();
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setLoading(false);
            setError(status.error || 'Cào dữ liệu thất bại.');
          }
        } catch (e: any) {
          clearInterval(interval);
          setLoading(false);
          setError(e.message || 'Lỗi kiểm tra tiến trình.');
        }
      }, 1000);
    } catch (err: any) {
      setLoading(false);
      setError(err.message || 'Không thể bắt đầu cào dữ liệu.');
    }
  };

  const handleSelectDiscoveredPost = (post: DiscoveredPost) => {
    const title = post.content
      ? post.content.slice(0, 50) + (post.content.length > 50 ? '...' : '')
      : `Video Threads @${post.author_username}`;
    startCrawlWorkflow(post.threads_url, title);
  };

  const handleManualUrlSubmit = (url: string) => {
    startCrawlWorkflow(url, project?.title || 'Dự án Threads mới');
  };

  const post = project?.post;

  return (
    <div className="max-w-6xl mx-auto space-y-6 py-4">
      {/* Crawl Progress Overlay Modal */}
      {loading && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-violet-500/40 rounded-2xl p-6 max-w-md w-full shadow-2xl text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-violet-600/20 border border-violet-500/30 flex items-center justify-center mx-auto">
              <Loader2 className="w-8 h-8 text-violet-400 animate-spin" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">Đang Thu Thập Dữ Liệu Threads</h3>
              <p className="text-sm text-slate-400 mt-1">{progressMsg || 'Đang kết nối tới Threads...'}</p>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-violet-500 h-1.5 rounded-full animate-pulse w-3/4 mx-auto" />
            </div>
            <p className="text-xs text-slate-500">
              Hệ thống đang trích xuất bài viết gốc và toàn bộ cây phản hồi lồng nhau.
            </p>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/60 p-4 rounded-xl flex items-center justify-between text-rose-300 text-sm">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-xs font-semibold hover:underline"
          >
            Đóng
          </button>
        </div>
      )}

      {/* Already Crawled Post Banner (if re-entering Step 1) */}
      {post && (
        <div className="bg-gradient-to-r from-violet-950/60 via-slate-900 to-slate-900 border border-violet-500/30 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-violet-600/20 border border-violet-500/40 flex items-center justify-center text-sm font-bold text-violet-300 shrink-0">
              {post.author_display_name?.[0]?.toUpperCase() || post.author_username[0]?.toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-100">{post.author_display_name || post.author_username}</span>
                <span className="text-xs text-slate-400">@{post.author_username}</span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
                  Đã cào thành công
                </span>
              </div>
              <p className="text-xs text-slate-300 line-clamp-2 mt-1">{post.content}</p>
            </div>
          </div>

          <button
            onClick={onNext}
            className="bg-violet-600 hover:bg-violet-500 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition flex items-center justify-center gap-2 shrink-0 shadow-lg shadow-violet-600/20"
          >
            <span>Tiếp tục biên tập bình luận</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Main Automated Threads Discovery Panel */}
      <DiscoveryPanel
        onSelectPost={handleSelectDiscoveredPost}
        onManualUrlSubmit={handleManualUrlSubmit}
        isLoading={loading}
      />
    </div>
  );
};
