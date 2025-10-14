/**
 * 通用表格排序Hook
 * 用于在Ant Design Table中实现后端排序功能
 */

import { useState } from 'react';
import { SorterResult } from 'antd/es/table/interface';

export interface SortConfig {
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

export interface UseTableSortOptions {
  defaultSortBy?: string;
  defaultSortOrder?: 'asc' | 'desc';
}

export interface UseTableSortReturn {
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  handleTableChange: (sorter: SorterResult<any> | SorterResult<any>[]) => void;
  getSortParams: () => { sort_by: string; sort_order: string };
  resetSort: () => void;
}

/**
 * 表格排序Hook
 *
 * @param options 配置选项
 * @returns 排序状态和操作方法
 *
 * @example
 * ```tsx
 * const { handleTableChange, getSortParams } = useTableSort({
 *   defaultSortBy: 'created_at',
 *   defaultSortOrder: 'desc'
 * });
 *
 * // 在API请求中使用
 * const { data } = useQuery({
 *   queryKey: ['videos', page, ...Object.values(getSortParams())],
 *   queryFn: () => axios.get('/api/videos', { params: { ...getSortParams() } })
 * });
 *
 * // 在Table中使用
 * <Table onChange={(_, __, sorter) => handleTableChange(sorter)} />
 * ```
 */
export function useTableSort(options: UseTableSortOptions = {}): UseTableSortReturn {
  const {
    defaultSortBy = 'created_at',
    defaultSortOrder = 'desc',
  } = options;

  const [sortBy, setSortBy] = useState<string>(defaultSortBy);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>(defaultSortOrder);

  /**
   * 处理表格排序变化
   */
  const handleTableChange = (sorter: SorterResult<any> | SorterResult<any>[]) => {
    // 处理多列排序（取第一列）
    const currentSorter = Array.isArray(sorter) ? sorter[0] : sorter;

    if (!currentSorter || !currentSorter.order) {
      // 取消排序 - 恢复默认
      setSortBy(defaultSortBy);
      setSortOrder(defaultSortOrder);
      return;
    }

    // 更新排序字段和顺序
    if (currentSorter.field) {
      const field = Array.isArray(currentSorter.field)
        ? currentSorter.field.join('.')
        : String(currentSorter.field);

      setSortBy(field);
    }

    // Ant Design 使用 'ascend' 和 'descend'，转换为 'asc' 和 'desc'
    setSortOrder(currentSorter.order === 'ascend' ? 'asc' : 'desc');
  };

  /**
   * 获取排序参数（用于API请求）
   */
  const getSortParams = () => ({
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  /**
   * 重置排序为默认值
   */
  const resetSort = () => {
    setSortBy(defaultSortBy);
    setSortOrder(defaultSortOrder);
  };

  return {
    sortBy,
    sortOrder,
    handleTableChange,
    getSortParams,
    resetSort,
  };
}
