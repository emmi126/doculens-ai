// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: Date;
}

// Course types
export type CourseColor = 'blue' | 'purple' | 'green' | 'indigo' | 'teal' | 'pink' | 'orange' | 'red';

export interface Course {
  id: string;
  name: string;
  description?: string;
  icon: string;
  color: CourseColor;
  documentCount: number;
  status: 'active' | 'trash';
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date;
}

export interface CourseCreate {
  name: string;
  description?: string;
  icon?: string;
  color?: CourseColor;
}

export interface CourseUpdate {
  name?: string;
  description?: string;
  icon?: string;
  color?: CourseColor;
}

// Document types
export interface Document {
  id: string;
  courseId: string;
  title: string;
  originalText: string;
  formattedNote: string;
  excerpt: string;
  imagePath?: string;
  status: 'active' | 'trash';
  processingTime?: number;
  metadata?: DocumentMetadata;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date;
  // Study materials (from multi-agent processing)
  studyMaterials?: StudyMaterials;
}

export interface DocumentMetadata {
  ocrConfidence?: number;
  fileName?: string;
  context?: string;
  multiAgent?: boolean;
  agentsRun?: string[];
  qaCount?: number;
  ragContextCount?: number;
}

export interface StudyMaterials {
  flashcards: Flashcard[];
  knowledgeCards: KnowledgeCard[];
  keyConcepts: KeyConcept[];
}

export interface Flashcard {
  id: string;
  question: string;
  answer: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  concept?: string;
}

export interface KnowledgeCard {
  id: string;
  term: string;
  definition: string;
  tags: string[];
  concept?: string;
}

export interface KeyConcept {
  id: string;
  concept: string;
  definition?: string;
  importance: number; // 0-100
}

export interface RelatedNote {
  id: string;
  title: string;
  excerpt: string;
  similarity: number;
  createdAt: Date | null;
}

// API response types
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

// Color class mapping for UI
export const colorClasses: Record<CourseColor, string> = {
  blue: 'bg-blue-100 text-blue-600 border-blue-200',
  purple: 'bg-purple-100 text-purple-600 border-purple-200',
  green: 'bg-green-100 text-green-600 border-green-200',
  indigo: 'bg-indigo-100 text-indigo-600 border-indigo-200',
  teal: 'bg-teal-100 text-teal-600 border-teal-200',
  pink: 'bg-pink-100 text-pink-600 border-pink-200',
  orange: 'bg-orange-100 text-orange-600 border-orange-200',
  red: 'bg-red-100 text-red-600 border-red-200',
};

// Helper function to format dates
export function formatDate(date: Date): string {
  const now = new Date();
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

// Helper function to get confidence badge color
export function getConfidenceBadgeColor(confidence: number): string {
  if (confidence >= 90) return 'bg-green-100 text-green-700 border-green-200';
  if (confidence >= 80) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
  return 'bg-red-100 text-red-700 border-red-200';
}
