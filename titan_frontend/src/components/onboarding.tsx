/**
 * TITAN Analytics Platform - Onboarding Component
 * Interactive tutorial for new users
 */

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  IconRocket, 
  IconSearch, 
  IconTemplate,
  IconReportAnalytics,
  IconSettings,
  IconCheck,
  IconArrowRight,
  IconArrowLeft,
  IconPlayerPlay
} from '@tabler/icons-react';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  content: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingProps {
  onComplete?: () => void;
  onSkip?: () => void;
  userName?: string;
}

export function Onboarding({ onComplete, onSkip, userName = 'User' }: OnboardingProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to TITAN Analytics',
      description: 'Your AI-powered analytics platform',
      icon: <IconRocket size={48} className="text-primary" />,
      content: (
        <div className="text-center space-y-4">
          <p className="text-lg">
            Hello, <span className="font-semibold">{userName}</span>! 👋
          </p>
          <p className="text-muted-foreground">
            TITAN Analytics helps you transform any data into actionable insights using
            the power of AI. Let's take a quick tour of the key features.
          </p>
          <div className="flex justify-center gap-4 pt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">11+</div>
              <div className="text-sm text-muted-foreground">AI Processors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">5+</div>
              <div className="text-sm text-muted-foreground">Export Formats</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">∞</div>
              <div className="text-sm text-muted-foreground">Possibilities</div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'search',
      title: 'Smart Semantic Search',
      description: 'Find exactly what you need',
      icon: <IconSearch size={48} className="text-blue-500" />,
      content: (
        <div className="space-y-4">
          <p>
            Our intelligent search engine understands context and synonyms, helping you
            find relevant information even when your search terms don't exactly match.
          </p>
          <div className="bg-muted rounded-lg p-4 space-y-2">
            <p className="font-medium">Key Features:</p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <IconCheck size={16} className="text-green-500" />
                Synonym expansion with RuWordNet
              </li>
              <li className="flex items-center gap-2">
                <IconCheck size={16} className="text-green-500" />
                Morphological analysis for better matching
              </li>
              <li className="flex items-center gap-2">
                <IconCheck size={16} className="text-green-500" />
                Relevance-based ranking
              </li>
              <li className="flex items-center gap-2">
                <IconCheck size={16} className="text-green-500" />
                Multi-source search (web, PDF, video)
              </li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      id: 'templates',
      title: 'Template Library & Marketplace',
      description: 'Start with ready-made solutions',
      icon: <IconTemplate size={48} className="text-purple-500" />,
      content: (
        <div className="space-y-4">
          <p>
            Don't start from scratch! Use our pre-built templates for common analytics
            tasks, or create your own and share them with the community.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: 'Market Analysis', uses: '150+' },
              { name: 'Competitor Research', uses: '120+' },
              { name: 'Brand Monitoring', uses: '90+' },
              { name: 'Literature Review', uses: '80+' },
            ].map(template => (
              <div key={template.name} className="bg-muted rounded-lg p-3">
                <div className="font-medium text-sm">{template.name}</div>
                <div className="text-xs text-muted-foreground">{template.uses} uses</div>
              </div>
            ))}
          </div>
          <p className="text-sm text-muted-foreground">
            💡 Tip: Check out the Marketplace for community-created templates!
          </p>
        </div>
      ),
    },
    {
      id: 'reports',
      title: 'AI-Powered Reports',
      description: 'Generate insights automatically',
      icon: <IconReportAnalytics size={48} className="text-green-500" />,
      content: (
        <div className="space-y-4">
          <p>
            Create comprehensive analytics reports with just a few clicks. Our AI
            processors handle the heavy lifting:
          </p>
          <div className="space-y-3">
            {[
              { name: 'Sentiment Analysis', desc: 'Understand emotions and opinions' },
              { name: 'Trend Detection', desc: 'Identify emerging patterns' },
              { name: 'Entity Extraction', desc: 'Find key people, places, organizations' },
              { name: 'Anomaly Detection', desc: 'Spot unusual patterns (Enterprise)' },
              { name: 'Recommendations', desc: 'Get AI-powered suggestions (Enterprise)' },
            ].map(processor => (
              <div key={processor.name} className="flex items-center gap-3 bg-muted rounded-lg p-3">
                <IconPlayerPlay size={16} className="text-primary" />
                <div>
                  <div className="font-medium text-sm">{processor.name}</div>
                  <div className="text-xs text-muted-foreground">{processor.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ),
    },
    {
      id: 'settings',
      title: 'Customize Your Experience',
      description: 'Make TITAN work for you',
      icon: <IconSettings size={48} className="text-orange-500" />,
      content: (
        <div className="space-y-4">
          <p>
            Personalize your analytics workflow with custom settings and preferences:
          </p>
          <div className="space-y-3">
            <div className="bg-muted rounded-lg p-4">
              <p className="font-medium">🤖 AI Model Selection</p>
              <p className="text-sm text-muted-foreground">
                Choose from YandexGPT, OpenAI GPT-4, or Anthropic Claude for your analyses
              </p>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <p className="font-medium">📊 Default Templates</p>
              <p className="text-sm text-muted-foreground">
                Set your favorite templates as defaults for quick access
              </p>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <p className="font-medium">📤 Export Preferences</p>
              <p className="text-sm text-muted-foreground">
                Configure default export formats (PDF, Word, Excel)
              </p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'complete',
      title: 'You\'re All Set! 🎉',
      description: 'Start creating amazing insights',
      icon: <IconRocket size={48} className="text-primary" />,
      content: (
        <div className="text-center space-y-6">
          <p className="text-lg">
            Congratulations! You're ready to start using TITAN Analytics.
          </p>
          <div className="space-y-4">
            <p className="font-medium">Quick Start Suggestions:</p>
            <div className="grid gap-3">
              <Button variant="outline" className="w-full justify-start">
                <IconSearch className="mr-2" size={18} />
                Try your first search
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <IconTemplate className="mr-2" size={18} />
                Browse template library
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <IconReportAnalytics className="mr-2" size={18} />
                Create your first report
              </Button>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Need help? Visit our documentation or contact support anytime.
          </p>
        </div>
      ),
    },
  ];

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  const handleNext = () => {
    setCompletedSteps(new Set([...completedSteps, currentStepData.id]));
    if (isLastStep) {
      onComplete?.();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirstStep) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    onSkip?.();
  };

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        {/* Progress indicator */}
        <div className="px-6 pt-6">
          <div className="flex gap-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`h-2 flex-1 rounded-full transition-colors ${
                  index <= currentStep 
                    ? 'bg-primary' 
                    : 'bg-muted'
                }`}
              />
            ))}
          </div>
          <div className="text-sm text-muted-foreground mt-2">
            Step {currentStep + 1} of {steps.length}
          </div>
        </div>

        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {currentStepData.icon}
          </div>
          <CardTitle className="text-2xl">{currentStepData.title}</CardTitle>
          <CardDescription className="text-base">
            {currentStepData.description}
          </CardDescription>
        </CardHeader>

        <CardContent>
          {currentStepData.content}
        </CardContent>

        <CardFooter className="flex justify-between">
          <div className="flex gap-2">
            {!isFirstStep && (
              <Button variant="outline" onClick={handlePrev}>
                <IconArrowLeft size={16} className="mr-2" />
                Back
              </Button>
            )}
            {!isLastStep && (
              <Button variant="ghost" onClick={handleSkip}>
                Skip Tutorial
              </Button>
            )}
          </div>
          <Button onClick={handleNext}>
            {isLastStep ? (
              <>
                Get Started
                <IconRocket size={16} className="ml-2" />
              </>
            ) : (
              <>
                Next
                <IconArrowRight size={16} className="ml-2" />
              </>
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

export default Onboarding;
