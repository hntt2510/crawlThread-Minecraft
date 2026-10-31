import React from 'react';
import { 
  Film, 
  FolderKanban, 
  PlusCircle, 
  Video, 
  Send, 
  KeyRound, 
  Settings, 
  Layers 
} from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string) => void;
  activeProjectId?: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate, activeProjectId }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Bảng Điều Khiển', icon: FolderKanban },
    { id: 'new_project', label: 'Dự Án Mới', icon: PlusCircle },
    { id: 'studio', label: 'Xưởng Sản Xuất', icon: Film, disabled: !activeProjectId },
    { id: 'media', label: 'Kho Media & Gameplay', icon: Video },
    { id: 'publish', label: 'Trung Tâm Xuất Bản', icon: Send },
    { id: 'accounts', label: 'Tài Khoản Liên Kết', icon: KeyRound },
    { id: 'settings', label: 'Cài Đặt Hệ Thống', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-zinc-800/80 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
          <Layers className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-wide text-zinc-100 uppercase">Threads Video</h1>
          <p className="text-xs text-zinc-400 font-medium">Studio v1.0 • Local</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          const isDisabled = item.disabled;

          return (
            <button
              key={item.id}
              disabled={isDisabled}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-violet-600/15 text-violet-400 border border-violet-500/30'
                  : isDisabled
                  ? 'opacity-35 cursor-not-allowed text-zinc-500'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/80'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-violet-400' : 'text-zinc-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-zinc-900 bg-zinc-950/40 text-xs text-zinc-500">
        <div className="flex items-center justify-between mb-1">
          <span>Engine FFmpeg:</span>
          <span className="text-emerald-400 font-mono">v8.1.1 OK</span>
        </div>
        <div className="flex items-center justify-between">
          <span>CapCut Desktop:</span>
          <span className="text-indigo-400 font-mono">Sẵn sàng</span>
        </div>
      </div>
    </aside>
  );
};
