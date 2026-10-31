import React, { useState } from 'react';
import { 
  ArrowRight, 
  ArrowLeft, 
  Download, 
  Film, 
  FolderDown, 
  CheckCircle2, 
  Loader2, 
  AlertCircle, 
  Share2, 
  ExternalLink 
} from 'lucide-react';
import { api } from '../../api/client';
import { Project } from '../../types';

interface Step5Props {
  project: Project;
  onNext: () => void;
  onBack: () => void;
}

export const Step5Export: React.FC<Step5Props> = ({ project, onNext, onBack }) => {
  const [capcutLoading, setCapcutLoading] = useState(false);
  const [capcutResult, setCapcutResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const videoUrl = `/api/render/video/${project.id}?t=${Date.now()}`;

  const handleExportCapCut = async () => {
    setCapcutLoading(true);
    setError(null);
    try {
      const res = await api.exportCapCut(project.id, true);
      setCapcutResult(res);
    } catch (err: any) {
      setError(err.message || 'Lỗi xuất CapCut project');
    } finally {
      setCapcutLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      {/* Step Header */}
      <div>
        <h2 className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
          <span>Bước 5 — Xuất Video Hoàn Thiện & Dự Án CapCut Desktop</span>
        </h2>
        <p className="text-xs text-zinc-400 mt-1">
          Xem trước video MP4 đã dựng hoàn chỉnh và nhận dự án CapCut đa track (Multi-track) để có thể chỉnh sửa lại linh hoạt trên máy tính.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        {/* Left Column: 9:16 Video Player Preview */}
        <div className="md:col-span-5 flex flex-col items-center">
          <div className="w-[280px] h-[497px] bg-black rounded-3xl overflow-hidden shadow-2xl border-4 border-zinc-800 relative flex items-center justify-center">
            <video
              src={videoUrl}
              controls
              className="w-full h-full object-cover"
              poster="/placeholder-preview.png"
            >
              Trình duyệt của bạn không hỗ trợ video HTML5.
            </video>
          </div>

          <div className="w-[280px] mt-4">
            <a
              href={videoUrl}
              download={`${project.title}.mp4`}
              className="w-full bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs py-3 rounded-xl flex items-center justify-center space-x-2 shadow-lg shadow-violet-600/30 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Tải Video MP4 Về Máy</span>
            </a>
          </div>
        </div>

        {/* Right Column: CapCut Desktop Exporter Card & Actions */}
        <div className="md:col-span-7 space-y-6">
          {/* CapCut Studio Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
                <Film className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-zinc-100">Dự Án CapCut Desktop (Có Thể Chỉnh Sửa)</h3>
                <p className="text-xs text-zinc-400">Giữ nguyên các track độc lập: V1 nền, V2-V3 thẻ, A1 tiếng nói, A2 nhạc nền.</p>
              </div>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              Tạo file dự án bản địa chuẩn CapCut Desktop Windows. Người dùng có thể mở ngay trên máy này hoặc tải file ZIP để chia sẻ cho bất kỳ máy Windows nào khác.
            </p>

            <div className="pt-2">
              <button
                onClick={handleExportCapCut}
                disabled={capcutLoading}
                className="w-full bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 text-amber-300 font-semibold text-xs py-3 rounded-xl border border-amber-500/30 flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-md"
              >
                {capcutLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                    <span>Đang Tạo Dự Án CapCut...</span>
                  </>
                ) : (
                  <>
                    <FolderDown className="w-4 h-4" />
                    <span>Tạo & Xuất Dự Án CapCut Desktop</span>
                  </>
                )}
              </button>
            </div>

            {capcutResult && (
              <div className="bg-zinc-950 border border-emerald-800/40 p-4 rounded-xl space-y-3">
                <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  <span>Đã Xuất Dự Án CapCut Thành Công!</span>
                </div>

                {capcutResult.installed_to_capcut && (
                  <p className="text-[11px] text-zinc-400 font-mono break-all">
                    Đã copy thẳng vào CapCut Desktop: <br />
                    <span className="text-zinc-300">{capcutResult.draft_dir}</span>
                  </p>
                )}

                <div className="pt-1">
                  <a
                    href={`/api/capcut/download/${project.id}`}
                    download={`${capcutResult.draft_name}_CapCut_Package.zip`}
                    className="w-full bg-emerald-700/30 hover:bg-emerald-700/50 text-emerald-300 text-xs font-medium py-2 rounded-lg flex items-center justify-center space-x-2 border border-emerald-600/40 transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Tải Gói Bàn Giao CapCut (.ZIP Đầy Đủ)</span>
                  </a>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-rose-950/40 border border-rose-800/40 p-4 rounded-xl flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                <p className="text-xs text-rose-300">{error}</p>
              </div>
            )}
          </div>

          {/* Publishing CTA Card */}
          <div className="bg-gradient-to-r from-violet-950/40 to-indigo-950/40 border border-violet-800/30 rounded-2xl p-6 space-y-3">
            <h4 className="text-sm font-semibold text-zinc-100 flex items-center space-x-2">
              <Share2 className="w-4 h-4 text-violet-400" />
              <span>Sẵn Sàng Xuất Bản Lên Mạng Xã Hội?</span>
            </h4>
            <p className="text-xs text-zinc-400">
              Đăng video đã dựng lên YouTube Shorts, Facebook Page Reels hoặc TikTok với 1 cú nhấp chuột.
            </p>
            <div className="pt-1">
              <button
                onClick={onNext}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
              >
                <span>Sang Trung Tâm Xuất Bản (Publish Center)</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <button
          onClick={onBack}
          className="border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại Bước 4</span>
        </button>
      </div>
    </div>
  );
};
