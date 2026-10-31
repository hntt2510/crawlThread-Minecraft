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
  Sparkles 
} from 'lucide-react';
import { api } from '../../api/client';
import { Project, ThreadsComment, CommentSelection } from '../../types';

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

  const handleTextChange = (index: number, field: 'display_text' | 'tts_text', value: string) => {
    const updated = [...selections];
    updated[index][field] = value;
    setSelections(updated);
  };

  const handleRestore = async (index: number, commentId: string) => {
    try {
      const originalText = await api.restoreComment(project.id, commentId);
      const updated = [...selections];
      updated[index].display_text = originalText;
      updated[index].tts_text = originalText;
      setSelections(updated);
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
    } finally {
      setSaving(false);
    }
  };

  const filteredComments = allComments.filter((c) => {
    if (filterType === 'top_level') return !c.parent_comment_id;
    if (filterType === 'replies') return !!c.parent_comment_id;
    return true;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-6">
      {/* Step Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-zinc-100">Bước 2 — Quản Lý & Lựa Chọn Bình Luận</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Chọn các bình luận ấn tượng nhất để xuất hiện trong video. Tách biệt nội dung hiển thị (Display Text) và lời đọc máy (TTS Text).
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-zinc-400">Đã chọn:</span>
          <span className="bg-violet-600/30 text-violet-300 font-bold px-3 py-1 rounded-full text-xs border border-violet-500/30">
            {selections.length} bình luận
          </span>
        </div>
      </div>

      {/* Quick Action Toolbar */}
      <div className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
        {/* Quick select buttons */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-zinc-400 font-medium flex items-center space-x-1">
            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
            <span>Chọn nhanh:</span>
          </span>
          <button
            onClick={() => handleSelectTopN(3)}
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs px-3 py-1.5 rounded-lg border border-zinc-700 transition-colors"
          >
            Top 3 Like
          </button>
          <button
            onClick={() => handleSelectTopN(5)}
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs px-3 py-1.5 rounded-lg border border-zinc-700 transition-colors"
          >
            Top 5 Like
          </button>
          <button
            onClick={() => handleSelectTopN(10)}
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs px-3 py-1.5 rounded-lg border border-zinc-700 transition-colors"
          >
            Top 10 Like
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center space-x-1 bg-zinc-950 p-1 rounded-lg border border-zinc-800 text-xs">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'all' ? 'bg-violet-600 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'}`}
          >
            Tất cả ({allComments.length})
          </button>
          <button
            onClick={() => setFilterType('top_level')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'top_level' ? 'bg-violet-600 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'}`}
          >
            Bình luận gốc
          </button>
          <button
            onClick={() => setFilterType('replies')}
            className={`px-3 py-1 rounded-md transition-colors ${filterType === 'replies' ? 'bg-violet-600 text-white font-medium' : 'text-zinc-400 hover:text-zinc-200'}`}
          >
            Phản hồi con
          </button>
        </div>
      </div>

      {/* Main Grid: Selected Pipeline vs Raw Comments Pool */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Selected Comments Pipeline (Ordering & Editing) */}
        <div className="lg:col-span-7 space-y-4">
          <h3 className="text-sm font-semibold uppercase text-zinc-300 tracking-wider flex items-center justify-between">
            <span>Thứ Tự Phân Cảnh Xuất Hiện Trong Video ({selections.length})</span>
            <span className="text-xs font-normal text-zinc-500">Kéo/Dùng nút để đổi thứ tự</span>
          </h3>

          {selections.length === 0 ? (
            <div className="border border-dashed border-zinc-800 rounded-2xl p-8 text-center text-zinc-500 text-sm">
              Chưa có bình luận nào được chọn. Hãy tick chọn các bình luận bên phải hoặc bấm các nút chọn nhanh ở trên.
            </div>
          ) : (
            <div className="space-y-4">
              {selections.map((sel, idx) => (
                <div key={sel.comment_id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3 relative group">
                  {/* Item Header */}
                  <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2.5">
                    <div className="flex items-center space-x-2">
                      <span className="w-5 h-5 rounded-full bg-violet-600 text-white font-bold text-xs flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <span className="font-semibold text-xs text-zinc-200">{sel.author_display_name || sel.author_username}</span>
                      <span className="text-xs text-zinc-500">@{sel.author_username}</span>
                    </div>

                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleMove(idx, 'up')}
                        disabled={idx === 0}
                        className="p-1 rounded hover:bg-zinc-800 text-zinc-400 disabled:opacity-30 cursor-pointer"
                        title="Di chuyển lên trước"
                      >
                        <MoveUp className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleMove(idx, 'down')}
                        disabled={idx === selections.length - 1}
                        className="p-1 rounded hover:bg-zinc-800 text-zinc-400 disabled:opacity-30 cursor-pointer"
                        title="Di chuyển xuống sau"
                      >
                        <MoveDown className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleRestore(idx, sel.comment_id)}
                        className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-amber-400 cursor-pointer"
                        title="Khôi phục nguyên bản"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setSelections(selections.filter((_, i) => i !== idx))}
                        className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-rose-400 cursor-pointer"
                        title="Xóa khỏi video"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Dual Text Inputs */}
                  <div className="space-y-2">
                    <div>
                      <label className="block text-[11px] font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                        1. Nội dung hiển thị trên thẻ video (Display Text)
                      </label>
                      <textarea
                        value={sel.display_text}
                        onChange={(e) => handleTextChange(idx, 'display_text', e.target.value)}
                        rows={2}
                        className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-xs text-zinc-200 focus:outline-none focus:border-violet-500"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-indigo-400 uppercase tracking-wider mb-1">
                        2. Lời đọc thuyết minh tiếng Việt (TTS Text)
                      </label>
                      <textarea
                        value={sel.tts_text}
                        onChange={(e) => handleTextChange(idx, 'tts_text', e.target.value)}
                        rows={2}
                        className="w-full bg-zinc-950 border border-indigo-900/50 rounded-lg p-2.5 text-xs text-indigo-200 focus:outline-none focus:border-indigo-500 font-medium"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Pool of all crawled comments */}
        <div className="lg:col-span-5 space-y-4">
          <h3 className="text-sm font-semibold uppercase text-zinc-300 tracking-wider">
            Kho Bình Luận Gốc Đã Thu Thập ({filteredComments.length})
          </h3>

          <div className="max-h-[640px] overflow-y-auto space-y-2.5 pr-1">
            {filteredComments.map((comment) => {
              const isSelected = selections.some((s) => s.comment_id === comment.id);

              return (
                <div
                  key={comment.id}
                  onClick={() => handleToggleSelect(comment)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer text-xs space-y-2 ${
                    isSelected
                      ? 'bg-violet-950/20 border-violet-500/50 shadow-sm'
                      : 'bg-zinc-900/90 border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {isSelected ? (
                        <CheckSquare className="w-4 h-4 text-violet-400 flex-shrink-0" />
                      ) : (
                        <Square className="w-4 h-4 text-zinc-600 flex-shrink-0" />
                      )}
                      <span className="font-semibold text-zinc-200">{comment.author_display_name || comment.author_username}</span>
                      <span className="text-zinc-500">@{comment.author_username}</span>
                    </div>

                    <div className="flex items-center space-x-3 text-zinc-400 text-[11px]">
                      <span className="flex items-center space-x-1">
                        <Heart className="w-3 h-3 text-rose-500" />
                        <span>{comment.like_count ?? 0}</span>
                      </span>
                      {comment.reply_count ? (
                        <span className="flex items-center space-x-1">
                          <MessageCircle className="w-3 h-3 text-indigo-400" />
                          <span>{comment.reply_count}</span>
                        </span>
                      ) : null}
                    </div>
                  </div>

                  <p className="text-zinc-300 leading-relaxed line-clamp-3">{comment.content}</p>
                </div>
              );
            })}
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
          <span>Quay lại Bước 1</span>
        </button>

        <button
          onClick={handleSaveAndContinue}
          disabled={saving || selections.length === 0}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs font-semibold px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all cursor-pointer"
        >
          <span>{saving ? 'Đang lưu...' : 'Lưu & Sang Phòng Thu Giọng Đọc'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
