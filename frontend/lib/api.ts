import axios, { AxiosProgressEvent } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions for API responses
export interface HealthResponse {
  status: string;
  message: string;
}

export interface ProcessNoteResponse {
  success: boolean;
  original_text: string;
  formatted_note: string;
  processing_time: number;
  document_id: string | null;
  error: string | null;
}

export interface RelatedNote {
  id: string;
  title: string;
  excerpt: string;
  similarity: number;
  created_at: string | null;
}

export interface OCRResponse {
  success: boolean;
  text: string;
  confidence: number;
  error: string | null;
}

export interface UploadResponse {
  filename: string;
  message: string;
  file_path: string;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout (OCR + LLM may take time)
});

/**
 * Health check
 */
export const healthCheck = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Process note - complete pipeline
 * @param file - Image file
 * @param additionalContext - Additional context
 * @param onProgress - Progress callback
 */
export const processNote = async (
  file: File,
  courseId?: string,
  additionalContext: string = '',
  token?: string,
  onProgress: ((progress: number) => void) | null = null
): Promise<ProcessNoteResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (courseId) {
      formData.append('course_id', courseId);
    }
    if (additionalContext) {
      formData.append('additional_context', additionalContext);
    }

    const headers: Record<string, string> = {
      'Content-Type': 'multipart/form-data',
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await api.post<ProcessNoteResponse>('/process-note', formData, {
      headers,
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  } catch (error) {
    console.error('Process note failed:', error);
    throw error;
  }
};

/**
 * OCR only
 */
export const ocrOnly = async (file: File): Promise<OCRResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<OCRResponse>('/ocr', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('OCR failed:', error);
    throw error;
  }
};

/**
 * Upload file
 */
export const uploadFile = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Upload failed:', error);
    throw error;
  }
};

/**
 * Get related notes for a document
 * @param documentId - Document ID
 * @param topK - Number of related notes to retrieve (default: 5)
 * @param token - Auth0 access token (optional, for authenticated requests)
 */
export const getRelatedNotes = async (
  documentId: string,
  topK: number = 5,
  token?: string
): Promise<RelatedNote[]> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.get<RelatedNote[]>(
      `/api/documents/${documentId}/related`,
      {
        params: { top_k: topK },
        headers
      }
    );

    return response.data;
  } catch (error) {
    console.error('Failed to fetch related notes:', error);
    return []; // Return empty array on error
  }
};

// ===== Course API =====

export interface CourseResponse {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  document_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CourseCreate {
  name: string;
  description?: string;
  color?: string;
  icon?: string;
}

export interface CourseUpdate {
  name?: string;
  description?: string;
  color?: string;
  icon?: string;
}

/**
 * List all courses for the current user
 */
export const listCourses = async (
  status: string = 'active',
  token?: string
): Promise<CourseResponse[]> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.get<CourseResponse[]>('/api/courses', {
      params: { status },
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to fetch courses:', error);
    throw error;
  }
};

/**
 * Get a specific course
 */
export const getCourse = async (
  courseId: string,
  token?: string
): Promise<CourseResponse> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.get<CourseResponse>(`/api/courses/${courseId}`, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to fetch course:', error);
    throw error;
  }
};

/**
 * Create a new course
 */
export const createCourse = async (
  data: CourseCreate,
  token?: string
): Promise<{ id: string; name: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.post<{ id: string; name: string }>('/api/courses', data, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to create course:', error);
    throw error;
  }
};

/**
 * Update a course
 */
export const updateCourse = async (
  courseId: string,
  data: CourseUpdate,
  token?: string
): Promise<{ message: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.put<{ message: string }>(`/api/courses/${courseId}`, data, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to update course:', error);
    throw error;
  }
};

/**
 * Delete a course (soft delete)
 */
export const deleteCourse = async (
  courseId: string,
  token?: string
): Promise<{ message: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.delete<{ message: string }>(`/api/courses/${courseId}`, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to delete course:', error);
    throw error;
  }
};

/**
 * Restore a course from trash
 */
export const restoreCourse = async (
  courseId: string,
  token?: string
): Promise<{ message: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.post<{ message: string }>(`/api/courses/${courseId}/restore`, null, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to restore course:', error);
    throw error;
  }
};

// ===== Document API =====

export interface DocumentResponse {
  id: string;
  course_id: string;
  title: string;
  original_text: string;
  formatted_note: string;
  excerpt?: string;
  image_path?: string;
  status: string;
  processing_time?: number;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface DocumentCreate {
  course_id: string;
  title: string;
  original_text: string;
  formatted_note: string;
  excerpt?: string;
  image_path?: string;
  processing_time?: number;
  metadata?: Record<string, unknown>;
}

export interface DocumentUpdate {
  title?: string;
  formatted_note?: string;
  course_id?: string;
}

/**
 * List documents in a course
 */
export const listDocuments = async (
  courseId: string,
  status: string = 'active',
  token?: string
): Promise<DocumentResponse[]> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.get<DocumentResponse[]>(
      `/api/documents/courses/${courseId}/documents`,
      {
        params: { status },
        headers,
      }
    );

    return response.data;
  } catch (error) {
    console.error('Failed to fetch documents:', error);
    throw error;
  }
};

/**
 * Get a specific document
 */
export const getDocument = async (
  documentId: string,
  token?: string
): Promise<DocumentResponse> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.get<DocumentResponse>(`/api/documents/${documentId}`, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to fetch document:', error);
    throw error;
  }
};

/**
 * Create a new document
 */
export const createDocument = async (
  data: DocumentCreate,
  token?: string
): Promise<{ id: string; title: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.post<{ id: string; title: string }>('/api/documents', data, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to create document:', error);
    throw error;
  }
};

/**
 * Update a document
 */
export const updateDocument = async (
  documentId: string,
  data: DocumentUpdate,
  token?: string
): Promise<{ message: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.put<{ message: string }>(`/api/documents/${documentId}`, data, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to update document:', error);
    throw error;
  }
};

/**
 * Delete a document (soft delete)
 */
export const deleteDocument = async (
  documentId: string,
  token?: string
): Promise<{ message: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.delete<{ message: string }>(`/api/documents/${documentId}`, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to delete document:', error);
    throw error;
  }
};

/**
 * Restore a document from trash
 */
export const restoreDocument = async (
  documentId: string,
  token?: string
): Promise<{ message: string }> => {
  try {
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await api.post<{ message: string }>(`/api/documents/${documentId}/restore`, null, {
      headers,
    });

    return response.data;
  } catch (error) {
    console.error('Failed to restore document:', error);
    throw error;
  }
};

export default api;
