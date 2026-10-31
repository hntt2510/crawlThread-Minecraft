import React, { useState, useEffect } from 'react';
import { Video, Music, Upload, Film, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import { MediaAsset } from '../types';

export const MediaLibrary: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'background_video' | 'background_music'>('background_video');
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAssets();
  }, [activeTab]);

  const loadAssets = async () => {
    setLoading(true);
    try {
      const data = await api.listMedia(activeTab);
      setAssets(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await api.uploadMedia(file, activeTab);
      loadAssets();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-zinc-950 p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-zinc-100">Kho Media & Gameplay Minecraft</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Quản lý các đoạn video Minecraft gameplay nền và nhạc nền để tái sử dụng trên các dự án video Threads.
          </p>
        </div>

        <label className="bg-violet-600 hover:bg-violet-500 text-white font-medium text-xs px-5 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-violet-600/30 transition-all cursor-pointer">
          <Upload className="w-4 h-4" />
          <span>Tải File Mới Lên</span>
          <input
            type="file"
            accept={activeTab === 'background_video' ? 'video/mp4,video/quicktime' : 'audio/mp3,audio/wav'}
            onChange={handleUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-zinc-800">
        <button
          onClick={() => setActiveTab('background_video')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'background_video'
              ? 'border-violet-500 text-violet-400'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Video className="w-4 h-4" />
          <span>Video Nền Minecraft ({activeTab === 'background_video' ? assets.length : '...'})</span>
        </button>

        <button
          onClick={() => setActiveTab('background_music')}
          className={`pb-3 px-4 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'background_music'
              ? 'border-violet-500 text-violet-400'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Music className="w-4 h-4" />
          <span>Nhạc Nền BGM</span>
        </button>
      </div>

      {/* Asset Grid */}
      {loading ? (
        <div className="text-xs text-zinc-500 font-mono py-8 text-center">Đang tải kho media...</div>
      ) : assets.length === 0 ? (
        <div className="border border-dashed border-zinc-800 rounded-3xl p-12 text-center text-zinc-500 text-xs space-y-2">
          <Film className="w-8 h-8 text-zinc-600 mx-auto" />
          <p>Chưa có file media nào trong danh mục này.</p>
          <p className="text-[11px] text-zinc-600">Bấm nút "Tải File Mới Lên" để thêm video Minecraft hoặc nhạc nền MP3.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
          {assets.map((asset) => (
            <div key={asset.id} className="bg-zinc-900 border border-zinc-800 p-4 rounded-2xl space-y-3">
              <div className="flex items-center space-x-2 text-zinc-300 font-semibold text-xs truncate">
                {activeTab === 'background_video' ? <Film className="w-4 h-4 text-violet-400 flex-shrink-0" /> : <Music className="w-4 h-4 text-indigo-400 flex-shrink-0" />}
                <span className="truncate">{asset.name}</span>
              </div>
              <div className="text-[11px] text-zinc-500 font-mono flex items-center justify-between">
                <span>Thời lượng: {((asset.duration_ms || 0) / 1000).toFixed(1)}s</span>
                <span>{(asset.file_size_bytes / (1024 * 1024)).toFixed(1)} MB</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
