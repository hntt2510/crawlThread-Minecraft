import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { YoutubeIcon, FacebookIcon, TikTokIcon } from '../components/ui/PlatformIcons';

export const AccountsPage: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-zinc-950 p-8 space-y-8">
      <div>
        <h1 className="text-xl font-bold text-zinc-100">Tài Khoản Mạng Xã Hội Liên Kết</h1>
        <p className="text-xs text-zinc-400 mt-1">
          Quản lý kết nối an toàn với YouTube Shorts, Facebook Page Reels và TikTok để xuất bản video trực tiếp từ ứng dụng.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* YouTube */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-rose-950/60 border border-rose-800/40 flex items-center justify-center text-rose-500">
              <YoutubeIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-zinc-100">YouTube Data API v3</h3>
              <p className="text-xs text-zinc-400 mt-1">Hỗ trợ đăng tải trực tiếp vào kho Shorts của kênh qua OAuth 2.0.</p>
            </div>
          </div>
          <div className="pt-2">
            <span className="text-[11px] font-mono text-zinc-500 bg-zinc-950 px-2 py-1 rounded block mb-3 truncate">
              Scope: youtube.upload
            </span>
            <button className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold py-2 rounded-xl transition-colors cursor-pointer">
              Cấu Hình OAuth Token
            </button>
          </div>
        </div>

        {/* Facebook Page */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-500">
              <FacebookIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-zinc-100">Facebook Fanpage Reels</h3>
              <p className="text-xs text-zinc-400 mt-1">Đăng video Reel lên các Fanpage bạn đang quản lý qua Meta Graph API v19+.</p>
            </div>
          </div>
          <div className="pt-2">
            <span className="text-[11px] font-mono text-zinc-500 bg-zinc-950 px-2 py-1 rounded block mb-3 truncate">
              pages_manage_posts
            </span>
            <button className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold py-2 rounded-xl transition-colors cursor-pointer">
              Cấu Hình Page Token
            </button>
          </div>
        </div>

        {/* TikTok */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-teal-950/60 border border-teal-800/40 flex items-center justify-center text-teal-400">
              <TikTokIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-zinc-100">TikTok Content Posting</h3>
              <p className="text-xs text-zinc-400 mt-1">Xuất bản video trực tiếp lên tài khoản TikTok qua TikTok Posting API v2.</p>
            </div>
          </div>
          <div className="pt-2">
            <span className="text-[11px] font-mono text-zinc-500 bg-zinc-950 px-2 py-1 rounded block mb-3 truncate">
              video.publish
            </span>
            <button className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold py-2 rounded-xl transition-colors cursor-pointer">
              Cấu Hình Access Token
            </button>
          </div>
        </div>
      </div>

      <div className="bg-zinc-900/50 border border-zinc-800/80 rounded-2xl p-6 flex items-start space-x-3 text-xs text-zinc-400">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong>Nguyên tắc bảo mật:</strong> Ứng dụng chạy hoàn toàn trên máy cục bộ của bạn (Local-First). Mọi Access Token chỉ được dùng để gửi yêu cầu trực tiếp từ máy của bạn tới máy chủ của YouTube, Meta và TikTok, không bao giờ gửi qua máy chủ trung gian.
        </p>
      </div>
    </div>
  );
};
