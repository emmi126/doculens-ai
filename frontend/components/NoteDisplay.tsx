'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Copy, Check, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import RelatedNotes from './RelatedNotes';

interface NoteDisplayProps {
  originalText: string;
  formattedNote: string;
  processingTime?: number;
  documentId?: string | null;
  token?: string;
}

export default function NoteDisplay({
  originalText,
  formattedNote,
  processingTime,
  documentId,
  token
}: NoteDisplayProps) {
  const [copied, setCopied] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(formattedNote);
      setCopied(true);
      toast.success('已复制到剪贴板');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error('复制失败');
    }
  };

  const downloadMarkdown = () => {
    const blob = new Blob([formattedNote], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `note-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('笔记已下载');
  };

  return (
    <div className="space-y-4">
      {/* Header toolbar */}
      <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-blue-600" />
          <span className="font-medium text-gray-700">整理后的笔记</span>
          {processingTime && (
            <span className="text-sm text-gray-500">
              (处理时间: {processingTime.toFixed(2)}s)
            </span>
          )}
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => setShowOriginal(!showOriginal)}
            className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            {showOriginal ? '隐藏原文' : '查看原文'}
          </button>

          <button
            onClick={copyToClipboard}
            className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors flex items-center space-x-1"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                <span>已复制</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>复制</span>
              </>
            )}
          </button>

          <button
            onClick={downloadMarkdown}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-1"
          >
            <Download className="w-4 h-4" />
            <span>下载</span>
          </button>
        </div>
      </div>

      {/* Original text (expandable) */}
      {showOriginal && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-700 mb-2">OCR 识别的原始文本：</h3>
          <pre className="text-sm text-gray-600 whitespace-pre-wrap font-mono">
            {originalText}
          </pre>
        </div>
      )}

      {/* Main content: Markdown + Related Notes side by side on desktop */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Markdown rendering - takes 2 columns on large screens */}
        <div className="lg:col-span-2">
          <div className="bg-white border border-gray-200 rounded-lg p-6 prose prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ node, ...props }) => (
                  <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4" {...props} />
                ),
                h2: ({ node, ...props }) => (
                  <h2 className="text-xl font-bold text-gray-800 mt-5 mb-3" {...props} />
                ),
                h3: ({ node, ...props }) => (
                  <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2" {...props} />
                ),
                p: ({ node, ...props }) => (
                  <p className="text-gray-700 leading-relaxed mb-4" {...props} />
                ),
                ul: ({ node, ...props }) => (
                  <ul className="list-disc list-inside mb-4 space-y-2" {...props} />
                ),
                ol: ({ node, ...props }) => (
                  <ol className="list-decimal list-inside mb-4 space-y-2" {...props} />
                ),
                li: ({ node, ...props }) => (
                  <li className="text-gray-700" {...props} />
                ),
                code: ({ node, className, ...props }) => {
                  const isInline = !className?.includes('language-');
                  return isInline ? (
                    <code className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />
                  ) : (
                    <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono" {...props} />
                  );
                },
                blockquote: ({ node, ...props }) => (
                  <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4" {...props} />
                ),
                strong: ({ node, ...props }) => (
                  <strong className="font-bold text-gray-900" {...props} />
                ),
              }}
            >
              {formattedNote}
            </ReactMarkdown>
          </div>
        </div>

        {/* Related Notes - takes 1 column on large screens, stacks on mobile */}
        <div className="lg:col-span-1">
          <RelatedNotes documentId={documentId || null} token={token} />
        </div>
      </div>
    </div>
  );
}
