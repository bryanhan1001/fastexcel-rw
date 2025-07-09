# PyPI 发布指南

本指南介绍如何使用 GitHub Actions 自动打包并发布 fastexcel-rw 到 PyPI。

## 前提条件

### 1. 设置 PyPI API Token

1. 登录 [PyPI](https://pypi.org/) 
2. 进入 Account Settings → API tokens
3. 创建一个新的 API token，权限范围选择 "Entire account" 或者只针对 `fastexcel-rw` 项目
4. 复制生成的 token（格式类似 `pypi-...`）

### 2. 在 GitHub 中配置 Secret

1. 进入 GitHub 仓库的 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: 粘贴你的 PyPI API token
5. 点击 "Add secret"

## 发布流程

### 自动发布（推荐）

1. **确保代码已提交到 main 分支**
   ```bash
   git add .
   git commit -m "准备发布 v0.15.0"
   git push origin main
   ```

2. **创建并推送 tag**
   ```bash
   # 创建 tag（版本号要与 Cargo.toml 中的版本一致）
   git tag v0.15.0
   
   # 推送 tag 到 GitHub
   git push origin v0.15.0
   ```

3. **监控 GitHub Actions**
   - 推送 tag 后，GitHub Actions 会自动触发 `release.yml` 工作流
   - 访问 `https://github.com/your-username/fastexcel-rw/actions` 查看构建状态
   - 工作流会：
     - 在多个平台构建 wheel 文件
     - 构建源代码分发包（sdist）
     - 上传到 PyPI
     - 创建 GitHub Release

### 手动发布（备用）

如果需要手动发布，可以使用以下命令：

```bash
# 安装构建依赖
pip install -r build-requirements.txt

# 构建 wheel 和 sdist
maturin build --release

# 上传到 PyPI
maturin publish
```

## 发布检查清单

在创建新版本之前，请确保：

- [ ] 所有测试都通过
- [ ] 代码已经过 lint 检查
- [ ] 更新了 `Cargo.toml` 中的版本号
- [ ] 更新了 `CHANGELOG.md`（如果有）
- [ ] 文档已更新
- [ ] 在测试环境中验证了新功能

## 支持的平台和 Python 版本

当前配置支持：

**平台：**
- Linux (x86-64, aarch64)
- macOS (x86-64, aarch64)
- Windows (x86-64)

**Python 版本：**
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

## 故障排除

### 常见问题

1. **PyPI 上传失败**
   - 检查 `PYPI_API_TOKEN` 是否正确设置
   - 确保版本号没有重复
   - 检查 PyPI API token 的权限

2. **构建失败**
   - 检查 Rust toolchain 是否正确
   - 确保所有依赖都可用
   - 查看具体的构建日志

3. **版本号冲突**
   - 确保 `Cargo.toml` 中的版本号是新的
   - 检查 PyPI 上是否已经存在相同版本

### 查看日志

- GitHub Actions 日志：`https://github.com/your-username/fastexcel-rw/actions`
- PyPI 发布历史：`https://pypi.org/project/fastexcel-rw/#history`

## 最佳实践

1. **使用语义化版本**：遵循 `major.minor.patch` 格式
2. **测试后发布**：确保所有 CI 测试都通过
3. **保持版本一致性**：`Cargo.toml` 和 git tag 版本要一致
4. **及时更新文档**：每次发布后更新相关文档

## 联系

如果在发布过程中遇到问题，请：
1. 检查 GitHub Actions 日志
2. 在 GitHub 仓库中创建 Issue
3. 联系维护者

---

最后更新：2024-01-XX 