import { Eko } from '@eko-ai/eko';
import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

// Supported free models
const freeModels = [
  "tngtech/deepseek-r1t-chimera:free",
  "deepseek/deepseek-r1:free",
  "deepseek/deepseek-prover-v2:free",
  "meta-llama/llama-4-maverick:free"
];

// Select model using simple round-robin
const modelIndex = Math.floor(Math.random() * freeModels.length);
const selectedModel = freeModels[modelIndex];

const eko = new Eko({
  llm: {
    provider: process.env.EKO_LLM_PROVIDER || "claude",
    apiKey: process.env.ANTHROPIC_API_KEY,
    baseUrl: "https://api.anthropic.com/v1"
  },
  modelName: process.env.EKO_MODEL_NAME || "claude-3-5-sonnet-20241022",
  tools: {
    web: true,
    code: true,
    files: true
  }
});

const app = express();
const port = process.env.EKO_SERVICE_PORT || 3001;

app.use(express.json());

// Health check endpoints
app.get('/status', (req, res) => {
  res.json({ status: 'Eko service is running' });
});

app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy',
    service: 'eko_service',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/healthz', (req, res) => {
  res.status(200).json({ 
    status: 'healthy',
    service: 'eko_service',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Endpoint to run Eko workflows
app.post('/run_eko', async (req, res) => {
  const { prompt } = req.body;
  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }
  try {
    // Eko planning phase
    const workflow = await eko.generate(prompt);
    
    // Eko execution phase
    const result = await eko.execute(workflow);
    
    // Serialize workflow for storage if needed
    let workflowJson = null;
    try {
      // Assuming workflow object has a serialize method or is directly stringifiable
      workflowJson = JSON.stringify(workflow); 
    } catch (serializeError) {
       console.error('Error serializing workflow:', serializeError);
       // Continue without workflow JSON if serialization fails
    }

    console.log(`Eko workflow executed successfully for prompt: "${prompt}"`);
    res.json({
      workflow_id: workflow.id, // Assuming workflow object has an id
      workflow_plan_json: workflowJson, 
      result: result
    });
  } catch (error) {
    console.error('Eko execution error:', error);
    // Return a 500 error with details
    res.status(500).json({ error: 'Failed to execute Eko workflow', details: error.message });
  }
});

app.listen(port, () => {
  console.log(`Eko Node.js service listening on port ${port}`);
});
