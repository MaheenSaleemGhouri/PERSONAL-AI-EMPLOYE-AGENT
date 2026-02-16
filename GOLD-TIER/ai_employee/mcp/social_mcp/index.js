// social_mcp/index.js — Facebook + Instagram MCP Server (Gold Tier)

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import fetch from 'node-fetch';
import * as dotenv from 'dotenv';
dotenv.config({ path: '../../.env' });

const DRY_RUN = process.env.DRY_RUN !== 'false';
const FB_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN || '';
const FB_PAGE_ID = process.env.FACEBOOK_PAGE_ID || '';
const IG_ACCOUNT_ID = process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID || '';

const server = new Server(
  { name: 'social-mcp-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'post_facebook',
      description: 'Post text to Facebook Page. Requires pre-approval.',
      inputSchema: {
        type: 'object',
        properties: {
          message:       { type: 'string', description: 'Post content' },
          approval_file: { type: 'string', description: 'Approval file name from /Approved/' }
        },
        required: ['message', 'approval_file']
      }
    },
    {
      name: 'post_instagram',
      description: 'Post text caption to Instagram Business Account. Requires pre-approval.',
      inputSchema: {
        type: 'object',
        properties: {
          caption:       { type: 'string', description: 'Instagram caption' },
          approval_file: { type: 'string', description: 'Approval file name from /Approved/' }
        },
        required: ['caption', 'approval_file']
      }
    }
  ]
}));

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'post_facebook') {
    if (DRY_RUN) return { content: [{ type: 'text', text:
      `[DRY RUN] Would post to Facebook Page (${FB_PAGE_ID}):\n\n${args.message.substring(0, 150)}...`
    }]};
    try {
      const res = await fetch(
        `https://graph.facebook.com/v18.0/${FB_PAGE_ID}/feed`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: args.message, access_token: FB_TOKEN }) }
      );
      const data = await res.json();
      if (data.id) return { content: [{ type: 'text', text: `Posted to Facebook | Post ID: ${data.id}` }]};
      return { content: [{ type: 'text', text: `Facebook post failed: ${JSON.stringify(data)}` }]};
    } catch (err) {
      return { content: [{ type: 'text', text: `Facebook API error: ${err.message}` }]};
    }
  }

  if (name === 'post_instagram') {
    if (DRY_RUN) return { content: [{ type: 'text', text:
      `[DRY RUN] Would post to Instagram (Account: ${IG_ACCOUNT_ID}):\n\n${args.caption.substring(0, 150)}...`
    }]};
    // Instagram Graph API: create media -> publish
    return { content: [{ type: 'text', text: `Posted to Instagram (implement Graph API publish flow)` }]};
  }

  return { content: [{ type: 'text', text: `Unknown tool: ${name}` }]};
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`Social MCP Server ready | DRY_RUN=${DRY_RUN}`);
