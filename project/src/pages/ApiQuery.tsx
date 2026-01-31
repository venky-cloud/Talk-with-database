import { useState } from 'react';
import { Play } from 'lucide-react';
import { Editor } from '@monaco-editor/react';
import { post } from '../lib/api';

export default function ApiQuery() {
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<'rest' | 'graphql'>('rest');
  const [candidates, setCandidates] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const resp = await post<any, { candidates: string[]; mode: string; provider: string }>(
        '/api/generate',
        { text: input, mode }
      );
      setCandidates(resp.candidates || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-24 px-4 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Text to API Query
      </h1>
      <p className="text-gray-400 mb-8 text-lg">Convert natural language to REST or GraphQL requests</p>

      <div className="space-y-6">
        <div className="border border-[#00ff00]/30 rounded-lg p-6 bg-black/30">
          <div className="flex items-center gap-4 mb-4">
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as 'rest' | 'graphql')}
              className="bg-black/50 border border-[#00ff00]/30 rounded-md px-3 py-2 text-white"
            >
              <option value="rest">REST</option>
              <option value="graphql">GraphQL</option>
            </select>
          </div>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your API request in natural language..."
            className="w-full h-32 bg-black/50 border border-[#00ff00]/30 rounded-md px-4 py-2
              focus:outline-none focus:ring-2 focus:ring-[#00ff00]/50 text-white
              placeholder:text-gray-500 transition-all duration-300 hover:border-[#00ff00]/50"
          />
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="mt-4 w-full bg-[#00ff00]/10 text-[#00ff00] py-3 px-4 rounded-md 
              hover:bg-[#00ff00]/20 transition-all duration-300 hover-glow
              flex items-center justify-center space-x-2 border border-[#00ff00]/30
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-5 w-5" />
            <span>{loading ? 'Processing...' : 'Generate API Request'}</span>
          </button>
        </div>

        {candidates.length > 0 && (
          <div className="border border-[#00ff00]/30 rounded-lg overflow-hidden">
            <div className="bg-black/50 px-4 py-2 border-b border-[#00ff00]/30">
              <h3 className="text-[#00ff00] font-semibold">Generated {mode === 'rest' ? 'REST' : 'GraphQL'} Requests</h3>
            </div>
            <div className="grid grid-cols-1 gap-2 p-2">
              {candidates.map((cand, idx) => (
                <Editor
                  key={idx}
                  height="180px"
                  defaultLanguage={mode === 'rest' ? 'json' : 'graphql'}
                  value={cand}
                  theme="vs-dark"
                  options={{ minimap: { enabled: false }, readOnly: true, fontSize: 14 }}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}