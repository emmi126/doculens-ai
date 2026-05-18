'use client';

import React, { useState, useCallback } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import toast from 'react-hot-toast';

interface ImageUploaderProps {
  onImageSelect: (file: File | null) => void;
  disabled?: boolean;
}

export default function ImageUploader({ onImageSelect, disabled = false }: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = useCallback((file: File) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('请上传图片文件');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('文件大小不能超过 10MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Pass file to parent component
    onImageSelect(file);
  }, [onImageSelect]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const clearImage = useCallback(() => {
    setPreview(null);
    onImageSelect(null);
  }, [onImageSelect]);

  return (
    <div className="w-full">
      {!preview ? (
        <div
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-all duration-200
            ${isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !disabled && document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileInput}
            disabled={disabled}
          />

          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />

          <p className="text-lg font-medium text-gray-700 mb-2">
            拖拽图片到此处，或点击上传
          </p>
          <p className="text-sm text-gray-500">
            支持 JPG, PNG, JPEG 格式，最大 10MB
          </p>
        </div>
      ) : (
        <div className="relative border-2 border-gray-200 rounded-lg overflow-hidden">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-auto max-h-96 object-contain"
          />

          {!disabled && (
            <button
              onClick={clearImage}
              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors shadow-lg"
              title="移除图片"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-4">
            <div className="flex items-center text-white text-sm">
              <ImageIcon className="w-4 h-4 mr-2" />
              <span>图片已选择</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
