import React, { useState, useEffect } from 'react';
import { 
  FolderKanban, 
  PlusCircle, 
  Film, 
  Trash2, 
  Calendar, 
  ExternalLink, 
  ArrowRight, 
  MessageSquare, 
  Sparkles, 
  CheckCircle2 
} from 'lucide-react';
import { api } from '../api/client';
import { Project } from '../types';

interface DashboardProps {
  onOpenProject: (projectId: string) => void;
  onNewProject: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onOpenProject, onNewProject }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.listProjects();
      setProjects(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Bạn có chắc chắn muốn xóa dự án này?')) return;
    try {
      await api.deleteProject(id);
      setProjects(projects.filter((p) => p.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">Đã xuất bản</span>;
      case 'rendered':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-950/60 text-indigo-400 border border-indigo-800/40">Đã dựng MP4</span>;
      case 'synthesized':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-violet-950/60 text-violet-400 border border-violet-800/40">Đã có giọng đọc</span>;
      case 'crawled':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-950/60 text-blue-400 border border-blue-800/40">Đã cào dữ liệu</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-zinc-800 text-zinc-400">Bản nháp</span>;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-zinc-950 p-8 space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-violet-950/40 via-zinc-900 to-zinc-900 border border-violet-800/30 p-8 rounded-3xl flex items-center justify-between shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-violet-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>Threads Video Studio • Local-First Creator Suite</span>
          </div>
          <h1 className="text-2xl font-extrabold text-zinc-100">Xưởng Video Thuyết Minh Tiếng Việt Từ Threads</h1>
          <p className="text-xs text-zinc-400 max-w-xl">
            Tự động biến một đường dẫn bài viết Threads thành video ngắn dọc 9:16 trên nền Minecraft gameplay, kèm file dự án CapCut Desktop đa track có thể chỉnh sửa.
          </p>
        </div>

        <button
          onClick={onNewProject}
          className="bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs px-6 py-3.5 rounded-2xl flex items-center space-x-2 shadow-xl shadow-violet-600/30 transition-all cursor-pointer flex-shrink-0"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Tạo Dự Án Mới</span>
        </button>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-zinc-900/80 border border-zinc-800/80 p-5 rounded-2xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-violet-950/50 border border-violet-800/40 flex items-center justify-center text-violet-400">
            <FolderKanban className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-zinc-500 tracking-wider">Tổng Dự Án</span>
            <h3 className="text-xl font-bold text-zinc-100">{projects.length}</h3>
          </div>
        </div>

        <div className="bg-zinc-900/80 border border-zinc-800/80 p-5 rounded-2xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-950/50 border border-indigo-800/40 flex items-center justify-center text-indigo-400">
            <Film className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-zinc-500 tracking-wider">Video Đã Dựng</span>
            <h3 className="text-xl font-bold text-zinc-100">
              {projects.filter((p) => p.status === 'rendered' || p.status === 'published').length}
            </h3>
          </div>
        </div>

        <div className="bg-zinc-900/80 border border-zinc-800/80 p-5 rounded-2xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-950/50 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-zinc-500 tracking-wider">Đã Xuất Bản</span>
            <h3 className="text-xl font-bold text-zinc-100">
              {projects.filter((p) => p.status === 'published').length}
            </h3>
          </div>
        </div>
      </div>

      {/* Projects List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase text-zinc-300 tracking-wider">
            Danh Sách Dự Án Của Bạn ({projects.length})
          </h2>
        </div>

        {loading ? (
          <div className="text-xs text-zinc-500 font-mono py-8 text-center">Đang tải danh sách dự án...</div>
        ) : projects.length === 0 ? (
          <div className="border border-dashed border-zinc-800 rounded-3xl p-12 text-center space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-500 mx-auto">
              <FolderKanban className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-zinc-200">Chưa có dự án nào</h3>
              <p className="text-xs text-zinc-500 max-w-sm mx-auto">
                Bấm nút "Tạo Dự Án Mới" để dán liên kết Threads đầu tiên và tạo video tự động.
              </p>
            </div>
            <button
              onClick={onNewProject}
              className="bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs px-5 py-2.5 rounded-xl transition-all cursor-pointer shadow-lg shadow-violet-600/20"
            >
              Bắt đầu ngay
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {projects.map((proj) => (
              <div
                key={proj.id}
                onClick={() => onOpenProject(proj.id)}
                className="bg-zinc-900/90 border border-zinc-800 hover:border-violet-500/50 p-5 rounded-2xl space-y-4 cursor-pointer transition-all hover:shadow-xl hover:shadow-violet-950/20 group flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    {getStatusBadge(proj.status)}
                    <button
                      onClick={(e) => handleDelete(proj.id, e)}
                      className="p-1.5 rounded-lg text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 transition-colors"
                      title="Xóa dự án"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div>
                    <h3 className="font-semibold text-sm text-zinc-100 group-hover:text-violet-300 transition-colors line-clamp-1">
                      {proj.title}
                    </h3>
                    <p className="text-xs text-zinc-500 truncate font-mono mt-0.5">{proj.threads_url}</p>
                  </div>

                  {proj.post && (
                    <div className="bg-zinc-950 border border-zinc-800/80 p-3 rounded-xl text-xs space-y-1.5">
                      <div className="flex items-center space-x-1.5 text-zinc-400 font-medium text-[11px]">
                        <span>@{proj.post.author_username}</span>
                      </div>
                      <p className="text-zinc-300 line-clamp-2 leading-relaxed">{proj.post.content}</p>
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-zinc-800/80 flex items-center justify-between text-[11px] text-zinc-500">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{new Date(proj.created_at).toLocaleDateString('vi-VN')}</span>
                  </span>

                  <span className="text-violet-400 font-semibold group-hover:translate-x-1 transition-transform flex items-center space-x-1">
                    <span>Mở xưởng</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
