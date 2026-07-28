// Gemini 3 Pro Consultation - Writing, Processes, Ideas
// npm install @google/genai dotenv
// npm install -D @types/node typescript

import { GoogleGenAI } from '@google/genai';
import * as dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '.env') });

interface ConsultOptions {
  prompt: string;
  text: string;
  type?: 'grammar' | 'clarity' | 'style' | 'academic' | 'creative' | 'process' | 'ideas' | 'review';
  hebrew?: boolean;
  brief?: boolean;
  detailed?: boolean;
  profile?: boolean;
}

// Researcher profile for context
const RESEARCHER_PROFILE = `
WRITER: Elad Refoua, PhD student (Psychology, Bar-Ilan University). Research: AI in mental health, psychological needs, ESM methods. Writing style: Academic/APA.
`.trim();

function parseArgs(args: string[]): ConsultOptions {
  let prompt = '';
  let text = '';
  let type: ConsultOptions['type'] = undefined;
  let hebrew = false;
  let brief = false;
  let detailed = false;
  let profile = false;
  let filePath = '';

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--text' && args[i + 1]) {
      text = args[++i];
    } else if (arg === '--file' && args[i + 1]) {
      filePath = args[++i];
    } else if (arg === '--type' && args[i + 1]) {
      type = args[++i] as ConsultOptions['type'];
    } else if (arg === '--hebrew') {
      hebrew = true;
    } else if (arg === '--brief') {
      brief = true;
    } else if (arg === '--detailed') {
      detailed = true;
    } else if (arg === '--profile') {
      profile = true;
    } else if (!arg.startsWith('--')) {
      // Collect non-flag args as prompt
      if (!prompt) {
        prompt = arg;
      } else {
        // If no --text was provided, treat remaining as text
        if (!text) {
          text = arg;
        }
      }
    }
  }

  // Read file if specified
  if (filePath) {
    try {
      const resolvedPath = path.resolve(filePath);
      text = fs.readFileSync(resolvedPath, 'utf-8');
      console.log(`Read ${text.length} characters from ${filePath}`);
    } catch (err) {
      console.error(`Error reading file: ${filePath}`);
      process.exit(1);
    }
  }

  return { prompt, text, type, hebrew, brief, detailed, profile };
}

function buildSystemPrompt(options: ConsultOptions): string {
  const parts: string[] = [];

  // Set base role based on type
  if (options.type === 'process' || options.type === 'review') {
    parts.push('You are an expert consultant helping to review and improve workflows, processes, and work strategies.');
  } else if (options.type === 'ideas') {
    parts.push('You are a creative consultant and brainstorming partner. Generate innovative ideas and suggestions based on the context provided.');
  } else {
    parts.push('You are an expert writing consultant providing feedback on text.');
  }

  if (options.hebrew) {
    parts.push('Respond in Hebrew.');
    parts.push('Pay attention to Hebrew-specific conventions and context.');
  }

  if (options.type) {
    switch (options.type) {
      case 'grammar':
        parts.push('Focus on grammar, spelling, punctuation, and syntax errors.');
        parts.push('Point out specific errors and provide corrections.');
        break;
      case 'clarity':
        parts.push('Focus on readability, structure, and flow.');
        parts.push('Identify confusing sentences and suggest clearer alternatives.');
        break;
      case 'style':
        parts.push('Focus on tone, voice, and word choice.');
        parts.push('Suggest ways to make the writing more engaging or appropriate.');
        break;
      case 'academic':
        parts.push('Focus on academic writing conventions.');
        parts.push('Check for scholarly tone, proper citations style, and formal language.');
        parts.push('Ensure the writing follows academic standards (APA/AMA if applicable).');
        break;
      case 'creative':
        parts.push('Focus on creative elements: engagement, vivid language, impact.');
        parts.push('Suggest ways to make the writing more compelling and memorable.');
        break;
      case 'process':
        parts.push('Analyze the workflow or process described.');
        parts.push('Identify inefficiencies, bottlenecks, or areas for improvement.');
        parts.push('Suggest concrete steps to optimize the process.');
        parts.push('Consider automation opportunities and best practices.');
        break;
      case 'ideas':
        parts.push('Based on the context provided, generate creative and practical ideas.');
        parts.push('Think outside the box but keep suggestions actionable.');
        parts.push('Provide multiple options with pros and cons for each.');
        parts.push('Build on the existing context to suggest improvements or new directions.');
        break;
      case 'review':
        parts.push('Review the work or project described comprehensively.');
        parts.push('Identify strengths and weaknesses.');
        parts.push('Provide constructive feedback with specific recommendations.');
        parts.push('Suggest next steps or priorities.');
        break;
    }
  } else {
    // Auto-detect mode - let Gemini figure out what's needed
    parts.push(`Based on the request, automatically determine what type of help is needed:
- If it's about WRITING: check grammar, clarity, style, academic conventions as appropriate
- If it's about a PROCESS/WORKFLOW: analyze efficiency, suggest improvements
- If asking for IDEAS: brainstorm creative and practical suggestions
- If asking for REVIEW: provide comprehensive feedback with strengths, weaknesses, next steps

Adapt your response to what the user actually needs.`);
  }

  if (options.brief) {
    parts.push('Keep your response brief: 1-3 sentences with key points only.');
  } else if (options.detailed) {
    parts.push('Provide comprehensive, detailed feedback with examples and explanations.');
  } else {
    parts.push('Provide focused feedback with specific suggestions.');
  }

  // Add researcher profile if requested
  if (options.profile) {
    parts.push('\n' + RESEARCHER_PROFILE);
  }

  return parts.join('\n');
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (!options.prompt && !options.text) {
    console.error('Usage: npx tsx consult.ts "Your question" --text "Context or text"');
    console.error('       npx tsx consult.ts "Your question" --file path/to/file.md');
    console.error('');
    console.error('Options:');
    console.error('  --text "..."    Context or text to consult about');
    console.error('  --file PATH     Read context from file');
    console.error('  --type TYPE     Consultation type:');
    console.error('                  Writing: grammar, clarity, style, academic, creative');
    console.error('                  Work:    process, ideas, review');
    console.error('  --hebrew        Hebrew mode');
    console.error('  --profile       Include researcher profile (Elad Refoua context)');
    console.error('  --brief         Short response');
    console.error('  --detailed      Comprehensive feedback');
    process.exit(1);
  }

  if (!process.env.GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY not found');
    console.error('Create .env file with: GEMINI_API_KEY=your_key_here');
    process.exit(1);
  }

  const ai = new GoogleGenAI({
    apiKey: process.env.GEMINI_API_KEY,
  });

  const systemPrompt = buildSystemPrompt(options);

  let userMessage = options.prompt || 'Please review and provide feedback.';
  if (options.text) {
    userMessage += `\n\n---\nCONTEXT:\n---\n${options.text}`;
  }

  const fullPrompt = systemPrompt + '\n\n' + userMessage;

  console.log('='.repeat(60));
  console.log('SENT TO GEMINI:');
  console.log('='.repeat(60));
  console.log(fullPrompt);
  console.log('='.repeat(60));
  console.log('\nWaiting for response...\n');

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: [
        { role: 'user', parts: [{ text: fullPrompt }] }
      ],
    });

    const responseText = response.candidates?.[0]?.content?.parts?.[0]?.text;

    if (responseText) {
      console.log('='.repeat(60));
      console.log('GEMINI RESPONSE:');
      console.log('='.repeat(60));
      console.log(responseText);
      console.log('='.repeat(60));
    } else {
      console.error('No response received from Gemini');
    }
  } catch (error: any) {
    console.error('Error:', error.message || error);
    process.exit(1);
  }
}

main();
