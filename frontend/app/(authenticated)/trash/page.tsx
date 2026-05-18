'use client';

import { useEffect, useState } from 'react';
import { Menu, Trash2, RotateCcw, XCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { CourseResponse, DocumentResponse, listCourses, listDocuments, restoreCourse, restoreDocument } from '@/lib/api';
import { useAuth } from '@/lib/hooks/useAuth';

interface TrashItem {
  id: string;
  name: string;
  type: 'course' | 'document';
  deletedAt: string;
  icon?: string;
  courseId?: string;
}

function formatDate(value: string): string {
  const date = new Date(value);
  const diffInDays = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function TrashPage() {
  const { getAccessTokenSilently } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [trashItems, setTrashItems] = useState<TrashItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTrash = async () => {
    setLoading(true);
    try {
      const token = await getAccessTokenSilently();
      const trashedCourses = await listCourses('trash', token);
      const activeCourses = await listCourses('active', token);
      const trashedDocumentsByCourse = await Promise.all(
        activeCourses.map(async (course) => {
          try {
            const docs = await listDocuments(course.id, 'trash', token);
            return docs.map((doc) => ({ ...doc, courseName: course.name }));
          } catch {
            return [];
          }
        })
      );

      setTrashItems([
        ...trashedCourses.map((course: CourseResponse) => ({
          id: course.id,
          name: course.name,
          type: 'course' as const,
          deletedAt: course.updated_at,
          icon: course.icon,
        })),
        ...trashedDocumentsByCourse.flat().map((doc: DocumentResponse & { courseName?: string }) => ({
          id: doc.id,
          name: doc.title,
          type: 'document' as const,
          deletedAt: doc.updated_at,
          courseId: doc.course_id,
        })),
      ]);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load trash');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrash();
  }, []);

  const handleRestore = async (item: TrashItem) => {
    try {
      const token = await getAccessTokenSilently();
      if (item.type === 'course') {
        await restoreCourse(item.id, token);
      } else {
        await restoreDocument(item.id, token);
      }
      setTrashItems(items => items.filter(current => current.id !== item.id));
      toast.success('Item restored successfully');
    } catch (error) {
      console.error(error);
      toast.error('Failed to restore item');
    }
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"><Menu className="w-5 h-5" /></button>
            <div className="flex items-center gap-3">
              <Trash2 className="w-6 h-6 text-gray-600" />
              <h1 className="text-2xl font-semibold">Trash</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6 max-w-5xl mx-auto">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-gray-500"><Loader2 className="w-6 h-6 animate-spin mr-2" />Loading trash...</div>
        ) : trashItems.length === 0 ? (
          <EmptyTrash />
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-500">Items in trash can be restored.</div>
            <div className="space-y-3">
              {trashItems.map((item) => (
                <TrashItemCard key={`${item.type}-${item.id}`} item={item} daysAgo={formatDate(item.deletedAt)} onRestore={() => handleRestore(item)} />
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
}

function TrashItemCard({ item, daysAgo, onRestore }: { item: TrashItem; daysAgo: string; onRestore: () => void }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 flex items-center justify-between hover:shadow-md transition-all">
      <div className="flex items-center gap-4">
        {item.type === 'course' && item.icon && <div className="text-3xl">{item.icon}</div>}
        {item.type === 'document' && <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center"><Trash2 className="w-5 h-5 text-gray-400" /></div>}
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900">{item.name}</h3>
            <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{item.type}</span>
          </div>
          <p className="text-sm text-gray-500">Deleted {daysAgo}</p>
        </div>
      </div>
      <button onClick={onRestore} className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
        <RotateCcw className="w-4 h-4" />
        <span>Restore</span>
      </button>
    </div>
  );
}

function EmptyTrash() {
  return (
    <div className="text-center py-16">
      <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <XCircle className="w-10 h-10 text-gray-400" />
      </div>
      <h3 className="text-xl font-semibold mb-2 text-gray-900">Trash is empty</h3>
      <p className="text-gray-500">Deleted items will appear here</p>
    </div>
  );
}
