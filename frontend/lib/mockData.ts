import { Course, Document, User, CourseColor } from './types';

// Mock user
export const user: User = {
  id: 'user1',
  email: 'student@example.com',
  name: 'John Doe',
  avatar: 'JD',
  createdAt: new Date('2025-01-01'),
};

// Mock courses
export const courses: Course[] = [
  {
    id: 'course1',
    name: 'Mathematics',
    description: 'Calculus, Linear Algebra, and Statistics',
    icon: '📐',
    color: 'blue' as CourseColor,
    documentCount: 12,
    status: 'active',
    createdAt: new Date('2025-01-10'),
    updatedAt: new Date('2025-12-27'),
  },
  {
    id: 'course2',
    name: 'Computer Science',
    description: 'Algorithms, Data Structures, and Programming',
    icon: '💻',
    color: 'purple' as CourseColor,
    documentCount: 8,
    status: 'active',
    createdAt: new Date('2025-01-15'),
    updatedAt: new Date('2025-12-28'),
  },
  {
    id: 'course3',
    name: 'Physics',
    description: 'Mechanics, Thermodynamics, and Electromagnetism',
    icon: '⚛️',
    color: 'green' as CourseColor,
    documentCount: 5,
    status: 'active',
    createdAt: new Date('2025-02-01'),
    updatedAt: new Date('2025-12-26'),
  },
  {
    id: 'course4',
    name: 'Chemistry',
    description: 'Organic and Inorganic Chemistry',
    icon: '🧪',
    color: 'teal' as CourseColor,
    documentCount: 3,
    status: 'active',
    createdAt: new Date('2025-02-15'),
    updatedAt: new Date('2025-12-25'),
  },
  {
    id: 'course5',
    name: 'History',
    description: 'World History and Civilizations',
    icon: '📜',
    color: 'orange' as CourseColor,
    documentCount: 0,
    status: 'trash',
    createdAt: new Date('2025-03-01'),
    updatedAt: new Date('2025-12-20'),
    deletedAt: new Date('2025-12-25'),
  },
];

// Mock documents
export const documents: Document[] = [
  {
    id: 'doc1',
    courseId: 'course1',
    title: 'Calculus - Derivatives and Integrals',
    originalText: `Derivatives and Integrals
The derivative of a function f(x) is written as f'(x) or df/dx
Basic rules:
- Power rule: d/dx(x^n) = nx^(n-1)
- Sum rule: d/dx(f+g) = f' + g'
- Product rule: d/dx(fg) = f'g + fg'

Integration is the reverse of differentiation
∫ x^n dx = x^(n+1)/(n+1) + C`,
    formattedNote: `# Derivatives and Integrals

## Derivatives

The derivative of a function $f(x)$ is written as $f'(x)$ or $\\frac{df}{dx}$.

### Basic Derivative Rules

1. **Power Rule**: $\\frac{d}{dx}(x^n) = nx^{n-1}$
2. **Sum Rule**: $\\frac{d}{dx}(f+g) = f' + g'$
3. **Product Rule**: $\\frac{d}{dx}(fg) = f'g + fg'$

## Integration

Integration is the reverse of differentiation.

$$\\int x^n \\, dx = \\frac{x^{n+1}}{n+1} + C$$

where $C$ is the constant of integration.`,
    excerpt: 'The derivative of a function f(x) is written as f\'(x) or df/dx. Basic rules include power rule, sum rule, and product rule...',
    status: 'active',
    processingTime: 12.5,
    metadata: {
      ocrConfidence: 95,
      fileName: 'calculus_notes.jpg',
    },
    createdAt: new Date('2025-12-27'),
    updatedAt: new Date('2025-12-27'),
    studyMaterials: {
      flashcards: [
        {
          id: 'fc1',
          question: 'What is the power rule for derivatives?',
          answer: 'd/dx(x^n) = nx^(n-1)',
          difficulty: 'easy',
        },
        {
          id: 'fc2',
          question: 'What is the product rule?',
          answer: 'd/dx(fg) = f\'g + fg\'',
          difficulty: 'medium',
        },
        {
          id: 'fc3',
          question: 'What is the integral of x^n?',
          answer: 'x^(n+1)/(n+1) + C',
          difficulty: 'easy',
        },
      ],
      knowledgeCards: [
        {
          id: 'kc1',
          term: 'Derivative',
          definition: 'The rate of change of a function with respect to a variable.',
          tags: ['calculus', 'differentiation'],
        },
        {
          id: 'kc2',
          term: 'Integration',
          definition: 'The reverse process of differentiation, finding the antiderivative.',
          tags: ['calculus', 'integration'],
        },
      ],
      keyConcepts: [
        { id: 'key1', concept: 'Power Rule', importance: 95 },
        { id: 'key2', concept: 'Product Rule', importance: 85 },
        { id: 'key3', concept: 'Integration', importance: 90 },
        { id: 'key4', concept: 'Constant of Integration', importance: 70 },
      ],
    },
  },
  {
    id: 'doc2',
    courseId: 'course1',
    title: 'Linear Algebra - Matrix Operations',
    originalText: `Matrix Operations
A matrix is a rectangular array of numbers
Matrix addition: Add corresponding elements
Matrix multiplication: Row by column`,
    formattedNote: `# Matrix Operations

## What is a Matrix?

A matrix is a rectangular array of numbers arranged in rows and columns.

## Basic Operations

### Matrix Addition
Add corresponding elements of matrices with the same dimensions.

### Matrix Multiplication
Multiply row elements by column elements and sum the products.`,
    excerpt: 'A matrix is a rectangular array of numbers. Matrix addition adds corresponding elements...',
    status: 'active',
    processingTime: 8.2,
    metadata: {
      ocrConfidence: 92,
    },
    createdAt: new Date('2025-12-26'),
    updatedAt: new Date('2025-12-26'),
  },
  {
    id: 'doc3',
    courseId: 'course2',
    title: 'Data Structures - Binary Trees',
    originalText: `Binary Trees
A binary tree is a tree data structure
Each node has at most two children
Left child and right child`,
    formattedNote: `# Binary Trees

## Definition

A binary tree is a tree data structure where each node has at most two children, referred to as the left child and the right child.

## Key Properties

- Each node contains a value
- Maximum of 2 children per node
- Used for efficient searching and sorting

## Common Operations

1. **Insert**: Add a new node
2. **Search**: Find a value
3. **Delete**: Remove a node
4. **Traverse**: Visit all nodes`,
    excerpt: 'A binary tree is a tree data structure where each node has at most two children...',
    status: 'active',
    processingTime: 10.1,
    metadata: {
      ocrConfidence: 88,
    },
    createdAt: new Date('2025-12-28'),
    updatedAt: new Date('2025-12-28'),
    studyMaterials: {
      flashcards: [
        {
          id: 'fc4',
          question: 'How many children can each node have in a binary tree?',
          answer: 'At most two children (left and right)',
          difficulty: 'easy',
        },
      ],
      knowledgeCards: [
        {
          id: 'kc3',
          term: 'Binary Tree',
          definition: 'A tree data structure where each node has at most two children.',
          tags: ['data structures', 'trees'],
        },
      ],
      keyConcepts: [
        { id: 'key5', concept: 'Binary Tree', importance: 95 },
        { id: 'key6', concept: 'Tree Traversal', importance: 85 },
      ],
    },
  },
  {
    id: 'doc4',
    courseId: 'course3',
    title: 'Newton\'s Laws of Motion',
    originalText: `Newton's Laws
1st Law: Object at rest stays at rest
2nd Law: F = ma
3rd Law: Every action has equal and opposite reaction`,
    formattedNote: `# Newton's Laws of Motion

## First Law (Law of Inertia)

An object at rest stays at rest, and an object in motion stays in motion with the same speed and direction, unless acted upon by an external force.

## Second Law

$$F = ma$$

Force equals mass times acceleration.

## Third Law

For every action, there is an equal and opposite reaction.`,
    excerpt: 'Newton\'s First Law: An object at rest stays at rest. Second Law: F = ma...',
    status: 'active',
    processingTime: 7.5,
    metadata: {
      ocrConfidence: 94,
    },
    createdAt: new Date('2025-12-26'),
    updatedAt: new Date('2025-12-26'),
  },
  {
    id: 'doc5',
    courseId: 'course2',
    title: 'Algorithms - Sorting Methods',
    originalText: `Sorting Algorithms
Bubble Sort: Compare adjacent elements
Quick Sort: Divide and conquer
Merge Sort: Split and merge`,
    formattedNote: `# Sorting Algorithms

## Bubble Sort

Repeatedly compare adjacent elements and swap if out of order.

- Time Complexity: O(n²)
- Space Complexity: O(1)

## Quick Sort

Divide and conquer approach using a pivot element.

- Time Complexity: O(n log n) average
- Space Complexity: O(log n)

## Merge Sort

Recursively split the array and merge sorted halves.

- Time Complexity: O(n log n)
- Space Complexity: O(n)`,
    excerpt: 'Bubble Sort compares adjacent elements. Quick Sort uses divide and conquer...',
    status: 'trash',
    processingTime: 9.0,
    metadata: {
      ocrConfidence: 90,
    },
    createdAt: new Date('2025-12-20'),
    updatedAt: new Date('2025-12-20'),
    deletedAt: new Date('2025-12-27'),
  },
];

// Helper functions for mock data operations
export function getCourseById(id: string): Course | undefined {
  return courses.find(c => c.id === id);
}

export function getDocumentById(id: string): Document | undefined {
  return documents.find(d => d.id === id);
}

export function getDocumentsByCourseId(courseId: string): Document[] {
  return documents.filter(d => d.courseId === courseId && d.status !== 'trash');
}

export function getActiveCourses(): Course[] {
  return courses.filter(c => c.status === 'active');
}

export function getTrashedItems(): { courses: Course[]; documents: Document[] } {
  return {
    courses: courses.filter(c => c.status === 'trash'),
    documents: documents.filter(d => d.status === 'trash'),
  };
}
