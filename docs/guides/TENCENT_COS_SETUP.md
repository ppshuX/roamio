# 腾讯云 COS 对象存储集成指南

## 📋 功能概述

本项目已完成腾讯云 COS（对象存储）的集成，所有用户上传的媒体文件（头像、评论图片、评论视频）将自动上传到腾讯云 COS，而不是保存到服务器本地的 `media/` 目录。

### ✅ 已实现的功能

1. **自动上传到 COS**：文件先临时保存到 `/tmp/`，上传成功后自动删除临时文件
2. **唯一文件名**：使用时间戳 + UUID + 用户ID 生成唯一文件名，避免重复
3. **文件分类存储**：
   - 用户头像：`media/avatars/`
   - 评论图片：`media/comments/images/`
   - 评论视频：`media/comments/videos/`
4. **自动删除旧文件**：更新头像、图片时自动删除 COS 上的旧文件
5. **兼容旧数据**：序列化器支持同时处理 COS URL 和本地路径（兼容迁移前的数据）

---

## 🔧 配置步骤

### 1. 安装依赖包

依赖包已经添加到 `requirements.txt`，执行以下命令安装：

```bash
pip install cos-python-sdk-v5
```

### 2. 腾讯云 COS 配置

#### 2.1 创建存储桶

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/cos)
2. 创建存储桶（Bucket）
   - 名称格式：`bucket-appid`（如 `roamio-media-1234567890`）
   - 所属地域：推荐选择 `广州（ap-guangzhou）`
   - 访问权限：**公有读私有写**（允许公网访问，但只能通过 API 上传）

#### 2.2 获取密钥

1. 进入 [访问管理 > 访问密钥](https://console.cloud.tencent.com/cam/capi)
2. 创建新密钥或使用现有密钥
3. 记录以下信息：
   - `SecretId`
   - `SecretKey`

⚠️ **安全提示**：密钥信息非常重要，请妥善保管，不要提交到代码仓库！

### 3. 配置环境变量

在项目根目录的 `.env` 文件中添加以下配置（如果没有此文件，请创建）：

```bash
# 腾讯云 COS 配置
TENCENT_COS_SECRET_ID=你的SecretId
TENCENT_COS_SECRET_KEY=你的SecretKey
TENCENT_COS_BUCKET=你的存储桶名称   # 格式: bucket-appid
TENCENT_COS_REGION=ap-guangzhou    # 所属地域，默认广州
```

**示例**：
```bash
TENCENT_COS_SECRET_ID=AKID1234567890abcdefghijklmnopqrst
TENCENT_COS_SECRET_KEY=abcdefghijklmnopqrstuvwxyz1234567890
TENCENT_COS_BUCKET=roamio-media-1234567890
TENCENT_COS_REGION=ap-guangzhou
```

### 4. 应用数据库迁移

执行以下命令，将 `ImageField`/`FileField` 字段迁移为 `URLField`：

```bash
python manage.py migrate
```

这将应用迁移文件 `0015_alter_comment_image_alter_comment_video_and_more.py`。

---

## 📂 项目结构

### 新增文件

```
trips/
├── utils/
│   ├── tencent_cos.py           # 腾讯云 COS 上传/删除工具
│   └── file_upload_handler.py   # 统一文件上传处理器
```

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `trips/models/user_profile.py` | `avatar` 字段从 `ImageField` 改为 `URLField` |
| `trips/models/comment.py` | `image` 和 `video` 字段从 `ImageField`/`FileField` 改为 `URLField` |
| `trips/api/viewsets/user_viewset.py` | 头像上传逻辑改为上传到 COS |
| `trips/api/viewsets/comment_viewset.py` | 评论图片/视频上传逻辑改为上传到 COS |
| `trips/serializers/comment_serializer.py` | 序列化器支持同时处理 COS URL 和本地路径 |
| `roamio/settings.py` | 添加腾讯云 COS 配置项 |
| `requirements.txt` | 添加 `cos-python-sdk-v5` 依赖 |

---

## 🚀 使用说明

### 上传流程

1. **用户上传文件** → API 接收文件
2. **临时保存** → 文件保存到系统临时目录 `/tmp/`
3. **上传到 COS** → 调用 `upload_to_cos()` 函数上传
4. **获取 URL** → 返回 COS 公网访问链接（如 `https://roamio-media-xxx.cos.ap-guangzhou.myqcloud.com/media/avatars/user1_20251101_abc123.jpg`）
5. **保存到数据库** → 将 URL 存入数据库（不再保存本地路径）
6. **删除临时文件** → 自动清理 `/tmp/` 中的临时文件

### 文件命名规则

- **头像**：`user{用户ID}_{时间戳}_{UUID}.{扩展名}`
  - 示例：`user1_20251101_145830_abc12345.jpg`

- **评论图片/视频**：`user{用户ID}_{时间戳}_{UUID}.{扩展名}`
  - 示例：`user2_20251101_150000_def67890.mp4`

### API 示例

#### 上传头像

```bash
POST /api/v1/users/{user_id}/upload_avatar/
Content-Type: multipart/form-data

avatar: [文件]
```

**响应**：
```json
{
  "avatar_url": "https://roamio-media-xxx.cos.ap-guangzhou.myqcloud.com/media/avatars/user1_20251101_145830_abc12345.jpg",
  "detail": "头像上传成功"
}
```

#### 上传评论（带图片）

```bash
POST /api/v1/comments/
Content-Type: multipart/form-data

content: "这是评论内容"
image: [文件]
page: "trip1"
```

**响应**：
```json
{
  "id": 123,
  "user": {...},
  "content": "这是评论内容",
  "image": "https://roamio-media-xxx.cos.ap-guangzhou.myqcloud.com/media/comments/images/user2_20251101_150000_def67890.jpg",
  "video": null,
  "page": "trip1",
  "timestamp": "2025-11-01 15:00:00"
}
```

---

## 🔍 测试与验证

### 1. 启动服务器

```bash
python manage.py runserver
```

如果配置正确，你应该看到：
```
==================================================
[警告] 腾讯云 COS 配置不完整
[提示] 请在 .env 文件中配置以下环境变量：
  - TENCENT_COS_SECRET_ID
  - TENCENT_COS_SECRET_KEY
  - TENCENT_COS_BUCKET
  - TENCENT_COS_REGION (可选，默认 ap-guangzhou)
==================================================
```

如果看到上述警告，请检查 `.env` 文件配置。

### 2. 测试上传

使用 Postman 或前端界面上传一张头像：

1. 登录系统
2. 进入个人中心
3. 上传头像
4. 检查浏览器控制台，头像 URL 应为 COS 链接（以 `https://` 开头）

### 3. 验证 COS 存储桶

登录腾讯云控制台 → 进入 COS 存储桶 → 查看文件列表，应该能看到上传的文件。

---

## 🛠️ 故障排查

### 问题 1：上传失败，报错 `ModuleNotFoundError: No module named 'qcloud_cos'`

**原因**：未安装腾讯云 COS SDK

**解决方案**：
```bash
pip install cos-python-sdk-v5
```

---

### 问题 2：上传失败，报错 `TENCENT_COS_SECRET_ID not found`

**原因**：环境变量配置不正确

**解决方案**：
1. 检查 `.env` 文件是否存在
2. 确认配置项名称拼写正确（区分大小写）
3. 重启 Django 服务器使配置生效

---

### 问题 3：上传成功但无法访问图片

**原因**：COS 存储桶权限设置错误

**解决方案**：
1. 登录腾讯云控制台
2. 进入 COS 存储桶 → 权限管理
3. 将访问权限设置为 **公有读私有写**

---

### 问题 4：旧数据（本地路径）无法显示

**原因**：旧数据使用本地路径，需要手动迁移

**解决方案**：

序列化器已经支持兼容旧数据，旧数据会自动构建为完整 URL。如果需要完全迁移到 COS，可以编写脚本批量上传：

```python
# 示例脚本（需要根据实际情况调整）
from trips.models import UserProfile, Comment
from trips.utils.file_upload_handler import FileUploadHandler
import os

# 迁移头像
for profile in UserProfile.objects.exclude(avatar=''):
    if profile.avatar and not profile.avatar.startswith('http'):
        # 本地路径，需要上传到 COS
        local_path = profile.avatar.path
        if os.path.exists(local_path):
            cos_url = FileUploadHandler.upload_avatar(open(local_path, 'rb'), profile.user.id)
            profile.avatar = cos_url
            profile.save()
```

---

## 📊 数据库迁移说明

### 迁移文件：`0015_alter_comment_image_alter_comment_video_and_more.py`

**变更内容**：
- `UserProfile.avatar`：`ImageField` → `URLField(max_length=500)`
- `Comment.image`：`ImageField` → `URLField(max_length=500)`
- `Comment.video`：`FileField` → `URLField(max_length=500)`

**向后兼容性**：
- ✅ 旧数据（本地路径）会被保留，序列化器会自动构建为完整 URL
- ✅ 新数据（COS URL）直接存储为 `https://` 开头的完整链接
- ✅ 不影响现有功能

---

## 🎯 性能优化建议

### 1. 使用 CDN 加速

腾讯云 COS 支持 CDN 加速，可以显著提升图片加载速度：

1. 进入 COS 控制台 → 域名管理
2. 开启 CDN 加速
3. 配置自定义域名（可选）

### 2. 压缩图片

可以在上传前进行客户端压缩，或者在 COS 上配置图片处理规则（缩略图、水印等）。

### 3. 监控存储成本

定期检查 COS 存储用量和流量，删除不再使用的文件（可以编写定时任务）。

---

## 📝 注意事项

1. **密钥安全**：
   - ⚠️ 不要将 `.env` 文件提交到 Git 仓库
   - ⚠️ 在 `.gitignore` 中添加 `.env`

2. **权限设置**：
   - ✅ 存储桶访问权限：**公有读私有写**
   - ✅ API 上传权限：通过 SecretId/SecretKey 验证

3. **费用控制**：
   - 腾讯云 COS 按存储量和流量计费
   - 建议定期清理无用文件
   - 设置费用告警

4. **备份策略**：
   - 重要数据建议开启版本控制
   - 可配置跨地域复制

---

## 🔗 相关资源

- [腾讯云 COS 官方文档](https://cloud.tencent.com/document/product/436)
- [Python SDK 文档](https://cloud.tencent.com/document/product/436/12269)
- [COS 控制台](https://console.cloud.tencent.com/cos)
- [费用说明](https://cloud.tencent.com/document/product/436/6239)

---

## 📞 技术支持

如有问题，请参考：
1. 本文档的「故障排查」章节
2. 腾讯云官方文档
3. 提交 Issue 到项目仓库

---

**创建时间**：2025-11-01  
**最后更新**：2025-11-01  
**版本**：v1.0

