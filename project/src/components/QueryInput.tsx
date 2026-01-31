import { useState } from 'react';
import { ChevronDown, Play } from 'lucide-react';

const QUERY_TYPES = ['SQL', 'MongoDB', 'API'];

export default function QueryInput() {
  const [queryType, setQueryType] = useState('SQL');
  const [query, setQuery] = useState('');

  return (
    <div className="space-y-4 animate-gradient p-6 rounded-lg">
      <div className="flex space-x-2">
        <div className="relative">
          <select
            value={queryType}
            onChange={(e) => setQueryType(e.target.value)}
            className="appearance-none bg-black/50 border border-[#00ff00]/30 rounded-md px-3 py-2 pr-8 
              focus:outline-none focus:ring-2 focus:ring-[#00ff00]/50 text-[#00ff00]
              transition-all duration-300 hover:border-[#00ff00]/50"
          >
            {QUERY_TYPES.map(type => (
              <option key={type} value={type} className="bg-black">{type}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-3 h-4 w-4 text-[#00ff00]" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query in natural language..."
          className="flex-1 bg-black/50 border border-[#00ff00]/30 rounded-md px-3 py-2 
            focus:outline-none focus:ring-2 focus:ring-[#00ff00]/50 text-white
            placeholder:text-gray-500 transition-all duration-300 hover:border-[#00ff00]/50"
        />
      </div>
      <button
        className="w-full bg-[#00ff00]/10 text-[#00ff00] py-2 px-4 rounded-md 
          hover:bg-[#00ff00]/20 transition-all duration-300 hover-glow
          flex items-center justify-center space-x-2 border border-[#00ff00]/30"
      >
        <Play className="h-4 w-4" />
        <span>Run Query</span>
      </button>
    </div>
  );
}