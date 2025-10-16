/**
 * IP Blacklist Service Tests
 * IP黑名单服务测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import api from '@/utils/axios'
import ipBlacklistService from '../ipBlacklistService'

vi.mock('@/utils/axios')

describe('IP Blacklist Service', () => {
  const mockApi = vi.mocked(api)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockBlacklistItem = {
    ip: '192.168.1.100',
    reason: 'Spam activity',
    banned_at: '2024-01-01T00:00:00Z',
    expires_at: '2024-12-31T23:59:59Z',
    is_permanent: false,
  }

  describe('getList', () => {
    it('should fetch blacklist with default parameters', async () => {
      mockApi.get.mockResolvedValue({
        data: { total: 1, items: [mockBlacklistItem] },
      })

      const result = await ipBlacklistService.getList({})

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/', { params: {} })
      expect(result.items).toHaveLength(1)
      expect(result.items[0].ip).toBe('192.168.1.100')
    })

    it('should fetch with pagination', async () => {
      mockApi.get.mockResolvedValue({ data: { total: 0, items: [] } })

      await ipBlacklistService.getList({ page: 2, page_size: 50 })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/', {
        params: { page: 2, page_size: 50 },
      })
    })

    it('should search IPs', async () => {
      mockApi.get.mockResolvedValue({ data: { total: 1, items: [mockBlacklistItem] } })

      await ipBlacklistService.getList({ search: '192.168' })

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/', { params: { search: '192.168' } })
    })
  })

  describe('getStats', () => {
    it('should fetch blacklist statistics', async () => {
      const mockStats = {
        total_blacklisted: 100,
        permanent_count: 30,
        temporary_count: 70,
        auto_banned_count: 20,
      }

      mockApi.get.mockResolvedValue({ data: mockStats })

      const result = await ipBlacklistService.getStats()

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/stats/summary')
      expect(result.total_blacklisted).toBe(100)
      expect(result.permanent_count).toBe(30)
    })
  })

  describe('add', () => {
    it('should add IP to blacklist permanently', async () => {
      mockApi.post.mockResolvedValue({
        data: { ...mockBlacklistItem, is_permanent: true, expires_at: undefined },
      })

      const result = await ipBlacklistService.add({
        ip: '10.0.0.1',
        reason: 'Malicious activity',
      })

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/', {
        ip: '10.0.0.1',
        reason: 'Malicious activity',
      })
      expect(result.is_permanent).toBe(true)
    })

    it('should add IP with expiration', async () => {
      mockApi.post.mockResolvedValue({ data: mockBlacklistItem })

      await ipBlacklistService.add({
        ip: '10.0.0.2',
        reason: 'Temporary ban',
        duration: 86400, // 24 hours
      })

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/', {
        ip: '10.0.0.2',
        reason: 'Temporary ban',
        duration: 86400,
      })
    })

    it('should handle invalid IP format', async () => {
      mockApi.post.mockRejectedValue({ response: { status: 422, data: { detail: 'Invalid IP address' } } })

      await expect(
        ipBlacklistService.add({
          ip: 'invalid-ip',
          reason: 'Test',
        })
      ).rejects.toMatchObject({ response: { status: 422 } })
    })
  })

  describe('remove', () => {
    it('should remove IP from blacklist', async () => {
      mockApi.delete.mockResolvedValue({ data: { message: 'IP removed' } })

      await ipBlacklistService.remove('192.168.1.100')

      expect(mockApi.delete).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/192.168.1.100')
    })

    it('should handle non-existent IP', async () => {
      mockApi.delete.mockRejectedValue({ response: { status: 404 } })

      await expect(ipBlacklistService.remove('10.0.0.999')).rejects.toMatchObject({ response: { status: 404 } })
    })
  })

  describe('batchRemove', () => {
    it('should batch remove IPs', async () => {
      mockApi.post.mockResolvedValue({
        data: { message: 'Removed 3 IPs', count: 3 },
      })

      const result = await ipBlacklistService.batchRemove(['192.168.1.1', '192.168.1.2', '192.168.1.3'])

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/batch-remove', [
        '192.168.1.1',
        '192.168.1.2',
        '192.168.1.3',
      ])
      expect(result.count).toBe(3)
    })

    it('should handle empty batch', async () => {
      mockApi.post.mockResolvedValue({ data: { count: 0 } })

      const result = await ipBlacklistService.batchRemove([])

      expect(result.count).toBe(0)
    })
  })

  describe('checkIP', () => {
    it('should check if IP is blacklisted', async () => {
      mockApi.get.mockResolvedValue({ data: mockBlacklistItem })

      const result = await ipBlacklistService.checkIP('192.168.1.100')

      expect(mockApi.get).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/192.168.1.100')
      expect(result.ip).toBe('192.168.1.100')
    })

    it('should handle non-blacklisted IP', async () => {
      mockApi.get.mockRejectedValue({ response: { status: 404 } })

      await expect(ipBlacklistService.checkIP('1.1.1.1')).rejects.toMatchObject({ response: { status: 404 } })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'))

      await expect(ipBlacklistService.getList({})).rejects.toThrow('Network error')
    })

    it('should handle 401 unauthorized', async () => {
      mockApi.get.mockRejectedValue({ response: { status: 401 } })

      await expect(ipBlacklistService.getStats()).rejects.toMatchObject({ response: { status: 401 } })
    })

    it('should handle 500 server errors', async () => {
      mockApi.post.mockRejectedValue({ response: { status: 500 } })

      await expect(ipBlacklistService.add({ ip: '1.1.1.1', reason: 'test' })).rejects.toMatchObject({
        response: { status: 500 },
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle IPv6 addresses', async () => {
      mockApi.post.mockResolvedValue({
        data: { ...mockBlacklistItem, ip: '2001:0db8:85a3::8a2e:0370:7334' },
      })

      const result = await ipBlacklistService.add({
        ip: '2001:0db8:85a3::8a2e:0370:7334',
        reason: 'IPv6 ban',
      })

      expect(result.ip).toContain('2001')
    })

    it('should handle CIDR notation', async () => {
      mockApi.post.mockResolvedValue({
        data: { ...mockBlacklistItem, ip: '192.168.1.0/24' },
      })

      await ipBlacklistService.add({
        ip: '192.168.1.0/24',
        reason: 'Network ban',
      })

      expect(mockApi.post).toHaveBeenCalled()
    })

    it('should handle very long reasons', async () => {
      const longReason = 'A'.repeat(1000)
      mockApi.post.mockResolvedValue({ data: mockBlacklistItem })

      await ipBlacklistService.add({
        ip: '1.2.3.4',
        reason: longReason,
      })

      expect(mockApi.post).toHaveBeenCalledWith('/api/v1/admin/ip-blacklist/', {
        ip: '1.2.3.4',
        reason: longReason,
      })
    })

    it('should handle large batch operations', async () => {
      const manyIPs = Array.from({ length: 1000 }, (_, i) => `192.168.${Math.floor(i / 256)}.${i % 256}`)

      mockApi.post.mockResolvedValue({ data: { count: 1000 } })

      const result = await ipBlacklistService.batchRemove(manyIPs)

      expect(result.count).toBe(1000)
    })
  })
})
