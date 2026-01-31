
import { useState, useEffect } from 'react';
import { Play, Database, Loader2 } from 'lucide-react';
import { post } from '../lib/api';

interface MongoDBResult {
  operation: string;
  count?: number;
  documents?: any[];
  inserted_id?: string;
  acknowledged?: boolean;
  matched_count?: number;
  modified_count?: number;
  deleted_count?: number;
}

export default function MongoDbQuery() {
  const [input, setInput] = useState(() => {
    return localStorage.getItem('mongoQueryInput') || '';
  });
  const [generatedQueries, setGeneratedQueries] = useState<string[]>(() => {
    const saved = localStorage.getItem('mongoQueryGenerated');
    return saved ? JSON.parse(saved) : [];
  });
  const [selectedQuery, setSelectedQuery] = useState(() => {
    return localStorage.getItem('mongoQuerySelected') || '';
  });
  const [results, setResults] = useState<MongoDBResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Save input to localStorage
  useEffect(() => {
    localStorage.setItem('mongoQueryInput', input);
  }, [input]);

  // Save generated queries to localStorage
  useEffect(() => {
    localStorage.setItem('mongoQueryGenerated', JSON.stringify(generatedQueries));
  }, [generatedQueries]);

  // Save selected query to localStorage
  useEffect(() => {
    localStorage.setItem('mongoQuerySelected', selectedQuery);
  }, [selectedQuery]);

  const handleGenerate = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setGeneratedQueries([]);
    setSelectedQuery('');
    setResults(null);

    try {
      // Try to get MongoDB schema, use mock if connection fails
      let schema;
      try {
        schema = await post<{ db_type: string }, any>('/mongodb/inspect', {
          db_type: 'mongodb'
        });
      } catch {
        // Use mock schema if MongoDB not connected
        schema = {
          collections: {
            'test': ['users', 'customers', 'orders', 'products']
          }
        };
      }

      // Generate MongoDB query candidates
      const response = await post<any, { candidates: string[]; candidates_dict: any[] }>(
        '/mongodb/generate',
        {
          text: input,
          db_schema: schema,
          n_candidates: 5
        }
      );

      if (response.candidates && response.candidates.length > 0) {
        setGeneratedQueries(response.candidates);
        setSelectedQuery(response.candidates[0]);
      } else {
        setError('No MongoDB queries generated. Try rephrasing your request.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate MongoDB query');
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedQuery) return;

    setExecuting(true);
    setError(null);
    setResults(null);

    try {
      // Parse the MongoDB query string to extract details
      // Support both simple queries and aggregation pipelines
      
      // Try to match aggregation: db.collection.aggregate([...])
      const aggMatch = selectedQuery.match(/db\.(\w+)\.aggregate\s*\(\s*\[([\s\S]*)\]\s*\)/);
      
      if (aggMatch) {
        // Handle aggregation pipeline
        const collection = aggMatch[1];
        const pipelineString = '[' + aggMatch[2] + ']';
        
        setError('Aggregation pipelines cannot be executed here. Copy the query and use MongoDB Workbench or MongoDB Compass to run it.');
        setResults({
          operation: 'aggregate',
          documents: [{
            info: 'Aggregation pipeline generated successfully',
            note: 'Use MongoDB Workbench to execute this query',
            query: selectedQuery
          }]
        });
        setExecuting(false);
        return;
      }
      
      // Try to match simple query: db.collection.find({...})
      const simpleMatch = selectedQuery.match(/db\.(\w+)\.(\w+)\((.*)\)/s);
      
      if (!simpleMatch) {
        throw new Error('Invalid MongoDB query format. Expected: db.collection.operation({query})');
      }

      const collection = simpleMatch[1];
      const operation = simpleMatch[2];
      const queryString = simpleMatch[3] || '{}';
      
      let query = {};
      try {
        // Try to parse the query JSON
        query = JSON.parse(queryString || '{}');
      } catch (parseError) {
        throw new Error('Invalid JSON in query. Make sure to use proper JSON format.');
      }

      // Use default database
      const result = await post<any, MongoDBResult>('/mongodb/execute', {
        db_name: 'mydb',
        collection_name: collection,
        query: query,
        operation: operation,
        document: operation === 'insertOne' || operation === 'insert' ? query : undefined
      });

      setResults(result);
    } catch (err: any) {
      setError(err.message || 'Failed to execute MongoDB query');
    } finally {
      setExecuting(false);
    }
  };

  useEffect(() => {
    // Load schema on mount if needed
  }, []);

  return (
    <div className="py-24 px-4 max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Text to MongoDB
      </h1>
      <p className="text-gray-400 mb-8 text-lg">Transform text into MongoDB queries</p>

      <div className="space-y-6">
        <div className="border border-[#00ff00]/30 rounded-lg p-6 bg-black/30">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Try asking:
• Find all active users
• Get customers with age greater than 25
• Search for products with price less than 100
• Show documents where status is pending
• Find users created in the last month
• Count total orders
• Delete inactive records"
            className="w-full h-32 bg-black/50 border border-[#00ff00]/30 rounded-md px-4 py-2
              focus:outline-none focus:ring-2 focus:ring-[#00ff00]/50 text-white
              placeholder:text-gray-500 transition-all duration-300 hover:border-[#00ff00]/50"
          />
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="mt-4 w-full bg-[#00ff00]/10 text-[#00ff00] py-3 px-4 rounded-md
              hover:bg-[#00ff00]/20 transition-all duration-300 hover-glow
              flex items-center justify-center space-x-2 border border-[#00ff00]/30
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                <span>Generate MongoDB Query</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="border border-red-500/30 rounded-lg p-4 bg-red-900/20">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {selectedQuery && (
          <div className="border border-[#00ff00]/30 rounded-lg overflow-hidden">
            <div className="bg-black/50 px-4 py-2 border-b border-[#00ff00]/30 flex items-center justify-between">
              <h3 className="text-[#00ff00] font-semibold">Generated MongoDB Query</h3>
              <button
                onClick={handleExecute}
                disabled={executing}
                className="px-4 py-1 bg-[#00ff00]/10 text-[#00ff00] rounded-md hover:bg-[#00ff00]/20 
                  transition-all duration-300 border border-[#00ff00]/30 text-sm
                  disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executing ? 'Executing...' : 'Execute'}
              </button>
            </div>
            <div className="p-4 bg-black/30">
              <pre className="text-[#00ff00] font-mono text-sm overflow-x-auto">
                {selectedQuery}
              </pre>
              {generatedQueries.length > 1 && (
                <div className="mt-4 space-y-2">
                  <p className="text-gray-400 text-sm">Other candidates:</p>
                  {generatedQueries.slice(1).map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedQuery(q)}
                      className="block w-full text-left px-3 py-2 bg-black/50 border border-gray-700 
                        rounded hover:border-[#00ff00]/30 transition-all text-sm text-gray-400 
                        hover:text-[#00ff00] font-mono"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {results && (
          <div className="border border-[#00ff00]/30 rounded-lg overflow-hidden">
            <div className="bg-black/50 px-4 py-2 border-b border-[#00ff00]/30">
              <h3 className="text-[#00ff00] font-semibold flex items-center gap-2">
                <Database className="w-4 h-4" />
                MongoDB Results
              </h3>
            </div>
            <div className="p-4 bg-black/30">
              <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                  <span className="text-gray-400">Operation:</span>
                  <span className="text-[#00ff00] ml-2 font-mono">{results.operation}</span>
                </div>
                {results.count !== undefined && (
                  <div>
                    <span className="text-gray-400">Count:</span>
                    <span className="text-[#00ff00] ml-2">{results.count}</span>
                  </div>
                )}
                {results.matched_count !== undefined && (
                  <div>
                    <span className="text-gray-400">Matched:</span>
                    <span className="text-[#00ff00] ml-2">{results.matched_count}</span>
                  </div>
                )}
                {results.modified_count !== undefined && (
                  <div>
                    <span className="text-gray-400">Modified:</span>
                    <span className="text-[#00ff00] ml-2">{results.modified_count}</span>
                  </div>
                )}
              </div>

              {results.documents && results.documents.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-gray-300 font-semibold">Documents:</h4>
                  <div className="max-h-96 overflow-y-auto">
                    {results.documents.map((doc, index) => (
                      <div key={index} className="bg-black/50 border border-gray-600 rounded p-3 mb-2">
                        <pre className="whitespace-pre-wrap text-gray-300 font-mono text-sm">
                          {JSON.stringify(doc, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {results.inserted_id && (
                <div className="mt-4 p-3 bg-green-900/20 border border-green-500/30 rounded">
                  <p className="text-green-400 font-mono text-sm">
                    Inserted document with ID: {results.inserted_id}
                  </p>
                </div>
              )}

              {results.acknowledged === false && (
                <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded">
                  <p className="text-red-400 text-sm">
                    Operation was not acknowledged by MongoDB
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

