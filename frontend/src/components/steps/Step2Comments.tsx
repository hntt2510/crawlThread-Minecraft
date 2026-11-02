import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  ArrowLeft, 
  RotateCcw, 
  MoveUp, 
  MoveDown, 
  Trash2, 
  CheckSquare, 
  Square, 
  Heart, 
  MessageCircle, 
  Sparkles,
  CornerDownRight,
  ShieldCheck,
  AlertTriangle,
  Info
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, ThreadsComment, CommentSelection, CrawlQualityReport } from '../../types';

interface Step2Props {
  project: Project;
  onNext: () => void;
  onBack: () => void;
}

export const Step2Comments: React.FC<Step2Props> = ({ project, onNext, onBack }) => {
  const [allComments, setAllComments] = useState<ThreadsComment[]>([]);
  const [selections, setSelections] = useState<CommentSelection[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'top_level' | 'replies'>('all');
  const [curating, setCurating] = useState(false);
  const [curationInsight, setCurationInsight] = useState('');
  const [curationMode, setCurationMode] = useState<'balanced' | 'humor' | 'story' | 'controversy'>('balanced');

  const qualityReport: CrawlQualityReport | undefined = project.settings?.quality_report;

  const handleAiCurate = async (targetCount: number = 5, mode: string = curationMode) => {
    setCurating(true);
    try {
      const res = await api.curateComments(project.id, targetCount, mode, true);
      setCurationInsight(res.summary_insight || '');
      const sel = await api.getProjectSelections(project.id);
      setSelections(sel);
    } catch (e) {
      console.error('Error during curation:', e);
    } finally {
      setCurating(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [project.id]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [comments, sel] = await Promise.all([
        api.getProjectComments(project.id),
        api.getProjectSelections(project.id),
      ]);
      setAllComments(comments);
      setSelections(sel);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSelect = (comment: ThreadsComment) => {
    const exists = selections.find((s) => s.comment_id === comment.id);
    if (exists) {
      setSelections(selections.filter((s) => s.comment_id !== comment.id));
    } else {
      const newSel: CommentSelection = {
        id: `temp_${Date.now()}`,
        project_id: project.id,
        comment_id: comment.id,
        sequence_order: selections.length,
        display_text: comment.content,
        tts_text: comment.content,
        is_active: true,
        author_username: comment.author_username,
        author_display_name: comment.author_display_name,
        author_avatar_url: comment.author_avatar_url,
        like_count: comment.like_count,
        reply_count: comment.reply_count,
      };
      setSelections([...selections, newSel]);
    }
  };

  const handleSelectTopN = (n: number) => {
    const sorted = [...allComments].sort((a, b) => (b.like_count || 0) - (a.like_count || 0));
    const top = sorted.slice(0, n);
    const newSelections: CommentSelection[] = top.map((c, idx) => ({
      id: `temp_${idx}_${Date.now()}`,
      project_id: project.id,
      comment_id: c.id,
      sequence_order: idx,
      display_text: c.content,
      tts_text: c.content,
      is_active: true,
      author_username: c.author_username,
      author_display_name: c.author_display_name,
      like_count: c.like_count,
      reply_count: c.reply_count,
    }));
    setSelections(newSelections);
  };

  const handleMove = (index: number, direction: 'up' | 'down') => {
    const targetIdx = direction === 'up' ? index - 1 : index + 1;
    if (targetIdx < 0 || targetIdx >= selections.length) return;
    const reordered = [...selections];
    const [moved] = reordered.splice(index, 1);
    reordered.splice(targetIdx, 0, moved);
    setSelections(reordered);
  };

  const handleRemove = (commentId: string) => {
    setSelections(selections.filter((s) => s.comment_id !== commentId));
  };

  const handleTextChange = (commentId: string, field: 'display_text' | 'tts_text', value: string) => {
    setSelections(
      selections.map((s) => {
        if (s.comment_id === commentId) {
          return { ...s, [field]: value };
        }
        return s;
      })
    );
  };

  const handleRestoreOriginal = async (commentId: string) => {
    try {
      const origContent = await api.restoreComment(project.id, commentId);
      setSelections(
        selections.map((s) => {
          if (s.comment_id === commentId) {
            return { ...s, display_text: origContent, tts_text: origContent };
          }
          return s;
        })
      );
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveAndContinue = async () => {
    setSaving(true);
    try {
      const payload = selections.map((s, idx) => ({
        comment_id: s.comment_id,
        sequence_order: idx,
        display_text: s.display_text,
        tts_text: s.tts_text,
        voice_id: s.voice_id || 'vi-VN-HoaiMyNeural',
        voice_rate: s.voice_rate || 1.0,
        is_active: true,
      }));
      await api.saveSelections(project.id, payload);
      onNext();
    } catch (e) {
      console.error(e);
      alert('Không thể lưu danh sách bình luận đã chọn.');
    } finally {
      setSaving(false);
    }
  };

  const filteredComments = allComments.filter((c) => {
    if (filterType === 'top_level') return !c.parent_comment_id && c.nesting_depth === 0;
    if (filterType === 'replies') return !!c.parent_comment_id || c.nesting_depth > 0;
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto space-y-6 py-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <span>Bước 2 — Quản Lý & Lựa Chọn Bình Luận</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-violet-600/30 text-violet-300 border border-violet-500/30">
              Đã xác thực cây phân cấp
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Chọn các bình luận ấn tượng nhất để xuất hiện trong video. Tách biệt nội dung hiển thị (Display Text) và lời đọc máy (TTS Text).
          </p>
        </div>
        <div className="flex items-center space-x-2 shrink-0">
          <span className="text-xs text-slate-400">Đã chọn cho video:</span>
          <span className="bg-violet-600/30 text-violet-300 font-bold px-3 py-1 rounded-full text-xs border border-violet-500/30">
            {selections.length} bình luận
          </span>
        </div>
      </div>

      {/* Crawl Quality Report Banner */}
      {qualityReport && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              <strong>Dữ liệu chuẩn xác:</strong> Đã thu thập{' '}
              <strong className="text-white">{qualityReport.retrieved_comment_count}</strong> bình luận
              (gồm <strong className="text-violet-400">{qualityReport.retrieved_reply_count}</strong> phản hồi phân cấp).
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span>
              Nguồn: <strong className="text-slate-200">{qualityReport.data_source === 'threads_official_api' ? 'Meta Threads API' : 'Relay Cache Scraper'}</strong>
            </span>
            <span>
              Lọc trùng lặp: <strong className="text-slate-200">{qualityReport.duplicate_count}</strong>
            </span>
            {qualityReport.completeness_warnings.length > 0 && (
              <span className="text-amber-400 flex items-center gap-1" title={qualityReport.completeness_warnings.join(' | ')}>
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Cảnh báo hiển thị
              </span>
            )}
          </div>
        </div>
      )}
      {/* AI Smart Curation & Quick Action Toolbar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* AI Curation Button & Modes */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleAiCurate(5, curationMode)}
              disabled={curating}
              className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-md shadow-violet-600/20 transition"
            >
              <Sparkles className={`w-3.5 h-3.5 ${curating ? 'animate-spin' : ''}`} />
              <span>{curating ? 'AI đang phân tích...' : '🤖 AI Tuyển Chọn Thông Minh'}</span>
            </button>

            {/* Mode selection */}
            <select
              value={curationMode}
              onChange={(e) => setCurationMode(e.target.value as any)}
              className="bg-slate-800 border border-slate-700 text-slate-200 text-xs px-2.5 py-1.5 rounded-lg focus:outline-none"
            >
              <option value="balanced">🌟 Cân bằng (Viral tổng hợp)</option>
              <option value="humor">😂 Hài hước & Bẻ lái</option>
              <option value="story">📖 Kể chuyện & Trải nghiệm</option>
              <option value="controversy">⚡ Tranh luận & Đa chiều</option>
            </select>
          </div>

          {/* Quick select buttons & Filter */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400 font-medium">Chọn nhanh:</span>
              <button
                onClick={() => handleAiCurate(3, curationMode)}
                disabled={curating}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
              >
                Top 3 AI
              </button>
              <button
                onClick={() => handleAiCurate(5, curationMode)}
                disabled={curating}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
              >
                Top 5 AI
              </button>
              <button
                onClick={() => handleAiCurate(10, curationMode)}
                disabled={curating}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
              >
                Top 10 AI
              </button>
            </div>

            {/* Filter Tabs */}
            <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
              <button
                onClick={() => setFilterType('all')}
                className={`px-3 py-1 rounded-md transition ${filterType === 'all' ? 'bg-violet-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Tất cả ({allComments.length})
              </button>
              <button
                onClick={() => setFilterType('top_level')}
                className={`px-3 py-1 rounded-md transition ${filterType === 'top_level' ? 'bg-violet-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Bình luận gốc
              </button>
              <button
                onClick={() => setFilterType('replies')}
                className={`px-3 py-1 rounded-md transition ${filterType === 'replies' ? 'bg-violet-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Phản hồi con
              </button>
            </div>
          </div>
        </div>

        {curationInsight && (
          <div className="bg-violet-950/30 border border-violet-800/40 rounded-lg px-3 py-2 text-xs text-violet-300 flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-violet-400 shrink-0" />
            <span>{curationInsight}</span>
          </div>
        )}
      </div>

      {/* Main Grid: Selected Pipeline vs Raw Comments Pool */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Selected Comments Pipeline (Ordering & Editing) */}
        <div className="lg:col-span-7 space-y-4">
          <h3 className="text-sm font-semibold uppercase text-slate-300 tracking-wider flex items-center justify-between">
            <span>Thứ Tự Phân Cảnh Xuất Hiện Trong Video ({selections.length})</span>
            <span className="text-xs font-normal text-slate-500">Dùng nút di chuyển để đổi thứ tự</span>
          </h3>

          {selections.length === 0 ? (
            <div className="border border-dashed border-slate-800 rounded-2xl p-8 text-center text-slate-500 text-sm">
              Chưa có bình luận nào được chọn. Hãy tick chọn các bình luận bên phải hoặc bấm các nút chọn nhanh ở trên.
            </div>
          ) : (
            <div className="space-y-3.5 max-h-[660px] overflow-y-auto pr-2 custom-scrollbar">
              {selections.map((sel, idx) => (
                <div key={sel.comment_id} className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 relative group">
                  {/* Item Header */}
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
                    <div className="flex items-center space-x-2">
                      <span className="w-5 h-5 rounded-full bg-violet-600 text-white font-bold text-xs flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <span className="font-semibold text-xs text-slate-200">{sel.author_display_name || sel.author_username}</span>
                      <span className="text-xs text-slate-500">@{sel.author_username}</span>
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleMove(idx, 'up')}
                        disabled={idx === 0}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 disabled:opacity-30 cursor-pointer"
                        title="Di chuyển lên trước"
                      >
                        <MoveUp className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleMove(idx, 'down')}
                        disabled={idx === selections.length - 1}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 disabled:opacity-30 cursor-pointer"
                        title="Di chuyển xuống sau"
                      >
                        <MoveDown className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleRestoreOriginal(sel.comment_id)}
                        className="p-1 rounded hover:bg-slate-800 text-amber-400 cursor-pointer ml-1"
                        title="Khôi phục nội dung gốc"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleRemove(sel.comment_id)}
                        className="p-1 rounded hover:bg-rose-950/40 text-rose-400 cursor-pointer ml-1"
                        title="Xóa khỏi video"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Dual Text Editors */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    {/* Display Text */}
                    <div className="space-y-1">
                      <label className="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
                        <span>Chữ hiển thị trên thẻ video (Display)</span>
                        <span className="text-[10px] text-slate-500 font-normal">Tự động ngắt dòng</span>
                      </label>
                      <textarea
                        rows={3}
                        value={sel.display_text}
                        onChange={(e) => handleTextChange(sel.comment_id, 'display_text', e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-violet-500 transition resize-none leading-relaxed"
                      />
                    </div>

                    {/* TTS Text */}
                    <div className="space-y-1">
                      <label className="text-[11px] font-semibold text-violet-400 flex items-center justify-between">
                        <span>Lời đọc thuyết minh máy (TTS Voice)</span>
                        <span className="text-[10px] text-violet-400 font-normal">Thêm dấu câu để ngắt nghỉ</span>
                      </label>
                      <textarea
                        rows={3}
                        value={sel.tts_text}
                        onChange={(e) => handleTextChange(sel.comment_id, 'tts_text', e.target.value)}
                        className="w-full bg-slate-950 border border-violet-900/40 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-violet-500 transition resize-none leading-relaxed"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Pool of all crawled comments with Nested Tree Representation */}
        <div className="lg:col-span-5 space-y-4">
          <h3 className="text-sm font-semibold uppercase text-slate-300 tracking-wider">
            Kho Bình Luận Phân Cấp ({filteredComments.length})
          </h3>

          <div className="max-h-[660px] overflow-y-auto space-y-2.5 pr-2 custom-scrollbar">
            {filteredComments.map((comment) => {
              const isSelected = selections.some((s) => s.comment_id === comment.id);
              const isNested = comment.nesting_depth > 0 || !!comment.parent_comment_id;

              return (
                <div
                  key={comment.id}
                  onClick={() => handleToggleSelect(comment)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer text-xs space-y-2 ${
                    isNested ? 'ml-4 pl-3.5 border-l-2 border-violet-500/50' : ''
                  } ${
                    isSelected
                      ? 'bg-violet-950/20 border-violet-500/50 shadow-sm'
                      : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {isSelected ? (
                        <CheckSquare className="w-4 h-4 text-violet-400 flex-shrink-0" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-600 flex-shrink-0" />
                      )}
                      <span className="font-semibold text-slate-200">{comment.author_display_name || comment.author_username}</span>
                      <span className="text-slate-500">@{comment.author_username}</span>
                      {isNested && (
                        <span className="inline-flex items-center gap-0.5 text-[10px] px-1.5 py-0.2 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20">
                          <CornerDownRight className="w-2.5 h-2.5" />
                          {comment.parent_author_username ? `@${comment.parent_author_username}` : `Cấp ${comment.nesting_depth || 1}`}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-3 text-slate-400 text-[11px]">
                      <span className="flex items-center space-x-1" title="Lượt thích">
                        <Heart className="w-3 h-3 text-rose-500" />
                        <span>{comment.like_count !== null && comment.like_count !== undefined ? comment.like_count : 'N/A'}</span>
                      </span>
                      {comment.reply_count ? (
                        <span className="flex items-center space-x-1" title="Phản hồi">
                          <MessageCircle className="w-3 h-3 text-indigo-400" />
                          <span>{comment.reply_count}</span>
                        </span>
                      ) : null}
                    </div>
                  </div>

                  <p className="text-slate-300 leading-relaxed line-clamp-3">{comment.content}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-800">
        <button
          onClick={onBack}
          className="border border-slate-700 hover:bg-slate-800 text-slate-300 text-xs font-medium px-5 py-2.5 rounded-xl flex items-center space-x-2 transition cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Quay lại Bước 1 Khám Phá</span>
        </button>

        <button
          onClick={handleSaveAndContinue}
          disabled={saving || selections.length === 0}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs font-semibold px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition cursor-pointer"
        >
          <span>{saving ? 'Đang lưu...' : 'Lưu & Sang Phòng Thu Giọng Đọc'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
