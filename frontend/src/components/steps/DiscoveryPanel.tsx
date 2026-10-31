import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Search,
  RefreshCw,
  Flame,
  MessageCircle,
  Heart,
  Repeat,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Link as LinkIcon,
  CheckCircle2,
  AlertCircle,
  Filter,
  Film,
  Smile,
  Cpu,
  Users,
  TrendingUp,
  Utensils,
  Compass,
  Trophy,
  BookOpen,
  Layers,
  FileText,
  Image as ImageIcon,
  Video as VideoIcon
} from 'lucide-react';
import { api } from '../../api/client';
import { DiscoveredPost, TrendingTopic } from '../../types';

interface DiscoveryPanelProps {
  onSelectPost: (post: DiscoveredPost) => void;
  onManualUrlSubmit: (url: string) => void;
  isLoading: boolean;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  all: <Sparkles className="w-3.5 h-3.5" />,
  entertainment: <Film className="w-3.5 h-3.5" />,
  lifestyle: <Smile className="w-3.5 h-3.5" />,
  technology: <Cpu className="w-3.5 h-3.5" />,
  society: <Users className="w-3.5 h-3.5" />,
  business: <TrendingUp className="w-3.5 h-3.5" />,
  food: <Utensils className="w-3.5 h-3.5" />,
  travel: <Compass className="w-3.5 h-3.5" />,
  sports: <Trophy className="w-3.5 h-3.5" />,
  education: <BookOpen className="w-3.5 h-3.5" />,
  relationships: <Heart className="w-3.5 h-3.5" />
};

export const DiscoveryPanel: React.FC<DiscoveryPanelProps> = ({
  onSelectPost,
  onManualUrlSubmit,
  isLoading
}) => {
  const [categories, setCategories] = useState<Record<string, any>>({});
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [topics, setTopics] = useState<TrendingTopic[]>([]);
  const [posts, setPosts] = useState<DiscoveredPost[]>([]);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [activeQuery, setActiveQuery] = useState<string>('');
  const [mediaType, setMediaType] = useState<string>('ALL');
  const [timeWindow, setTimeWindow] = useState<'24h' | '3d' | '7d' | 'all'>('7d');
  const [apiStatus, setApiStatus] = useState<any>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [manualUrl, setManualUrl] = useState<string>('');
  const [showManualInput, setShowManualInput] = useState<boolean>(false);

  // Initial load
  useEffect(() => {
    loadCategories();
    loadStatus();
    loadDiscovery();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await api.getDiscoveryCategories();
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories', err);
    }
  };

  const loadStatus = async () => {
    try {
      const status = await api.getDiscoveryStatus();
      setApiStatus(status);
    } catch (err) {
      console.error('Failed to load discovery status', err);
    }
  };

  const loadDiscovery = async (overrideKeyword?: string, overrideCategory?: string) => {
    setIsSearching(true);
    try {
      const kw = overrideKeyword !== undefined ? overrideKeyword : searchKeyword;
      const cat = overrideCategory !== undefined ? overrideCategory : selectedCategory;

      const result = await api.searchDiscovery({
        keyword: kw,
        category: cat,
        search_type: 'BOTH',
        media_type: mediaType,
        time_window: timeWindow,
        limit: 30
      });

      setPosts(result.posts || []);
      setTopics(result.topics || []);
      setActiveQuery(result.query || '');
      if (result.api_status) {
        setApiStatus(result.api_status);
      }
    } catch (err) {
      console.error('Failed to search discovery', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCategorySelect = (catKey: string) => {
    setSelectedCategory(catKey);
    setSearchKeyword('');
    loadDiscovery('', catKey);
  };

  const handleTopicClick = (topicName: string) => {
    setSearchKeyword(topicName);
    loadDiscovery(topicName, selectedCategory);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadDiscovery();
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualUrl.trim()) {
      onManualUrlSubmit(manualUrl.trim());
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header & Live Status Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
                🇻🇳 Thị Trường Việt Nam
              </span>
              {apiStatus?.status === 'connected' ? (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Threads API Kết Nối: @{apiStatus.username}
                </span>
              ) : apiStatus?.status === 'permission_required' ? (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  Chờ duyệt Meta App Review (Sử dụng Gợi ý xu hướng VN)
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
                  Đề xuất xu hướng Việt Nam tự động
                </span>
              )}
            </div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-violet-400" />
              Khám Phá Bài Viết Threads Thịnh Hành
            </h2>
            <p className="text-sm text-slate-400">
              Tự động tìm kiếm chủ đề nóng, xếp hạng theo Studio Hot Score và tạo video trong 1 click.
            </p>
          </div>

          {/* Search Input Bar */}
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 max-w-md w-full">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Tìm từ khóa, nghệ sĩ, chủ đề..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-violet-500 transition"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="bg-violet-600 hover:bg-violet-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-1.5 shrink-0"
            >
              {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Tìm kiếm'}
            </button>
            <button
              type="button"
              onClick={() => loadDiscovery()}
              title="Làm mới dữ liệu"
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition border border-slate-700"
            >
              <RefreshCw className={`w-4 h-4 ${isSearching ? 'animate-spin' : ''}`} />
            </button>
          </form>
        </div>

        {/* Category Pills Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pt-4 mt-4 border-t border-slate-800 scrollbar-thin">
          {Object.entries(categories).map(([catKey, catInfo]) => {
            const isSelected = selectedCategory === catKey;
            return (
              <button
                key={catKey}
                onClick={() => handleCategorySelect(catKey)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? 'bg-violet-600 text-white shadow-md shadow-violet-600/30'
                    : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700/60 border border-slate-700/50'
                }`}
              >
                {CATEGORY_ICONS[catKey] || <Sparkles className="w-3.5 h-3.5" />}
                {catInfo.label}
              </button>
            );
          })}
        </div>

        {/* Trending Topic Tags */}
        {topics.length > 0 && (
          <div className="mt-3 flex items-center gap-2 overflow-x-auto py-1">
            <span className="text-xs text-slate-400 font-semibold shrink-0 flex items-center gap-1">
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              Chủ đề gợi ý:
            </span>
            <div className="flex items-center gap-1.5">
              {topics.slice(0, 8).map((top) => (
                <button
                  key={top.id}
                  onClick={() => handleTopicClick(top.name)}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-violet-500/50 transition whitespace-nowrap"
                >
                  <span>{top.name}</span>
                  {top.traffic_hint && (
                    <span className="text-[10px] px-1 py-0.2 rounded bg-violet-500/20 text-violet-300">
                      {top.traffic_hint}
                    </span>
                  )}
                  <span className="text-[9px] text-slate-400">({top.source_label})</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 2. Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
        <div className="flex items-center gap-3">
          <span className="text-slate-400 font-medium flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            Loại nội dung:
          </span>
          <div className="flex items-center gap-1 bg-slate-800 p-0.5 rounded-lg border border-slate-700">
            {['ALL', 'TEXT_POST', 'IMAGE', 'VIDEO', 'CAROUSEL'].map((mt) => (
              <button
                key={mt}
                onClick={() => {
                  setMediaType(mt);
                  loadDiscovery();
                }}
                className={`px-2.5 py-1 rounded text-xs transition ${
                  mediaType === mt ? 'bg-violet-600 text-white font-medium' : 'text-slate-400 hover:text-white'
                }`}
              >
                {mt === 'ALL'
                  ? 'Tất cả'
                  : mt === 'TEXT_POST'
                  ? 'Văn bản'
                  : mt === 'IMAGE'
                  ? 'Hình ảnh'
                  : mt === 'VIDEO'
                  ? 'Video'
                  : 'Album'}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-slate-400 font-medium">Thời gian:</span>
          <div className="flex items-center gap-1 bg-slate-800 p-0.5 rounded-lg border border-slate-700">
            {(['24h', '3d', '7d', 'all'] as const).map((tw) => (
              <button
                key={tw}
                onClick={() => {
                  setTimeWindow(tw);
                  loadDiscovery();
                }}
                className={`px-2 py-1 rounded text-xs transition ${
                  timeWindow === tw ? 'bg-violet-600 text-white font-medium' : 'text-slate-400 hover:text-white'
                }`}
              >
                {tw === '24h' ? '24h' : tw === '3d' ? '3 ngày' : tw === '7d' ? '7 ngày' : 'Tất cả'}
              </button>
            ))}
          </div>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400">
            Tìm thấy: <strong className="text-violet-400">{posts.length}</strong> bài viết
          </span>
        </div>
      </div>

      {/* 3. Discovered Posts Grid */}
      {isSearching ? (
        <div className="py-20 text-center">
          <RefreshCw className="w-8 h-8 text-violet-500 animate-spin mx-auto mb-3" />
          <p className="text-slate-300 font-medium">Đang khám phá Threads theo thời gian thực...</p>
          <p className="text-xs text-slate-500 mt-1">Đang phân tích tương tác và tính điểm Studio Hot Score</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="py-16 text-center bg-slate-900/40 rounded-xl border border-slate-800">
          <AlertCircle className="w-10 h-10 text-slate-500 mx-auto mb-2" />
          <h3 className="text-slate-200 font-medium">Không tìm thấy bài viết nào phù hợp</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Hãy thử đổi từ khóa khác hoặc bấm nút "Tất cả chủ đề" phía trên để khám phá nội dung mới.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {posts.map((post) => (
            <div
              key={post.id}
              className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-violet-500/50 rounded-xl p-4 flex flex-col justify-between transition-all duration-200 shadow-md hover:shadow-violet-500/10 group"
            >
              <div>
                {/* Author & Header */}
                <div className="flex items-center justify-between mb-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-violet-600/30 border border-violet-500/40 flex items-center justify-center text-xs font-bold text-violet-300">
                      {post.author_display_name?.[0]?.toUpperCase() || post.author_username[0]?.toUpperCase() || 'T'}
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-xs font-semibold text-slate-200 truncate">
                        {post.author_display_name || post.author_username}
                      </p>
                      <p className="text-[11px] text-slate-400 truncate">@{post.author_username}</p>
                    </div>
                  </div>

                  {/* Hot Score Pill */}
                  <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-bold shrink-0">
                    <Flame className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                    <span>{post.hot_score}</span>
                  </div>
                </div>

                {/* Content snippet */}
                <p className="text-sm text-slate-200 line-clamp-3 mb-3 leading-relaxed">
                  {post.content}
                </p>

                {/* Ranking Reason Banner */}
                <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-800 text-[11px] text-violet-300 mb-3 flex items-start gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-violet-400 shrink-0 mt-0.5" />
                  <span className="leading-tight">{post.ranking_reason}</span>
                </div>
              </div>

              <div>
                {/* Metrics Row */}
                <div className="flex items-center justify-between pt-2.5 border-t border-slate-800/80 text-xs text-slate-400 mb-3">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1" title="Lượt thích">
                      <Heart className="w-3.5 h-3.5 text-rose-400" />
                      {post.like_count !== null && post.like_count !== undefined ? post.like_count.toLocaleString() : 'N/A'}
                    </span>
                    <span className="flex items-center gap-1 font-medium text-slate-200" title="Bình luận">
                      <MessageCircle className="w-3.5 h-3.5 text-sky-400" />
                      {post.reply_count !== null && post.reply_count !== undefined ? post.reply_count.toLocaleString() : 'N/A'}
                    </span>
                    {post.repost_count !== null && post.repost_count !== undefined && (
                      <span className="flex items-center gap-1" title="Chia sẻ">
                        <Repeat className="w-3.5 h-3.5 text-emerald-400" />
                        {post.repost_count}
                      </span>
                    )}
                  </div>

                  <a
                    href={post.threads_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-slate-400 hover:text-white transition flex items-center gap-0.5 text-[11px]"
                    title="Mở bài viết gốc trên Threads"
                  >
                    Xem <ExternalLink className="w-3 h-3 ml-0.5" />
                  </a>
                </div>

                {/* Action Button */}
                <button
                  onClick={() => onSelectPost(post)}
                  disabled={isLoading}
                  className="w-full bg-violet-600 hover:bg-violet-500 text-white font-medium py-2 px-3 rounded-lg text-xs transition-all shadow-md shadow-violet-600/20 flex items-center justify-center gap-1.5 group-hover:scale-[1.01]"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Chọn làm video ngay
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 4. Collapsible Manual URL Input */}
      <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden transition">
        <button
          type="button"
          onClick={() => setShowManualInput(!showManualInput)}
          className="w-full p-4 flex items-center justify-between text-left text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/40 transition"
        >
          <div className="flex items-center gap-2">
            <LinkIcon className="w-4 h-4 text-violet-400" />
            <span>Hoặc nhập trực tiếp URL bài viết Threads (nếu bạn đã có sẵn link)</span>
          </div>
          {showManualInput ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showManualInput && (
          <div className="p-4 pt-1 border-t border-slate-800 bg-slate-900/60">
            <form onSubmit={handleManualSubmit} className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                placeholder="https://www.threads.net/@username/post/POST_ID"
                value={manualUrl}
                onChange={(e) => setManualUrl(e.target.value)}
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500"
              />
              <button
                type="submit"
                disabled={isLoading || !manualUrl.trim()}
                className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-5 py-2 rounded-lg text-sm font-medium transition shrink-0 disabled:opacity-50"
              >
                Bắt đầu cào dữ liệu
              </button>
            </form>
            <p className="text-xs text-slate-500 mt-2">
              Hỗ trợ cả dạng link chuẩn <code className="text-slate-400">https://www.threads.net/@user/post/ID</code> hoặc link rút gọn <code className="text-slate-400">/t/ID</code>.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
