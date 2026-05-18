'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight, Menu, Edit, Download, Trash2, FileText, Eye, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import toast from 'react-hot-toast';
import RelatedNotes from '@/components/RelatedNotes';
import { CourseResponse, deleteDocument, DocumentResponse, getCourse, getDocument } from '@/lib/api';
import { useAuth } from '@/lib/hooks/useAuth';

export default function DocumentView() {
  const params = useParams();
  const router = useRouter();
  const { getAccessTokenSilently } = useAuth();
  const documentId = params.documentId as string;
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'formatted' | 'raw'>('formatted');
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [course, setCourse] = useState<CourseResponse | null>(null);
  const [token, setToken] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDocument = async () => {
      setLoading(true);
      try {
        const accessToken = await getAccessTokenSilently();
        setToken(accessToken);
        const documentData = await getDocument(documentId, accessToken);
        const courseData = await getCourse(documentData.course_id, accessToken);
        setDocument(documentData);
        setCourse(courseData);
      } catch (error) {
        console.error(error);
        toast.error('Failed to load document');
      } finally {
        setLoading(false);
      }
    };
    loadDocument();
  }, [documentId]);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen text-gray-500"><Loader2 className="w-6 h-6 animate-spin mr-2" />Loading document...</div>;
  }

  if (!document || !course) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Document not found</h2>
          <Link href="/dashboard" className="text-blue-600 hover:underline">Return to Dashboard</Link>
        </div>
      </div>
    );
  }

  const handleDownload = () => {
    const blob = new Blob([document.formatted_note], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement('a');
    a.href = url;
    a.download = `${document.title}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDelete = async () => {
    if (!window.confirm('Move this document to trash?')) return;
    try {
      const accessToken = token || await getAccessTokenSilently();
      await deleteDocument(documentId, accessToken);
      toast.success('Document moved to trash');
      router.push(`/course/${course.id}`);
    } catch (error) {
      console.error(error);
      toast.error('Failed to delete document');
    }
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden p-2 hover:bg-gray-100 rounded-lg -ml-2"><Menu className="w-5 h-5" /></button>
            <Link href="/dashboard" className="hover:text-gray-900">Courses</Link>
            <ChevronRight className="w-4 h-4" />
            <Link href={`/course/${course.id}`} className="hover:text-gray-900">{course.name}</Link>
            <ChevronRight className="w-4 h-4" />
            <span className="text-gray-900">{document.title}</span>
          </div>
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-gray-900">{document.title}</h1>
            <div className="flex items-center gap-2">
              <button onClick={() => router.push(`/document/${documentId}/edit`)} className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"><Edit className="w-4 h-4" /><span>Edit</span></button>
              <button onClick={handleDownload} className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"><Download className="w-4 h-4" /><span>Download</span></button>
              <button onClick={handleDelete} className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"><Trash2 className="w-4 h-4" /><span>Delete</span></button>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6 max-w-6xl mx-auto">
        <div className="bg-white rounded-xl border border-gray-200 mb-6">
          <div className="border-b border-gray-200 px-6">
            <div className="flex gap-6">
              <button onClick={() => setActiveTab('formatted')} className={`flex items-center gap-2 px-4 py-4 border-b-2 transition-colors ${activeTab === 'formatted' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}><Eye className="w-4 h-4" /><span>Formatted Note</span></button>
              <button onClick={() => setActiveTab('raw')} className={`flex items-center gap-2 px-4 py-4 border-b-2 transition-colors ${activeTab === 'raw' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}><FileText className="w-4 h-4" /><span>Original Text</span></button>
            </div>
          </div>
          <div className="p-8">
            {activeTab === 'formatted' ? (
              <div className="prose prose-gray max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                  {document.formatted_note}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="font-mono text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-6 rounded-lg">{document.original_text}</div>
            )}
          </div>
        </div>
        <RelatedNotes documentId={document.id} token={token} />
      </div>
    </>
  );
}
