// twitter_mcp/index.js — Twitter/X MCP Server (Gold Tier)

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { TwitterApi } from 'twitter-api-v2';
import * as dotenv from 'dotenv';
dotenv.config({ path: '../../.env' });

const DRY_RUN = process.env.DRY_RUN !== 'false';

const twitterClient = new TwitterApi({
  appKey:            process.env.TWITTER_API_KEY || '',
  appSecret:         process.env.TWITTER_API_SECRET || '',
  accessToken:       process.env.TWITTER_ACCESS_TOKEN || '',
  accessSecret:      process.env.TWITTER_ACCESS_SECRET || '',
});

const server = new Server(
  { name: 'twitter-mcp-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'post_tweet',
      description: 'Post a tweet (max 280 characters). Requires pre-approval. Max 1 per day.',
      inputSchema: {
        type: 'object',
        properties: {
          text:          { type: 'string', description: 'Tweet text (max 280 characters)' },
          approval_file: { type: 'string', description: 'Approval file name from /Approved/' }
        },
        required: ['text', 'approval_file']
      }
    }
  ]
}));

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'post_tweet') {
    if (args.text.length > 280) {
      return { content: [{ type: 'text', text: `Tweet exceeds 280 characters (${args.text.length}). Shorten and retry.` }]};
    }
    if (DRY_RUN) return { content: [{ type: 'text', text:
      `[DRY RUN] Would tweet (${args.text.length} chars):\n\n${args.text}`
    }]};
    try {
      const rwClient = twitterClient.readWrite;
      const tweet = await rwClient.v2.tweet(args.text);
      return { content: [{ type: 'text', text: `Tweet posted | ID: ${tweet.data.id}` }]};
    } catch (err) {
      return { content: [{ type: 'text', text: `Twitter API error: ${err.message}` }]};
    }
  }

  return { content: [{ type: 'text', text: `Unknown tool: ${name}` }]};
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`Twitter MCP Server ready | DRY_RUN=${DRY_RUN}`);
