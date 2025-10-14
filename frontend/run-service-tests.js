#!/usr/bin/env node

/**
 * 服务测试运行脚本
 * 方便快速运行特定类型的服务测试
 */

const { spawn } = require('child_process')
const path = require('path')

const testGroups = {
  core: [
    'api.test.ts',
    'videoService.test.ts', 
    'userService.test.ts',
    'commentService.test.ts',
    'favoriteService.test.ts',
    'historyService.test.ts',
    'ratingService.test.ts'
  ],
  content: [
    'actorService.test.ts',
    'directorService.test.ts', 
    'seriesService.test.ts',
    'danmakuService.test.ts'
  ],
  features: [
    'notificationService.test.ts',
    'oauthService.test.ts',
    'shareService.test.ts', 
    'downloadService.test.ts'
  ],
  helpers: [
    'searchHistoryService.test.ts',
    'recommendationService.test.ts',
    'subtitleService.test.ts',
    'watchlistService.test.ts'
  ],
  data: [
    'dataService.test.ts',
    'favoriteFolderService.test.ts',
    'sharedWatchlistService.test.ts'
  ]
}

function runTests(files, groupName) {
  console.log(`\n🧪 Running ${groupName} service tests...\n`)
  
  const testPaths = files.map(f => `src/services/__tests__/${f}`).join(' ')
  const cmd = `pnpm vitest run ${testPaths}`
  
  console.log(`Command: ${cmd}\n`)
  
  const child = spawn('pnpm', ['vitest', 'run', ...files.map(f => `src/services/__tests__/${f}`)], {
    stdio: 'inherit',
    shell: true
  })
  
  child.on('close', (code) => {
    if (code === 0) {
      console.log(`\n✅ ${groupName} tests completed successfully!`)
    } else {
      console.log(`\n❌ ${groupName} tests failed with exit code ${code}`)
    }
  })
}

function showHelp() {
  console.log(`
🧪 Service Test Runner

Usage: node run-service-tests.js [group]

Available test groups:
  core      - Core business services (7 files)
  content   - Content-related services (4 files) 
  features  - Feature services (4 files)
  helpers   - Helper services (4 files)
  data      - Data services (3 files)
  all       - Run all service tests
  
Examples:
  node run-service-tests.js core      # Run core service tests
  node run-service-tests.js features  # Run feature service tests
  node run-service-tests.js all       # Run all service tests
  node run-service-tests.js           # Show this help
`)
}

const group = process.argv[2]

if (!group) {
  showHelp()
  process.exit(0)
}

if (group === 'all') {
  const allFiles = Object.values(testGroups).flat()
  runTests(allFiles, 'ALL')
} else if (testGroups[group]) {
  runTests(testGroups[group], group.toUpperCase())
} else {
  console.log(`❌ Unknown test group: ${group}`)
  showHelp()
  process.exit(1)
}
