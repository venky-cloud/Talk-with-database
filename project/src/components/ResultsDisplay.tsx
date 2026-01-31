import { Editor } from '@monaco-editor/react';

interface ResultsDisplayProps {
  query: string;
  results: any;
}

export default function ResultsDisplay({ query, results }: ResultsDisplayProps) {
  return (
    <div className="space-y-4">
      <div className="border border-[#00ff00]/30 rounded-md overflow-hidden transition-all duration-300 hover-glow">
        <div className="bg-black/50 px-4 py-2 border-b border-[#00ff00]/30">
          <h3 className="text-sm font-medium text-[#00ff00]">Generated Query</h3>
        </div>
        <Editor
          height="100px"
          defaultLanguage="sql"
          defaultValue={query}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            readOnly: true,
            scrollBeyondLastLine: false,
            fontSize: 14,
            padding: { top: 10, bottom: 10 },
          }}
        />
      </div>
      
      <div className="border border-[#00ff00]/30 rounded-md overflow-hidden transition-all duration-300 hover-glow">
        <div className="bg-black/50 px-4 py-2 border-b border-[#00ff00]/30">
          <h3 className="text-sm font-medium text-[#00ff00]">Results</h3>
        </div>
        <div className="p-4 bg-black/30">
          <pre className="whitespace-pre-wrap text-gray-300 font-mono text-sm">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}