import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

interface Column {
  name: string;
  type: string;
  nullable: string;
  key: string;
}

interface ERDiagramProps {
  tables: string[];
  columns: Record<string, Column[]>;
  foreign_keys: Array<{
    from_table: string;
    from_column: string;
    to_table: string;
    to_column: string;
    constraint_name: string;
  }>;
}

export default function ERDiagram({ tables, columns, foreign_keys }: ERDiagramProps) {
  // Layout nodes in a grid
  const nodeSpacingX = 350;
  const nodeSpacingY = 250;

  const nodes: Node[] = tables.map((table, i) => ({
    id: table,
    type: 'default',
    position: {
      x: (i % 3) * nodeSpacingX,
      y: Math.floor(i / 3) * nodeSpacingY,
    },
    data: {
      label: (
        <div className="bg-gray-800 border-2 border-green-400 rounded-lg shadow-lg min-w-[200px] max-w-[260px]">
          <div className="px-3 py-2 bg-green-600 text-white font-bold rounded-t-lg text-center">
            {table}
          </div>
          <div className="px-3 py-2">
            <table className="w-full text-xs">
              <tbody>
                {columns[table]?.map((col) => (
                  <tr key={col.name}>
                    <td className={`pr-2 font-mono ${col.key === 'PRI' ? 'text-yellow-400 font-bold' : 'text-gray-200'}`}>{col.name}</td>
                    <td className="pr-2 text-gray-400">{col.type}</td>
                    <td>{col.key === 'PRI' && <span className="text-yellow-400">PK</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ),
    },
  }));

  const edges: Edge[] = foreign_keys.map((fk, i) => ({
    id: `${fk.from_table}.${fk.from_column}->${fk.to_table}.${fk.to_column}`,
    source: fk.from_table,
    target: fk.to_table,
    label: `${fk.from_column} → ${fk.to_column}`,
    animated: true,
    style: { stroke: '#22d3ee', strokeWidth: 2 },
    labelStyle: { fill: '#22d3ee', fontWeight: 700 },
    type: 'smoothstep',
  }));

  return (
    <div style={{ width: '100%', height: '600px', background: 'transparent' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        minZoom={0.2}
        maxZoom={2}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
        panOnDrag
      >
        <MiniMap nodeColor={() => '#22d3ee'} nodeStrokeWidth={3} />
        <Controls />
        <Background color="#333" gap={20} />
      </ReactFlow>
    </div>
  );
}
