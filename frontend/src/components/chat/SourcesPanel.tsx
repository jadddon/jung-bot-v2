'use client'
import { Book, Tag, Star, ExternalLink } from 'lucide-react'

interface JungSource {
  chunk_id: string
  source: string
  concepts: string[]
  quality: number
}

interface SourcesPanelProps {
  sources: JungSource[]
}

export const SourcesPanel = ({ sources }: SourcesPanelProps) => {
  if (sources.length === 0) {
    return (
      <div className="h-full flex flex-col">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-primary-900 flex items-center space-x-2">
            <Book size={20} />
            <span>Jung Text Sources</span>
          </h3>
        </div>
        
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center px-4">
            <div className="w-12 h-12 mx-auto mb-4 bg-therapeutic-100 rounded-full flex items-center justify-center">
              <Book size={24} className="text-therapeutic-600" />
            </div>
            <p className="text-sm text-primary-600 leading-relaxed">
              Sources from Jung's works will appear here when Dr. Jung references his writings in the conversation.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-primary-900 flex items-center space-x-2">
          <Book size={20} />
          <span>Jung Text Sources</span>
        </h3>
        <p className="text-sm text-primary-600 mt-1">
          Referenced in the last response ({sources.length} sources)
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-4 p-4">
          {sources.map((source, index) => (
            <div 
              key={source.chunk_id} 
              className="bg-therapeutic-50 rounded-lg p-4 border border-therapeutic-200 hover:border-therapeutic-300 transition-colors duration-200"
            >
              {/* Source Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 rounded-full bg-therapeutic-100 flex items-center justify-center">
                    <span className="text-xs font-semibold text-therapeutic-600">
                      {index + 1}
                    </span>
                  </div>
                  <h4 className="font-semibold text-therapeutic-900">
                    {source.source}
                  </h4>
                </div>
                
                {/* Quality Score */}
                <div className="flex items-center space-x-1 text-xs">
                  <Star 
                    size={12} 
                    className={`${
                      source.quality >= 0.8 
                        ? 'text-yellow-500 fill-current' 
                        : 'text-therapeutic-400'
                    }`} 
                  />
                  <span className="text-therapeutic-600">
                    {(source.quality * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Concepts */}
              {source.concepts && source.concepts.length > 0 && (
                <div className="mb-3">
                  <div className="flex items-center space-x-2 mb-2">
                    <Tag size={14} className="text-therapeutic-600" />
                    <span className="text-xs font-medium text-therapeutic-600 uppercase tracking-wide">
                      Key Concepts
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {source.concepts.map((concept, idx) => (
                      <span
                        key={idx}
                        className="inline-block px-2 py-1 text-xs bg-therapeutic-200 text-therapeutic-800 rounded-md font-medium"
                      >
                        {concept}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Chunk ID */}
              <div className="text-xs text-therapeutic-500 font-mono">
                ID: {source.chunk_id}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Footer */}
      <div className="card-footer">
        <div className="flex items-center justify-between text-xs text-primary-600">
          <span>Referenced from Carl Jung's Collected Works</span>
          <button className="flex items-center space-x-1 hover:text-primary-900 transition-colors">
            <ExternalLink size={12} />
            <span>Learn More</span>
          </button>
        </div>
      </div>
    </div>
  )
} 