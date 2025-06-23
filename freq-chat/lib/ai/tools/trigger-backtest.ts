import { z } from 'zod';
import { Session } from 'next-auth';
import { DataStreamWriter, tool } from 'ai';
import { generateUUID } from '@/lib/utils';

interface TriggerBacktestProps {
  session: Session;
  dataStream: DataStreamWriter;
}

export const triggerBacktest = ({
  session,
  dataStream,
}: TriggerBacktestProps) =>
  tool({
    description: 'Trigger a FreqTrade backtest with specified strategy and timerange',
    parameters: z.object({
      strategy: z
        .string()
        .describe('The trading strategy to backtest (e.g., KrakenFreqAI_auto_stack)'),
      timerange: z
        .string()
        .optional()
        .describe('The timerange for the backtest (e.g., 20240101-20241201, or leave empty for default)'),
      config: z
        .string()
        .optional()
        .describe('Optional config file path (defaults to config_KrakenFreqAI_auto_stack.json)'),
    }),
    execute: async ({ strategy, timerange, config }) => {
      try {
        // Prepare the backtest payload
        const backtestPayload = {
          action: 'backtest',
          strategy: strategy,
          timerange: timerange || '20240101-20241201', // Default timerange
          config: config || 'config_KrakenFreqAI_auto_stack.json',
          run_id: generateUUID(), // Generate unique run ID
        };

        // Call the controller API
        const controllerUrl = process.env.CONTROLLER_API_URL || 'http://localhost:5050';
        const response = await fetch(`${controllerUrl}/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(backtestPayload),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Controller API error: ${response.status} ${errorText}`);
        }

        const result = await response.json();

        // Stream the initial response
        dataStream.writeData({
          type: 'backtest-triggered',
          content: {
            run_id: backtestPayload.run_id,
            strategy: strategy,
            timerange: backtestPayload.timerange,
            status: 'initiated',
            message: `Backtest initiated for strategy "${strategy}" with timerange "${backtestPayload.timerange}"`,
          },
        });

        // Wait a moment and then try to get initial status
        setTimeout(async () => {
          try {
            const statusResponse = await fetch(`${controllerUrl}/api/trade-history?run_id=${backtestPayload.run_id}`);
            if (statusResponse.ok) {
              const statusData = await statusResponse.json();
              if (statusData.results && statusData.results.length > 0) {
                dataStream.writeData({
                  type: 'backtest-completed',
                  content: {
                    run_id: backtestPayload.run_id,
                    results: statusData.results[0],
                    message: 'Backtest completed successfully!',
                  },
                });
              }
            }
          } catch (error) {
            console.log('Status check failed, backtest may still be running:', error);
          }
        }, 5000); // Check after 5 seconds

        return {
          success: true,
          run_id: backtestPayload.run_id,
          strategy: strategy,
          timerange: backtestPayload.timerange,
          message: `Backtest initiated successfully. Run ID: ${backtestPayload.run_id}`,
          controller_response: result,
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        
        dataStream.writeData({
          type: 'backtest-error',
          content: {
            error: errorMessage,
            strategy: strategy,
            timerange: timerange,
          },
        });

        return {
          success: false,
          error: errorMessage,
          strategy: strategy,
          timerange: timerange,
        };
      }
    },
  }); 