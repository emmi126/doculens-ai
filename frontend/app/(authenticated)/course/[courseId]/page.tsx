'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight, Plus, Search, MoreVertical, Menu, FileText, Upload, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { CourseResponse, deleteDocument, DocumentResponse, getCourse, listDocuments } from '@/lib/api';
import { useAuth } from '@/lib/hooks/useAuth';

function formatDate(value: string): string {
  const date = new Date(value);
  const diffInDays = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function CourseDetail() {
  const params = useParams();
  const router = useRouter();
  const { getAccessTokenSilently } = useAuth();
  const courseId = params.courseId as string;
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [course, setCourse] = useState<CourseResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const loadCourse = async () => {
    setLoading(true);
    try {
      const token = await getAccessTokenSilently();
      const [courseData, documentData] = await Promise.all([
        getCourse(courseId, token),
        listDocuments(courseId, 'active', token),
      ]);
      setCourse(courseData);
      setDocuments(documentData);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCourse();
  }, [courseId]);

  const handleDeleteDocument = async (documentId: string) => {
    if (!window.confirm('Move this document to trash?')) return;

    try {
      const token = await getAccessTokenSilently();
      await deleteDocument(documentId, token);
      setDocuments((items) => items.filter((doc) => doc.id !== documentId));
      toast.success('Document moved to trash');
    } catch (error) {
      console.error(error);
      toast.error('Failed to delete document');
    }
  };

  if (loading) {
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

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (doc.excerpt || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

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
            <Link href="/dashboard" className="hover:text-gray-900">
              Courses
            </Link>
            <ChevronRight className="w-4 h-4" />
            <span className="text-gray-900">{course.name}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-4xl">{course.icon || 'Book'}</div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">{course.name}</h1>
                <p className="text-gray-500">
                  {documents.length} {documents.length === 1 ? 'document' : 'documents'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search in course..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
                />
              </div>
              <button
                onClick={() => router.push(`/course/${courseId}/upload`)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-5 h-5" />
                <span>New Note</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6">
        {filteredDocuments.length === 0 ? (
          <EmptyState searchQuery={searchQuery} courseId={courseId} />
        ) : (
          <div className="space-y-3">
            {filteredDocuments.map((doc) => (
              <DocumentItem key={doc.id} document={doc} onDelete={handleDeleteDocument} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}

function DocumentItem({ document, onDelete }: { document: DocumentResponse; onDelete: (documentId: string) => void }) {
  const [showMenu, setShowMenu] = useState(false);
  const wordCount = document.formatted_note.split(/\s+/).filter(Boolean).length;

  return (
    <Link
      href={`/document/${document.id}`}
      className="group bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-all duration-200 flex items-start justify-between relative block"
    >
      <div className="flex-1 min-w-0 pr-4">
        <div className="flex items-start gap-3 mb-2">
          <FileText className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-gray-900 mb-1">{document.title}</h3>
            <p className="text-sm text-gray-500 line-clamp-2">{document.excerpt || document.formatted_note.slice(0, 160)}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500 ml-8">
          <span>{formatDate(document.created_at)}</span>
          <span>•</span>
          <span>{wordCount} words</span>
        </div>
      </div>

      <button
        onClick={(e) => {
          e.preventDefault();
          setShowMenu(!showMenu);
        }}
        className="p-2 opacity-0 group-hover:opacity-100 hover:bg-gray-100 rounded-lg transition-opacity flex-shrink-0"
      >
        <MoreVertical className="w-5 h-5 text-gray-600" />
      </button>

      {showMenu && (
        <div
          className="absolute top-12 right-6 bg-white border border-gray-200 rounded-lg shadow-lg py-2 min-w-[160px] z-10"
          onClick={(e) => e.preventDefault()}
        >
          <button className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm">
            Open
          </button>
          <button
            onClick={() => onDelete(document.id)}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm text-red-600"
          >
            Delete
          </button>
        </div>
      )}
    </Link>
  );
}

function EmptyState({ searchQuery, courseId }: { searchQuery: string; courseId: string }) {
  const router = useRouter();

  if (searchQuery) {
    return (
      <div className="text-center py-16">
        <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold mb-2 text-gray-900">No results for &quot;{searchQuery}&quot;</h3>
        <p className="text-gray-500">Try searching with different keywords</p>
      </div>
    );
  }

  return (
    <div className="text-center py-16">
      <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Upload className="w-10 h-10 text-blue-600" />
      </div>
      <h3 className="text-xl font-semibold mb-2 text-gray-900">No documents yet</h3>
      <p className="text-gray-500 mb-6">Upload your first note to get started</p>
      <button
        onClick={() => router.push(`/course/${courseId}/upload`)}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Upload First Note
      </button>
    </div>
  );
}
