'use client';

import { BookOpen, FolderOpen, Trash2, LogOut } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout({ logoutParams: { returnTo: window.location.origin } });
  };

  // Get user initials for avatar
  const getInitials = (name?: string) => {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <>
      {/* Sidebar */}
      <aside
        className={`
          w-[280px] bg-white border-r border-gray-200 flex flex-col h-screen
          fixed lg:sticky top-0 z-40
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          transition-transform duration-300
        `}
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center gap-2">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-semibold">DocuLens AI</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <Link
            href="/dashboard"
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors
              ${pathname === '/dashboard' || pathname.startsWith('/course')
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-700 hover:bg-gray-50'
              }
            `}
          >
            <FolderOpen className="w-5 h-5" />
            <span>Courses</span>
          </Link>

          <Link
            href="/trash"
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
              ${pathname === '/trash'
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-700 hover:bg-gray-50'
              }
            `}
          >
            <Trash2 className="w-5 h-5" />
            <span>Trash</span>
          </Link>
        </nav>

        {/* User Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-medium">
              {user?.picture ? (
                <img
                  src={user.picture}
                  alt={user.name || 'User'}
                  className="w-10 h-10 rounded-full"
                />
              ) : (
                getInitials(user?.name)
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="truncate font-medium">{user?.name || 'User'}</div>
              <div className="text-sm text-gray-500 truncate">{user?.email}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 lg:hidden z-30"
          onClick={onClose}
        />
      )}
    </>
  );
}
