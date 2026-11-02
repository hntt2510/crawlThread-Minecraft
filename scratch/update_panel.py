with open('frontend/src/components/steps/DiscoveryPanel.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add state
old_state = "  const [showManualInput, setShowManualInput] = useState<boolean>(false);"
new_state = """  const [showManualInput, setShowManualInput] = useState<boolean>(false);
  const [suggestedTopics, setSuggestedTopics] = useState<string[]>([]);
  const [matchedCluster, setMatchedCluster] = useState<string | null>(null);"""

code = code.replace(old_state, new_state)

# 2. Update loadDiscovery
old_load = """      setPosts(result.posts || []);
      setTopics(result.topics || []);
      setActiveQuery(result.query || '');
      if (result.api_status) {
        setApiStatus(result.api_status);
      }"""

new_load = """      setPosts(result.posts || []);
      setTopics(result.topics || []);
      setActiveQuery(result.query || '');
      setSuggestedTopics(result.suggested_topics || []);
      setMatchedCluster(result.matched_cluster || null);
      if (result.api_status) {
        setApiStatus(result.api_status);
      }"""

code = code.replace(old_load, new_load)

# 3. Update handleSearchSubmit
old_submit = """  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadDiscovery();
  };"""

new_submit = """  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadDiscovery(searchKeyword.trim());
  };"""

code = code.replace(old_submit, new_submit)

# 4. Update Result Count & Matched Cluster in controls bar
old_count = """          <span className="text-slate-500">|</span>
          <span className="text-slate-400">
            Tìm thấy: <strong className="text-violet-400 font-bold">{posts.length}</strong> bài viết
          </span>"""

new_count = """          <span className="text-slate-500">|</span>
          <div className="flex items-center gap-2">
            <span className="text-slate-400">
              Tìm thấy: <strong className="text-violet-400 font-bold">{posts.length}</strong> bài viết
            </span>
            {matchedCluster && searchKeyword.trim() && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                🎯 {matchedCluster}
              </span>
            )}
          </div>"""

code = code.replace(old_count, new_count)

# 5. Update Empty State with smart suggestions
old_empty = """      ) : posts.length === 0 ? (
        <div className="py-16 text-center bg-slate-900/40 rounded-xl border border-slate-800">
          <AlertCircle className="w-10 h-10 text-slate-500 mx-auto mb-2" />
          <h3 className="text-slate-200 font-medium">Không tìm thấy bài viết nào phù hợp</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Hãy thử bấm các từ khóa nóng hôm nay phía trên hoặc chọn danh mục khác để khám phá.
          </p>
        </div>"""

new_empty = """      ) : posts.length === 0 ? (
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
        </div>"""

code = code.replace(old_empty, new_empty)

with open('frontend/src/components/steps/DiscoveryPanel.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print('Updated DiscoveryPanel.tsx successfully!')

