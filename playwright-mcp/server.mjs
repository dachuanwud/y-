/**
 * Playwright MCP Server
 *
 * 提供基础浏览器操作能力：
 * - open_page: 打开 URL
 * - click: 点击元素
 * - fill: 输入文本
 * - wait_for_selector: 等待元素出现
 *
 * 使用前请先在本目录执行：
 *   npm install
 *   npx playwright install
 */

import { chromium } from 'playwright';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

/** @type {import('playwright').Browser | null} */
let browser = null;
/** @type {import('playwright').Page | null} */
let page = null;

async function ensureBrowser() {
  if (!browser) {
    browser = await chromium.launch({ headless: false });
  }
  if (!page) {
    const ctx = await browser.newContext();
    page = await ctx.newPage();
  }
}

const mcpServer = new McpServer(
  {
    name: 'playwright-mcp',
    version: '0.1.0',
    description: 'Control a Chromium browser via Playwright',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 打开页面
mcpServer.registerTool('open_page', {
  description: 'Open a URL in a browser page',
  inputSchema: {
    url: z.string().describe('Target URL to open')
  }
}, async ({ url }) => {
  await ensureBrowser();
  await page.goto(url, { waitUntil: 'load' });
  return {
    content: [
      {
        type: 'text',
        text: `Opened URL: ${url}`
      }
    ]
  };
});

// 点击元素
mcpServer.registerTool('click', {
  description: 'Click an element by CSS selector on the current page',
  inputSchema: {
    selector: z.string().describe('CSS selector of the element to click')
  }
}, async ({ selector }) => {
  if (!page) {
    throw new Error('No page is open. Call open_page first.');
  }
  await page.click(selector);
  return {
    content: [
      {
        type: 'text',
        text: `Clicked element: ${selector}`
      }
    ]
  };
});

// 填写输入框
mcpServer.registerTool('fill', {
  description: 'Fill an input element with text',
  inputSchema: {
    selector: z.string().describe('CSS selector of the input element'),
    value: z.string().describe('Text value to fill')
  }
}, async ({ selector, value }) => {
  if (!page) {
    throw new Error('No page is open. Call open_page first.');
  }
  await page.fill(selector, value);
  return {
    content: [
      {
        type: 'text',
        text: `Filled ${selector} with: ${value}`
      }
    ]
  };
});

// 等待元素出现
mcpServer.registerTool('wait_for_selector', {
  description: 'Wait for an element to appear on the current page',
  inputSchema: {
    selector: z.string().describe('CSS selector of the element to wait for'),
    timeout_ms: z.number().default(10000).optional().describe('Timeout in milliseconds')
  }
}, async ({ selector, timeout_ms = 10000 }) => {
  if (!page) {
    throw new Error('No page is open. Call open_page first.');
  }
  await page.waitForSelector(selector, { timeout: timeout_ms });
  return {
    content: [
      {
        type: 'text',
        text: `Selector appeared: ${selector}`
      }
    ]
  };
});

// 关闭浏览器
mcpServer.registerTool('close_browser', {
  description: 'Close the current browser instance and clear state',
  inputSchema: {}
}, async () => {
  if (browser) {
    await browser.close();
  }
  browser = null;
  page = null;
  return {
    content: [
      {
        type: 'text',
        text: 'Browser closed.'
      }
    ]
  };
});

async function main() {
  const transport = new StdioServerTransport();
  await mcpServer.connect(transport);
}

main().catch((err) => {
  console.error('Playwright MCP server error:', err);
});

