import React, { useState } from 'react';
import { DownloadCloud, ArrowRight, CheckCircle2, AlertCircle, Loader2, Heart, MessageCircle, ExternalLink } from 'lucide-react';
import { api } from '../../api/client';
import { Project } from '../../types';

interface Step1Props {
  project: Project | null;
  onProjectUpdated: (project: Project) => void;
  onNext: () => void;
}

export const Step1Import: React.FC<Step1Props> = ({ project, onProjectUpdated, onNext }) => {
  const [url, setUrl] = useState(project?.threads_url || 'https://www.threads.net/@zuck/post/DeZgeQhm6RW');
  const [title, setTitle] = useState(project?.title || 'Video bình luận Threads vui nhộn');
  const [maxComments, setMaxComments] = useState(30);
  const [loading, setLoading] = useState(false);
  const [progressMsg, setProgressMsg] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleCrawl = async () => {
    if (!url.trim()) {
      setError('Vui lòng nhập đường dẫn Threads.');
      return;
    }
    setError(null);
    setLoading(true);
    setProgressMsg('Đang khởi động tiến trình cào Threads...');

    try {
      let activeProjectId = project?.id;
      if (!activeProjectId) {
        const newProj = await api.createProject(title, url);
        activeProjectId = newProj.id;
      }

      const { job_id } = await api.startCrawl(url, activeProjectId, maxComments);

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
      setError(err.message || 'Không thể cào dữ liệu.');
    }
  };

  const post = project?.post;

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      {/* Intro Banner */}
      <div className="bg-gradient-to-r from-violet-950/40 via-zinc-900 to-zinc-900 border border-violet-900/30 p-6 rounded-2xl shadow-xl">
        <h2 className="text-xl font-bold text-zinc-100 mb-2 flex items-center space-x-2">
          <span>Bước 1 — Nhập Bài Viết Threads Cần Chuyển Đổi</span>
        </h2>
        <p className="text-sm text-zinc-400">
          Dán URL bài viết Threads công khai. Hệ thống sẽ tự động trích xuất bài viết gốc, tác giả, hình ảnh cùng toàn bộ các bình luận và phản hồi lồng nhau.
        </p>
      </div>

      {/* Input Form Card */}
      <div className="bg-zinc-900/80 border border-zinc-800 p-6 rounded-2xl space-y-5">
        <div>
          <label className="block text-xs font-semibold uppercase text-zinc-400 tracking-wider mb-2">
            Tiêu Đề Dự Án
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Đặt tên cho dự án video..."
            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-violet-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase text-zinc-400 tracking-wider mb-2">
            Đường Dẫn Threads (Post URL)
          </label>
          <div className="flex space-x-3">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.threads.net/@username/post/POST_ID"
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-violet-500 transition-colors font-mono"
            />
            <button
              onClick={handleCrawl}
              disabled={loading}
              className="bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium text-sm px-6 py-3 rounded-xl flex items-center space-x-2 shadow-lg shadow-violet-600/30 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang Cào...</span>
                </>
              ) : (
                <>
                  <DownloadCloud className="w-4 h-4" />
                  <span>Cào Dữ Liệu</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-6 text-xs text-zinc-400 pt-1">
          <label className="flex items-center space-x-2 cursor-pointer">
            <span>Giới hạn số bình luận tối đa:</span>
            <select
              value={maxComments}
              onChange={(e) => setMaxComments(Number(e.target.value))}
              className="bg-zinc-950 border border-zinc-800 rounded-lg px-2.5 py-1 text-zinc-200"
            >
              <option value={15}>15 bình luận</option>
              <option value={30}>30 bình luận</option>
              <option value={50}>50 bình luận</option>
              <option value={100}>100 bình luận</option>
            </select>
          </label>
        </div>

        {/* Live Loading / Error Feedback */}
        {loading && (
          <div className="bg-zinc-950/80 border border-violet-800/40 p-4 rounded-xl flex items-center space-x-3">
            <Loader2 className="w-5 h-5 text-violet-400 animate-spin flex-shrink-0" />
            <p className="text-xs text-violet-300 font-mono animate-pulse">{progressMsg}</p>
          </div>
        )}

        {error && (
          <div className="bg-rose-950/40 border border-rose-800/40 p-4 rounded-xl flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <p className="text-xs text-rose-300">{error}</p>
          </div>
        )}
      </div>

      {/* Crawled Post Preview */}
      {post && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase text-emerald-400 flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>Đã Thu Thập Thành Công Bài Gốc</span>
            </span>
            <a
              href={post.url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-zinc-500 hover:text-zinc-300 flex items-center space-x-1"
            >
              <span>Mở bài viết gốc</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          {/* Post Card Layout */}
          <div className="bg-zinc-950 border border-zinc-800 p-5 rounded-xl space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-11 h-11 rounded-full bg-violet-600 flex items-center justify-center font-bold text-white uppercase text-base">
                {post.author_display_name?.[0] || post.author_username?.[0] || 'U'}
              </div>
              <div>
                <h4 className="font-semibold text-zinc-100 text-sm">{post.author_display_name || post.author_username}</h4>
                <p className="text-xs text-zinc-500">@{post.author_username}</p>
              </div>
            </div>

            <p className="text-zinc-200 text-sm leading-relaxed whitespace-pre-wrap">{post.content}</p>

            <div className="flex items-center space-x-6 pt-2 text-xs text-zinc-400 border-t border-zinc-900">
              <span className="flex items-center space-x-1.5">
                <Heart className="w-3.5 h-3.5 text-rose-500" />
                <span>{post.like_count !== null && post.like_count !== undefined ? post.like_count.toLocaleString() : 'N/A'} lượt thích</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <MessageCircle className="w-3.5 h-3.5 text-indigo-400" />
                <span>{post.reply_count !== null && post.reply_count !== undefined ? post.reply_count.toLocaleString() : 'N/A'} phản hồi</span>
              </span>
            </div>
          </div>

          {/* Action to proceed */}
          <div className="pt-2 flex justify-end">
            <button
              onClick={onNext}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
            >
              <span>Tiếp tục: Chọn bình luận</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
