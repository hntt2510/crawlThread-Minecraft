import { 
  DownloadCloud, 
  MessageSquare, 
  Flame,
  Mic2, 
  Sliders, 
  Film, 
  Share2, 
  CheckCircle2 
} from 'lucide-react';

interface HeaderProps {
  currentStep: number;
  onSelectStep: (step: number) => void;
  projectTitle: string;
}

export const Header: React.FC<HeaderProps> = ({ currentStep, onSelectStep, projectTitle }) => {
  const steps = [
    { num: 1, label: '1. Nhập Threads', icon: DownloadCloud },
    { num: 2, label: '2. Chọn Bình Luận', icon: MessageSquare },
    { num: 3, label: '3. Tạo Hook AI', icon: Flame },
    { num: 4, label: '4. Giọng Đọc & TTS', icon: Mic2 },
    { num: 5, label: '5. Preview Timeline', icon: Sliders },
    { num: 6, label: '6. Dựng Video', icon: Film },
    { num: 7, label: '7. Xuất & Đăng', icon: Share2 },
  ];

  return (
    <header className="h-16 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between px-6 z-10">
      {/* Project Title */}
      <div className="flex items-center space-x-3">
        <span className="text-xs uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono font-medium">Dự Án</span>
        <h2 className="text-sm font-semibold text-zinc-100 truncate max-w-[240px]">{projectTitle || 'Dự án chưa lưu'}</h2>
      </div>

      {/* Production Stepper */}
      <div className="flex items-center space-x-1">
        {steps.map((s) => {
          const Icon = s.icon;
          const isActive = currentStep === s.num;
          const isDone = currentStep > s.num;

          return (
            <button
              key={s.num}
              onClick={() => onSelectStep(s.num)}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-violet-600 text-white shadow-md shadow-violet-600/30 font-semibold'
                  : isDone
                  ? 'text-emerald-400 hover:bg-zinc-900'
                  : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Icon className="w-3.5 h-3.5" />
              )}
              <span>{s.label}</span>
            </button>
          );
        })}
      </div>

      {/* Live Status indicator */}
      <div className="flex items-center space-x-2">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <span className="text-xs text-zinc-400 font-medium">Local Server 8000</span>
      </div>
    </header>
  );
};
