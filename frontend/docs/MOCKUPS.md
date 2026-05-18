# DocuLens Dashboard - Visual Mockups

## Desktop Layout (1440px)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  Header                                                                              │
│  ┌──────────────┐                                                    ┌─────────────┐│
│  │ 📷 DocuLens  │                                                    │  [Avatar]   ││
│  └──────────────┘                                                    │  John Doe ▼ ││
│                                                                       └─────────────┘│
└─────────────────────────────────────────────────────────────────────────────────────┘
┌───────────────────┬─────────────────────────────────────────────────────────────────┐
│                   │  Main Section                                                   │
│  Sidebar          │  ┌───────────────────────────────────────────────────────────┐  │
│  280px            │  │  [+ New doc]                          [🔍 Search docs...]  │  │
│                   │  └───────────────────────────────────────────────────────────┘  │
│ ┌───────────────┐ │                                                                 │
│ │ 📄 Docs       │ │  ┌─────────────────────────────────────────────────────────┐   │
│ │               │ │  │ Machine Learning Notes                    Oct 15, 2024  │   │
│ └───────────────┘ │  │ This is a machine learning course note about...         │   │
│                   │  │ Created 2 days ago • 1,234 words                    [⋮] │   │
│ ┌───────────────┐ │  └─────────────────────────────────────────────────────────┘   │
│ │ 🗑️  Trash     │ │                                                                 │
│ │               │ │  ┌─────────────────────────────────────────────────────────┐   │
│ └───────────────┘ │  │ Physics Chapter 5                         Oct 14, 2024  │   │
│                   │  │ Newton's laws of motion and their applications...       │   │
│                   │  │ Created 3 days ago • 856 words                      [⋮] │   │
│ ─────────────────  │  └─────────────────────────────────────────────────────────┘   │
│                   │                                                                 │
│ User Footer       │  ┌─────────────────────────────────────────────────────────┐   │
│ ┌───────────────┐ │  │ Chemistry Lab Report                      Oct 12, 2024  │   │
│ │ [👤]          │ │  │ Experimental results and analysis from today's lab...   │   │
│ │ John Doe      │ │  │ Created 5 days ago • 2,105 words                    [⋮] │   │
│ │ john@email    │ │  └─────────────────────────────────────────────────────────┘   │
│ └───────────────┘ │                                                                 │
│                   │                                                                 │
└───────────────────┴─────────────────────────────────────────────────────────────────┘
```

---

## Mobile Layout (375px)

### Main View (Sidebar Hidden)
```
┌─────────────────────────────────┐
│ ☰  DocuLens           [Avatar]  │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ [+ New doc]                     │
│                                 │
│ [🔍 Search documents...]        │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ ML Notes          Oct 15, 2024  │
│ This is a machine learning...   │
│ 2 days ago • 1,234 words    [⋮] │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ Physics Ch 5      Oct 14, 2024  │
│ Newton's laws of motion...      │
│ 3 days ago • 856 words      [⋮] │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ Chem Lab          Oct 12, 2024  │
│ Experimental results...         │
│ 5 days ago • 2,105 words    [⋮] │
└─────────────────────────────────┘
```

### Sidebar Open (Overlay)
```
┌─────────────────┬───────────────┐
│                 │ DocuLens  [X] │
│  Sidebar        ├───────────────┤
│  240px          │               │
│                 │  (Main faded) │
│ ┌─────────────┐ │               │
│ │ 📄 Docs     │ │               │
│ │             │ │               │
│ └─────────────┘ │               │
│                 │               │
│ ┌─────────────┐ │               │
│ │ 🗑️  Trash   │ │               │
│ │             │ │               │
│ └─────────────┘ │               │
│                 │               │
│ ─────────────── │               │
│                 │               │
│ ┌─────────────┐ │               │
│ │ [👤]        │ │               │
│ │ John Doe    │ │               │
│ │ john@email  │ │               │
│ └─────────────┘ │               │
└─────────────────┴───────────────┘
```

---

## Detailed Component Mockups

### Document Card - Normal State
```
┌────────────────────────────────────────────────────────────────────┐
│  Machine Learning Course Notes                        Oct 15, 2024 │
│                                                                [⋮] │
│  This is a machine learning course note about neural networks      │
│  and deep learning architectures including CNNs and RNNs...        │
│                                                                     │
│  📅 Created 2 days ago  •  📝 1,234 words  •  ✓ 95% confidence    │
└────────────────────────────────────────────────────────────────────┘
```

### Document Card - Hover State
```
┌────────────────────────────────────────────────────────────────────┐
│  Machine Learning Course Notes                        Oct 15, 2024 │
│                                                                [⋮] │
│  This is a machine learning course note about neural networks      │
│  and deep learning architectures including CNNs and RNNs...        │
│                                                                     │
│  📅 Created 2 days ago  •  📝 1,234 words  •  ✓ 95% confidence    │
│                                                                     │
│  ← Shadow elevation increases                                      │
└────────────────────────────────────────────────────────────────────┘
```

### Document Card - Trash View
```
┌────────────────────────────────────────────────────────────────────┐
│  🗑️  Machine Learning Course Notes                   Oct 15, 2024 │
│                                                                [⋮] │
│  This is a machine learning course note about neural networks      │
│  and deep learning architectures including CNNs and RNNs...        │
│                                                                     │
│  📅 Deleted 1 hour ago  •  📝 1,234 words                          │
│  ─────────────────────────────────────────────────────────────────  │
│  [↻ Restore]                                    [🗑️ Delete Forever] │
└────────────────────────────────────────────────────────────────────┘
```

### Action Menu Dropdown
```
Document Card                                           ┌───────────────┐
┌──────────────────────────────────────────┐           │ Open          │
│  Title                        Date   [⋮]─┼──────────▶│ Rename        │
│                                           │           │ Duplicate     │
│  Description...                           │           │ ─────────────  │
└──────────────────────────────────────────┘           │ Move to Trash │
                                                        └───────────────┘
```

---

## Empty States

### No Documents
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                          📄                                     │
│                                                                 │
│                    No documents yet                             │
│              Click "New doc" to create your                     │
│                    first note                                   │
│                                                                 │
│                   ┌────────────────┐                            │
│                   │  [+ New doc]   │                            │
│                   └────────────────┘                            │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Trash Empty
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                          🗑️                                     │
│                                                                 │
│                     Trash is empty                              │
│              Deleted documents will appear here                 │
│                                                                 │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Search No Results
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                          🔍                                     │
│                                                                 │
│                   No results found for                          │
│                    "quantum physics"                            │
│                                                                 │
│                Try a different search term                      │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Loading States

### Document List Loading
```
┌─────────────────────────────────────────────────────────────────┐
│  ████████████████                                               │
│  ████████████████████████████████████████                       │
│  ██████████████████                                             │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  ████████████████                                               │
│  ████████████████████████████████████████                       │
│  ██████████████████                                             │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  ████████████████                                               │
│  ████████████████████████████████████████                       │
│  ██████████████████                                             │
└─────────────────────────────────────────────────────────────────┘

← Shimmer animation from left to right
```

---

## Sidebar States

### Expanded (280px)
```
┌─────────────────────┐
│                     │
│  Navigation (80%)   │
│                     │
│  ┌────────────────┐ │
│  │ 📄  Docs       │ │
│  └────────────────┘ │
│                     │
│  ┌────────────────┐ │
│  │ 🗑️   Trash     │ │
│  └────────────────┘ │
│                     │
│                     │
│                     │
│  ─────────────────  │
│  Footer (20%)       │
│  ┌────────────────┐ │
│  │ [👤] John Doe  │ │
│  │      john@...  │ │
│  └────────────────┘ │
└─────────────────────┘
```

### Collapsed (80px)
```
┌──────┐
│      │
│ Nav  │
│      │
│ ┌──┐ │
│ │📄│ │
│ └──┘ │
│      │
│ ┌──┐ │
│ │🗑️│ │
│ └──┘ │
│      │
│      │
│      │
│ ──── │
│ Foot │
│ ┌──┐ │
│ │👤│ │
│ └──┘ │
└──────┘
```

---

## Header Variations

### Desktop Header
```
┌───────────────────────────────────────────────────────────────────────┐
│  ┌──────────────┐                                   ┌───────────────┐ │
│  │ 📷 DocuLens  │                                   │  [👤]         │ │
│  └──────────────┘                                   │  John Doe   ▼ │ │
│                                                      └───────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

### Mobile Header
```
┌────────────────────────────────────────────┐
│  ☰  📷 DocuLens                [👤]        │
└────────────────────────────────────────────┘
```

### User Dropdown Menu
```
Header                                      ┌──────────────────┐
┌────────────────────────────┐             │ John Doe         │
│  DocuLens         [👤] ▼  ─┼────────────▶│ john@email.com   │
└────────────────────────────┘             │ ──────────────── │
                                            │ Profile          │
                                            │ Settings         │
                                            │ ──────────────── │
                                            │ Sign Out         │
                                            └──────────────────┘
```

---

## Search Bar States

### Empty State
```
┌────────────────────────────────────────────┐
│  🔍  Search documents...                   │
└────────────────────────────────────────────┘
```

### Focused State
```
┌────────────────────────────────────────────┐
│  🔍  machine learning                   [X]│ ← Clear button appears
└────────────────────────────────────────────┘
    └─ Blue ring around border
```

### With Suggestions (Future)
```
┌────────────────────────────────────────────┐
│  🔍  machine                            [X]│
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│  📄 Machine Learning Course Notes          │
│  📄 ML Algorithms Overview                 │
│  📄 Machine Learning Project Ideas         │
└────────────────────────────────────────────┘
```

---

## Document View Page

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Header                                                                 │
│  📷 DocuLens  /  Docs  /  Machine Learning Notes            [👤] John  │
└─────────────────────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────────────────────────┐
│ Sidebar  │  Document View                                               │
│          │  ┌────────────────────────────────────────────────────────┐  │
│          │  │  Machine Learning Course Notes                         │  │
│          │  │  Created Oct 15, 2024 • Last edited 2 hours ago        │  │
│          │  │                                                         │  │
│          │  │  [✏️ Edit] [📥 Download] [🗑️ Delete] [↗️ Share]         │  │
│          │  └────────────────────────────────────────────────────────┘  │
│          │                                                               │
│          │  ┌────────────────────────────────────────────────────────┐  │
│          │  │  # Neural Networks                                     │  │
│          │  │                                                         │  │
│          │  │  Neural networks are a fundamental concept in...       │  │
│          │  │                                                         │  │
│          │  │  ## Architecture                                       │  │
│          │  │                                                         │  │
│          │  │  - Input layer                                         │  │
│          │  │  - Hidden layers                                       │  │
│          │  │  - Output layer                                        │  │
│          │  │                                                         │  │
│          │  │  ...                                                   │  │
│          │  └────────────────────────────────────────────────────────┘  │
└──────────┴──────────────────────────────────────────────────────────────┘
```

---

## Color Palette

```
Primary Blue:
████  #3b82f6  (buttons, links, active states)
████  #2563eb  (hover)
████  #eff6ff  (light background)

Grays:
████  #f9fafb  (backgrounds)
████  #e5e7eb  (borders)
████  #6b7280  (secondary text)
████  #111827  (primary text)

Semantic:
████  #10b981  (success - green)
████  #ef4444  (error/delete - red)
████  #f59e0b  (warning - yellow)
```

---

## Icon Reference

- 📷 Camera - App logo
- 📄 FileText - Documents
- 🗑️  Trash - Trash section
- 👤 User - User avatar
- 🔍 Search - Search functionality
- ➕ Plus - New document
- ⋮ MoreVertical - Actions menu
- ✏️ Edit - Edit action
- 📥 Download - Download action
- ↗️ Share - Share action
- ↻ Rotate - Restore action
- ✓ Check - Success/confirmation
- ✗ X - Close/delete
- ⚙️ Settings - Settings

---

**Last Updated**: 2025-01-17
**Design Status**: Proposal
