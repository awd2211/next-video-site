/**
 * SearchInput - 带历史记录和建议的搜索输入框
 */

import React, { useState, useEffect, useRef } from 'react'
import { Input, Dropdown, List, Typography, Space, Button, Empty } from 'antd'
import {
  SearchOutlined,
  ClockCircleOutlined,
  CloseOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import {
  getSearchHistory,
  addSearchHistory,
  clearSearchHistory,
  removeSearchHistoryItem,
  getSearchSuggestions,
  type SearchHistoryItem,
} from '../utils/searchHistory'

const { Text } = Typography

interface SearchInputProps {
  value?: string
  onChange: (value: string) => void
  onSearch: (value: string) => void
  placeholder?: string
  style?: React.CSSProperties
}

const SearchInput: React.FC<SearchInputProps> = ({
  value = '',
  onChange,
  onSearch,
  placeholder = '搜索文件或文件夹...',
  style,
}) => {
  const [inputValue, setInputValue] = useState(value)
  const [dropdownVisible, setDropdownVisible] = useState(false)
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const inputRef = useRef<any>(null)

  // 加载搜索历史
  useEffect(() => {
    setSearchHistory(getSearchHistory())
  }, [dropdownVisible])

  // 根据输入更新建议
  useEffect(() => {
    if (inputValue.trim()) {
      setSuggestions(getSearchSuggestions(inputValue, 5))
    } else {
      setSuggestions([])
    }
  }, [inputValue])

  // 同步外部 value
  useEffect(() => {
    setInputValue(value)
  }, [value])

  // 处理输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInputValue(newValue)
    onChange(newValue)
  }

  // 处理搜索
  const handleSearch = (searchText: string) => {
    if (searchText.trim()) {
      addSearchHistory(searchText)
      onSearch(searchText)
      setDropdownVisible(false)
    } else {
      onSearch('')
    }
  }

  // 选择历史记录或建议
  const handleSelectItem = (text: string) => {
    setInputValue(text)
    onChange(text)
    handleSearch(text)
  }

  // 删除单条历史
  const handleRemoveItem = (text: string, e: React.MouseEvent) => {
    e.stopPropagation()
    removeSearchHistoryItem(text)
    setSearchHistory(getSearchHistory())
  }

  // 清空全部历史
  const handleClearAll = () => {
    clearSearchHistory()
    setSearchHistory([])
  }

  // 下拉内容
  const dropdownContent = (
    <div style={{ width: 300, maxHeight: 400, overflow: 'auto', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.15)' }}>
      {/* 搜索建议 */}
      {suggestions.length > 0 && (
        <div style={{ padding: '8px 16px 4px', borderBottom: '1px solid #f0f0f0' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            搜索建议
          </Text>
          <List
            size="small"
            dataSource={suggestions}
            renderItem={(item) => (
              <List.Item
                style={{
                  cursor: 'pointer',
                  padding: '8px 0',
                  borderBottom: 'none',
                }}
                onClick={() => handleSelectItem(item)}
              >
                <Space>
                  <SearchOutlined style={{ color: '#8c8c8c' }} />
                  <Text>{item}</Text>
                </Space>
              </List.Item>
            )}
          />
        </div>
      )}

      {/* 搜索历史 */}
      {searchHistory.length > 0 ? (
        <div style={{ padding: '8px 16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              搜索历史
            </Text>
            <Button
              type="text"
              size="small"
              icon={<DeleteOutlined />}
              onClick={handleClearAll}
              style={{ fontSize: 12 }}
            >
              清空
            </Button>
          </div>
          <List
            size="small"
            dataSource={searchHistory}
            renderItem={(item) => (
              <List.Item
                style={{
                  cursor: 'pointer',
                  padding: '8px 0',
                  borderBottom: 'none',
                }}
                onClick={() => handleSelectItem(item.text)}
                actions={[
                  <CloseOutlined
                    key="remove"
                    style={{ fontSize: 12, color: '#8c8c8c' }}
                    onClick={(e) => handleRemoveItem(item.text, e)}
                  />,
                ]}
              >
                <Space>
                  <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
                  <Text ellipsis style={{ maxWidth: 200 }}>
                    {item.text}
                  </Text>
                </Space>
              </List.Item>
            )}
          />
        </div>
      ) : (
        !suggestions.length && (
          <div style={{ padding: 32 }}>
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无搜索历史"
            />
          </div>
        )
      )}
    </div>
  )

  return (
    <Dropdown
      open={dropdownVisible}
      onOpenChange={setDropdownVisible}
      dropdownRender={() => dropdownContent}
      trigger={['click']}
      placement="bottomLeft"
    >
      <Input
        ref={inputRef}
        value={inputValue}
        onChange={handleInputChange}
        onPressEnter={() => handleSearch(inputValue)}
        placeholder={placeholder}
        prefix={<SearchOutlined />}
        allowClear
        onClear={() => {
          setInputValue('')
          onChange('')
          onSearch('')
        }}
        style={style}
      />
    </Dropdown>
  )
}

export default SearchInput
