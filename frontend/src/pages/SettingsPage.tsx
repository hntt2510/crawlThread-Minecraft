import React, { useState, useEffect } from 'react';
import { Settings, Save, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';

export const SettingsPage: React.FC = () => {
  const [capcutFolder, setCapcutFolder] = useState('');
  const [fptKey, setFptKey] = useState('');
  const [googleCreds, setGoogleCreds] = useState('');
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await api.getSettings();
      setCapcutFolder(data.capcut_draft_folder || '');
      setFptKey(data.fptai_api_key || '');
      setGoogleCreds(data.google_application_credentials || '');
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await api.updateSettings({
        capcut_draft_folder: capcutFolder,
        default_tts_provider: 'edge_tts',
        fptai_api_key: fptKey,
        google_application_credentials: googleCreds,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
          <Settings className="w-5 h-5 text-violet-400" />
          <span>Cài Đặt Hệ Thống</span>
        </h1>
        <p className="text-xs text-zinc-400 mt-1">
          Cấu hình đường dẫn thư mục CapCut Desktop, API key giọng đọc bên thứ ba và các tham số môi trường.
        </p>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 space-y-6">
        <div>
          <label className="block text-xs font-semibold uppercase text-zinc-400 tracking-wider mb-2">
            Thư Mục Dự Án CapCut Desktop (Draft Folder)
          </label>
          <input
            type="text"
            value={capcutFolder}
            onChange={(e) => setCapcutFolder(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-xs text-zinc-200 font-mono focus:outline-none focus:border-violet-500"
          />
          <p className="text-[11px] text-zinc-500 mt-1.5">
            Mặc định trên Windows: <code className="text-zinc-400">%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft</code>
          </p>
        </div>

        <div className="border-t border-zinc-800 pt-5 space-y-5">
          <h3 className="text-xs font-bold uppercase text-zinc-300 tracking-wider">Cấu Hình Giọng Đọc Mở Rộng (Tùy Chọn)</h3>
          
          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-1.5">
              FPT.AI Speech API Key (Miền Bắc, Trung, Nam)
            </label>
            <input
              type="password"
              value={fptKey}
              onChange={(e) => setFptKey(e.target.value)}
              placeholder="Nhập API Key từ console.fpt.ai..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-violet-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-400 mb-1.5">
              Google Cloud Credentials JSON Path
            </label>
            <input
              type="text"
              value={googleCreds}
              onChange={(e) => setGoogleCreds(e.target.value)}
              placeholder="C:\keys\google-service-account.json"
              className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-zinc-200 font-mono focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>

        <div className="pt-4 border-t border-zinc-800 flex items-center justify-between">
          {saved && (
            <span className="text-xs text-emerald-400 font-medium flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>Đã lưu cài đặt thành công!</span>
            </span>
          )}
          {!saved && <div />}

          <button
            onClick={handleSave}
            className="bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs px-6 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-violet-600/30 transition-all cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>Lưu Cài Đặt</span>
          </button>
        </div>
      </div>
    </div>
  );
};
