/**
 * Scheduling Service Tests
 * 调度服务测试 - 最复杂的服务，包含30+方法
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from '@/utils/axios'
import { schedulingService } from '../scheduling'
import type {
  ScheduledVideo,
  ScheduledVideosResponse,
  ScheduleCreate,
  ScheduleUpdate,
  SchedulingStats,
  CalendarData,
  SuggestedTime,
  ScheduleHistory,
  CronValidation,
  CronPatternsResponse,
} from '../scheduling'

// Mock axios module
vi.mock('@/utils/axios')

describe('Scheduling Service', () => {
  const mockAxios = vi.mocked(axios)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Mock data
  const mockScheduledVideo: ScheduledVideo = {
    id: 1,
    content_id: 100,
    content_type: 'video',
    title: 'Test Scheduled Video',
    description: 'Test description',
    status: 'pending',
    scheduled_time: '2024-12-01T10:00:00Z',
    actual_publish_time: null,
    end_time: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    auto_publish: true,
    auto_expire: false,
    notify_subscribers: true,
    priority: 5,
    recurrence: 'none',
    publish_strategy: 'immediate',
    tags: ['test', 'scheduled'],
    is_overdue: false,
    is_due: false,
  }

  describe('getScheduledVideos', () => {
    it('should fetch scheduled videos with default parameters', async () => {
      const mockResponse: ScheduledVideosResponse = {
        items: [mockScheduledVideo],
        total: 1,
        skip: 0,
        limit: 20,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      const result = await schedulingService.getScheduledVideos()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/', {
        params: expect.objectContaining({
          content_type: 'video',
          skip: 0,
          limit: 20,
        }),
      })
      expect(result.items).toHaveLength(1)
    })

    it('should fetch with custom filters', async () => {
      const mockResponse: ScheduledVideosResponse = {
        items: [],
        total: 0,
        skip: 0,
        limit: 10,
      }

      mockAxios.get.mockResolvedValue({ data: mockResponse })

      await schedulingService.getScheduledVideos({
        status: 'published',
        content_type: 'video',
        skip: 10,
        limit: 10,
        search: 'test',
        sort_by: 'scheduled_time',
        sort_order: 'asc',
      })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/', {
        params: expect.objectContaining({
          status: 'published',
          search: 'test',
          sort_order: 'asc',
        }),
      })
    })

    it('should filter by status', async () => {
      const statuses: Array<'pending' | 'published' | 'cancelled' | 'failed' | 'expired'> = [
        'pending',
        'published',
        'cancelled',
        'failed',
        'expired',
      ]

      for (const status of statuses) {
        mockAxios.get.mockResolvedValue({ data: { items: [], total: 0, skip: 0, limit: 20 } })
        await schedulingService.getScheduledVideos({ status })
        expect(mockAxios.get).toHaveBeenLastCalledWith(
          '/api/v1/admin/scheduling/',
          expect.objectContaining({
            params: expect.objectContaining({ status }),
          })
        )
      }
    })

    it('should handle date range filtering', async () => {
      mockAxios.get.mockResolvedValue({ data: { items: [], total: 0, skip: 0, limit: 20 } })

      await schedulingService.getScheduledVideos({
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      })

      expect(mockAxios.get).toHaveBeenCalledWith(
        '/api/v1/admin/scheduling/',
        expect.objectContaining({
          params: expect.objectContaining({
            start_date: '2024-01-01',
            end_date: '2024-12-31',
          }),
        })
      )
    })
  })

  describe('createSchedule', () => {
    it('should create a new schedule', async () => {
      const createData: ScheduleCreate = {
        content_type: 'video',
        content_id: 100,
        scheduled_time: '2024-12-01T10:00:00Z',
        auto_publish: true,
        notify_subscribers: true,
        priority: 5,
      }

      mockAxios.post.mockResolvedValue({ data: mockScheduledVideo })

      const result = await schedulingService.createSchedule(createData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/', createData)
      expect(result.id).toBe(1)
      expect(result.status).toBe('pending')
    })

    it('should create schedule with recurrence', async () => {
      const createData: ScheduleCreate = {
        content_type: 'video',
        content_id: 100,
        scheduled_time: '2024-12-01T10:00:00Z',
        recurrence: '0 10 * * *', // Daily at 10:00
        recurrence_config: { type: 'daily' },
      }

      mockAxios.post.mockResolvedValue({ data: mockScheduledVideo })

      await schedulingService.createSchedule(createData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/', createData)
    })

    it('should create schedule with publish strategy', async () => {
      const createData: ScheduleCreate = {
        content_type: 'video',
        content_id: 100,
        scheduled_time: '2024-12-01T10:00:00Z',
        publish_strategy: 'gradual',
        strategy_config: { duration: 3600 },
      }

      mockAxios.post.mockResolvedValue({ data: mockScheduledVideo })

      await schedulingService.createSchedule(createData)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/', createData)
    })
  })

  describe('scheduleVideo (legacy)', () => {
    it('should schedule video using legacy format', async () => {
      mockAxios.post.mockResolvedValue({ data: mockScheduledVideo })

      const result = await schedulingService.scheduleVideo({
        video_id: 100,
        scheduled_publish_at: '2024-12-01T10:00:00Z',
        auto_publish: true,
        notify_subscribers: false,
      })

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/', {
        content_type: 'video',
        content_id: 100,
        scheduled_time: '2024-12-01T10:00:00Z',
        auto_publish: true,
        notify_subscribers: false,
      })
      expect(result.id).toBe(1)
    })
  })

  describe('updateSchedule', () => {
    it('should update schedule', async () => {
      const updateData: ScheduleUpdate = {
        scheduled_time: '2024-12-02T10:00:00Z',
        priority: 10,
        notify_subscribers: false,
      }

      mockAxios.put.mockResolvedValue({ data: { ...mockScheduledVideo, ...updateData } })

      const result = await schedulingService.updateSchedule(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/scheduling/1', updateData)
      expect(result.priority).toBe(10)
    })

    it('should update tags', async () => {
      const updateData: ScheduleUpdate = {
        tags: ['updated', 'new-tag'],
      }

      mockAxios.put.mockResolvedValue({ data: mockScheduledVideo })

      await schedulingService.updateSchedule(1, updateData)

      expect(mockAxios.put).toHaveBeenCalledWith('/api/v1/admin/scheduling/1', updateData)
    })
  })

  describe('cancelSchedule', () => {
    it('should cancel schedule without reason', async () => {
      mockAxios.delete.mockResolvedValue({ data: { message: 'Schedule cancelled' } })

      await schedulingService.cancelSchedule(1)

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/scheduling/1', {
        params: { reason: undefined },
      })
    })

    it('should cancel schedule with reason', async () => {
      mockAxios.delete.mockResolvedValue({ data: { message: 'Schedule cancelled' } })

      await schedulingService.cancelSchedule(1, 'Content updated')

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/scheduling/1', {
        params: { reason: 'Content updated' },
      })
    })
  })

  describe('batchCancelSchedules', () => {
    it('should batch cancel schedules', async () => {
      mockAxios.delete.mockResolvedValue({
        data: { message: 'Cancelled 3 schedules', count: 3 },
      })

      const result = await schedulingService.batchCancelSchedules([1, 2, 3])

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/scheduling/batch/cancel', {
        params: { schedule_ids: [1, 2, 3], reason: undefined },
      })
      expect(result.count).toBe(3)
    })

    it('should batch cancel with reason', async () => {
      mockAxios.delete.mockResolvedValue({ data: { count: 2 } })

      await schedulingService.batchCancelSchedules([1, 2], 'Bulk update')

      expect(mockAxios.delete).toHaveBeenCalledWith('/api/v1/admin/scheduling/batch/cancel', {
        params: { schedule_ids: [1, 2], reason: 'Bulk update' },
      })
    })
  })

  describe('executeSchedule', () => {
    it('should execute schedule normally', async () => {
      mockAxios.post.mockResolvedValue({
        data: { success: true, message: 'Schedule executed' },
      })

      const result = await schedulingService.executeSchedule(1)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/1/execute', {
        force: false,
      })
      expect(result.success).toBe(true)
    })

    it('should force execute schedule', async () => {
      mockAxios.post.mockResolvedValue({ data: { success: true } })

      await schedulingService.executeSchedule(1, true)

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/1/execute', {
        force: true,
      })
    })
  })

  describe('publishScheduledVideos', () => {
    it('should execute all due schedules', async () => {
      mockAxios.post.mockResolvedValue({
        data: { executed: 5, failed: 0, message: 'Executed 5 schedules' },
      })

      const result = await schedulingService.publishScheduledVideos()

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/execute-due')
      expect(result.executed).toBe(5)
    })
  })

  describe('getStats', () => {
    it('should fetch scheduling statistics', async () => {
      const mockStats: SchedulingStats = {
        pending_count: 10,
        published_today: 5,
        published_this_week: 20,
        failed_count: 2,
        overdue_count: 1,
        upcoming_24h: 8,
        by_content_type: { video: 10 },
        by_status: { pending: 10, published: 20 },
        by_strategy: { immediate: 15, gradual: 15 },
      }

      mockAxios.get.mockResolvedValue({ data: mockStats })

      const result = await schedulingService.getStats()

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/stats')
      expect(result.pending_count).toBe(10)
      expect(result.upcoming_24h).toBe(8)
    })
  })

  describe('getCalendarData', () => {
    it('should fetch calendar data for specific month', async () => {
      const mockCalendar: CalendarData = {
        events: [
          {
            id: 1,
            title: 'Test Event',
            content_type: 'video',
            scheduled_time: '2024-12-15T10:00:00Z',
            end_time: null,
            status: 'pending',
            priority: 5,
            color: 'blue',
          },
        ],
        month: 12,
        year: 2024,
      }

      mockAxios.get.mockResolvedValue({ data: mockCalendar })

      const result = await schedulingService.getCalendarData({ year: 2024, month: 12 })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/calendar', {
        params: { year: 2024, month: 12 },
      })
      expect(result.events).toHaveLength(1)
      expect(result.year).toBe(2024)
    })
  })

  describe('getSuggestedTimes', () => {
    it('should get suggested publishing times', async () => {
      const mockSuggested: SuggestedTime = {
        recommended_times: [
          { hour: 10, score: 95, reason: 'High user activity' },
          { hour: 14, score: 85, reason: 'Peak engagement' },
        ],
        content_type: 'video',
        based_on: 'historical_data',
      }

      mockAxios.get.mockResolvedValue({ data: mockSuggested })

      const result = await schedulingService.getSuggestedTimes('video')

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/suggest-time', {
        params: { content_type: 'video' },
      })
      expect(result.recommended_times).toHaveLength(2)
    })
  })

  describe('getScheduleHistory', () => {
    it('should fetch schedule history', async () => {
      const mockHistory: ScheduleHistory[] = [
        {
          id: 1,
          schedule_id: 1,
          action: 'executed',
          status_before: 'pending',
          status_after: 'published',
          success: true,
          message: 'Successfully published',
          details: {},
          executed_at: '2024-01-02T00:00:00Z',
          executed_by: 1,
          is_automatic: true,
          execution_time_ms: 1500,
        },
      ]

      mockAxios.get.mockResolvedValue({ data: mockHistory })

      const result = await schedulingService.getScheduleHistory(1, 0, 50)

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/1/history', {
        params: { skip: 0, limit: 50 },
      })
      expect(result).toHaveLength(1)
      expect(result[0].action).toBe('executed')
    })
  })

  describe('getAllHistories', () => {
    it('should fetch all histories with filters', async () => {
      mockAxios.get.mockResolvedValue({ data: [] })

      await schedulingService.getAllHistories({
        skip: 0,
        limit: 100,
        action: 'executed',
        content_type: 'video',
        start_date: '2024-01-01',
        end_date: '2024-12-31',
      })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/history', {
        params: expect.objectContaining({
          action: 'executed',
          content_type: 'video',
        }),
      })
    })
  })

  describe('getTemplates', () => {
    it('should fetch schedule templates', async () => {
      const mockTemplates = [
        {
          id: 1,
          name: 'Daily Upload',
          is_active: true,
          content_type: 'video',
        },
      ]

      mockAxios.get.mockResolvedValue({ data: mockTemplates })

      const result = await schedulingService.getTemplates({ is_active: true })

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/templates', {
        params: { is_active: true },
      })
      expect(result).toHaveLength(1)
    })
  })

  describe('applyTemplate', () => {
    it('should apply template to create schedule', async () => {
      mockAxios.post.mockResolvedValue({ data: mockScheduledVideo })

      const result = await schedulingService.applyTemplate(1, {
        content_type: 'video',
        content_id: 100,
        scheduled_time: '2024-12-01T10:00:00Z',
        override_priority: 8,
      })

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/templates/1/apply', {
        content_type: 'video',
        content_id: 100,
        scheduled_time: '2024-12-01T10:00:00Z',
        override_priority: 8,
      })
      expect(result.id).toBe(1)
    })
  })

  describe('Cron Expression Tools', () => {
    describe('validateCron', () => {
      it('should validate correct cron expression', async () => {
        const mockValidation: CronValidation = {
          valid: true,
          description: 'Every day at 10:00 AM',
          next_occurrences: [
            '2024-12-01T10:00:00Z',
            '2024-12-02T10:00:00Z',
            '2024-12-03T10:00:00Z',
          ],
        }

        mockAxios.post.mockResolvedValue({ data: mockValidation })

        const result = await schedulingService.validateCron('0 10 * * *')

        expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/cron/validate', {
          expression: '0 10 * * *',
        })
        expect(result.valid).toBe(true)
        expect(result.next_occurrences).toHaveLength(3)
      })

      it('should handle invalid cron expression', async () => {
        const mockValidation: CronValidation = {
          valid: false,
          error_message: 'Invalid cron expression',
          description: '',
          next_occurrences: [],
        }

        mockAxios.post.mockResolvedValue({ data: mockValidation })

        const result = await schedulingService.validateCron('invalid')

        expect(result.valid).toBe(false)
        expect(result.error_message).toBeDefined()
      })
    })

    describe('getCronPatterns', () => {
      it('should fetch predefined cron patterns', async () => {
        const mockPatterns: CronPatternsResponse = {
          patterns: [
            {
              name: 'Daily at 10:00 AM',
              expression: '0 10 * * *',
              description: 'Runs every day at 10:00 AM',
              category: 'daily',
            },
            {
              name: 'Every Monday',
              expression: '0 0 * * 1',
              description: 'Runs every Monday at midnight',
              category: 'weekly',
            },
          ],
          categories: ['daily', 'weekly', 'monthly'],
        }

        mockAxios.get.mockResolvedValue({ data: mockPatterns })

        const result = await schedulingService.getCronPatterns()

        expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/scheduling/cron/patterns')
        expect(result.patterns).toHaveLength(2)
        expect(result.categories).toContain('daily')
      })
    })

    describe('getCronNextRuns', () => {
      it('should calculate next run times', async () => {
        const mockNextRuns = {
          expression: '0 10 * * *',
          description: 'Daily at 10:00 AM',
          next_runs: [
            '2024-12-01T10:00:00Z',
            '2024-12-02T10:00:00Z',
            '2024-12-03T10:00:00Z',
          ],
        }

        mockAxios.post.mockResolvedValue({ data: mockNextRuns })

        const result = await schedulingService.getCronNextRuns('0 10 * * *', 3)

        expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/cron/next-runs', {
          expression: '0 10 * * *',
          count: 3,
          from_time: undefined,
        })
        expect(result.next_runs).toHaveLength(3)
      })

      it('should calculate from specific time', async () => {
        mockAxios.post.mockResolvedValue({
          data: { expression: '0 10 * * *', description: '', next_runs: [] },
        })

        await schedulingService.getCronNextRuns('0 10 * * *', 5, '2024-12-01T00:00:00Z')

        expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/scheduling/cron/next-runs', {
          expression: '0 10 * * *',
          count: 5,
          from_time: '2024-12-01T00:00:00Z',
        })
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network error'))
      await expect(schedulingService.getScheduledVideos()).rejects.toThrow('Network error')
    })

    it('should handle 404 errors', async () => {
      mockAxios.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Schedule not found' } },
      })
      await expect(schedulingService.getStats()).rejects.toMatchObject({
        response: { status: 404 },
      })
    })

    it('should handle validation errors', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 422, data: { detail: 'Invalid schedule time' } },
      })
      await expect(
        schedulingService.createSchedule({
          content_type: 'video',
          content_id: 1,
          scheduled_time: 'invalid',
        })
      ).rejects.toMatchObject({
        response: { status: 422 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty schedule list', async () => {
      mockAxios.get.mockResolvedValue({
        data: { items: [], total: 0, skip: 0, limit: 20 },
      })

      const result = await schedulingService.getScheduledVideos()
      expect(result.items).toHaveLength(0)
    })

    it('should handle large schedule IDs', async () => {
      const largeId = 999999999
      mockAxios.post.mockResolvedValue({ data: { success: true } })

      await schedulingService.executeSchedule(largeId)

      expect(mockAxios.post).toHaveBeenCalledWith(
        `/api/v1/admin/scheduling/${largeId}/execute`,
        expect.any(Object)
      )
    })

    it('should handle empty batch cancel', async () => {
      mockAxios.delete.mockResolvedValue({ data: { count: 0 } })

      const result = await schedulingService.batchCancelSchedules([])
      expect(result.count).toBe(0)
    })

    it('should handle past scheduled times', async () => {
      const pastTime = '2020-01-01T00:00:00Z'
      mockAxios.post.mockResolvedValue({ data: mockScheduledVideo })

      await schedulingService.createSchedule({
        content_type: 'video',
        content_id: 1,
        scheduled_time: pastTime,
      })

      expect(mockAxios.post).toHaveBeenCalled()
    })
  })
})
