import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  ArrowLeft, 
  Play, 
  Pause, 
  Mic2, 
  Sparkles, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Volume2 
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, VoiceInfo, CommentSelection } from '../../types';

interface Step3Props {
  project: Project;
  onNext: () => void;
  onBack: () => void;
}

export const Step3Voice: React.FC<Step3Props> = ({ project, onNext, onBack }) => {
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [selections, setSelections] = useState<CommentSelection[]>([]);
  const [selectedVoice, setSelectedVoice] = useState('vi-VN-HoaiMyNeural');
  const [speedRate, setSpeedRate] = useState(1.0);
  const [previewText, setPreviewText] = useState('Xin chào! Đây là bản nghe thử giọng đọc thuyết minh tự động.');
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewAudioUrl, setPreviewAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const [generating, setGenerating] = useState(false);
  const [genProgress, setGenProgress] = useState(0);
  const [genMessage, setGenMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [project.id]);

  const loadData = async () => {
    try {
      const [vList, sList] = await Promise.all([
        api.listVoices(),
        api.getProjectSelections(project.id),
      ]);
      setVoices(vList);
      setSelections(sList);
    } catch (e) {
      console.error(e);
    }
  };

  const handlePreviewVoice = async () => {
    setPreviewLoading(true);
    setError(null);
    try {
      const audioUrl = await api.previewVoice(previewText, selectedVoice, 'edge_tts', speedRate);
      setPreviewAudioUrl(audioUrl);
      const audio = new Audio(audioUrl);
      setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
      audio.play();
    } catch (err: any) {
      setError(err.message || 'Lỗi nghe thử');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleGenerateAll = async () => {
    setGenerating(true);
    setError(null);
    setGenProgress(5);
    setGenMessage('Đang chuẩn bị phòng thu...');

    try {
      const { job_id } = await api.generateTTS(project.id, selectedVoice, speedRate);

      const interval = setInterval(async () => {
        try {
          const status = await api.getTTSStatus(job_id);
          setGenProgress(status.progress);
          setGenMessage(status.message);

          if (status.status === 'completed') {
            clearInterval(interval);
            setGenerating(false);
            // Refresh selections to show duration badges
            const refreshed = await api.getProjectSelections(project.id);
            setSelections(refreshed);
          } else if (status.status === 'failed') {
            clearInterval(interval);
            setGenerating(false);
            setError(status.error || 'Tạo giọng đọc thất bại.');
          }
        } catch (e: any) {
          clearInterval(interval);
          setGenerating(false);
          setError(e.message || 'Lỗi kiểm tra tiến trình.');
        }
      }, 1000);
    } catch (err: any) {
      setGenerating(false);
      setError(err.message || 'Không thể bắt đầu tạo giọng đọc.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      {/* Step Header */}
      <div>
        <h2 className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
          <span>Bước 3 — Phòng Thu Giọng Đọc Thuyết Minh Tiếng Việt</span>
        </h2>
        <p className="text-xs text-zinc-400 mt-1">
          Hệ thống tích hợp sẵn Microsoft Edge TTS Neural tiếng Việt chuẩn, không tốn phí, kèm hỗ trợ FPT.AI và Google Cloud Wavenet.
        </p>
      </div>

      {/* Voice Configuration Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Voice Selector */}
          <div>
            <label className="block text-xs font-semibold uppercase text-zinc-400 tracking-wider mb-2">
              Chọn Giọng Đọc Chủ Đạo
            </label>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-zinc-100 focus:outline-none focus:border-violet-500 font-medium"
            >
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.accent})
                </option>
              ))}
            </select>
            <p className="text-[11px] text-zinc-500 mt-1.5">
              Khuyên dùng Hoài My (Nữ) hoặc Nam Minh (Nam) cho giọng đọc tự nhiên, chuẩn chính tả.
            </p>
          </div>

          {/* Speed Rate Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold uppercase text-zinc-400 tracking-wider">
                Tốc Độ Đọc (Speed Rate)
              </label>
              <span className="text-xs font-mono font-bold text-violet-400 bg-violet-950/40 px-2 py-0.5 rounded border border-violet-800/40">
                {speedRate.toFixed(2)}x
              </span>
            </div>
            <input
              type="range"
              min="0.8"
              max="1.4"
              step="0.05"
              value={speedRate}
              onChange={(e) => setSpeedRate(parseFloat(e.target.value))}
              className="w-full accent-violet-600 bg-zinc-950 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-500 mt-1 font-mono">
              <span>0.8x (Chậm)</span>
              <span>1.0x (Chuẩn)</span>
              <span>1.4x (Nhanh)</span>
            </div>
          </div>
        </div>

        {/* Live Audio Preview Test */}
        <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3 w-full md:w-auto">
            <button
              onClick={handlePreviewVoice}
              disabled={previewLoading}
              className="w-10 h-10 rounded-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white flex items-center justify-center flex-shrink-0 shadow-md shadow-violet-600/30 cursor-pointer"
            >
              {previewLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : isPlaying ? (
                <Pause className="w-5 h-5" />
              ) : (
                <Play className="w-5 h-5 ml-0.5" />
              )}
            </button>
            <div className="flex-1">
              <p className="text-xs text-zinc-300 font-medium line-clamp-1">{previewText}</p>
              <p className="text-[11px] text-zinc-500">Bấm nút để nghe thử giọng mẫu trên máy</p>
            </div>
          </div>

          <button
            onClick={handleGenerateAll}
            disabled={generating || selections.length === 0}
            className="w-full md:w-auto bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-semibold px-6 py-2.5 rounded-xl shadow-lg shadow-violet-600/25 flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-40"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Đang Tạo Âm Thanh ({genProgress}%)...</span>
              </>
            ) : (
              <>
                <Mic2 className="w-4 h-4" />
                <span>Tạo Toàn Bộ Giọng Đọc ({selections.length} đoạn)</span>
              </>
            )}
          </button>
        </div>

        {/* Progress Display */}
        {generating && (
          <div className="space-y-2">
            <div className="w-full bg-zinc-950 h-2 rounded-full overflow-hidden border border-zinc-800">
              <div
                className="bg-violet-600 h-full transition-all duration-300 rounded-full"
                style={{ width: `${genProgress}%` }}
              />
            </div>
            <p className="text-xs text-violet-300 font-mono text-center animate-pulse">{genMessage}</p>
          </div>
        )}

        {error && (
          <div className="bg-rose-950/40 border border-rose-800/40 p-4 rounded-xl flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <p className="text-xs text-rose-300">{error}</p>
          </div>
        )}
      </div>

      {/* Voiceover Review List */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-sm font-semibold uppercase text-zinc-300 tracking-wider">
          Danh Sách Các Đoạn Giọng Đọc Sẽ Ghép Vào Video ({selections.length})
        </h3>

        <div className="space-y-3">
          {selections.map((sel, idx) => (
            <div
              key={sel.id}
              className="bg-zinc-950 border border-zinc-800/80 p-3.5 rounded-xl flex items-center justify-between text-xs"
            >
              <div className="flex items-center space-x-3 overflow-hidden">
                <span className="w-5 h-5 rounded-full bg-zinc-800 text-zinc-400 font-mono font-bold flex items-center justify-center text-[10px] flex-shrink-0">
                  {idx + 1}
                </span>
                <span className="text-zinc-300 font-medium truncate max-w-[480px]">
                  {sel.tts_text}
                </span>
              </div>

              <div className="flex items-center space-x-3 flex-shrink-0">
                {sel.has_audio ? (
                  <span className="text-emerald-400 flex items-center space-x-1 font-mono text-[11px] bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{((sel.audio_duration_ms || 0) / 1000).toFixed(1)}s</span>
                  </span>
                ) : (
                  <span className="text-zinc-500 text-[11px]">Chưa tạo audio</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <button
          onClick={onBack}
          className="border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại Bước 2</span>
        </button>

        <button
          onClick={onNext}
          className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
        >
          <span>Tiếp tục: Cấu Hình Video Minecraft</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
