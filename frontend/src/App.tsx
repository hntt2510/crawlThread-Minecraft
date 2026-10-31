import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { ProjectStudio } from './pages/ProjectStudio';
import { MediaLibrary } from './pages/MediaLibrary';
import { AccountsPage } from './pages/AccountsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('dashboard');
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

  const handleOpenProject = (id: string) => {
    setActiveProjectId(id);
    setCurrentView('studio');
  };

  const handleNewProject = () => {
    setActiveProjectId(null);
    setCurrentView('studio');
  };

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 overflow-hidden font-sans">
      {/* Global Sidebar Navigation */}
      <Sidebar
        currentView={currentView}
        onNavigate={(view) => {
          if (view === 'new_project') {
            handleNewProject();
          } else {
            setCurrentView(view);
          }
        }}
        activeProjectId={activeProjectId}
      />

      {/* Main Content View */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {currentView === 'dashboard' && (
          <Dashboard
            onOpenProject={handleOpenProject}
            onNewProject={handleNewProject}
          />
        )}

        {currentView === 'studio' && (
          <ProjectStudio
            projectId={activeProjectId}
            onNewProject={handleNewProject}
          />
        )}

        {currentView === 'media' && <MediaLibrary />}

        {currentView === 'accounts' && <AccountsPage />}

        {currentView === 'settings' && <SettingsPage />}
      </div>
    </div>
  );
};

export default App;
