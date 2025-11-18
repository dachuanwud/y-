# Playwright MCP Server

为本项目提供一个基于 Playwright 的 MCP 服务器，使我可以通过 MCP 工具自动操作浏览器（打开页面、点击元素、填写表单等）。

## 安装与启动

在 `playwright-mcp` 目录下执行：

```bash
cd playwright-mcp
npm install
npx playwright install
npm start
```

启动后，该进程会通过 STDIO 作为一个 MCP 服务器等待客户端连接。

## 提供的工具

- `open_page`：打开指定 URL。
- `click`：通过 CSS 选择器点击元素。
- `fill`：向输入框填写文本。
- `wait_for_selector`：等待某个元素出现在页面上。
- `close_browser`：关闭浏览器并清空状态。

## 在 Cursor 中的配置步骤

### 方法一：通过 Cursor 设置界面配置（推荐）

1. 打开 Cursor，按 `Cmd + ,`（macOS）或 `Ctrl + ,`（Windows/Linux）打开设置
2. 在设置搜索框中输入 "MCP" 或 "Model Context Protocol"
3. 找到 MCP Servers 配置部分
4. 点击 "Edit in settings.json" 或直接编辑配置文件

### 方法二：直接编辑配置文件

1. 打开 Cursor 的配置文件：
   - macOS: `~/Library/Application Support/Cursor/User/settings.json`
   - Windows: `%APPDATA%\Cursor\User\settings.json`
   - Linux: `~/.config/Cursor/User/settings.json`

2. 在配置文件中添加以下内容（如果已有 `mcp.servers` 配置，则合并到现有配置中）：

```json
{
  "mcp.servers": {
    "playwright-mcp": {
      "command": "node",
      "args": ["/Users/houjl/Downloads/Y_idx_newV2_spot/playwright-mcp/server.mjs"]
    }
  }
}
```

**注意**：请将路径 `/Users/houjl/Downloads/Y_idx_newV2_spot/playwright-mcp/server.mjs` 替换为你实际的绝对路径。

3. 保存配置文件并重启 Cursor

### 验证配置

配置完成后，重启 Cursor。你可以在 Cursor 的设置中查看 MCP 服务器状态，如果 playwright-mcp 显示为已连接状态，说明配置成功。

## 在其他 MCP 客户端中的配置示例

不同 MCP 客户端的配置方式略有不同，一般可以在配置文件里添加类似条目（示意）：

```yaml
servers:
  playwright-mcp:
    command: ["node", "/绝对路径/到/本仓库/playwright-mcp/server.mjs"]
```

保存后重启你的 MCP 客户端（如 Codex CLI）。之后你就可以对我发出类似指令：

- “使用 `open_page` 打开 https://example.com”
- “点击页面上的 `#login-button`”
- “在 `input[name=email]` 中填入我的邮箱”

我会通过 Playwright MCP 工具在你的浏览器里完成这些操作。

