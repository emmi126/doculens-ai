'use client';

import React, { useEffect, useState } from 'react';
import { Link2, Sparkles, Calendar } from 'lucide-react';
import { getRelatedNotes, RelatedNote } from '@/lib/api';

interface RelatedNotesProps {
  documentId: string | null;
  token?: string;
}

export default function RelatedNotes({ documentId, token }: RelatedNotesProps) {
  const [relatedNotes, setRelatedNotes] = useState<RelatedNote[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!documentId) {
      setRelatedNotes([]);
      return;
    }

    const fetchRelatedNotes = async () => {
      setLoading(true);
      try {
        const notes = await getRelatedNotes(documentId, 5, token);
        setRelatedNotes(notes);
      } catch (error) {
        console.error('Error fetching related notes:', error);
        setRelatedNotes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRelatedNotes();
  }, [documentId, token]);

  if (!documentId) {
    return null;
  }

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Sparkles className="w-5 h-5 text-purple-600 animate-pulse" />
          <h3 className="font-semibold text-gray-900">相关笔记</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
      </div>
    );
  }

  if (relatedNotes.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900">相关笔记</h3>
        </div>
        <p className="text-sm text-gray-500 text-center py-4">
          暂无相关笔记。继续添加笔记，AI 将自动关联相似内容。
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Sparkles className="w-5 h-5 text-purple-600" />
        <h3 className="font-semibold text-gray-900">相关笔记</h3>
        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
          AI 推荐
        </span>
      </div>

      <div className="space-y-3">
        {relatedNotes.map((note) => (
          <div
            key={note.id}
            className="group p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium text-gray-900 group-hover:text-purple-700 transition-colors flex-1">
                {note.title}
              </h4>
              <div className="flex items-center space-x-1 text-xs text-purple-600 font-medium">
                <Link2 className="w-3 h-3" />
                <span>{Math.round(note.similarity * 100)}%</span>
              </div>
            </div>

            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
              {note.excerpt}
            </p>

            {note.created_at && (
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <Calendar className="w-3 h-3" />
                <span>{new Date(note.created_at).toLocaleDateString('zh-CN')}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          基于 AI 向量相似度分析，这些笔记与当前内容最相关
        </p>
      </div>
    </div>
  );
}
