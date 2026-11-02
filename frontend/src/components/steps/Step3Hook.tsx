import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Volume2,
  RefreshCw,
  CheckCircle2,
  Flame,
  HelpCircle,
  AlertCircle,
  Edit3
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, HookOption } from '../../types';

interface Step3HookProps {
  project: Project;
  onNext: () => void;
  onBack: () => void;
}

export const Step3Hook: React.FC<Step3HookProps> = ({ project, onNext, onBack }) => {
  const [hooks, setHooks] = useState<HookOption[]>([]);
  const [selectedHook, setSelectedHook] = useState<HookOption | null>(null);
  const [customText, setCustomText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [playingAudio, setPlayingAudio] = useState<boolean>(false);
  const [hookEnabled, setHookEnabled] = useState<boolean>(true);
  const [detectedTopic, setDetectedTopic] = useState<string>('');

  useEffect(() => {
    loadExistingOrGenerate();
  }, [project.id]);

  const loadExistingOrGenerate = async () => {
    setLoading(true);
    try {
      // Check existing hook in project settings
      const existing = await api.getProjectHook(project.id);
      if (existing) {
        setSelectedHook(existing);
        setCustomText(existing.hook_text);
        setHookEnabled(existing.is_enabled !== false);
      }

      // Generate hook suggestions
      const data = await api.generateHooks(project.id);
      setHooks(data.hooks || []);
      setDetectedTopic(data.detected_topic || 'Chủ đề thảo luận');

      if (!existing && data.hooks && data.hooks.length > 0) {
        setSelectedHook(data.hooks[0]);
        setCustomText(data.hooks[0].hook_text);
      }
    } catch (e) {
      console.error('Error loading hooks:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshHooks = async () => {
    setGenerating(true);
    try {
      const data = await api.generateHooks(project.id);
      setHooks(data.hooks || []);
      if (data.hooks && data.hooks.length > 0) {
        setSelectedHook(data.hooks[0]);
        setCustomText(data.hooks[0].hook_text);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectHook = (h: HookOption) => {
    setSelectedHook(h);
    setCustomText(h.hook_text);
  };

  const handlePlayPreview = async () => {
    if (!customText) return;
    setPlayingAudio(true);
    try {
      const audioUrl = await api.previewVoice(
        customText,
        project.settings?.default_voice || 'vi-VN-HoaiMyNeural',
        'edge_tts',
        1.05
      );
      if (audioUrl) {
        const audio = new Audio(audioUrl);
        audio.onended = () => setPlayingAudio(false);
        audio.onerror = () => setPlayingAudio(false);
        await audio.play();
      } else {
        setPlayingAudio(false);
      }
    } catch (e) {
      console.error(e);
      setPlayingAudio(false);
    }
  };

  const handleSaveAndNext = async () => {
    setSaving(true);
    try {
      if (hookEnabled && customText.trim()) {
        await api.selectHook(project.id, {
          style: selectedHook?.style || 'custom',
          title_badge: selectedHook?.title_badge || '⚡ MỞ ĐẦU',
          hook_text: customText.trim(),
          tts_text: customText.trim(),
          voice_id: project.settings?.default_voice || 'vi-VN-HoaiMyNeural'
        }, true);
      } else {
        await api.selectHook(project.id, { hook_text: '' }, false);
      }
      onNext();
    } catch (e) {
      console.error('Error saving hook:', e);
      onNext();
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4">
        <Sparkles className="w-8 h-8 text-amber-400 animate-spin" />
        <span className="text-zinc-400 text-sm font-medium">AI đang phân tích bài viết và sáng tạo 3 Hook mở đầu cuốn hút...</span>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-amber-500/15 via-orange-500/10 to-transparent border border-amber-500/30 rounded-2xl p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                P0 AI Video Studio
              </span>
              <span className="text-xs text-zinc-400">Chủ đề nhận diện: <strong className="text-zinc-200">{detectedTopic}</strong></span>
            </div>
            <h2 className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
              <Flame className="w-5 h-5 text-amber-400" />
              <span>AI Tạo Hook Mở Đầu Giữ Chân Người Xem (0 - 3s)</span>
            </h2>
            <p className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
              3 giây đầu tiên quyết định 80% người xem có lướt qua hay ở lại xem hết video. Hệ thống AI đã phân tích câu chuyện Threads và đề xuất 3 công thức hook thịnh hành.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefreshHooks}
              disabled={generating}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-medium bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 text-zinc-300 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
              <span>Tạo lại</span>
            </button>
            <label className="flex items-center space-x-2 text-xs text-zinc-300 cursor-pointer bg-zinc-900/80 px-3 py-2 rounded-xl border border-zinc-800">
              <input
                type="checkbox"
                checked={hookEnabled}
                onChange={(e) => setHookEnabled(e.target.checked)}
                className="w-4 h-4 rounded text-amber-500 focus:ring-0 bg-zinc-800 border-zinc-700"
              />
              <span className="font-medium">Bật phân cảnh Hook</span>
            </label>
          </div>
        </div>
      </div>

      {hookEnabled ? (
        <div className="space-y-6">
          {/* 3 Suggested Hooks Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {hooks.map((h) => {
              const isSelected = selectedHook?.id === h.id;
              return (
                <div
                  key={h.id}
                  onClick={() => handleSelectHook(h)}
                  className={`cursor-pointer rounded-2xl p-5 border transition-all relative flex flex-col justify-between ${
                    isSelected
                      ? 'bg-amber-950/20 border-amber-500/80 shadow-lg shadow-amber-500/10 ring-1 ring-amber-500/50'
                      : 'bg-zinc-900/60 border-zinc-800 hover:border-zinc-700 hover:bg-zinc-900'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-zinc-800 border border-zinc-700 text-amber-300">
                        {h.title_badge}
                      </span>
                      {isSelected ? (
                        <CheckCircle2 className="w-5 h-5 text-amber-400" />
                      ) : (
                        <div className="w-5 h-5 rounded-full border border-zinc-700" />
                      )}
                    </div>

                    <p className="text-sm font-medium text-zinc-100 leading-snug">
                      "{h.hook_text}"
                    </p>

                    <p className="text-xs text-zinc-400 italic">
                      💡 {h.reason}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-zinc-800/80 flex items-center justify-between text-[11px] text-zinc-500">
                    <span>Thời lượng: ~{h.estimated_duration_sec}s</span>
                    <span className="text-amber-400/80 font-medium">Bấm để chọn</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Active Hook Customizer */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-zinc-200 flex items-center space-x-2">
                <Edit3 className="w-4 h-4 text-amber-400" />
                <span>Nội Dung Hook Đã Chọn (Có thể tự do chỉnh sửa)</span>
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePlayPreview}
                  disabled={playingAudio || !customText}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500 hover:bg-amber-600 text-zinc-950 transition font-semibold"
                >
                  <Volume2 className={`w-3.5 h-3.5 ${playingAudio ? 'animate-pulse' : ''}`} />
                  <span>{playingAudio ? 'Đang đọc...' : 'Nghe thử giọng'}</span>
                </button>
              </div>
            </div>

            <textarea
              rows={3}
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder="Nhập câu hook mở đầu video..."
              className="w-full bg-zinc-950 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-amber-500"
            />

            <div className="flex items-center justify-between text-xs text-zinc-500">
              <span>Độ dài: {customText.length} ký tự ({customText.split(/\s+/).filter(Boolean).length} từ)</span>
              <span>Phân cảnh Hook sẽ xuất hiện ở giây 0 - 3s trước khi bài viết gốc và bình luận hiển thị</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-zinc-900/50 border border-dashed border-zinc-800 rounded-2xl p-12 text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-zinc-500 mx-auto" />
          <h4 className="text-sm font-semibold text-zinc-300">Đã tắt phân cảnh mở đầu (Hook)</h4>
          <p className="text-xs text-zinc-500 max-w-md mx-auto">
            Video sẽ bắt đầu trực tiếp từ thẻ bài viết Threads gốc. Bạn có thể bật lại Hook bất cứ lúc nào ở góc trên.
          </p>
        </div>
      )}

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-6 border-t border-zinc-800">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại: Chọn bình luận</span>
        </button>

        <button
          onClick={handleSaveAndNext}
          disabled={saving}
          className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold shadow-lg shadow-violet-600/20 transition"
        >
          <span>Tiếp tục: Giọng đọc & Timeline</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
