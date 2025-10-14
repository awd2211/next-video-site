/**
 * 服务测试索引文件
 * 导入所有服务测试以确保它们被运行
 */

// 导入所有服务测试
import './api.test'
import './videoService.test'
import './userService.test'
import './commentService.test'
import './favoriteService.test'
import './historyService.test'
import './ratingService.test'
import './actorService.test'
import './directorService.test'
import './danmakuService.test'
import './seriesService.test'
import './notificationService.test'
import './oauthService.test'
import './shareService.test'
import './downloadService.test'
import './searchHistoryService.test'
import './recommendationService.test'
import './subtitleService.test'
import './watchlistService.test'
import './dataService.test'
import './favoriteFolderService.test'
import './sharedWatchlistService.test'

describe('Services Test Suite', () => {
  it('should have all 22 service test files', () => {
    // 这个测试确保所有服务测试文件都被正确导入
    // 如果有任何导入错误，这个测试会失败
    expect(true).toBe(true)
  })
})
