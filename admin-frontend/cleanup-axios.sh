#!/bin/bash

# 清理所有文件中的手动token获取和headers传递

cd src

# 1. 移除 const token = localStorage.getItem('admin_access_token')
find . -name "*.tsx" -o -name "*.ts" | while read file; do
  # 检查文件中是否包含该行
  if grep -q "const token = localStorage.getItem('admin_access_token')" "$file"; then
    # 删除该行
    sed -i "/const token = localStorage.getItem('admin_access_token')/d" "$file"
    echo "Removed token line from $file"
  fi
done

# 2. 移除axios请求中的headers参数
# 这个比较复杂,需要处理多行
# 将会处理类似这样的模式:
# const response = await axios.get('/api/v1/admin/stats/overview', {
#   headers: { Authorization: `Bearer ${token}` },
# })
# 变成:
# const response = await axios.get('/api/v1/admin/stats/overview')

echo "清理完成!"
