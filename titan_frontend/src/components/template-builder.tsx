/**
 * TITAN Analytics Platform - Template Builder Component
 * Drag-and-drop template creation for non-technical users
 */

import React, { useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  IconPlus, 
  IconTrash, 
  IconGripVertical,
  IconChartBar,
  IconMoodSmile,
  IconTimeline,
  IconNetwork,
  IconAlertTriangle,
  IconBulb,
  IconTrendingUp,
  IconCategory,
  IconFileText
} from '@tabler/icons-react';

// Block type definitions
export interface BlockType {
  id: string;
  type: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  isEnterprise?: boolean;
}

export interface TemplateBlock {
  id: string;
  type: string;
  queryTemplate: string;
  position: number;
  filters: Record<string, unknown>;
  processingParams: Record<string, unknown>;
}

export interface TemplateBuilderProps {
  onSave?: (template: {
    name: string;
    description: string;
    blocks: TemplateBlock[];
  }) => void;
  initialBlocks?: TemplateBlock[];
  initialName?: string;
  initialDescription?: string;
}

// Available block types
const BLOCK_TYPES: BlockType[] = [
  {
    id: 'text',
    type: 'text',
    label: 'Text Analysis',
    description: 'Basic text content analysis',
    icon: <IconFileText size={20} />,
  },
  {
    id: 'plotly',
    type: 'plotly',
    label: 'Chart Visualization',
    description: 'Interactive Plotly charts',
    icon: <IconChartBar size={20} />,
  },
  {
    id: 'sentiment',
    type: 'sentiment',
    label: 'Sentiment Analysis',
    description: 'Analyze text emotions and sentiment',
    icon: <IconMoodSmile size={20} />,
  },
  {
    id: 'timeline',
    type: 'timeline',
    label: 'Timeline',
    description: 'Event timeline visualization',
    icon: <IconTimeline size={20} />,
  },
  {
    id: 'network',
    type: 'network',
    label: 'Network Graph',
    description: 'Entity relationship mapping',
    icon: <IconNetwork size={20} />,
  },
  {
    id: 'trend',
    type: 'trend',
    label: 'Trend Analysis',
    description: 'Identify emerging trends',
    icon: <IconTrendingUp size={20} />,
  },
  {
    id: 'clustering',
    type: 'clustering',
    label: 'Clustering',
    description: 'Automatic content grouping',
    icon: <IconCategory size={20} />,
  },
  {
    id: 'anomaly',
    type: 'anomaly',
    label: 'Anomaly Detection',
    description: 'Detect outliers and anomalies',
    icon: <IconAlertTriangle size={20} />,
    isEnterprise: true,
  },
  {
    id: 'recommendation',
    type: 'recommendation',
    label: 'Recommendations',
    description: 'AI-powered suggestions',
    icon: <IconBulb size={20} />,
    isEnterprise: true,
  },
];

export function TemplateBuilder({
  onSave,
  initialBlocks = [],
  initialName = '',
  initialDescription = '',
}: TemplateBuilderProps) {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [blocks, setBlocks] = useState<TemplateBlock[]>(initialBlocks);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  // Generate unique ID
  const generateId = () => `block_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;

  // Add a new block
  const addBlock = useCallback((blockType: BlockType) => {
    const newBlock: TemplateBlock = {
      id: generateId(),
      type: blockType.type,
      queryTemplate: '',
      position: blocks.length,
      filters: {},
      processingParams: {},
    };
    setBlocks([...blocks, newBlock]);
  }, [blocks]);

  // Remove a block
  const removeBlock = useCallback((id: string) => {
    setBlocks(blocks.filter(block => block.id !== id).map((block, index) => ({
      ...block,
      position: index,
    })));
  }, [blocks]);

  // Update block query
  const updateBlockQuery = useCallback((id: string, query: string) => {
    setBlocks(blocks.map(block => 
      block.id === id ? { ...block, queryTemplate: query } : block
    ));
  }, [blocks]);

  // Drag and drop handlers
  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newBlocks = [...blocks];
    const draggedBlock = newBlocks[draggedIndex];
    newBlocks.splice(draggedIndex, 1);
    newBlocks.splice(index, 0, draggedBlock);
    
    // Update positions
    const updatedBlocks = newBlocks.map((block, i) => ({
      ...block,
      position: i,
    }));
    
    setBlocks(updatedBlocks);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  // Save template
  const handleSave = () => {
    if (onSave) {
      onSave({
        name,
        description,
        blocks,
      });
    }
  };

  // Get block type info
  const getBlockTypeInfo = (type: string) => 
    BLOCK_TYPES.find(bt => bt.type === type) || BLOCK_TYPES[0];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Block Palette */}
      <div className="lg:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Block Types</CardTitle>
            <CardDescription>Click to add blocks to your template</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {BLOCK_TYPES.map(blockType => (
              <button
                key={blockType.id}
                onClick={() => addBlock(blockType)}
                className="w-full flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors text-left"
              >
                <div className="text-primary">{blockType.icon}</div>
                <div className="flex-1">
                  <div className="font-medium flex items-center gap-2">
                    {blockType.label}
                    {blockType.isEnterprise && (
                      <span className="text-xs bg-gradient-to-r from-purple-500 to-blue-500 text-white px-2 py-0.5 rounded-full">
                        Enterprise
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {blockType.description}
                  </div>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Template Editor */}
      <div className="lg:col-span-3 space-y-6">
        {/* Template Info */}
        <Card>
          <CardHeader>
            <CardTitle>Template Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="template-name">Template Name</Label>
              <Input
                id="template-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Analytics Template"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="template-description">Description</Label>
              <Input
                id="template-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what this template analyzes..."
              />
            </div>
          </CardContent>
        </Card>

        {/* Blocks List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Template Blocks</span>
              <span className="text-sm font-normal text-muted-foreground">
                {blocks.length} block{blocks.length !== 1 ? 's' : ''}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {blocks.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <IconPlus className="mx-auto h-12 w-12 opacity-50" />
                <p className="mt-2">No blocks added yet</p>
                <p className="text-sm">Click on block types to add them</p>
              </div>
            ) : (
              <div className="space-y-4">
                {blocks.map((block, index) => {
                  const blockType = getBlockTypeInfo(block.type);
                  return (
                    <div
                      key={block.id}
                      draggable
                      onDragStart={() => handleDragStart(index)}
                      onDragOver={(e) => handleDragOver(e, index)}
                      onDragEnd={handleDragEnd}
                      className={`border rounded-lg p-4 bg-card transition-all ${
                        draggedIndex === index ? 'opacity-50 border-primary' : ''
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="cursor-grab text-muted-foreground hover:text-foreground">
                          <IconGripVertical size={20} />
                        </div>
                        <div className="text-primary">{blockType.icon}</div>
                        <div className="flex-1 space-y-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="font-medium">{blockType.label}</span>
                              <span className="ml-2 text-xs text-muted-foreground">
                                Position {index + 1}
                              </span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeBlock(block.id)}
                              className="text-destructive hover:text-destructive"
                            >
                              <IconTrash size={16} />
                            </Button>
                          </div>
                          <div className="space-y-2">
                            <Label>Query Template</Label>
                            <Input
                              value={block.queryTemplate}
                              onChange={(e) => updateBlockQuery(block.id, e.target.value)}
                              placeholder="Enter your search query or analysis prompt..."
                            />
                            <p className="text-xs text-muted-foreground">
                              Use {'{topic}'} as a placeholder for dynamic content
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
          {blocks.length > 0 && (
            <CardFooter className="flex justify-end gap-4">
              <Button variant="outline" onClick={() => setBlocks([])}>
                Clear All
              </Button>
              <Button onClick={handleSave} disabled={!name.trim()}>
                Save Template
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  );
}

export default TemplateBuilder;
