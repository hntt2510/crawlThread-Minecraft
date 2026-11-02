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
  Clock,
  Zap,
  Layers
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
  const [sortBy, setSortBy] = useState<'hot' | 'latest' | 'comments'>('latest');
  const [apiStatus, setApiStatus] = useState<any>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [isRefreshingTopics, setIsRefreshingTopics] = useState<boolean>(false);
  const [manualUrl, setManualUrl] = useState<string>('');
  const [showManualInput, setShowManualInput] = useState<boolean>(false);
  const [suggestedTopics, setSuggestedTopics] = useState<string[]>([]);
  const [matchedCluster, setMatchedCluster] = useState<string | null>(null);

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

  const loadDiscovery = async (
    overrideKeyword?: string,
    overrideCategory?: string,
    overrideSortBy?: 'hot' | 'latest' | 'comments'
  ) => {
    setIsSearching(true);
    try {
      const kw = overrideKeyword !== undefined ? overrideKeyword : searchKeyword;
      const cat = overrideCategory !== undefined ? overrideCategory : selectedCategory;
      const sort = overrideSortBy !== undefined ? overrideSortBy : sortBy;

      const result = await api.searchDiscovery({
        keyword: kw,
        category: cat,
        search_type: 'BOTH',
        media_type: mediaType,
        time_window: timeWindow,
        sort_by: sort,
        limit: 45
      });

      setPosts(result.posts || []);
      setTopics(result.topics || []);
      setActiveQuery(result.query || '');
      setSuggestedTopics(result.suggested_topics || []);
      setMatchedCluster(result.matched_cluster || null);
      if (result.api_status) {
        setApiStatus(result.api_status);
      }
    } catch (err) {
      console.error('Failed to search discovery', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleRefreshTopics = async () => {
    setIsRefreshingTopics(true);
    try {
      const freshTopics = await api.getDiscoveryTopics(selectedCategory, true);
      setTopics(freshTopics || []);
    } catch (err) {
      console.error('Failed to refresh topics', err);
    } finally {
      setIsRefreshingTopics(false);
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

  const handleSortChange = (newSort: 'hot' | 'latest' | 'comments') => {
    setSortBy(newSort);
    loadDiscovery(undefined, undefined, newSort);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadDiscovery(searchKeyword.trim());
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualUrl.trim()) {
      onManualUrlSubmit(manualUrl.trim());
    }
  };

  // Get human readable last updated time from topics
  const lastUpdated = topics.find((t) => t.updated_at_human)?.updated_at_human || '';

  return (
    <div className="space-y-6">
      {/* 1. Header & Live Search Bar */}
      <div className="bg-slate-900/95 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
                🇻🇳 Xu Hướng Việt Nam
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Threads Relay Stream
              </span>
            </div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-violet-400" />
              Khám Phá Bài Viết Threads Thịnh Hành
            </h2>
            <p className="text-sm text-slate-400">
              Tự động bắt trend nóng trong ngày, phân tích thảo luận người trẻ và chọn làm video Minecraft 1-click.
            </p>
          </div>

          {/* Search Input Bar */}
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 max-w-md w-full">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Tìm từ khóa, drama, idol, red flag..."
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
              title="Làm mới dữ liệu bài viết"
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition border border-slate-700"
            >
              <RefreshCw className={`w-4 h-4 ${isSearching ? 'animate-spin' : ''}`} />
            </button>
          </form>
        </div>

        {/* 2. Real-Time Trending Keywords (Updated by Date & Time) */}
        <div className="mt-4 pt-3.5 border-t border-slate-800">
          <div className="flex items-center justify-between pb-2 mb-1 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-amber-400 fill-amber-400" />
              <span className="text-xs font-bold text-amber-300 uppercase tracking-wide">
                ⚡ Từ Khóa Nóng Hôm Nay:
              </span>
            </div>
            <div className="flex items-center gap-3">
              {lastUpdated && (
                <span className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-500" />
                  Cập nhật: <strong className="text-slate-300 font-medium">{lastUpdated}</strong>
                </span>
              )}
              <button
                type="button"
                onClick={handleRefreshTopics}
                disabled={isRefreshingTopics}
                className="text-[11px] text-violet-400 hover:text-violet-300 flex items-center gap-1 transition px-1.5 py-0.5 rounded hover:bg-slate-800"
                title="Lấy dữ liệu xu hướng mới nhất"
              >
                <RefreshCw className={`w-3 h-3 ${isRefreshingTopics ? 'animate-spin' : ''}`} />
                Làm mới trend
              </button>
            </div>
          </div>

          {/* Horizontal Scrolling Trending Topics */}
          {topics.length > 0 ? (
            <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-thin">
              {topics.slice(0, 15).map((top) => {
                const isActive = searchKeyword.toLowerCase() === top.name.toLowerCase();
                return (
                  <button
                    key={top.id}
                    onClick={() => handleTopicClick(top.name)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition whitespace-nowrap border ${
                      isActive
                        ? 'bg-amber-500 text-slate-950 font-bold border-amber-400 shadow-md shadow-amber-500/20'
                        : 'bg-slate-800/80 hover:bg-slate-700 text-slate-200 border-slate-700 hover:border-amber-500/50'
                    }`}
                  >
                    <span>{top.name}</span>
                    {top.traffic_hint && (
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                          isActive
                            ? 'bg-slate-950/20 text-slate-950'
                            : 'bg-violet-500/20 text-violet-300'
                        }`}
                      >
                        {top.traffic_hint}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-1 italic">Đang tải xu hướng hôm nay...</p>
          )}
        </div>

        {/* 3. Category Filter Pills */}
        <div className="pt-3 mt-3 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto scrollbar-thin">
          <span className="text-xs text-slate-400 font-semibold shrink-0 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-violet-400" />
            Lĩnh vực:
          </span>
          <div className="flex items-center gap-1.5">
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
        </div>
      </div>

      {/* 4. Controls & Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
        {/* Sort Controls */}
        <div className="flex items-center gap-3">
          <span className="text-slate-300 font-semibold flex items-center gap-1">
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            Sắp xếp:
          </span>
          <div className="flex items-center gap-1 bg-slate-800 p-0.5 rounded-lg border border-slate-700">
            <button
              onClick={() => handleSortChange('latest')}
              className={`px-3 py-1 rounded text-xs font-medium transition flex items-center gap-1 ${
                sortBy === 'latest' ? 'bg-violet-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Clock className="w-3 h-3" />
              ⚡ Mới nhất
            </button>
            <button
              onClick={() => handleSortChange('hot')}
              className={`px-3 py-1 rounded text-xs font-medium transition flex items-center gap-1 ${
                sortBy === 'hot' ? 'bg-violet-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Flame className="w-3 h-3 text-amber-400" />
              🔥 Sôi nổi nhất
            </button>
            <button
              onClick={() => handleSortChange('comments')}
              className={`px-3 py-1 rounded text-xs font-medium transition flex items-center gap-1 ${
                sortBy === 'comments' ? 'bg-violet-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
              }`}
            >
              <MessageCircle className="w-3 h-3 text-sky-400" />
              💬 Nhiều bình luận
            </button>
          </div>
        </div>

        {/* Content Type & Time Window Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Thời gian:</span>
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
                  {tw === '24h' ? '24h qua' : tw === '3d' ? '3 ngày' : tw === '7d' ? '7 ngày' : 'Tất cả'}
                </button>
              ))}
            </div>
          </div>

          <span className="text-slate-500">|</span>
          <div className="flex items-center gap-2">
            <span className="text-slate-400">
              Tìm thấy: <strong className="text-violet-400 font-bold">{posts.length}</strong> bài viết
            </span>
            {matchedCluster && searchKeyword.trim() && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                🎯 {matchedCluster}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 5. Discovered Posts Grid */}
      {isSearching ? (
        <div className="py-20 text-center">
          <RefreshCw className="w-8 h-8 text-violet-500 animate-spin mx-auto mb-3" />
          <p className="text-slate-300 font-medium">Đang quét bài viết Threads theo thời gian thực...</p>
          <p className="text-xs text-slate-500 mt-1">Đang đối soát mật độ bàn luận và tính điểm xếp hạng khách quan</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="py-14 text-center bg-slate-900/60 rounded-xl border border-slate-800 p-6 shadow-xl">
          <div className="w-12 h-12 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 flex items-center justify-center mx-auto mb-3 shadow-inner">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-100">
            {searchKeyword.trim()
              ? `Không tìm thấy bài viết trực tiếp cho từ khóa "${searchKeyword}"`
              : 'Không tìm thấy bài viết nào phù hợp'}
          </h3>
          <p className="text-xs text-slate-400 mt-1.5 max-w-md mx-auto mb-5 leading-relaxed">
            {suggestedTopics.length > 0
              ? 'Chủ đề này chưa có bài thảo luận trực tiếp trên Threads lúc này. Bạn có thể bấm chọn ngay các chủ đề hot liên quan sau để khám phá:'
              : 'Hãy thử tìm bằng từ khóa phổ biến hơn hoặc bấm chọn các từ khóa nóng hôm nay ở thanh trên.'}
          </p>
          {suggestedTopics.length > 0 && (
            <div className="flex flex-wrap justify-center gap-2 max-w-lg mx-auto">
              {suggestedTopics.map((top, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSearchKeyword(top);
                    loadDiscovery(top);
                  }}
                  className="px-3.5 py-1.5 rounded-full bg-violet-600/20 hover:bg-violet-600 text-violet-300 hover:text-white border border-violet-500/30 text-xs font-semibold transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
                >
                  <Flame className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                  <span>{top}</span>
                </button>
              ))}
            </div>
          )}
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
                    <div className="w-8 h-8 rounded-full bg-violet-600/30 border border-violet-500/40 flex items-center justify-center text-xs font-bold text-violet-300 shrink-0">
                      {post.author_display_name?.[0]?.toUpperCase() || post.author_username[0]?.toUpperCase() || 'T'}
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-xs font-semibold text-slate-200 truncate">
                        {post.author_display_name || post.author_username}
                      </p>
                      <p className="text-[11px] text-slate-400 truncate">@{post.author_username}</p>
                    </div>
                  </div>

                  {/* Hot Score & Recency Badges */}
                  <div className="flex items-center gap-1.5 shrink-0">
                    {post.age_label && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-[10px] font-medium">
                        <Clock className="w-2.5 h-2.5" />
                        {post.age_label}
                      </span>
                    )}
                    <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-bold">
                      <Flame className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                      <span>{post.hot_score}</span>
                    </div>
                  </div>
                </div>

                {/* Gen Z Tag Indicator */}
                {post.is_youth_trend && (
                  <div className="mb-2">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-pink-500/15 text-pink-400 border border-pink-500/30">
                      ⚡ Gen Z Viral
                    </span>
                  </div>
                )}

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
                    <span className="flex items-center gap-1 font-bold text-sky-300 bg-sky-500/10 px-1.5 py-0.5 rounded border border-sky-500/20" title="Bình luận (Rất quan trọng để làm video)">
                      <MessageCircle className="w-3.5 h-3.5 text-sky-400" />
                      {post.reply_count !== null && post.reply_count !== undefined ? post.reply_count.toLocaleString() : 'N/A'} cmt
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

      {/* 6. Collapsible Manual URL Input */}
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
