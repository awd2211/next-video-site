#!/bin/bash
# Quick fix for unused variables - prefix with underscore

# MyList.tsx
sed -i 's/const \[{ isDragging }, drag\]/const [{ isDragging: _isDragging }, drag]/' src/pages/MyList/index.tsx
sed -i 's/const formatDuration = (minutes: number)/const _formatDuration = (minutes: number)/' src/pages/MyList/index.tsx

# SharedList
sed -i "s/import { useState, useEffect } from 'react'/import { useState } from 'react'/" src/pages/SharedList/index.tsx

# Category
sed -i "s/import { useParams, Link } from 'react-router-dom'/import { useParams } from 'react-router-dom'/" src/pages/Category/index.tsx

# Components
sed -i 's/import VideoCardSkeleton from/import { VideoCardSkeleton as _VideoCardSkeleton } from/' src/components/VirtualVideoGrid/index.tsx 2>/dev/null || true

echo "✅ Fixed unused variables"
