'use client';

import { useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Upload, X, ChevronRight, Menu, CheckCircle2, Loader2 } from 'lucide-react';
import { getCourse, CourseResponse, processNote } from '@/lib/api';
import { useAuth } from '@/lib/hooks/useAuth';
import toast from 'react-hot-toast';

type ProcessingStage = 'idle' | 'uploading' | 'extracting' | 'analyzing' | 'formatting' | 'generating' | 'complete' | 'error';

export default function UploadFlow() {
  const params = useParams();
  const router = useRouter();
  const { getAccessTokenSilently } = useAuth();
  const courseId = params.courseId as string;
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [course, setCourse] = useState<CourseResponse | null>(null);
  const [courseLoading, setCourseLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [additionalContext, setAdditionalContext] = useState('');
  const [processingStage, setProcessingStage] = useState<ProcessingStage>('idle');
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadCourse = async () => {
      setCourseLoading(true);
      try {
        const token = await getAccessTokenSilently();
        setCourse(await getCourse(courseId, token));
      } catch (err) {
        console.error(err);
        toast.error('Failed to load course');
      } finally {
        setCourseLoading(false);
      }
    };
    loadCourse();
  }, [courseId]);

  if (courseLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-gray-500">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        Loading course...
      </div>
    );
  }

  if (!course) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Course not found</h2>
          <Link href="/dashboard" className="text-blue-600 hover:underline">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFileSelect(file);
    } else {
      toast.error('Please upload an image file');
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleProcess = async () => {
    if (!selectedFile) return;

    setError(null);
    setProcessingStage('uploading');

    try {
      const stagePromise = simulateStages();
      const token = await getAccessTokenSilently();
      const response = await processNote(
        selectedFile,
        courseId,
        additionalContext,
        token,
        (progress) => {
          if (progress < 100) setProcessingStage('uploading');
        }
      );

      await stagePromise;

      if (response.success) {
        setProcessingStage('complete');
        toast.success('Note processed successfully!');
        setTimeout(() => {
          router.push(response.document_id ? `/document/${response.document_id}` : `/course/${courseId}`);
        }, 1500);
      } else {
        throw new Error(response.error || 'Processing failed');
      }
    } catch (err) {
      console.error('Processing error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Processing failed';
      setError(errorMessage);
      setProcessingStage('error');
      toast.error(errorMessage);
    }
  };

  const simulateStages = async () => {
    const stages: ProcessingStage[] = ['extracting', 'analyzing', 'formatting', 'generating'];
    for (const stage of stages) {
      setProcessingStage(stage);
      await new Promise(resolve => setTimeout(resolve, 1200));
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setAdditionalContext('');
    setProcessingStage('idle');
    setError(null);
  };

  const getStageText = (stage: ProcessingStage) => {
    switch (stage) {
      case 'uploading': return 'Uploading image...';
      case 'extracting': return 'Extracting text...';
      case 'analyzing': return 'Analyzing structure...';
      case 'formatting': return 'Formatting note...';
      case 'generating': return 'Generating study materials...';
      case 'complete': return 'Complete!';
      case 'error': return 'Error occurred';
      default: return '';
    }
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg -ml-2"
            >
              <Menu className="w-5 h-5" />
            </button>
            <Link href="/dashboard" className="hover:text-gray-900">Courses</Link>
            <ChevronRight className="w-4 h-4" />
            <Link href={`/course/${courseId}`} className="hover:text-gray-900">{course.name}</Link>
            <ChevronRight className="w-4 h-4" />
            <span className="text-gray-900">Upload Note</span>
          </div>
          <h1 className="text-2xl font-semibold text-gray-900">Upload New Note</h1>
        </div>
      </header>

      <div className="p-6 max-w-4xl mx-auto">
        {processingStage === 'idle' ? (
          <>
            <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-12 mb-6">
              {!selectedFile ? (
                <div onDrop={handleDrop} onDragOver={(e) => e.preventDefault()} className="text-center">
                  <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">Drag and drop your image here</h3>
                  <p className="text-gray-500 mb-6">Or click to browse your files</p>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Browse Files
                  </button>
                  <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileInput} className="hidden" />
                  <p className="text-sm text-gray-400 mt-4">Supports JPG, PNG, HEIC (Max 10MB)</p>
                </div>
              ) : (
                <div className="relative">
                  <button onClick={resetUpload} className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 z-10">
                    <X className="w-5 h-5" />
                  </button>
                  <img src={previewUrl!} alt="Preview" className="max-h-96 mx-auto rounded-lg" />
                  <p className="text-center mt-4 text-gray-600">{selectedFile.name}</p>
                </div>
              )}
            </div>

            {selectedFile && (
              <>
                <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                  <label className="block font-medium mb-2 text-gray-900">Additional Context (Optional)</label>
                  <textarea
                    value={additionalContext}
                    onChange={(e) => setAdditionalContext(e.target.value)}
                    placeholder="Add any context that might help with processing..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    rows={4}
                  />
                </div>
                <div className="flex items-center justify-end gap-3">
                  <button onClick={() => router.push(`/course/${courseId}`)} className="px-6 py-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                    Cancel
                  </button>
                  <button onClick={handleProcess} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Process Note
                  </button>
                </div>
              </>
            )}
          </>
        ) : (
          <ProcessingView stage={processingStage} stageText={getStageText(processingStage)} error={error} onRetry={resetUpload} />
        )}
      </div>
    </>
  );
}

function ProcessingView({ stage, error, onRetry }: { stage: ProcessingStage; stageText: string; error: string | null; onRetry: () => void }) {
  const stages = [
    { id: 'extracting', label: 'Extracting text...' },
    { id: 'analyzing', label: 'Analyzing structure...' },
    { id: 'formatting', label: 'Formatting note...' },
    { id: 'generating', label: 'Generating study materials...' },
  ];
  const currentStageIndex = stages.findIndex(s => s.id === stage);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
      <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
        {stage === 'complete' ? <CheckCircle2 className="w-10 h-10 text-green-600" /> : stage === 'error' ? <X className="w-10 h-10 text-red-600" /> : <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />}
      </div>
      <h2 className="text-2xl font-semibold mb-2 text-gray-900">{stage === 'complete' ? 'Processing Complete!' : stage === 'error' ? 'Processing Failed' : 'Processing Your Note'}</h2>
      <p className="text-gray-500 mb-8">{stage === 'complete' ? 'Your note has been successfully processed' : stage === 'error' ? error || 'An error occurred during processing' : 'This usually takes 10-30 seconds'}</p>

      {stage !== 'error' && (
        <div className="max-w-md mx-auto space-y-3">
          {stages.map((s, index) => (
            <div key={s.id} className={`flex items-center gap-3 p-3 rounded-lg ${index < currentStageIndex || stage === 'complete' ? 'bg-green-50' : index === currentStageIndex ? 'bg-blue-50' : 'bg-gray-50'}`}>
              {index < currentStageIndex || stage === 'complete' ? <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" /> : index === currentStageIndex ? <Loader2 className="w-5 h-5 text-blue-600 animate-spin flex-shrink-0" /> : <div className="w-5 h-5 rounded-full border-2 border-gray-300 flex-shrink-0" />}
              <span className={`${index <= currentStageIndex || stage === 'complete' ? 'text-gray-900' : 'text-gray-500'}`}>{s.label}</span>
            </div>
          ))}
        </div>
      )}
      {stage === 'complete' && <p className="text-sm text-gray-500 mt-8">Redirecting to your note...</p>}
      {stage === 'error' && <button onClick={onRetry} className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">Try Again</button>}
    </div>
  );
}
