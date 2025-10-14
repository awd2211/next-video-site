# Security Testing Guide

本文档提供全面的安全测试指南，用于验证所有已实施的安全措施。

## 目录

1. [XSS 防护测试](#xss-防护测试)
2. [输入验证测试](#输入验证测试)
3. [限流测试](#限流测试)
4. [CSP 测试](#csp-测试)
5. [文件上传安全测试](#文件上传安全测试)
6. [密码强度测试](#密码强度测试)
7. [URL 验证测试](#url-验证测试)

---

## XSS 防护测试

### 测试目标
验证所有用户输入都经过 HTML 清理，防止 XSS 攻击。

### 测试步骤

#### 1. 评论区 XSS 测试

```javascript
// 在浏览器控制台运行
// 测试脚本注入
const xssPayloads = [
  '<script>alert("XSS")</script>',
  '<img src=x onerror=alert("XSS")>',
  '<svg onload=alert("XSS")>',
  '<iframe src="javascript:alert(\'XSS\')">',
  '<body onload=alert("XSS")>',
  '<input onfocus=alert("XSS") autofocus>',
  'javascript:alert("XSS")',
  '<a href="javascript:alert(\'XSS\')">Click</a>',
]

// 逐个测试每个 payload
xssPayloads.forEach((payload, index) => {
  console.log(`测试 ${index + 1}: ${payload}`)
  // 在评论框中输入 payload 并提交
  // 预期结果：脚本被清理，不会执行
})
```

**预期结果:**
- 所有 `<script>` 标签被移除
- 事件处理器（如 `onerror`、`onload`）被移除
- `javascript:` 协议被移除
- 只保留安全的 HTML 标签（如 `<p>`、`<br>`、`<strong>`）

#### 2. 弹幕 XSS 测试

在弹幕输入框中测试相同的 XSS payloads。

**预期结果:**
- 所有 HTML 标签被完全移除
- 只显示纯文本内容

#### 3. 搜索框 XSS 测试

```javascript
// 测试搜索框
const searchPayloads = [
  '<script>alert(1)</script>',
  '"><script>alert(1)</script>',
  '%3Cscript%3Ealert(1)%3C/script%3E',
]

searchPayloads.forEach(payload => {
  // 在搜索框输入 payload
  // 检查 URL 和页面显示
  console.log(`测试搜索: ${payload}`)
})
```

**预期结果:**
- 搜索关键词被清理
- 不会触发脚本执行
- 特殊字符被正确编码

---

## 输入验证测试

### 测试目标
验证所有输入字段的长度限制、格式验证和字符过滤。

### 测试脚本

```javascript
// 评论长度测试
function testCommentLength() {
  const maxLength = 500

  // 测试正常长度
  const normalComment = 'A'.repeat(100)
  console.log('测试正常评论:', normalComment.length, '字符')

  // 测试最大长度
  const maxComment = 'A'.repeat(maxLength)
  console.log('测试最大长度评论:', maxComment.length, '字符')

  // 测试超出长度
  const tooLongComment = 'A'.repeat(maxLength + 1)
  console.log('测试超长评论:', tooLongComment.length, '字符 - 应该被拒绝')

  return { normalComment, maxComment, tooLongComment }
}

// 弹幕长度测试
function testDanmakuLength() {
  const maxLength = 100

  const normalDanmaku = 'A'.repeat(50)
  const maxDanmaku = 'A'.repeat(maxLength)
  const tooLongDanmaku = 'A'.repeat(maxLength + 1)

  console.log('弹幕测试:', {
    normal: normalDanmaku.length,
    max: maxDanmaku.length,
    tooLong: tooLongDanmaku.length
  })

  return { normalDanmaku, maxDanmaku, tooLongDanmaku }
}

// 用户名验证测试
function testUsernameValidation() {
  const testCases = [
    { username: 'user123', valid: true, desc: '正常用户名' },
    { username: 'ab', valid: false, desc: '太短（最少3个字符）' },
    { username: 'a'.repeat(51), valid: false, desc: '太长（最多50个字符）' },
    { username: 'user@123', valid: false, desc: '包含非法字符' },
    { username: 'user name', valid: false, desc: '包含空格' },
    { username: '<script>alert(1)</script>', valid: false, desc: 'XSS 攻击' },
  ]

  testCases.forEach(test => {
    console.log(`${test.desc}:`, test.username, '预期:', test.valid ? '✓' : '✗')
  })

  return testCases
}

// 执行所有测试
console.log('=== 输入验证测试 ===')
testCommentLength()
testDanmakuLength()
testUsernameValidation()
```

**预期结果:**
- 超出长度限制的输入被拒绝
- 字符计数器正确显示
- 提交按钮在超出限制时禁用

---

## 限流测试

### 测试目标
验证登录、评论、弹幕等操作的速率限制。

### 测试脚本

```javascript
// 登录限流测试
async function testLoginRateLimit() {
  console.log('=== 测试登录限流 ===')
  const maxAttempts = 5
  const waitTime = 5 * 60 * 1000 // 5分钟

  for (let i = 1; i <= maxAttempts + 2; i++) {
    console.log(`尝试 ${i}/${maxAttempts}`)
    // 尝试登录（使用错误的凭据）
    // 预期: 前5次允许，第6次被拒绝

    if (i > maxAttempts) {
      console.log('应该被限流，显示等待时间')
    }

    await new Promise(resolve => setTimeout(resolve, 500))
  }
}

// 评论限流测试
async function testCommentRateLimit() {
  console.log('=== 测试评论限流 ===')
  const maxAttempts = 10
  const windowMs = 60 * 1000 // 1分钟

  for (let i = 1; i <= maxAttempts + 2; i++) {
    console.log(`评论 ${i}/${maxAttempts}`)
    // 提交评论
    // 预期: 前10次允许，第11次被拒绝

    if (i > maxAttempts) {
      console.log('应该被限流')
    }

    await new Promise(resolve => setTimeout(resolve, 100))
  }
}

// 弹幕限流测试
async function testDanmakuRateLimit() {
  console.log('=== 测试弹幕限流 ===')
  const maxAttempts = 20
  const windowMs = 60 * 1000 // 1分钟

  for (let i = 1; i <= maxAttempts + 2; i++) {
    console.log(`弹幕 ${i}/${maxAttempts}`)
    // 发送弹幕
    // 预期: 前20条允许，第21条被拒绝

    if (i > maxAttempts) {
      console.log('应该被限流')
    }

    await new Promise(resolve => setTimeout(resolve, 50))
  }
}

// 限流重置测试
function testRateLimitReset() {
  console.log('=== 测试限流重置 ===')

  // 清除特定键的限流记录
  localStorage.removeItem('rate_limit_login')
  console.log('✓ 登录限流已重置')

  localStorage.removeItem('rate_limit_comment')
  console.log('✓ 评论限流已重置')

  localStorage.removeItem('rate_limit_danmaku')
  console.log('✓ 弹幕限流已重置')
}

// 查看当前限流状态
function checkRateLimitStatus() {
  console.log('=== 当前限流状态 ===')

  const keys = Object.keys(localStorage).filter(key => key.startsWith('rate_limit_'))

  keys.forEach(key => {
    const data = JSON.parse(localStorage.getItem(key) || '{}')
    console.log(`${key}:`, {
      attempts: data.attempts,
      resetTime: new Date(data.resetTime).toLocaleString(),
      blocked: data.attempts >= data.maxAttempts
    })
  })
}

// 运行测试
testLoginRateLimit()
testCommentRateLimit()
testDanmakuRateLimit()
checkRateLimitStatus()
```

**预期结果:**
- 超过限制后显示错误提示
- 显示剩余等待时间
- 时间窗口过后自动重置
- localStorage 中正确记录限流状态

---

## CSP 测试

### 测试目标
验证 Content Security Policy 正确配置并阻止不安全的资源加载。

### 测试步骤

#### 1. 检查 CSP 头部

```javascript
// 在浏览器控制台运行
const meta = document.querySelector('meta[http-equiv="Content-Security-Policy"]')
if (meta) {
  console.log('✓ CSP 已配置')
  console.log('CSP 策略:', meta.getAttribute('content'))
} else {
  console.log('✗ CSP 未配置')
}
```

#### 2. 测试内联脚本阻止

```javascript
// 尝试注入内联脚本（应该被 CSP 阻止）
const script = document.createElement('script')
script.textContent = 'console.log("内联脚本执行")'
document.body.appendChild(script)

// 预期: CSP 应该阻止执行并在控制台显示警告
```

#### 3. 测试外部资源加载

```javascript
// 测试从不允许的域加载资源
const img = document.createElement('img')
img.src = 'https://evil.com/malicious.jpg'
document.body.appendChild(img)

// 预期: 如果域名不在白名单中，应该被阻止
```

#### 4. 检查 CSP 违规报告

打开浏览器开发者工具 → Console，查看是否有 CSP 违规警告：

```
Content Security Policy: The page's settings blocked the loading of a resource...
```

**预期结果:**
- CSP meta 标签存在
- 不安全的内联脚本被阻止
- 只允许来自允许域的资源
- 控制台显示 CSP 违规警告

---

## 文件上传安全测试

### 测试目标
验证文件类型、大小、文件名的验证机制。

### 测试脚本

```javascript
// 文件验证测试
function testFileValidation() {
  console.log('=== 文件上传安全测试 ===')

  // 测试用例
  const testCases = [
    {
      name: '正常头像.jpg',
      size: 3 * 1024 * 1024, // 3MB
      type: 'image/jpeg',
      expected: 'valid',
      desc: '正常 JPEG 图片'
    },
    {
      name: '超大图片.jpg',
      size: 10 * 1024 * 1024, // 10MB
      type: 'image/jpeg',
      expected: 'invalid',
      desc: '超过5MB限制'
    },
    {
      name: '病毒.exe',
      size: 1 * 1024 * 1024,
      type: 'application/x-msdownload',
      expected: 'invalid',
      desc: '可执行文件'
    },
    {
      name: '脚本.php',
      size: 1024,
      type: 'application/x-php',
      expected: 'invalid',
      desc: 'PHP 脚本'
    },
    {
      name: '图片<script>.jpg',
      size: 1024 * 1024,
      type: 'image/jpeg',
      expected: 'sanitized',
      desc: '文件名包含特殊字符'
    },
    {
      name: '../../../etc/passwd',
      size: 1024,
      type: 'text/plain',
      expected: 'sanitized',
      desc: '路径遍历攻击'
    },
  ]

  testCases.forEach((test, index) => {
    console.log(`\n测试 ${index + 1}: ${test.desc}`)
    console.log('文件名:', test.name)
    console.log('大小:', test.size / 1024 / 1024, 'MB')
    console.log('类型:', test.type)
    console.log('预期结果:', test.expected)
  })
}

// 文件扩展名与 MIME 类型匹配测试
function testMimeTypeMismatch() {
  console.log('\n=== MIME 类型匹配测试 ===')

  const mismatchTests = [
    {
      name: 'image.jpg',
      type: 'text/plain',
      desc: 'JPEG 扩展名但类型为 text'
    },
    {
      name: 'video.mp4',
      type: 'image/jpeg',
      desc: 'MP4 扩展名但类型为 image'
    },
    {
      name: 'script.jpg',
      type: 'application/javascript',
      desc: 'JPG 扩展名但实际是脚本'
    },
  ]

  mismatchTests.forEach(test => {
    console.log(`\n${test.desc}:`)
    console.log('文件名:', test.name)
    console.log('MIME:', test.type)
    console.log('预期: 被拒绝')
  })
}

testFileValidation()
testMimeTypeMismatch()
```

### 手动测试步骤

1. **头像上传测试:**
   - 进入个人资料页面
   - 尝试上传各种文件类型
   - 验证只接受 JPG、PNG、WebP、GIF
   - 验证大小限制为 5MB

2. **视频上传测试（管理后台）:**
   - 进入视频管理页面
   - 尝试上传视频文件
   - 验证只接受 MP4、WebM、OGG 等视频格式
   - 验证大小限制为 2GB

3. **恶意文件名测试:**
   - 尝试上传包含特殊字符的文件（`<script>.jpg`）
   - 尝试路径遍历（`../../etc/passwd`）
   - 验证文件名被清理

**预期结果:**
- 只接受允许的文件类型
- 超过大小限制的文件被拒绝
- 文件名中的特殊字符被清理
- MIME 类型与扩展名不匹配时被拒绝

---

## 密码强度测试

### 测试目标
验证密码强度计算和要求。

### 测试脚本

```javascript
// 密码强度测试
function testPasswordStrength() {
  console.log('=== 密码强度测试 ===')

  const testPasswords = [
    { password: '12345678', expected: 'weak', desc: '纯数字' },
    { password: 'password', expected: 'weak', desc: '纯小写字母' },
    { password: 'Password', expected: 'weak', desc: '大小写字母' },
    { password: 'Password123', expected: 'medium', desc: '字母+数字' },
    { password: 'Pass123!', expected: 'medium', desc: '字母+数字+特殊字符（短）' },
    { password: 'Password123!', expected: 'strong', desc: '完整密码' },
    { password: 'MyP@ssw0rd2024!', expected: 'strong', desc: '强密码' },
  ]

  testPasswords.forEach(test => {
    console.log(`\n测试: ${test.desc}`)
    console.log('密码:', test.password)
    console.log('预期强度:', test.expected)

    // 在密码修改页面输入并查看强度指示器
  })
}

// 密码要求验证
function testPasswordRequirements() {
  console.log('\n=== 密码要求验证 ===')

  const requirements = [
    '✓ 最少 8 个字符',
    '✓ 包含大写字母',
    '✓ 包含小写字母',
    '✓ 包含数字',
    '✓ 包含特殊字符',
    '✓ 强度至少为 "中等"（40%）'
  ]

  console.log('密码必须满足以下条件:')
  requirements.forEach(req => console.log(req))
}

testPasswordStrength()
testPasswordRequirements()
```

**预期结果:**
- 弱密码（强度 < 40%）被拒绝
- 密码强度指示器正确显示（红/黄/绿）
- 实时反馈密码强度
- 提示用户改进密码

---

## URL 验证测试

### 测试目标
验证 URL 输入的格式验证和协议限制。

### 测试脚本

```javascript
// URL 验证测试
function testURLValidation() {
  console.log('=== URL 验证测试 ===')

  const testURLs = [
    { url: 'https://example.com/image.jpg', valid: true, desc: '正常 HTTPS URL' },
    { url: 'http://example.com/image.jpg', valid: true, desc: '正常 HTTP URL' },
    { url: 'javascript:alert(1)', valid: false, desc: 'JavaScript 协议' },
    { url: 'data:text/html,<script>alert(1)</script>', valid: false, desc: 'Data URL' },
    { url: 'file:///etc/passwd', valid: false, desc: 'File 协议' },
    { url: 'ftp://example.com/file', valid: false, desc: 'FTP 协议' },
    { url: '//example.com/image.jpg', valid: false, desc: '协议相对 URL' },
    { url: 'example.com/image.jpg', valid: false, desc: '缺少协议' },
    { url: '<script>alert(1)</script>', valid: false, desc: 'XSS 攻击' },
  ]

  testURLs.forEach(test => {
    console.log(`\n${test.desc}:`)
    console.log('URL:', test.url)
    console.log('预期:', test.valid ? '✓ 有效' : '✗ 无效')
  })
}

testURLValidation()
```

### 手动测试步骤

1. **头像 URL 测试:**
   - 进入个人资料编辑页面
   - 在头像 URL 字段测试各种 URL
   - 验证只接受 http:// 和 https://

2. **视频链接测试（管理后台）:**
   - 进入视频编辑页面
   - 测试各种 URL 格式
   - 验证所有 URL 字段都有正确验证

**预期结果:**
- 只接受 http:// 和 https:// 协议
- 拒绝 javascript:、data:、file:// 等危险协议
- 显示清晰的错误提示
- 无效 URL 无法提交

---

## 自动化测试脚本

创建一个完整的测试脚本用于自动化测试：

```javascript
// security-test-suite.js
// 在浏览器控制台运行完整的安全测试套件

(async function runSecurityTests() {
  console.log('╔══════════════════════════════════════╗')
  console.log('║   VideoSite 安全测试套件            ║')
  console.log('╚══════════════════════════════════════╝\n')

  const results = {
    passed: 0,
    failed: 0,
    warnings: 0
  }

  // 测试 1: CSP 配置
  console.log('📋 测试 1: CSP 配置检查')
  const cspMeta = document.querySelector('meta[http-equiv="Content-Security-Policy"]')
  if (cspMeta) {
    console.log('✓ CSP 已配置')
    results.passed++
  } else {
    console.log('✗ CSP 未配置')
    results.failed++
  }

  // 测试 2: XSS 防护工具
  console.log('\n📋 测试 2: XSS 防护工具检查')
  if (typeof DOMPurify !== 'undefined') {
    console.log('✓ DOMPurify 已加载')
    results.passed++
  } else {
    console.log('⚠ DOMPurify 未检测到')
    results.warnings++
  }

  // 测试 3: 限流机制
  console.log('\n📋 测试 3: 限流机制检查')
  const rateLimitKeys = Object.keys(localStorage).filter(k => k.startsWith('rate_limit_'))
  console.log(`发现 ${rateLimitKeys.length} 个限流配置`)
  if (rateLimitKeys.length > 0) {
    console.log('✓ 限流机制已激活')
    results.passed++
  } else {
    console.log('ℹ 限流机制未使用（可能尚未触发）')
  }

  // 测试 4: 安全头部
  console.log('\n📋 测试 4: 安全头部检查')
  const securityHeaders = [
    'X-Content-Type-Options',
    'X-Frame-Options',
  ]

  securityHeaders.forEach(header => {
    const meta = document.querySelector(`meta[http-equiv="${header}"]`)
    if (meta) {
      console.log(`✓ ${header}: ${meta.getAttribute('content')}`)
      results.passed++
    } else {
      console.log(`✗ ${header} 未配置`)
      results.failed++
    }
  })

  // 测试 5: 表单验证
  console.log('\n📋 测试 5: 表单验证检查')
  const inputs = document.querySelectorAll('input[maxlength], textarea[maxlength]')
  console.log(`发现 ${inputs.length} 个带长度限制的输入字段`)
  if (inputs.length > 0) {
    console.log('✓ 输入长度限制已应用')
    results.passed++
  } else {
    console.log('ℹ 当前页面无输入字段')
  }

  // 输出测试结果
  console.log('\n╔══════════════════════════════════════╗')
  console.log('║           测试结果摘要               ║')
  console.log('╚══════════════════════════════════════╝')
  console.log(`✓ 通过: ${results.passed}`)
  console.log(`✗ 失败: ${results.failed}`)
  console.log(`⚠ 警告: ${results.warnings}`)

  const total = results.passed + results.failed
  const percentage = total > 0 ? (results.passed / total * 100).toFixed(1) : 0
  console.log(`\n总体得分: ${percentage}%`)

  if (results.failed === 0) {
    console.log('\n🎉 所有测试通过！')
  } else {
    console.log('\n⚠️  发现问题，请检查失败的测试项')
  }
})()
```

---

## 测试检查清单

使用此检查清单确保所有安全功能已测试：

### XSS 防护
- [ ] 评论区 XSS 注入测试
- [ ] 弹幕 XSS 注入测试
- [ ] 搜索框 XSS 注入测试
- [ ] 用户资料 XSS 注入测试
- [ ] HTML 清理功能验证

### 输入验证
- [ ] 评论长度限制（500字符）
- [ ] 弹幕长度限制（100字符）
- [ ] 用户名格式验证
- [ ] 邮箱格式验证
- [ ] 字符计数器显示

### 限流机制
- [ ] 登录限流（5次/5分钟）
- [ ] 评论限流（10次/分钟）
- [ ] 弹幕限流（20次/分钟）
- [ ] 注册限流（3次/小时）
- [ ] 限流重置功能

### CSP 配置
- [ ] CSP meta 标签存在
- [ ] 内联脚本被阻止
- [ ] 外部资源白名单
- [ ] CSP 违规报告

### 文件上传
- [ ] 文件类型验证
- [ ] 文件大小限制
- [ ] 文件名清理
- [ ] MIME 类型匹配
- [ ] 恶意文件拒绝

### 密码安全
- [ ] 最小长度要求（8字符）
- [ ] 复杂度要求（大小写+数字+特殊字符）
- [ ] 密码强度指示器
- [ ] 弱密码拒绝

### URL 验证
- [ ] 协议限制（仅 http/https）
- [ ] 危险协议拒绝（javascript:、data:）
- [ ] URL 格式验证
- [ ] 错误提示清晰

---

## 持续安全监控

### 浏览器开发者工具

1. **控制台监控:**
   - 查看 CSP 违规警告
   - 检查 XSS 防护日志
   - 监控网络请求

2. **网络面板:**
   - 检查请求头
   - 验证响应头
   - 监控文件上传

3. **应用面板:**
   - 检查 localStorage 中的限流数据
   - 验证 token 存储
   - 清理测试数据

### 日志分析

定期检查以下日志：
- 浏览器控制台错误
- CSP 违规报告
- 限流触发记录
- 文件上传失败日志

---

## 问题报告

如果发现安全问题，请记录以下信息：

1. **问题描述**: 详细描述发现的安全问题
2. **重现步骤**: 如何重现该问题
3. **预期行为**: 应该如何表现
4. **实际行为**: 实际发生了什么
5. **浏览器信息**: 浏览器类型和版本
6. **截图/日志**: 相关的截图或控制台日志

---

## 下一步

完成所有测试后：

1. ✅ 记录测试结果
2. ✅ 修复发现的问题
3. ✅ 更新文档
4. ✅ 部署到生产环境
5. ✅ 建立持续监控机制
