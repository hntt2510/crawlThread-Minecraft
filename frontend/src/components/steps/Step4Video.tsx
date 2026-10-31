import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  ArrowLeft, 
  Film, 
  Upload, 
  Sliders, 
  Volume2, 
  Play, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles 
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, MediaAsset } from '../../types';

interface Step4Props {
  project: Project;
  onNext: () => void;
  onBack: () => void;
}

export const Step4Video: React.FC<Step4Props> = ({ project, onNext, onBack }) => {
  const [backgrounds, setBackgrounds] = useState<MediaAsset[]>([]);
  const [selectedBgId, setSelectedBgId] = useState<string>('');
  const [bgVolume, setBgVolume] = useState<number>(0.2);
  const [voiceVolume, setVoiceVolume] = useState<number>(1.0);
  const [cardTheme, setCardTheme] = useState<'dark' | 'glass'>('dark');
  const [startOffsetSec, setStartOffsetSec] = useState<number>(0);

  const [rendering, setRendering] = useState(false);
  const [renderProgress, setRenderProgress] = useState(0);
  const [renderMessage, setRenderMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMedia();
  }, []);

  const loadMedia = async () => {
    try {
      const mediaList = await api.listMedia('background_video');
      setBackgrounds(mediaList);
      if (mediaList.length > 0 && !selectedBgId) {
        setSelectedBgId(mediaList[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const asset = await api.uploadMedia(file, 'background_video');
      setBackgrounds([asset, ...backgrounds]);
      setSelectedBgId(asset.id);
    } catch (err: any) {
      setError(err.message || 'Lỗi upload video nền');
    }
  };

  const handleStartRender = async () => {
    setRendering(true);
    setError(null);
    setRenderProgress(5);
    setRenderMessage('Đang khởi động tiến trình dựng video...');

    try {
      const { job_id } = await api.startRender({
        project_id: project.id,
        background_asset_id: selectedBgId || undefined,
        background_volume: bgVolume,
        voice_volume: voiceVolume,
        card_theme: cardTheme,
      });

      const interval = setInterval(async () => {
        try {
          const status = await api.getRenderStatus(job_id);
          setRenderProgress(status.progress);
          setRenderMessage(status.message);

          if (status.status === 'completed') {
            clearInterval(interval);
            setRendering(false);
            onNext();
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setRendering(false);
            setError(status.error || 'Dựng video thất bại.');
          }
        } catch (e: any) {
          clearInterval(interval);
          setRendering(false);
          setError(e.message || 'Lỗi kiểm tra tiến trình dựng.');
        }
      }, 1000);
    } catch (err: any) {
      setRendering(false);
      setError(err.message || 'Không thể bắt đầu dựng video.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
          <span>Bước 4 — Cấu Hình Video & Nền Minecraft Gameplay</span>
        </h2>
        <p className="text-xs text-zinc-400 mt-1">
          Ghép nền gameplay Minecraft 9:16 vertical chuẩn Shorts/Reels/TikTok, canh chỉnh thẻ bình luận và cân bằng âm thanh.
        </p>
      </div>

      {/* Main Settings Form */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-6">
        {/* Background Gameplay Video Selection */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
              Chọn Video Nền Minecraft Gameplay (1080x1920)
            </label>
            <label className="text-xs text-violet-400 hover:text-violet-300 font-medium flex items-center space-x-1 cursor-pointer">
              <Upload className="w-3.5 h-3.5" />
              <span>Tải file video nền từ máy</span>
              <input type="file" accept="video/mp4,video/quicktime" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>

          {backgrounds.length === 0 ? (
            <div className="border border-dashed border-zinc-800 rounded-xl p-6 text-center text-xs text-zinc-500 space-y-2">
              <p>Chưa có video gameplay trong kho. Bạn có thể bấm nút "Tải file video nền từ máy" ở trên.</p>
              <p className="text-[11px] text-zinc-600">
                (Nếu không chọn, hệ thống sẽ tự động dùng phông nền Dark Studio tối ưu cho video ngắn)
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {backgrounds.map((bg) => {
                const isSelected = selectedBgId === bg.id;
                return (
                  <div
                    key={bg.id}
                    onClick={() => setSelectedBgId(bg.id)}
                    className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-violet-950/30 border-violet-500 text-violet-300 font-semibold'
                        : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'
                    }`}
                  >
                    <div className="flex items-center space-x-2 truncate mb-1">
                      <Film className="w-3.5 h-3.5 flex-shrink-0" />
                      <span className="truncate">{bg.name}</span>
                    </div>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {((bg.duration_ms || 0) / 1000).toFixed(0)}s • {(bg.file_size_bytes / (1024 * 1024)).toFixed(1)}MB
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Sliders: Volumes & Offset */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Audio Balance */}
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                  Âm Lượng Giọng Đọc
                </span>
                <span className="text-xs font-mono font-bold text-zinc-200">
                  {Math.round(voiceVolume * 100)}%
                </span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.05"
                value={voiceVolume}
                onChange={(e) => setVoiceVolume(parseFloat(e.target.value))}
                className="w-full accent-violet-600 bg-zinc-950 h-2 rounded-lg cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                  Âm Lượng Nhạc Nền / Gameplay
                </span>
                <span className="text-xs font-mono font-bold text-zinc-200">
                  {Math.round(bgVolume * 100)}%
                </span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.8"
                step="0.05"
                value={bgVolume}
                onChange={(e) => setBgVolume(parseFloat(e.target.value))}
                className="w-full accent-violet-600 bg-zinc-950 h-2 rounded-lg cursor-pointer"
              />
            </div>
          </div>

          {/* Card Appearance & Styling */}
          <div>
            <label className="block text-xs font-semibold uppercase text-zinc-400 tracking-wider mb-2">
              Giao Diện Thẻ Bình Luận
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setCardTheme('dark')}
                className={`p-3 rounded-xl border text-xs font-medium text-left transition-colors cursor-pointer ${
                  cardTheme === 'dark'
                    ? 'bg-zinc-950 border-violet-500 text-violet-300'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'
                }`}
              >
                <div className="font-semibold text-zinc-200 mb-0.5">Thẻ Tối Sang Trọng</div>
                <div className="text-[11px] text-zinc-500">Nền đen tuyền, tương phản cao trên gameplay</div>
              </button>

              <button
                onClick={() => setCardTheme('glass')}
                className={`p-3 rounded-xl border text-xs font-medium text-left transition-colors cursor-pointer ${
                  cardTheme === 'glass'
                    ? 'bg-zinc-950 border-violet-500 text-violet-300'
                    : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700'
                }`}
              >
                <div className="font-semibold text-zinc-200 mb-0.5">Kính Mờ (Glass)</div>
                <div className="text-[11px] text-zinc-500">Mờ đục tinh tế, phong cách hiện đại</div>
              </button>
            </div>
          </div>
        </div>

        {/* Start Render Button & Progress */}
        <div className="pt-4 border-t border-zinc-800/80">
          <button
            onClick={handleStartRender}
            disabled={rendering}
            className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold text-sm py-3.5 rounded-xl shadow-xl shadow-violet-600/30 flex items-center justify-center space-x-2 transition-all cursor-pointer"
          >
            {rendering ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Đang Tiến Hành Dựng Video Bằng FFmpeg ({renderProgress}%)...</span>
              </>
            ) : (
              <>
                <Film className="w-5 h-5" />
                <span>Dựng Video Hoàn Chỉnh (MP4)</span>
              </>
            )}
          </button>

          {rendering && (
            <div className="space-y-2 mt-4">
              <div className="w-full bg-zinc-950 h-2 rounded-full overflow-hidden border border-zinc-800">
                <div
                  className="bg-violet-600 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${renderProgress}%` }}
                />
              </div>
              <p className="text-xs text-violet-300 font-mono text-center animate-pulse">{renderMessage}</p>
            </div>
          )}

          {error && (
            <div className="bg-rose-950/40 border border-rose-800/40 p-4 rounded-xl flex items-center space-x-3 mt-4">
              <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
              <p className="text-xs text-rose-300">{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <button
          onClick={onBack}
          className="border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại Bước 3</span>
        </button>

        <button
          onClick={onNext}
          className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
        >
          <span>Xem Video & Xuất CapCut</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
