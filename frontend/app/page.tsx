'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import { BookOpen, Sparkles, FolderTree, Brain, CheckCircle2, Loader2 } from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleLogin = () => {
    loginWithRedirect();
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-semibold">DocuLens AI</span>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleLogin}
              className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              Log In
            </button>
            <button
              onClick={handleLogin}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Sign Up Free
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full mb-6">
          <Sparkles className="w-4 h-4" />
          <span className="text-sm font-medium">AI-Powered Note Processing</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-bold mb-6 text-gray-900">
          Convert messy notes to clean
          <br />
          <span className="text-blue-600">Markdown in seconds</span>
        </h1>

        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
          Transform handwritten notes, blackboard photos, and presentation screenshots
          into beautifully formatted study materials with AI-powered OCR.
        </p>

        <div className="flex gap-4 justify-center mb-16">
          <button
            onClick={handleLogin}
            className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200 font-medium"
          >
            Get Started Free
          </button>
          <button className="px-8 py-4 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-colors border border-gray-300 font-medium">
            Watch Demo
          </button>
        </div>

        {/* Demo Image Placeholder */}
        <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
          <div className="aspect-video bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center">
            <div className="text-center">
              <BookOpen className="w-24 h-24 text-blue-400 mx-auto mb-4" />
              <p className="text-gray-500">App Demo Screenshot</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Everything you need to organize your studies
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Sparkles className="w-8 h-8 text-blue-600" />}
              title="Smart OCR"
              description="Advanced optical character recognition extracts text from handwritten notes and images with high accuracy."
            />
            <FeatureCard
              icon={<Brain className="w-8 h-8 text-indigo-600" />}
              title="AI Formatting"
              description="Automatically structures your notes with proper headers, lists, and formatting for easy reading."
            />
            <FeatureCard
              icon={<FolderTree className="w-8 h-8 text-purple-600" />}
              title="Course Organization"
              description="Keep notes organized by courses and subjects. Find what you need instantly with semantic search."
            />
            <FeatureCard
              icon={<CheckCircle2 className="w-8 h-8 text-green-600" />}
              title="Study Materials"
              description="Auto-generate flashcards, Q&A pairs, and key concepts to help you study more effectively."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            From photo to formatted notes in 3 steps
          </h2>

          <div className="grid md:grid-cols-3 gap-12">
            <StepCard
              number="1"
              title="Upload Your Notes"
              description="Drag and drop photos of handwritten notes, whiteboards, or presentation slides."
            />
            <StepCard
              number="2"
              title="AI Processing"
              description="Our AI extracts text, analyzes structure, and formats everything into clean Markdown."
            />
            <StepCard
              number="3"
              title="Study & Organize"
              description="Access formatted notes, auto-generated flashcards, and organize by course."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to transform your note-taking?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of students who are studying smarter with DocuLens AI.
          </p>
          <button
            onClick={handleLogin}
            className="px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors shadow-lg font-medium"
          >
            Start Free Today
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <BookOpen className="w-6 h-6" />
            <span>DocuLens AI</span>
          </div>
          <p className="text-sm">Powered by Claude AI & Google Vision</p>
          <p className="text-sm mt-2">© 2025 DocuLens AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
        {number}
      </div>
      <h3 className="font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
