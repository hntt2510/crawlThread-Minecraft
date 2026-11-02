import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  MoveUp,
  MoveDown,
  Volume2,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  Wrench,
  CheckCircle2,
  Layers,
  ArrowRight,
  ArrowLeft,
  Music,
  Clock,
  Flame,
  MessageSquare,
  FileText
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, TimelinePlan, TimelineScene, QualityCheckReport } from '../../types';

interface Step5TimelinePreviewProps {
  project: Project;
  onNext: () => void;
  onBack: () => void;
}

export const Step5TimelinePreview: React.FC<Step5TimelinePreviewProps> = ({ project, onNext, onBack }) => {
  const [plan, setPlan] = useState<TimelinePlan | null>(null);
  const [qualityReport, setQualityReport] = useState<QualityCheckReport | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeSceneIndex, setActiveSceneIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTimeSec, setCurrentTimeSec] = useState<number>(0);
  const [fixing, setFixing] = useState<boolean>(false);
  const [reordering, setReordering] = useState<boolean>(false);

  const playbackTimerRef = useRef<any>(null);

  useEffect(() => {
    loadTimelineAndQuality();
  }, [project.id]);

  const loadTimelineAndQuality = async () => {
    setLoading(true);
    try {
      const [p, q] = await Promise.all([
        api.getTimelinePlan(project.id, project.settings?.video_pace || 'balanced'),
        api.getQualityReport(project.id),
      ]);
      setPlan(p);
      setQualityReport(q);
      setActiveSceneIndex(0);
      setCurrentTimeSec(0);
    } catch (e) {
      console.error('Error loading timeline/quality:', e);
    } finally {
      setLoading(false);
    }
  };

  // Playback simulation
  useEffect(() => {
    if (isPlaying && plan) {
      playbackTimerRef.current = setInterval(() => {
        setCurrentTimeSec((prev) => {
          const next = prev + 0.1;
          if (next >= plan.total_duration_sec) {
            setIsPlaying(false);
            return 0;
          }
          // Find which scene is active at next
          const activeIdx = plan.scenes.findIndex(
            (s) => next >= s.start_time_sec && next < s.end_time_sec
          );
          if (activeIdx !== -1) {
            setActiveSceneIndex(activeIdx);
          }
          return next;
        });
      }, 100);
    } else {
      if (playbackTimerRef.current) clearInterval(playbackTimerRef.current);
    }
    return () => {
      if (playbackTimerRef.current) clearInterval(playbackTimerRef.current);
    };
  }, [isPlaying, plan]);

  const handleTogglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSelectScene = (idx: number) => {
    if (!plan || !plan.scenes[idx]) return;
    setActiveSceneIndex(idx);
    setCurrentTimeSec(plan.scenes[idx].start_time_sec);
  };

  const handleMoveScene = async (currentIndex: number, direction: 'up' | 'down') => {
    if (!plan) return;
    const targetIdx = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (targetIdx < 0 || targetIdx >= plan.scenes.length) return;

    // Filter only comment scenes for DB order
    const commentScenes = plan.scenes.filter((s) => s.scene_type === 'comment');
    const commentIds = commentScenes.map((s) => {
      // scene id e.g. scene_02_c_0 -> extract comment_id
      return s.id;
    });

    setReordering(true);
    try {
      // Re-order local array first
      const newScenes = [...plan.scenes];
      const temp = newScenes[currentIndex];
      newScenes[currentIndex] = newScenes[targetIdx];
      newScenes[targetIdx] = temp;
      setPlan({ ...plan, scenes: newScenes });
      setActiveSceneIndex(targetIdx);

      // Reload fresh timeline plan
      await loadTimelineAndQuality();
    } catch (e) {
      console.error(e);
    } finally {
      setReordering(false);
    }
  };

  const handleAutoFix = async () => {
    setFixing(true);
    try {
      await api.autoFixQuality(project.id);
      await loadTimelineAndQuality();
    } catch (e) {
      console.error(e);
    } finally {
      setFixing(false);
    }
  };

  if (loading || !plan) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4">
        <Sparkles className="w-8 h-8 text-violet-500 animate-spin" />
        <span className="text-zinc-400 text-sm font-medium">Đang đồng bộ kịch bản Timeline và phân tích chất lượng video...</span>
      </div>
    );
  }

  const activeScene = plan.scenes[activeSceneIndex] || plan.scenes[0];

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      {/* Top Banner: Quality Score & Auto-Fix */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg border ${
              (qualityReport?.score || 100) >= 80
                ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                : 'bg-amber-500/10 border-amber-500/40 text-amber-400'
            }`}>
              {qualityReport?.score || 100}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold text-zinc-100">Quality Checker (Kiểm Định Chất Lượng)</span>
                {qualityReport?.is_passed ? (
                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Đạt tiêu chuẩn xuất bản</span>
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-red-500/20 text-red-300 border border-red-500/30 flex items-center space-x-1">
                    <XCircle className="w-3 h-3" />
                    <span>Có lỗi cần xử lý</span>
                  </span>
                )}
              </div>
              <p className="text-xs text-zinc-400">
                {qualityReport?.suggestions[0] || 'Tất cả thông số an toàn (âm lượng, khoảng lặng, vùng hiển thị)'}
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {((qualityReport?.warnings.length || 0) > 0 || !qualityReport?.is_passed) && (
            <button
              onClick={handleAutoFix}
              disabled={fixing}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-amber-500 hover:bg-amber-600 text-zinc-950 transition shadow-md shadow-amber-500/20"
            >
              <Wrench className={`w-3.5 h-3.5 ${fixing ? 'animate-spin' : ''}`} />
              <span>{fixing ? 'Đang sửa...' : 'Tự động sửa lỗi (Auto-Fix)'}</span>
            </button>
          )}

          <div className="flex items-center space-x-2 text-xs font-mono bg-zinc-950 px-3 py-2 rounded-xl border border-zinc-800 text-zinc-300">
            <Clock className="w-3.5 h-3.5 text-zinc-500" />
            <span>Tổng thời lượng: <strong className="text-violet-400">{plan.total_duration_sec}s</strong></span>
          </div>
        </div>
      </div>

      {/* Main Grid: Interactive 9:16 Video Player vs Timeline Scenes List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: 9:16 Interactive Visual Mockup Player (lg:col-span-5) */}
        <div className="lg:col-span-5 flex flex-col items-center sticky top-4">
          <div className="w-[320px] h-[568px] bg-zinc-950 rounded-3xl border-4 border-zinc-800 shadow-2xl overflow-hidden relative flex flex-col justify-between p-4">
            {/* Background Procedural Simulation */}
            <div className="absolute inset-0 bg-gradient-to-b from-indigo-950/40 via-zinc-900 to-zinc-950 -z-10" />

            {/* Top Indicator */}
            <div className="flex items-center justify-between z-10 text-[10px] text-zinc-400 bg-zinc-900/80 backdrop-blur-sm px-2.5 py-1 rounded-full border border-zinc-800">
              <span className="flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                <span>REC 1080x1920</span>
              </span>
              <span className="font-mono">{currentTimeSec.toFixed(1)}s / {plan.total_duration_sec}s</span>
            </div>

            {/* Card Overlay In Center */}
            <div className="flex-1 flex items-center justify-center z-10 px-1 py-4">
              {activeScene && (
                <div className={`w-full rounded-2xl p-4 border transition-all duration-300 transform ${
                  activeScene.zoom_effect ? 'scale-[1.03]' : 'scale-100'
                } ${
                  activeScene.scene_type === 'hook'
                    ? 'bg-zinc-900/95 border-amber-500/80 shadow-xl shadow-amber-500/10'
                    : activeScene.scene_type === 'post'
                    ? 'bg-zinc-900/95 border-violet-500/60 shadow-xl shadow-violet-500/10'
                    : 'bg-zinc-900/90 border-zinc-700/80 shadow-lg'
                }`}>
                  {/* Card Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-7 h-7 rounded-full bg-violet-600 flex items-center justify-center font-bold text-xs text-white">
                        {(activeScene.author_display_name || activeScene.author_username || 'U')[0].toUpperCase()}
                      </div>
                      <div>
                        <div className="text-[11px] font-bold text-zinc-100 truncate max-w-[130px]">
                          {activeScene.author_display_name || activeScene.author_username}
                        </div>
                        <div className="text-[9px] text-zinc-400">@{activeScene.author_username}</div>
                      </div>
                    </div>

                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                      activeScene.scene_type === 'hook'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : activeScene.scene_type === 'post'
                        ? 'bg-zinc-800 text-zinc-300 border-zinc-700'
                        : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                    }`}>
                      {activeScene.scene_type === 'hook' ? '⚡ MỞ ĐẦU' : activeScene.scene_type === 'post' ? 'BÀI GỐC' : 'BÌNH LUẬN'}
                    </span>
                  </div>

                  {/* Card Content */}
                  <p className="text-xs text-zinc-200 leading-relaxed font-sans line-clamp-6">
                    {activeScene.display_text}
                  </p>
                </div>
              )}
            </div>

            {/* Bottom Safe Zone & Smart Captions Preview */}
            <div className="z-10 space-y-2 mb-4">
              {/* Burned-in Caption Preview */}
              {activeScene && (
                <div className="bg-black/80 backdrop-blur-sm rounded-lg px-3 py-1.5 text-center text-xs font-bold text-white border border-zinc-800 shadow-md">
                  <span className="text-amber-300">
                    {activeScene.tts_text.slice(0, 32)}
                  </span>
                </div>
              )}

              {/* Safe Margin Indicator */}
              <div className="text-[9px] text-zinc-600 text-center uppercase tracking-wider font-mono">
                TikTok / Reels Safe Zone (Above Navigation)
              </div>
            </div>
          </div>

          {/* Player Controls Bar */}
          <div className="w-[320px] mt-4 flex items-center justify-between bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-2.5">
            <button
              onClick={handleTogglePlay}
              className="flex items-center space-x-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white transition"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span>{isPlaying ? 'Tạm dừng' : 'Xem trước'}</span>
            </button>

            <button
              onClick={() => {
                setIsPlaying(false);
                setCurrentTimeSec(0);
                setActiveSceneIndex(0);
              }}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
              title="Phát lại từ đầu"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <span className="text-xs font-mono text-zinc-400">
              Phân cảnh {activeSceneIndex + 1}/{plan.scenes.length}
            </span>
          </div>
        </div>

        {/* Right Column: Timeline Scenes List & Detailed Controls (lg:col-span-7) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase text-zinc-300 tracking-wider flex items-center space-x-2">
              <Layers className="w-4 h-4 text-violet-400" />
              <span>Các Phân Cảnh Timeline ({plan.scenes.length})</span>
            </h3>
            <span className="text-xs text-zinc-500">Bấm phân cảnh để xem trước khung hình tương ứng</span>
          </div>

          <div className="space-y-3 max-h-[640px] overflow-y-auto pr-2 custom-scrollbar">
            {plan.scenes.map((s, idx) => {
              const isActive = activeSceneIndex === idx;
              return (
                <div
                  key={s.id}
                  onClick={() => handleSelectScene(idx)}
                  className={`cursor-pointer rounded-2xl p-4 border transition-all ${
                    isActive
                      ? 'bg-zinc-900 border-violet-500/80 shadow-md ring-1 ring-violet-500/30'
                      : 'bg-zinc-900/60 border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    {/* Scene Badge & Author */}
                    <div className="flex items-center space-x-2">
                      <span className={`w-6 h-6 rounded-lg text-xs font-bold flex items-center justify-center ${
                        s.scene_type === 'hook'
                          ? 'bg-amber-500 text-zinc-950 font-black'
                          : s.scene_type === 'post'
                          ? 'bg-violet-600 text-white'
                          : 'bg-zinc-800 text-zinc-300 border border-zinc-700'
                      }`}>
                        {idx + 1}
                      </span>

                      <span className="text-xs font-semibold text-zinc-200">
                        {s.author_display_name || s.author_username}
                      </span>

                      <span className={`text-[10px] font-medium px-2 py-0.5 rounded border ${
                        s.scene_type === 'hook'
                          ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                          : s.scene_type === 'post'
                          ? 'bg-violet-500/15 text-violet-300 border-violet-500/30'
                          : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                      }`}>
                        {s.scene_type === 'hook' ? '⚡ Hook' : s.scene_type === 'post' ? 'Bài Gốc' : 'Bình Luận'}
                      </span>

                      {s.is_punchline && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-300 border border-pink-500/30">
                          😂 Punchline
                        </span>
                      )}

                      {s.sfx_id && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-sky-500/15 text-sky-300 border border-sky-500/30 flex items-center space-x-1">
                          <Volume2 className="w-3 h-3" />
                          <span>{s.sfx_id}</span>
                        </span>
                      )}
                    </div>

                    {/* Timing & Reorder Buttons */}
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono text-zinc-400">
                        {s.start_time_sec}s - {s.end_time_sec}s ({s.duration_sec}s)
                      </span>

                      {s.scene_type === 'comment' && (
                        <div className="flex items-center space-x-1 bg-zinc-950 p-0.5 rounded-lg border border-zinc-800">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMoveScene(idx, 'up');
                            }}
                            disabled={idx <= (plan.has_hook ? 2 : 1) || reordering}
                            className="p-1 text-zinc-400 hover:text-zinc-200 disabled:opacity-20"
                            title="Di chuyển lên"
                          >
                            <MoveUp className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMoveScene(idx, 'down');
                            }}
                            disabled={idx >= plan.scenes.length - 1 || reordering}
                            className="p-1 text-zinc-400 hover:text-zinc-200 disabled:opacity-20"
                            title="Di chuyển xuống"
                          >
                            <MoveDown className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-zinc-300 mt-2 line-clamp-2">
                    {s.display_text}
                  </p>

                  <div className="mt-2 pt-2 border-t border-zinc-800/60 flex items-center justify-between text-[11px] text-zinc-500">
                    <span>Lời đọc TTS: <em className="text-zinc-400">{s.tts_text.slice(0, 45)}...</em></span>
                    <span>Khoảng nghỉ: {s.pause_buffer_sec}s</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-6 border-t border-zinc-800">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại: Giọng đọc</span>
        </button>

        <button
          onClick={onNext}
          className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold shadow-lg shadow-violet-600/20 transition"
        >
          <span>Tiến hành dựng video</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
