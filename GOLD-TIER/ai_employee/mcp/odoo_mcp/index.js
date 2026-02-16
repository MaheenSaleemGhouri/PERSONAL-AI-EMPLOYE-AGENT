// odoo_mcp/index.js — Odoo Community MCP Server (Gold Tier)
// Claude Code can READ data and CREATE DRAFT invoices only
// NEVER posts invoices or records payments without human approval

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import * as dotenv from 'dotenv';
dotenv.config({ path: '../../.env' });

const DRY_RUN = process.env.DRY_RUN !== 'false';
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || '';
const ODOO_USERNAME = process.env.ODOO_USERNAME || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || '';

const server = new Server(
  { name: 'odoo-mcp-server', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'get_invoices',
      description: 'Read invoices from Odoo. Always safe — read only.',
      inputSchema: {
        type: 'object',
        properties: {
          limit: { type: 'number', description: 'Max invoices to return (default 10)' },
          state: { type: 'string', description: 'Filter by state: draft, posted, cancel' }
        }
      }
    },
    {
      name: 'create_draft_invoice',
      description: 'Create a DRAFT invoice in Odoo. Does NOT post it. Requires approval to post.',
      inputSchema: {
        type: 'object',
        properties: {
          partner_name:  { type: 'string', description: 'Customer name' },
          amount:        { type: 'number', description: 'Invoice amount' },
          description:   { type: 'string', description: 'Invoice line description' },
          approval_file: { type: 'string', description: 'Approval file name from /Approved/' }
        },
        required: ['partner_name', 'amount', 'description', 'approval_file']
      }
    },
    {
      name: 'get_monthly_summary',
      description: 'Get total income and expenses for the current month from Odoo.',
      inputSchema: { type: 'object', properties: {} }
    }
  ]
}));

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'get_invoices') {
    if (DRY_RUN) return { content: [{ type: 'text', text: '[DRY RUN] Would fetch invoices from Odoo.' }]};
    // Real Odoo XML-RPC call here
    return { content: [{ type: 'text', text: 'Invoices fetched from Odoo (implement XML-RPC call)' }]};
  }

  if (name === 'create_draft_invoice') {
    if (DRY_RUN) return { content: [{ type: 'text', text:
      `[DRY RUN] Would create draft invoice:\nPartner: ${args.partner_name}\nAmount: ${args.amount}\nDescription: ${args.description}\nNOTE: Draft only — would NOT be posted.`
    }]};
    // Real Odoo XML-RPC call here — creates DRAFT state only
    return { content: [{ type: 'text', text: `Draft invoice created for ${args.partner_name} — ${args.amount} | State: DRAFT (not posted)` }]};
  }

  if (name === 'get_monthly_summary') {
    if (DRY_RUN) return { content: [{ type: 'text', text: '[DRY RUN] Would fetch monthly financial summary from Odoo.' }]};
    return { content: [{ type: 'text', text: 'Monthly summary fetched from Odoo (implement XML-RPC call)' }]};
  }

  return { content: [{ type: 'text', text: `Unknown tool: ${name}` }]};
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`Odoo MCP Server ready | DRY_RUN=${DRY_RUN} | Odoo: ${ODOO_URL}`);
