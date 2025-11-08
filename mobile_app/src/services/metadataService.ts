// src/services/metadataService.ts
/**
 * Metadata Service - Multi-LLM Support
 * Supports Gemini, Claude, GPT-4, Ollama for generating music metadata
 */

export interface MetadataGenerationRequest {
  title?: string;
  artist?: string;
  description?: string;
}

export interface MetadataGenerationResult {
  genre?: string;
  mood?: string;
  bpm?: number;
  keySignature?: string;
  description?: string;
  tags?: string[];
}

export type AIBackend = 'gemini' | 'claude' | 'gpt4' | 'ollama' | 'manual';

export class MetadataService {
  private static instance: MetadataService;
  private apiKeys: Record<string, string> = {};
  private selectedBackend: AIBackend = 'manual';

  private constructor() {}

  static getInstance(): MetadataService {
    if (!MetadataService.instance) {
      MetadataService.instance = new MetadataService();
    }
    return MetadataService.instance;
  }

  /**
   * Set API key for a specific provider
   */
  setApiKey(provider: string, key: string): void {
    this.apiKeys[provider] = key;
  }

  /**
   * Set selected AI backend
   */
  setSelectedBackend(backend: AIBackend): void {
    this.selectedBackend = backend;
  }

  /**
   * Generate metadata using selected AI backend
   */
  async generateMetadata(
    request: MetadataGenerationRequest
  ): Promise<MetadataGenerationResult> {
    if (this.selectedBackend === 'manual') {
      return {
        genre: 'Unknown',
        mood: 'Unknown',
        description: 'Manual metadata entry',
      };
    }

    try {
      switch (this.selectedBackend) {
        case 'gemini':
          return await this.generateViaGemini(request);
        case 'claude':
          return await this.generateViaClaude(request);
        case 'gpt4':
          return await this.generateViaGPT4(request);
        case 'ollama':
          return await this.generateViaOllama(request);
        default:
          throw new Error(`Unknown backend: ${this.selectedBackend}`);
      }
    } catch (error) {
      console.error('Metadata generation failed:', error);
      throw error;
    }
  }

  /**
   * Generate metadata using Google Gemini
   */
  private async generateViaGemini(
    request: MetadataGenerationRequest
  ): Promise<MetadataGenerationResult> {
    const apiKey = this.apiKeys['gemini'];
    if (!apiKey) {
      throw new Error('Gemini API key not configured');
    }

    const prompt = this.buildMetadataPrompt(request);

    try {
      const response = await fetch(
        'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-goog-api-key': apiKey,
          },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
          }),
        }
      );

      const data = await response.json();
      return this.parseMetadataResponse(data.candidates?.[0]?.content?.parts?.[0]?.text || '');
    } catch (error) {
      console.error('Gemini API error:', error);
      throw error;
    }
  }

  /**
   * Generate metadata using Anthropic Claude
   */
  private async generateViaClaude(
    request: MetadataGenerationRequest
  ): Promise<MetadataGenerationResult> {
    const apiKey = this.apiKeys['claude'];
    if (!apiKey) {
      throw new Error('Claude API key not configured');
    }

    const prompt = this.buildMetadataPrompt(request);

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-3-sonnet-20240229',
          max_tokens: 500,
          messages: [{ role: 'user', content: prompt }],
        }),
      });

      const data = await response.json();
      return this.parseMetadataResponse(data.content?.[0]?.text || '');
    } catch (error) {
      console.error('Claude API error:', error);
      throw error;
    }
  }

  /**
   * Generate metadata using OpenAI GPT-4
   */
  private async generateViaGPT4(
    request: MetadataGenerationRequest
  ): Promise<MetadataGenerationResult> {
    const apiKey = this.apiKeys['openai'];
    if (!apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    const prompt = this.buildMetadataPrompt(request);

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: 'gpt-4',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 500,
        }),
      });

      const data = await response.json();
      return this.parseMetadataResponse(data.choices?.[0]?.message?.content || '');
    } catch (error) {
      console.error('OpenAI API error:', error);
      throw error;
    }
  }

  /**
   * Generate metadata using local Ollama
   */
  private async generateViaOllama(
    request: MetadataGenerationRequest
  ): Promise<MetadataGenerationResult> {
    const ollamaUrl = this.apiKeys['ollama'] || 'http://localhost:11434';
    const prompt = this.buildMetadataPrompt(request);

    try {
      const response = await fetch(`${ollamaUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'mistral',
          prompt: prompt,
          stream: false,
        }),
      });

      const data = await response.json();
      return this.parseMetadataResponse(data.response || '');
    } catch (error) {
      console.error('Ollama API error:', error);
      throw error;
    }
  }

  /**
   * Build prompt for metadata generation
   */
  private buildMetadataPrompt(request: MetadataGenerationRequest): string {
    const title = request.title || 'Unknown';
    const artist = request.artist || 'Unknown';

    return `Analyze the following song and provide metadata in JSON format:

Song Title: ${title}
Artist: ${artist}

Provide the following fields in your response (as JSON):
- genre: Primary music genre
- mood: Mood/emotional tone (e.g., happy, melancholic, energetic)
- bpm: Estimated tempo in beats per minute
- keySignature: Musical key (e.g., C major, D minor)
- description: Brief 2-3 sentence description
- tags: Array of 5-7 relevant tags

Response format:
{
  "genre": "...",
  "mood": "...",
  "bpm": ...,
  "keySignature": "...",
  "description": "...",
  "tags": [...]
}`;
  }

  /**
   * Parse metadata response from LLM
   */
  private parseMetadataResponse(response: string): MetadataGenerationResult {
    try {
      // Try to extract JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Failed to parse metadata response:', error);
    }

    // Return default if parsing fails
    return {
      genre: 'Unknown',
      mood: 'Unknown',
      description: 'Unable to generate metadata',
    };
  }
}

export const metadataService = MetadataService.getInstance();
