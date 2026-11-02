import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { Step1Import } from '../components/steps/Step1Import';
import { Step2Comments } from '../components/steps/Step2Comments';
import { Step3Hook } from '../components/steps/Step3Hook';
import { Step3Voice } from '../components/steps/Step3Voice';
import { Step5TimelinePreview } from '../components/steps/Step5TimelinePreview';
import { Step4Video } from '../components/steps/Step4Video';
import { Step5Export } from '../components/steps/Step5Export';
import { Step6Publish } from '../components/steps/Step6Publish';
import { api } from '../api/client';
import { Project } from '../types';

interface ProjectStudioProps {
  projectId?: string | null;
  onNewProject: () => void;
}

export const ProjectStudio: React.FC<ProjectStudioProps> = ({ projectId, onNewProject }) => {
  const [project, setProject] = useState<Project | null>(null);
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
    } else {
      setLoading(false);
    }
  }, [projectId]);

  const loadProject = async (id: string) => {
    setLoading(true);
    try {
      const data = await api.getProject(id);
      setProject(data);
      // Auto advance to step based on status
      if (data.status === 'crawled') setStep(2);
      else if (data.status === 'synthesized') setStep(5);
      else if (data.status === 'rendered') setStep(7);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectUpdated = (updated: Project) => {
    setProject(updated);
    setStep(2);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center h-screen bg-zinc-950 text-zinc-400 text-xs font-mono">
        Đang tải dữ liệu dự án...
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-zinc-950">
      <Header
        currentStep={step}
        onSelectStep={(s) => setStep(s)}
        projectTitle={project?.title || 'Dự án mới'}
      />

      <main className="flex-1 overflow-y-auto p-6 custom-scrollbar">
        {step === 1 && (
          <Step1Import
            project={project}
            onProjectUpdated={handleProjectUpdated}
            onNext={() => setStep(2)}
          />
        )}

        {step === 2 && project && (
          <Step2Comments
            project={project}
            onNext={() => setStep(3)}
            onBack={() => setStep(1)}
          />
        )}

        {step === 3 && project && (
          <Step3Hook
            project={project}
            onNext={() => setStep(4)}
            onBack={() => setStep(2)}
          />
        )}

        {step === 4 && project && (
          <Step3Voice
            project={project}
            onNext={() => setStep(5)}
            onBack={() => setStep(3)}
          />
        )}

        {step === 5 && project && (
          <Step5TimelinePreview
            project={project}
            onNext={() => setStep(6)}
            onBack={() => setStep(4)}
          />
        )}

        {step === 6 && project && (
          <Step4Video
            project={project}
            onNext={() => setStep(7)}
            onBack={() => setStep(5)}
          />
        )}

        {step === 7 && project && (
          <div className="space-y-6">
            <Step5Export
              project={project}
              onNext={() => setStep(8)}
              onBack={() => setStep(6)}
            />
          </div>
        )}

        {step === 8 && project && (
          <Step6Publish
            project={project}
            onBack={() => setStep(7)}
          />
        )}
      </main>
    </div>
  );
};
