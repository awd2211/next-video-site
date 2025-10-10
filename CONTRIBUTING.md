# 贡献指南

感谢您对 VideoSite 项目的关注！本文档提供了参与本项目贡献的指南和说明。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [开发工作流](#开发工作流)
- [编码规范](#编码规范)
- [提交规范](#提交规范)
- [Pull Request 流程](#pull-request-流程)
- [测试指南](#测试指南)
- [文档编写](#文档编写)

## 行为准则

本项目遵循行为准则，所有贡献者都应遵守。请在贡献前阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 如何贡献

### 报告 Bug

在创建 bug 报告前，请先检查现有 issue 以避免重复。创建 bug 报告时，请包含:

- **清晰的标题和描述**
- **复现步骤**
- **预期行为 vs 实际行为**
- **截图**(如适用)
- **环境详情**(操作系统、浏览器、版本)
- **错误日志或控制台输出**

示例 bug 报告:

```markdown
**Bug**: 视频播放器无法恢复播放位置

**复现步骤**:
1. 开始观看一个视频
2. 关闭浏览器
3. 重新打开并导航到同一视频

**预期行为**: 视频从上次位置继续播放
**实际行为**: 视频从头开始播放

**环境**:
- 操作系统: Ubuntu 22.04
- 浏览器: Firefox 120
- 前端版本: 1.0.0
```

### 建议功能增强

功能增强建议通过 GitHub Issues 跟踪。创建功能建议时:

- **使用清晰的标题**描述增强功能
- **提供详细描述**说明建议的功能
- **解释为什么这个增强功能有用**
- **包含示意图或示例**(如适用)

### 首次贡献者

寻找标记为 `good first issue` 或 `help wanted` 的 issue。这些是新贡献者的很好起点。

## 开发环境设置

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+
- Docker 和 Docker Compose (可选但推荐)
- pnpm (用于前端开发)

### 快速设置

```bash
# 克隆你的 fork
git clone https://github.com/YOUR-USERNAME/next-video-site.git
cd next-video-site

# 添加上游远程仓库
git remote add upstream https://github.com/awd2211/next-video-site.git

# 启动基础设施
make infra-up

# 安装所有依赖
make all-install

# 初始化数据库
make db-init
```

### 后端设置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
alembic upgrade head
uvicorn app.main:app --reload
```

### 前端设置

```bash
cd frontend
pnpm install
pnpm run dev
```

### 管理后台设置

```bash
cd admin-frontend
pnpm install
pnpm run dev
```

## 开发工作流

### 分支策略

我们使用简化的 Git 工作流:

- `master` - 主分支，始终可部署
- `feature/*` - 功能分支
- `bugfix/*` - Bug 修复分支
- `hotfix/*` - 紧急生产修复

### 创建功能分支

```bash
# 更新本地 master
git checkout master
git pull upstream master

# 创建功能分支
git checkout -b feature/your-feature-name
```

### 在功能分支上工作

```bash
# 进行修改
git add .
git commit -m "feat: 添加很棒的功能"

# 保持分支更新
git fetch upstream
git rebase upstream/master

# 推送到你的 fork
git push origin feature/your-feature-name
```

## 编码规范

### Python (后端)

#### 代码风格

- 遵循 **PEP 8** 风格指南
- 使用 **Black** 进行代码格式化 (行长度: 100)
- 使用 **isort** 进行导入排序
- 使用 **mypy** 进行类型检查
- 使用 **pylint** 或 **flake8** 进行代码检查

```bash
# 格式化代码
black app/ tests/

# 排序导入
isort app/ tests/

# 类型检查
mypy app/

# 代码检查
flake8 app/ tests/
```

#### 最佳实践

1. **类型提示**: 始终为函数参数和返回值使用类型提示

```python
async def get_video(db: AsyncSession, video_id: int) -> Optional[Video]:
    """根据 ID 检索视频。"""
    result = await db.execute(select(Video).where(Video.id == video_id))
    return result.scalar_one_or_none()
```

2. **异步/等待**: 所有数据库和 I/O 操作使用 async/await

```python
# 好的做法
async def create_video(db: AsyncSession, video: VideoCreate) -> Video:
    db_video = Video(**video.dict())
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)
    return db_video

# 不好的做法 - 阻塞操作
def create_video(db: Session, video: VideoCreate) -> Video:
    db_video = Video(**video.dict())
    db.add(db_video)
    db.commit()  # 阻塞事件循环
    return db_video
```

3. **错误处理**: 使用适当的异常处理和 HTTP 异常

```python
from fastapi import HTTPException, status

async def get_video_or_404(db: AsyncSession, video_id: int) -> Video:
    video = await get_video(db, video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {video_id} 的视频未找到"
        )
    return video
```

4. **文档**: 为所有公共函数和类添加文档字符串

```python
def calculate_video_duration(file_path: str) -> float:
    """
    计算视频文件的时长(秒)。

    Args:
        file_path: 视频文件路径

    Returns:
        时长(秒)

    Raises:
        ValueError: 如果文件不是有效的视频
        FileNotFoundError: 如果文件不存在
    """
    # 实现
```

### TypeScript/React (前端)

#### 代码风格

- 遵循 **Airbnb JavaScript 风格指南**
- 使用 **ESLint** 进行代码检查
- 使用 **Prettier** 进行格式化
- 使用 **TypeScript 严格模式**

```bash
# 检查代码
pnpm run lint

# 修复检查问题
pnpm run lint:fix

# 类型检查
pnpm run type-check
```

#### 最佳实践

1. **类型安全**: 为所有 props 和 state 定义适当的类型

```typescript
interface VideoCardProps {
  video: Video;
  onPlay?: (videoId: number) => void;
  showActions?: boolean;
}

const VideoCard: React.FC<VideoCardProps> = ({
  video,
  onPlay,
  showActions = true
}) => {
  // 组件实现
}
```

2. **React Hooks**: 遵循 hooks 规则和命名约定

```typescript
// 自定义 hook 示例
function useVideoPlayer(videoId: number) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    // 设置播放器
    return () => {
      // 清理
    };
  }, [videoId]);

  return { isPlaying, currentTime, setIsPlaying };
}
```

3. **组件结构**: 使用函数组件和 hooks

```typescript
// 好的做法 - 函数组件
const VideoList: React.FC<VideoListProps> = ({ categoryId }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['videos', categoryId],
    queryFn: () => videoService.getVideos({ categoryId })
  });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return <div>{/* 渲染视频 */}</div>;
}

// 避免 - 类组件
class VideoList extends React.Component {
  // 类实现
}
```

4. **API 调用**: 使用 TanStack Query 进行数据获取

```typescript
// 定义查询 hook
export function useVideo(videoId: number) {
  return useQuery({
    queryKey: ['video', videoId],
    queryFn: () => videoService.getVideo(videoId),
    staleTime: 5 * 60 * 1000, // 5 分钟
  });
}

// 在组件中使用
const { data: video, isLoading } = useVideo(videoId);
```

### 数据库迁移

始终为数据库更改创建迁移:

```bash
# 创建迁移
make db-migrate MSG="添加用户头像字段"

# 查看生成的迁移文件
# 必要时进行编辑

# 应用迁移
make db-upgrade

# 如需回滚
alembic downgrade -1
```

**迁移指南**:
- 永远不要编辑已应用的迁移
- 始终先在开发数据库上测试迁移
- 包含升级和降级路径
- 为外键和常查询列添加索引
- 记录复杂的迁移

### CSS/样式

- 使用 **TailwindCSS** 实用类
- 遵循移动优先的响应式设计
- 为自定义 CSS 使用语义化类名
- 避免内联样式，除非是动态值

```tsx
// 好的做法 - TailwindCSS 实用类
<div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg">
  <h2 className="text-xl font-semibold">标题</h2>
</div>

// 避免 - 内联样式
<div style={{ display: 'flex', padding: '16px', background: '#f3f4f6' }}>
  <h2 style={{ fontSize: '1.25rem', fontWeight: '600' }}>标题</h2>
</div>
```

## 提交规范

我们遵循 **约定式提交** 规范:

### 提交消息格式

```
<类型>(<范围>): <主题>

<正文>

<页脚>
```

### 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更改
- `style`: 代码样式更改(格式化、分号等)
- `refactor`: 代码重构，不改变功能
- `perf`: 性能改进
- `test`: 添加或更新测试
- `chore`: 构建过程或辅助工具更改
- `ci`: CI/CD 配置更改

### 示例

```bash
# 新功能
git commit -m "feat(video): 添加视频续播功能"

# Bug 修复
git commit -m "fix(auth): 解决令牌过期问题"

# 文档
git commit -m "docs(readme): 更新安装说明"

# 破坏性更改
git commit -m "feat(api): 更改视频响应格式

BREAKING CHANGE: 视频 API 现在返回驼峰式而不是下划线式"
```

### 规则

- 使用现在时("添加功能"而不是"已添加功能")
- 使用祈使语气("移动光标到..."而不是"移动光标到...")
- 第一行应为 50 个字符或更少
- 自由引用 issue 和 pull request
- 考虑在提交消息开头使用 emoji 以提高可读性(可选)

## Pull Request 流程

### 提交前

1. **更新你的分支**到最新的 master
2. **运行所有测试**并确保通过
3. **运行代码检查**并修复任何问题
4. **更新文档**(如需要)
5. **在本地环境手动测试**

### 提交 Pull Request

1. **推送到你的 fork**:
```bash
git push origin feature/your-feature-name
```

2. **在 GitHub 上创建 Pull Request**，包含:
   - 遵循提交约定的清晰标题
   - 详细描述更改内容
   - 链接到相关 issue
   - UI 更改的截图/GIF
   - 已完成任务的检查清单

### Pull Request 模板

```markdown
## 描述
简要描述此 PR 的内容

## 相关 Issue
修复 #123
关联 #456

## 更改内容
- 添加功能 X
- 修复 bug Y
- 重构组件 Z

## 测试
- [ ] 添加/更新了单元测试
- [ ] 执行了手动测试
- [ ] 所有测试通过

## 截图 (如适用)
[在此添加截图]

## 检查清单
- [ ] 代码遵循项目风格指南
- [ ] 完成自我审查
- [ ] 更新了文档
- [ ] 没有产生新的警告
- [ ] 添加/更新了测试
```

### 审查流程

- 合并前需要至少**一个审批**
- 处理所有审查意见
- 保持讨论专业和建设性
- 维护者可能会要求更改或额外测试

### 审批后

- **Squash 和 merge** 用于更清晰的历史(小型 PR)
- **Rebase 和 merge** 用于较大的功能分支
- 合并后**删除分支**

## 测试指南

### 后端测试

位于 `backend/tests/`，使用 **pytest** 和 **pytest-asyncio**。

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_videos.py

# 运行带覆盖率
pytest --cov=app tests/

# 详细输出
pytest -v
```

**测试结构**:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_video_success(async_client: AsyncClient):
    """测试成功检索视频。"""
    response = await async_client.get("/api/v1/videos/1")
    assert response.status_code == 200
    assert "title" in response.json()

@pytest.mark.asyncio
async def test_get_video_not_found(async_client: AsyncClient):
    """测试视频未找到错误。"""
    response = await async_client.get("/api/v1/videos/99999")
    assert response.status_code == 404
```

### 前端测试

使用 **Vitest** 和 **React Testing Library** (待实现)。

```typescript
import { render, screen } from '@testing-library/react';
import VideoCard from './VideoCard';

test('渲染视频标题', () => {
  const video = { id: 1, title: '测试视频' };
  render(<VideoCard video={video} />);
  expect(screen.getByText('测试视频')).toBeInTheDocument();
});
```

### 测试最佳实践

- 为新功能编写测试
- 修改现有功能时更新测试
- 目标代码覆盖率 >80%
- 测试边界情况和错误条件
- 使用有意义的测试名称和描述
- Mock 外部依赖

## 文档编写

### 代码文档

- 为所有公共函数/类添加文档字符串
- 添加端点时更新 API 文档
- 记录复杂算法和业务逻辑
- 为不明显的代码添加内联注释

### 用户文档

- 主要功能更新 README.md
- 在 `docs/` 中为复杂功能创建指南
- 开发工作流更改时更新 CLAUDE.md
- 添加示例和使用说明

### API 文档

FastAPI 自动生成 API 文档，但确保:
- 所有端点都有适当的描述
- 请求/响应模式已记录
- 提供示例值
- 记录错误响应

```python
@router.post("/videos/", response_model=VideoResponse)
async def create_video(
    video: VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Video:
    """
    创建新视频。

    Args:
        video: 视频创建数据
        db: 数据库会话
        current_user: 已认证用户

    Returns:
        已创建的视频对象

    Raises:
        HTTPException: 如果视频创建失败
    """
    return await VideoService.create_video(db, video, current_user.id)
```

## 社区

### 获取帮助

- **GitHub Discussions**: 用于一般问题和讨论
- **GitHub Issues**: 用于 bug 报告和功能请求
- **Discord/Slack**: (如有) 用于实时聊天

### 认可

贡献者将在以下位置获得认可:
- GitHub 贡献者页面
- 项目 README(重大贡献)
- 发布说明

## 许可证

通过为 VideoSite 做出贡献，您同意您的贡献将根据 MIT 许可证授权。

---

感谢您为 VideoSite 做出贡献！您的努力帮助这个项目变得更好！
