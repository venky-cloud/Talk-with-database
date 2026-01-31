import { Link } from 'react-router-dom';
import { Database, Apple as Api, Table2, Layout } from 'lucide-react';

export default function Home() {
  const queryTypes = [
    {
      icon: Database,
      title: 'Text to SQL',
      description: 'Convert natural language to SQL queries',
      path: '/sql-query',
      color: 'from-green-400 to-emerald-600'
    },
    {
      icon: Api,
      title: 'Text to API',
      description: 'Generate API requests from text',
      path: '/api-query',
      color: 'from-purple-400 to-pink-600'
    },
    {
      icon: Database,
      title: 'Text to MongoDB',
      description: 'Transform text into MongoDB queries',
      path: '/mongodb-query',
      color: 'from-blue-400 to-blue-600'
    },
    {
      icon: Layout,
      title: 'MongoDB Schema',
      description: 'Explore MongoDB collections and relationships',
      path: '/mongodb-schema',
      color: 'from-teal-400 to-cyan-600'
    },
    {
      icon: Table2,
      title: 'SQL Schema',
      description: 'View MySQL database tables and ER diagram',
      path: '/schema',
      color: 'from-indigo-400 to-purple-600'
    },
    {
      icon: Database,
      title: 'MongoDB Workbench',
      description: 'Execute MongoDB queries directly',
      path: '/mongodb-workbench',
      color: 'from-green-500 to-emerald-700'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto py-24 px-4">
      {/* <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Talk with Database
      </h1> */}
      <p className="text-gray-400 mb-12 text-lg">Transform natural language into powerful database queries</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {queryTypes.map(({ icon: Icon, title, description, path, color }) => (
          <Link
            key={path}
            to={path}
            className="group border border-[#00ff00]/30 rounded-xl p-6 hover:bg-[#00ff00]/5 
              transition-all duration-300 hover-glow"
          >
            <div className={`h-12 w-12 rounded-lg bg-gradient-to-r ${color} p-3 mb-4`}>
              <Icon className="h-full w-full text-white" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2 group-hover:text-[#00ff00]">
              {title}
            </h2>
            <p className="text-gray-400">{description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}