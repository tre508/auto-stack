// Simple test script to test the backtest command functionality
const { parseBacktestCommand, executeBacktest } = require('./freq-chat/lib/backtest-processor.ts');

async function testBacktestCommand() {
  console.log('Testing backtest command parsing...');
  
  // Test command parsing
  const testCommands = [
    '/backtest TestStrategy',
    '/backtest KrakenFreqAI_auto_stack 20240101-20240301',
    '/backtest MyStrategy 20240101-20240301 custom_config.json',
    'regular message',
    '/BACKTEST TestStrategy', // case insensitive
  ];
  
  testCommands.forEach(cmd => {
    const result = parseBacktestCommand(cmd);
    console.log(`Command: "${cmd}" -> Parsed:`, result);
  });
  
  console.log('\nTesting backtest execution...');
  
  // Test backtest execution
  const testCommand = {
    strategy: 'TestStrategy',
    timerange: '20240101-20240301',
  };
  
  try {
    const result = await executeBacktest(testCommand);
    console.log('Backtest execution result:', result);
  } catch (error) {
    console.error('Backtest execution error:', error);
  }
}

// Run the test
testBacktestCommand().catch(console.error); 