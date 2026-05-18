'use client';

import { useEffect, useState } from 'react';
import { Plus, Search, MoreVertical, Menu, Loader2 } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { createCourse, deleteCourse, listCourses, CourseResponse } from '@/lib/api';
import { useAuth } from '@/lib/hooks/useAuth';

function formatDate(value: string): string {
  const date = new Date(value);
  const diffInDays = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function Dashboard() {
  const { getAccessTokenSilently } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [courses, setCourses] = useState<CourseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const loadCourses = async () => {
    setLoading(true);
    try {
      const token = await getAccessTokenSilently();
      setCourses(await listCourses('active', token));
    } catch (error) {
      console.error(error);
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCourses();
  }, []);

  const handleCreateCourse = async () => {
    const name = window.prompt('Course name');
    if (!name?.trim()) return;

    setCreating(true);
    try {
      const token = await getAccessTokenSilently();
      await createCourse({
        name: name.trim(),
        description: '',
        color: '#2563eb',
        icon: '📘',
      }, token);
      toast.success('Course created');
      await loadCourses();
    } catch (error) {
      console.error(error);
      toast.error('Failed to create course');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteCourse = async (courseId: string) => {
    if (!window.confirm('Move this course to trash?')) return;

    try {
      const token = await getAccessTokenSilently();
      await deleteCourse(courseId, token);
      setCourses((items) => items.filter((course) => course.id !== courseId));
      toast.success('Course moved to trash');
    } catch (error) {
      console.error(error);
      toast.error('Failed to delete course');
    }
  };

  const filteredCourses = courses.filter(course =>
    course.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-2xl font-semibold">Courses</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>
            <button
              onClick={handleCreateCourse}
              disabled={creating}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60 transition-colors"
            >
              {creating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
              <span>New Course</span>
            </button>
          </div>
        </div>
      </header>

      <div className="p-6">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-gray-500">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            Loading courses...
          </div>
        ) : filteredCourses.length === 0 ? (
          <EmptyState searchQuery={searchQuery} onCreate={handleCreateCourse} />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredCourses.map((course) => (
              <CourseCard key={course.id} course={course} onDelete={handleDeleteCourse} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}

function getCourseIcon(icon?: string): string {
  if (!icon || icon === 'Book') return '📘';
  return icon;
}

function CourseCard({ course, onDelete }: { course: CourseResponse; onDelete: (courseId: string) => void }) {
  const [showMenu, setShowMenu] = useState(false);
  const icon = getCourseIcon(course.icon);

  return (
    <Link
      href={`/course/${course.id}`}
      className="group bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-all duration-200 relative"
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-14 h-14 rounded-xl border flex items-center justify-center text-2xl"
          style={{ backgroundColor: `${course.color || '#2563eb'}20`, color: course.color || '#2563eb' }}
        >
          {icon}
        </div>
        <button
          onClick={(e) => {
            e.preventDefault();
            setShowMenu(!showMenu);
          }}
          className="p-2 opacity-0 group-hover:opacity-100 hover:bg-gray-100 rounded-lg transition-opacity"
        >
          <MoreVertical className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      <h3 className="font-semibold mb-2 text-gray-900">{course.name}</h3>
      <p className="text-sm text-gray-500 line-clamp-2 min-h-[2.5rem]">{course.description || 'No description'}</p>

      <div className="flex items-center justify-between text-sm text-gray-500 mt-4">
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded">
          {course.document_count} {course.document_count === 1 ? 'note' : 'notes'}
        </span>
        <span>Updated {formatDate(course.updated_at)}</span>
      </div>

      {showMenu && (
        <div className="absolute top-16 right-6 bg-white border border-gray-200 rounded-lg shadow-lg py-2 min-w-[160px] z-10">
          <button
            onClick={(e) => {
              e.preventDefault();
              onDelete(course.id);
            }}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm text-red-600"
          >
            Delete Course
          </button>
        </div>
      )}
    </Link>
  );
}

function EmptyState({ searchQuery, onCreate }: { searchQuery: string; onCreate: () => void }) {
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
        <Plus className="w-10 h-10 text-blue-600" />
      </div>
      <h3 className="text-xl font-semibold mb-2 text-gray-900">No courses yet</h3>
      <p className="text-gray-500 mb-6">Create your first course to organize your notes</p>
      <button
        onClick={onCreate}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Create First Course
      </button>
    </div>
  );
}
