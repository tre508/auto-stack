import { generateUUID } from '@/lib/utils';

export interface BacktestCommand {
  strategy: string;
  timerange?: string;
  config?: string;
}

export interface BacktestResult {
  success: boolean;
  run_id?: string;
  message: string;
  error?: string;
  data?: any;
}

export function parseBacktestCommand(message: string): BacktestCommand | null {
  // Check if message starts with /backtest
  const backtestRegex = /^\/backtest\s+(\S+)(?:\s+(\S+))?(?:\s+(\S+))?/i;
  const match = message.trim().match(backtestRegex);
  
  if (!match) {
    return null;
  }
  
  const [, strategy, timerange, config] = match;
  
  return {
    strategy,
    timerange,
    config,
  };
}

export async function executeBacktest(command: BacktestCommand): Promise<BacktestResult> {
  try {
    const run_id = generateUUID();
    
    // Prepare the backtest payload
    const backtestPayload = {
      action: 'backtest',
      strategy: command.strategy,
      timerange: command.timerange || '20240101-20241201', // Default timerange
      config: command.config || 'config_KrakenFreqAI_auto_stack.json',
      run_id: run_id,
    };

    // Call the controller API
    const controllerUrl = process.env.CONTROLLER_API_URL || 'http://localhost:5050';
    
    // Show initial status
    console.log(`🚀 Initiating backtest for strategy: ${command.strategy}`);
    
    const response = await fetch(`${controllerUrl}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backtestPayload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return {
        success: false,
        message: `❌ **Backtest Failed to Start**\n\nError: ${response.status} ${errorText}\n\nPlease check the controller service and try again.`,
        error: `Controller API error: ${response.status}`,
      };
    }

    const result = await response.json();
    
    // Check if this was a mock response (for testing) or real execution
    const isMockResponse = result.status === 'mock_success';
    const webhookUsed = result.webhook_used || 'unknown';

    let statusMessage = '';
    if (isMockResponse) {
      statusMessage = `⚠️ **Backtest Initiated (Test Mode)**\n\n**Details:**\n- Strategy: ${command.strategy}\n- Timerange: ${backtestPayload.timerange}\n- Run ID: ${run_id}\n- Status: Mock execution (n8n webhook unavailable)\n\n*Note: This is a test response. Real backtest execution requires n8n workflows to be active.*`;
    } else {
      statusMessage = `✅ **Backtest Successfully Initiated**\n\n**Details:**\n- Strategy: ${command.strategy}\n- Timerange: ${backtestPayload.timerange}\n- Run ID: ${run_id}\n- Webhook: ${webhookUsed}\n- Status: Executing via n8n workflow\n\n⏳ **Execution in Progress...**\nThe backtest is now running through the FreqTrade pipeline. Results will be available shortly.\n\n💡 **Next Steps:**\n- Check results with: \`/results ${run_id}\`\n- View recent backtests: \`/recent-backtests\`\n- Monitor logs: \`/logs\``;
    }

    // Wait a moment and try to get initial status
    setTimeout(async () => {
      try {
        const statusCheck = await fetch(`${controllerUrl}/api/trade-history?run_id=${run_id}`);
        if (statusCheck.ok) {
          const statusData = await statusCheck.json();
          console.log(`📊 Backtest status check for ${run_id}:`, statusData);
        }
      } catch (e) {
        console.log(`⚠️ Could not check initial status for ${run_id}`);
      }
    }, 2000);

    return {
      success: true,
      run_id: run_id,
      message: statusMessage,
      data: result,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    
    return {
      success: false,
      message: `❌ **Backtest Execution Failed**\n\nError: ${errorMessage}\n\nThis could be due to:\n- Controller service unavailable\n- Network connectivity issues\n- Invalid strategy or parameters\n\nPlease check the system status and try again.`,
      error: errorMessage,
    };
  }
}

export async function getBacktestResults(run_id: string): Promise<any> {
  try {
    const controllerUrl = process.env.CONTROLLER_API_URL || 'http://localhost:5050';
    const response = await fetch(`${controllerUrl}/api/trade-history?run_id=${run_id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get results: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting backtest results:', error);
    return null;
  }
} 