import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  progress?: number | null;
}

export default function LoadingSpinner({
  message = '处理中...',
  progress = null
}: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
      <div className="text-center">
        <p className="text-lg font-medium text-gray-700">{message}</p>
        {progress !== null && (
          <div className="mt-4 w-64">
            <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-500 mt-2">{progress}%</p>
          </div>
        )}
      </div>
    </div>
  );
}
