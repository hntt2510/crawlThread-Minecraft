import React, { useState } from 'react';
import { 
  ArrowLeft, 
  Send, 
  Video, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  ExternalLink, 
  ShieldCheck 
} from 'lucide-react';
import { YoutubeIcon, FacebookIcon, TikTokIcon } from '../ui/PlatformIcons';
import { api } from '../../api/client';
import { Project } from '../../types';

interface Step6Props {
  project: Project;
  onBack: () => void;
}

export const Step6Publish: React.FC<Step6Props> = ({ project, onBack }) => {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['youtube']);
  const [activeTab, setActiveTab] = useState<'youtube' | 'facebook' | 'tiktok'>('youtube');

  // Metadata states
  const [ytTitle, setYtTitle] = useState(`${project.title} #Shorts`);
  const [ytDesc, setYtDesc] = useState(`Bình luận Threads vui nhộn được tạo bằng Threads Video Studio.\n\n#Shorts #Threads #HaiHuoc`);
  const [ytToken, setYtToken] = useState('');
  const [ytPrivacy, setYtPrivacy] = useState('public');

  const [fbPageId, setFbPageId] = useState('');
  const [fbToken, setFbToken] = useState('');
  const [fbCaption, setFbCaption] = useState(`${project.title} - Bình luận siêu cuốn! #reels #threads`);

  const [ttCaption, setTtCaption] = useState(`${project.title} #trending #xuhuong #fyp`);
  const [ttToken, setTtToken] = useState('');

  // Confirmation Modal
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [progressMsg, setProgressMsg] = useState('');
  const [publishResult, setPublishResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const togglePlatform = (p: string) => {
    if (selectedPlatforms.includes(p)) {
      setSelectedPlatforms(selectedPlatforms.filter((item) => item !== p));
    } else {
      setSelectedPlatforms([...selectedPlatforms, p]);
    }
  };

  const handleExecutePublish = async () => {
    setShowConfirmModal(false);
    setPublishing(true);
    setError(null);
    setProgressMsg('Đang chuẩn bị gói dữ liệu xuất bản...');

    try {
      const payload = {
        project_id: project.id,
        platforms: selectedPlatforms,
        confirm_publish: true,
        youtube_metadata: {
          title: ytTitle,
          description: ytDesc,
          access_token: ytToken,
          privacy: ytPrivacy,
        },
        facebook_metadata: {
          page_id: fbPageId,
          page_access_token: fbToken,
          description: fbCaption,
        },
        tiktok_metadata: {
          caption: ttCaption,
          access_token: ttToken,
          privacy: 'PUBLIC_TO_EVERYONE',
        },
      };

      const { job_id } = await api.publishVideo(payload);

      const interval = setInterval(async () => {
        try {
          const status = await api.getPublishStatus(job_id);
          setProgressMsg(status.message);

          if (status.status === 'completed') {
            clearInterval(interval);
            setPublishing(false);
            setPublishResult(status.result);
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setPublishing(false);
            setError(status.error || 'Xuất bản thất bại.');
          }
        } catch (e: any) {
          clearInterval(interval);
          setPublishing(false);
          setError(e.message || 'Lỗi kiểm tra tiến trình xuất bản.');
        }
      }, 1000);
    } catch (err: any) {
      setPublishing(false);
      setError(err.message || 'Không thể bắt đầu xuất bản.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
          <span>Bước 6 — Trung Tâm Xuất Bản Đa Nền Tảng</span>
        </h2>
        <p className="text-xs text-zinc-400 mt-1">
          Đăng video trực tiếp lên YouTube Shorts, Facebook Page Reels và TikTok. Luôn yêu cầu xác nhận rõ ràng trước khi tải lên.
        </p>
      </div>

      {/* Platform Multi-select Badges */}
      <div className="bg-zinc-900 border border-zinc-800 p-5 rounded-2xl space-y-3">
        <label className="block text-xs font-semibold uppercase text-zinc-400 tracking-wider">
          Chọn Các Nền Tảng Muốn Đăng Tải
        </label>
        <div className="grid grid-cols-3 gap-3">
          <button
            onClick={() => togglePlatform('youtube')}
            className={`p-3.5 rounded-xl border flex items-center justify-between transition-colors cursor-pointer ${
              selectedPlatforms.includes('youtube')
                ? 'bg-rose-950/30 border-rose-600/60 text-rose-300 font-semibold'
                : 'bg-zinc-950 border-zinc-800 text-zinc-500'
            }`}
          >
            <div className="flex items-center space-x-2">
              <YoutubeIcon className="w-4 h-4 text-rose-500" />
              <span className="text-xs">YouTube Shorts</span>
            </div>
            <div className={`w-3.5 h-3.5 rounded-full border ${selectedPlatforms.includes('youtube') ? 'bg-rose-500 border-rose-400' : 'border-zinc-700'}`} />
          </button>

          <button
            onClick={() => togglePlatform('facebook')}
            className={`p-3.5 rounded-xl border flex items-center justify-between transition-colors cursor-pointer ${
              selectedPlatforms.includes('facebook')
                ? 'bg-blue-950/30 border-blue-600/60 text-blue-300 font-semibold'
                : 'bg-zinc-950 border-zinc-800 text-zinc-500'
            }`}
          >
            <div className="flex items-center space-x-2">
              <FacebookIcon className="w-4 h-4 text-blue-500" />
              <span className="text-xs">Facebook Reels</span>
            </div>
            <div className={`w-3.5 h-3.5 rounded-full border ${selectedPlatforms.includes('facebook') ? 'bg-blue-500 border-blue-400' : 'border-zinc-700'}`} />
          </button>

          <button
            onClick={() => togglePlatform('tiktok')}
            className={`p-3.5 rounded-xl border flex items-center justify-between transition-colors cursor-pointer ${
              selectedPlatforms.includes('tiktok')
                ? 'bg-teal-950/30 border-teal-600/60 text-teal-300 font-semibold'
                : 'bg-zinc-950 border-zinc-800 text-zinc-500'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Video className="w-4 h-4 text-teal-400" />
              <span className="text-xs">TikTok</span>
            </div>
            <div className={`w-3.5 h-3.5 rounded-full border ${selectedPlatforms.includes('tiktok') ? 'bg-teal-500 border-teal-400' : 'border-zinc-700'}`} />
          </button>
        </div>
      </div>

      {/* Metadata Configuration Tabs */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
        {/* Tab Header */}
        <div className="flex border-b border-zinc-800 bg-zinc-950/60">
          <button
            onClick={() => setActiveTab('youtube')}
            className={`flex-1 py-3 text-xs font-medium flex items-center justify-center space-x-2 border-b-2 transition-colors ${
              activeTab === 'youtube'
                ? 'border-rose-500 text-rose-400 bg-zinc-900'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <YoutubeIcon className="w-4 h-4" />
            <span>YouTube Shorts</span>
          </button>

          <button
            onClick={() => setActiveTab('facebook')}
            className={`flex-1 py-3 text-xs font-medium flex items-center justify-center space-x-2 border-b-2 transition-colors ${
              activeTab === 'facebook'
                ? 'border-blue-500 text-blue-400 bg-zinc-900'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <FacebookIcon className="w-4 h-4" />
            <span>Facebook Reels</span>
          </button>

          <button
            onClick={() => setActiveTab('tiktok')}
            className={`flex-1 py-3 text-xs font-medium flex items-center justify-center space-x-2 border-b-2 transition-colors ${
              activeTab === 'tiktok'
                ? 'border-teal-500 text-teal-400 bg-zinc-900'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <TikTokIcon className="w-4 h-4" />
            <span>TikTok</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="p-6 space-y-4">
          {activeTab === 'youtube' && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                  Tiêu Đề Video (Bao gồm #Shorts)
                </label>
                <input
                  type="text"
                  value={ytTitle}
                  onChange={(e) => setYtTitle(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-100"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                  Mô Tả (Description)
                </label>
                <textarea
                  value={ytDesc}
                  onChange={(e) => setYtDesc(e.target.value)}
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                    Trạng Thái Hiển Thị
                  </label>
                  <select
                    value={ytPrivacy}
                    onChange={(e) => setYtPrivacy(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-200"
                  >
                    <option value="public">Công khai (Public)</option>
                    <option value="unlisted">Không công khai (Unlisted)</option>
                    <option value="private">Riêng tư (Private)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                    YouTube OAuth Access Token
                  </label>
                  <input
                    type="password"
                    value={ytToken}
                    onChange={(e) => setYtToken(e.target.value)}
                    placeholder="Bearer ya29..."
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-100 font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'facebook' && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                  Nội Dung Caption Reel
                </label>
                <textarea
                  value={fbCaption}
                  onChange={(e) => setFbCaption(e.target.value)}
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                    Facebook Page ID
                  </label>
                  <input
                    type="text"
                    value={fbPageId}
                    onChange={(e) => setFbPageId(e.target.value)}
                    placeholder="e.g. 1029384756..."
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-100 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                    Page Access Token
                  </label>
                  <input
                    type="password"
                    value={fbToken}
                    onChange={(e) => setFbToken(e.target.value)}
                    placeholder="EAA..."
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-100 font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tiktok' && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                  Tiêu Đề / Caption TikTok
                </label>
                <input
                  type="text"
                  value={ttCaption}
                  onChange={(e) => setTtCaption(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-100"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                  TikTok Access Token
                </label>
                <input
                  type="password"
                  value={ttToken}
                  onChange={(e) => setTtToken(e.target.value)}
                  placeholder="act.example..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-100 font-mono"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Publish Button */}
      <div className="space-y-4">
        <button
          onClick={() => setShowConfirmModal(true)}
          disabled={publishing || selectedPlatforms.length === 0}
          className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-semibold text-sm py-3.5 rounded-xl shadow-xl shadow-emerald-600/30 flex items-center justify-center space-x-2 transition-all cursor-pointer"
        >
          {publishing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Đang Tải Lên Video...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Xác Nhận & Xuất Bản Lên ({selectedPlatforms.length}) Nền Tảng Đã Chọn</span>
            </>
          )}
        </button>

        {publishing && (
          <p className="text-xs text-emerald-400 font-mono text-center animate-pulse">{progressMsg}</p>
        )}

        {publishResult && (
          <div className="bg-zinc-950 border border-emerald-800/40 p-5 rounded-xl space-y-3">
            <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Đã Đăng Tải Thành Công!</span>
            </div>
            {Object.entries(publishResult).map(([platform, info]: [string, any]) => (
              <div key={platform} className="text-xs flex items-center justify-between border-t border-zinc-900 pt-2">
                <span className="capitalize text-zinc-300 font-semibold">{platform}:</span>
                {info.video_url ? (
                  <a
                    href={info.video_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-violet-400 hover:text-violet-300 flex items-center space-x-1"
                  >
                    <span>Xem video vừa đăng</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                ) : (
                  <span className="text-zinc-500 font-mono">{info.message || info.status}</span>
                )}
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="bg-rose-950/40 border border-rose-800/40 p-4 rounded-xl flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <p className="text-xs text-rose-300">{error}</p>
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center space-x-3 text-emerald-400">
              <div className="w-10 h-10 rounded-full bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-zinc-100">Xác Nhận Xuất Bản</h3>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              Bạn sắp đăng video dự án <strong>"{project.title}"</strong> lên các nền tảng:{' '}
              <span className="text-emerald-400 font-semibold">{selectedPlatforms.join(', ').toUpperCase()}</span>.
            </p>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
              >
                Hủy bỏ
              </button>
              <button
                onClick={handleExecutePublish}
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-600/30 transition-all cursor-pointer"
              >
                Đồng ý Xuất Bản Ngay
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Back button */}
      <div className="pt-4 border-t border-zinc-800">
        <button
          onClick={onBack}
          className="border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại Bước 5</span>
        </button>
      </div>
    </div>
  );
};
