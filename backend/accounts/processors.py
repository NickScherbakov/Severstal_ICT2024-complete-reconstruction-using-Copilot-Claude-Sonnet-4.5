"""
TITAN Analytics Platform - Data Processors Registry
Enterprise-ready data processing system with AI/ML capabilities

Features:
- Multi-LLM support (YandexGPT, OpenAI, Anthropic)
- Anomaly detection and pattern recognition
- Recommendation engine
- Streaming data processing support
- Extensible processor architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
import json
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers for multi-LLM integration"""
    YANDEX_GPT = 'yandexgpt'
    YANDEX_GPT_LITE = 'yandexgpt-lite'
    OPENAI_GPT4 = 'gpt-4'
    OPENAI_GPT35 = 'gpt-3.5-turbo'
    ANTHROPIC_CLAUDE = 'claude-3'
    LOCAL = 'local'


@dataclass
class ProcessorMetadata:
    """Metadata for processor discovery and documentation"""
    name: str
    description: str
    category: str
    supported_data_types: List[str]
    output_types: List[str]
    requires_llm: bool = False
    is_enterprise: bool = False
    version: str = '1.0.0'


class DataProcessor(ABC):
    """
    Base class for data processors
    
    Enterprise-ready processor with:
    - Metadata for discovery
    - Multi-LLM support
    - Streaming capability
    - Error handling and logging
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        """Return processor metadata for documentation"""
        return ProcessorMetadata(
            name=self.get_name(),
            description=self.__doc__ or '',
            category='general',
            supported_data_types=['text'],
            output_types=['json'],
        )
    
    @abstractmethod
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        """Check if processor can handle this data type"""
        pass
    
    @abstractmethod
    def process(self, data: Any, params: Dict) -> Dict:
        """Process data and return representation"""
        pass
    
    def process_stream(self, data: Any, params: Dict, callback: Callable[[Dict], None]) -> None:
        """
        Process data in streaming mode (for real-time analytics)
        Default implementation calls regular process method
        """
        result = self.process(data, params)
        callback(result)
    
    def get_name(self) -> str:
        """Return processor name"""
        return self.__class__.__name__
    
    def validate_data(self, data: Any) -> bool:
        """Validate input data before processing"""
        return data is not None


class LLMIntegration:
    """
    Multi-LLM integration layer
    Supports switching between different LLM providers
    """
    
    @staticmethod
    def get_llm_response(prompt: str, provider: str = 'yandexgpt', params: Dict = None) -> str:
        """
        Get response from configured LLM provider
        
        Args:
            prompt: The prompt to send to LLM
            provider: LLM provider identifier
            params: Additional parameters for the LLM
        
        Returns:
            String response from the LLM
        """
        params = params or {}
        
        if provider in ['yandexgpt', 'yandexgpt-lite']:
            return LLMIntegration._call_yandex_gpt(prompt, provider, params)
        elif provider in ['gpt-4', 'gpt-3.5-turbo']:
            return LLMIntegration._call_openai(prompt, provider, params)
        elif provider in ['claude-3']:
            return LLMIntegration._call_anthropic(prompt, provider, params)
        else:
            # Fallback to YandexGPT
            return LLMIntegration._call_yandex_gpt(prompt, 'yandexgpt', params)
    
    @staticmethod
    def _call_yandex_gpt(prompt: str, model: str, params: Dict) -> str:
        """Call YandexGPT API"""
        from search.yagpt import ask_yagpt
        from analyst.settings import YANDEX_SEARCH_API_TOKEN
        return ask_yagpt(prompt, YANDEX_SEARCH_API_TOKEN, model)
    
    @staticmethod
    def _call_openai(prompt: str, model: str, params: Dict) -> str:
        """
        Call OpenAI API
        Requires OPENAI_API_KEY in settings
        """
        try:
            from django.conf import settings
            from openai import OpenAI
            
            api_key = getattr(settings, 'OPENAI_API_KEY', '')
            if not api_key:
                logger.warning("OpenAI API key not configured, falling back to YandexGPT")
                return LLMIntegration._call_yandex_gpt(prompt, 'yandexgpt', params)
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=params.get('temperature', 0.7),
                max_tokens=params.get('max_tokens', 1024)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMIntegration._call_yandex_gpt(prompt, 'yandexgpt', params)
    
    @staticmethod
    def _call_anthropic(prompt: str, model: str, params: Dict) -> str:
        """
        Call Anthropic Claude API
        Requires ANTHROPIC_API_KEY in settings
        """
        try:
            from django.conf import settings
            import anthropic
            
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
            if not api_key:
                logger.warning("Anthropic API key not configured, falling back to YandexGPT")
                return LLMIntegration._call_yandex_gpt(prompt, 'yandexgpt', params)
            
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=params.get('max_tokens', 1024),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return LLMIntegration._call_yandex_gpt(prompt, 'yandexgpt', params)


class ProcessorRegistry:
    """
    Registry for data processors
    
    Features:
    - Processor discovery and documentation
    - Category-based filtering
    - Enterprise processor support
    """
    _processors: List[DataProcessor] = []
    _initialized = False
    
    @classmethod
    def register(cls, processor: DataProcessor):
        """Register a new processor"""
        if processor not in cls._processors:
            cls._processors.append(processor)
            logger.info(f"✅ Registered processor: {processor.get_name()}")
    
    @classmethod
    def unregister(cls, processor_name: str) -> bool:
        """Unregister a processor by name"""
        for i, p in enumerate(cls._processors):
            if p.get_name() == processor_name:
                cls._processors.pop(i)
                return True
        return False
    
    @classmethod
    def get_processor(cls, block_type: str, data_type: str = 'text') -> Optional[DataProcessor]:
        """Find appropriate processor for block type"""
        for processor in cls._processors:
            if processor.can_process(block_type, data_type):
                return processor
        return None
    
    @classmethod
    def list_processors(cls) -> List[str]:
        """Return list of registered processor names"""
        return [p.get_name() for p in cls._processors]
    
    @classmethod
    def get_processors_metadata(cls) -> List[Dict]:
        """Return metadata for all registered processors"""
        return [
            {
                'name': p.metadata.name,
                'description': p.metadata.description,
                'category': p.metadata.category,
                'supported_data_types': p.metadata.supported_data_types,
                'output_types': p.metadata.output_types,
                'requires_llm': p.metadata.requires_llm,
                'is_enterprise': p.metadata.is_enterprise,
                'version': p.metadata.version,
            }
            for p in cls._processors
        ]
    
    @classmethod
    def get_by_category(cls, category: str) -> List[DataProcessor]:
        """Get processors by category"""
        return [p for p in cls._processors if p.metadata.category == category]
    
    @classmethod
    def initialize(cls):
        """Initialize all base processors"""
        if cls._initialized:
            return
        
        # Core processors
        cls.register(SentimentAnalysisProcessor())
        cls.register(NetworkGraphProcessor())
        cls.register(TimelineProcessor())
        cls.register(ComparisonProcessor())
        cls.register(ForecastProcessor())
        cls.register(TableProcessor())
        
        # Advanced processors (NEW)
        cls.register(AnomalyDetectionProcessor())
        cls.register(RecommendationProcessor())
        cls.register(TrendAnalysisProcessor())
        cls.register(ClusteringProcessor())
        cls.register(SummaryProcessor())
        
        cls._initialized = True
        logger.info(f"🚀 TITAN Analytics: Initialized {len(cls._processors)} processors")


class SentimentAnalysisProcessor(DataProcessor):
    """
    Sentiment analysis processor using AI
    
    Analyzes text sentiment with multi-LLM support:
    - Positive/negative/neutral classification
    - Emotional intensity scoring
    - Key emotion extraction
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='SentimentAnalysisProcessor',
            description='Analyze text sentiment and emotions',
            category='nlp',
            supported_data_types=['text'],
            output_types=['json', 'visualization'],
            requires_llm=True,
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'sentiment'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """
        Analyze text sentiment
        
        Args:
            data: Text data to analyze
            params: Processing parameters (model, detailed, etc.)
        
        Returns:
            Dict with sentiment analysis results
        """
        if not self.validate_data(data):
            return {'type': 'sentiment', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        
        prompt = f"""Analyze the sentiment of the following text.

Determine:
1. Overall sentiment: positive, negative, or neutral
2. Emotional intensity (1-10)
3. Key emotions
4. Main reasons for the sentiment

Return result in JSON format:
{{
  "sentiment": "positive|negative|neutral",
  "score": 0-10,
  "emotions": ["emotion1", "emotion2"],
  "reasons": ["reason1", "reason2"],
  "summary": "brief summary"
}}

Text: {text[:2000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                analysis = json.loads(result)
            except json.JSONDecodeError:
                analysis = {'summary': result}
            
            return {
                'type': 'sentiment',
                'analysis': analysis,
                'raw_text': result,
                'visualization': {
                    'type': 'sentiment_gauge',
                    'value': analysis.get('score', 5) if isinstance(analysis, dict) else 5,
                    'sentiment': analysis.get('sentiment', 'neutral') if isinstance(analysis, dict) else 'neutral'
                }
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'type': 'sentiment', 'error': f'Analysis error: {str(e)}'}


class NetworkGraphProcessor(DataProcessor):
    """
    Network graph processor for entity relationship extraction
    
    Builds relationship graphs between entities:
    - Organizations, people, events
    - Connection strength and types
    - Cytoscape visualization support
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='NetworkGraphProcessor',
            description='Build entity relationship graphs',
            category='visualization',
            supported_data_types=['text'],
            output_types=['json', 'graph'],
            requires_llm=True,
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'network'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Build relationship graph from text"""
        if not self.validate_data(data):
            return {'type': 'network', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        
        prompt = f"""Extract all important entities (organizations, people, events) and their relationships from the text.

Return result in JSON format:
{{
  "nodes": [
    {{"id": "node1", "label": "Name", "type": "organization|person|event"}},
    {{"id": "node2", "label": "Name", "type": "organization|person|event"}}
  ],
  "edges": [
    {{"from": "node1", "to": "node2", "label": "relationship type", "weight": 1-10}}
  ]
}}

Text: {text[:2000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                graph_data = json.loads(result)
            except json.JSONDecodeError:
                graph_data = {
                    'nodes': [{'id': '1', 'label': 'Data', 'type': 'data'}],
                    'edges': []
                }
            
            return {
                'type': 'network',
                'graph_data': graph_data,
                'visualization': 'cytoscape',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Network graph error: {e}")
            return {'type': 'network', 'error': f'Graph building error: {str(e)}'}


class TimelineProcessor(DataProcessor):
    """
    Timeline processor for event extraction
    
    Extracts events with dates and builds timelines:
    - Date parsing and normalization
    - Event importance scoring
    - Interactive timeline visualization
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='TimelineProcessor',
            description='Build event timelines from text',
            category='visualization',
            supported_data_types=['text'],
            output_types=['json', 'timeline'],
            requires_llm=True,
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'timeline'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Extract events and build timeline"""
        if not self.validate_data(data):
            return {'type': 'timeline', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        
        prompt = f"""Extract all event mentions with dates from the text.

Return result in JSON format:
{{
  "events": [
    {{
      "date": "YYYY-MM-DD",
      "title": "Brief event title",
      "description": "Description",
      "importance": 1-10
    }}
  ]
}}

If exact date is unknown, use approximate or "unknown".

Text: {text[:2000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                timeline_data = json.loads(result)
            except json.JSONDecodeError:
                timeline_data = {'events': []}
            
            return {
                'type': 'timeline',
                'timeline_data': timeline_data,
                'visualization': 'timeline',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Timeline error: {e}")
            return {'type': 'timeline', 'error': f'Timeline building error: {str(e)}'}


class ComparisonProcessor(DataProcessor):
    """
    Comparative analysis processor
    
    Features:
    - Multi-aspect comparison
    - Scoring and ranking
    - Radar chart visualization
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='ComparisonProcessor',
            description='Perform comparative analysis',
            category='analysis',
            supported_data_types=['text'],
            output_types=['json', 'radar_chart'],
            requires_llm=True,
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'comparison'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Perform comparative analysis"""
        if not self.validate_data(data):
            return {'type': 'comparison', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        comparison_items = params.get('items', [])
        
        if comparison_items:
            prompt = f"""Compare the following aspects: {', '.join(comparison_items)}

Based on text:
{text[:2000]}

Return result in JSON format:
{{
  "comparison": [
    {{
      "item": "aspect name",
      "value": "value/description",
      "score": 1-10
    }}
  ],
  "summary": "overall conclusion"
}}"""
        else:
            prompt = f"""Perform comparative analysis of information in the text.
Identify key aspects for comparison.

Text: {text[:2000]}

Return result in JSON format with comparison array."""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                comparison_data = json.loads(result)
            except json.JSONDecodeError:
                comparison_data = {'summary': result}
            
            return {
                'type': 'comparison',
                'comparison_data': comparison_data,
                'visualization': 'radar_chart',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return {'type': 'comparison', 'error': f'Comparison error: {str(e)}'}


class ForecastProcessor(DataProcessor):
    """
    Forecasting processor for predictive analytics
    
    Features:
    - Short/medium/long term forecasts
    - Scenario analysis
    - Risk and opportunity identification
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='ForecastProcessor',
            description='Generate forecasts and scenario analysis',
            category='analytics',
            supported_data_types=['text', 'numeric'],
            output_types=['json', 'forecast_chart'],
            requires_llm=True,
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'forecast'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Generate forecast based on data"""
        if not self.validate_data(data):
            return {'type': 'forecast', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        
        prompt = f"""Based on the presented information, make a forecast of the situation development.

Information:
{text[:2000]}

Return result in JSON format:
{{
  "forecast": {{
    "short_term": "near-term forecast",
    "medium_term": "medium-term forecast",
    "long_term": "long-term forecast"
  }},
  "scenarios": [
    {{
      "name": "scenario name",
      "probability": 0-100,
      "description": "description"
    }}
  ],
  "risks": ["risk1", "risk2"],
  "opportunities": ["opportunity1", "opportunity2"]
}}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                forecast_data = json.loads(result)
            except json.JSONDecodeError:
                forecast_data = {'forecast': {'summary': result}}
            
            return {
                'type': 'forecast',
                'forecast_data': forecast_data,
                'visualization': 'forecast_chart',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return {'type': 'forecast', 'error': f'Forecasting error: {str(e)}'}


class TableProcessor(DataProcessor):
    """
    Table data processor
    
    Features:
    - Automatic table extraction
    - Data formatting and normalization
    - CSV/Excel export support
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='TableProcessor',
            description='Process and display tabular data',
            category='data',
            supported_data_types=['json', 'csv', 'text'],
            output_types=['table'],
            requires_llm=False,
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'table'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Extract and format table data"""
        if not data:
            return {'type': 'table', 'error': 'No data to display'}
        
        if isinstance(data, dict) and 'data' in data:
            table_data = data['data']
            
            if isinstance(table_data, list) and len(table_data) > 0:
                return {
                    'type': 'table',
                    'table_data': {
                        'headers': list(table_data[0].keys()) if isinstance(table_data[0], dict) else [],
                        'rows': table_data
                    },
                    'visualization': 'table'
                }
        
        return {
            'type': 'table',
            'table_data': data,
            'visualization': 'table'
        }


# ============================================================================
# NEW ADVANCED PROCESSORS
# ============================================================================


class AnomalyDetectionProcessor(DataProcessor):
    """
    Anomaly Detection Processor (Enterprise Feature)
    
    Detects anomalies and outliers in data:
    - Statistical anomaly detection
    - Pattern deviation identification
    - Alert generation for unusual patterns
    
    Use cases:
    - Fraud detection
    - Quality monitoring
    - Security analysis
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='AnomalyDetectionProcessor',
            description='Detect anomalies and outliers in data',
            category='ml',
            supported_data_types=['text', 'numeric', 'timeseries'],
            output_types=['json', 'alert', 'visualization'],
            requires_llm=True,
            is_enterprise=True,
            version='1.0.0',
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'anomaly'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Detect anomalies in the data"""
        if not self.validate_data(data):
            return {'type': 'anomaly', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        sensitivity = params.get('sensitivity', 'medium')  # low, medium, high
        
        prompt = f"""Analyze the following data for anomalies and unusual patterns.

Sensitivity level: {sensitivity}

Identify:
1. Any unusual values or patterns
2. Deviations from expected behavior
3. Potential outliers or suspicious data points
4. Patterns that warrant attention

Return result in JSON format:
{{
  "anomalies": [
    {{
      "type": "value_outlier|pattern_deviation|trend_break|missing_data",
      "description": "Description of the anomaly",
      "severity": "low|medium|high|critical",
      "location": "Where in the data the anomaly was found",
      "recommendation": "Suggested action"
    }}
  ],
  "summary": {{
    "total_anomalies": 0,
    "critical_count": 0,
    "high_count": 0,
    "data_quality_score": 0-100,
    "overall_assessment": "description"
  }},
  "alerts": [
    {{
      "message": "Alert message",
      "priority": "low|medium|high|critical"
    }}
  ]
}}

Data to analyze:
{text[:3000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                anomaly_data = json.loads(result)
            except json.JSONDecodeError:
                anomaly_data = {
                    'anomalies': [],
                    'summary': {'total_anomalies': 0, 'overall_assessment': result}
                }
            
            return {
                'type': 'anomaly',
                'anomaly_data': anomaly_data,
                'visualization': 'anomaly_chart',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return {'type': 'anomaly', 'error': f'Anomaly detection error: {str(e)}'}


class RecommendationProcessor(DataProcessor):
    """
    Recommendation Engine Processor (Enterprise Feature)
    
    Generates personalized recommendations:
    - Content-based recommendations
    - Action recommendations based on analysis
    - Strategic suggestions
    
    Use cases:
    - Product recommendations
    - Content personalization
    - Strategic decision support
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='RecommendationProcessor',
            description='Generate intelligent recommendations',
            category='ml',
            supported_data_types=['text', 'json'],
            output_types=['json', 'list'],
            requires_llm=True,
            is_enterprise=True,
            version='1.0.0',
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'recommendation'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Generate recommendations based on data"""
        if not self.validate_data(data):
            return {'type': 'recommendation', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        context = params.get('context', 'general')
        user_profile = params.get('user_profile', {})
        
        prompt = f"""Based on the following data and context, generate personalized recommendations.

Context: {context}
User preferences: {json.dumps(user_profile) if user_profile else 'Not specified'}

Analyze the data and provide:
1. Immediate action recommendations
2. Strategic recommendations
3. Related content or resources
4. Prioritized next steps

Return result in JSON format:
{{
  "recommendations": [
    {{
      "id": "rec_1",
      "type": "action|content|strategy|improvement",
      "title": "Recommendation title",
      "description": "Detailed description",
      "priority": "high|medium|low",
      "confidence": 0-100,
      "reasoning": "Why this is recommended",
      "related_items": ["item1", "item2"]
    }}
  ],
  "summary": {{
    "total_recommendations": 0,
    "top_priority": "Most important recommendation",
    "quick_wins": ["Easy to implement items"],
    "long_term": ["Strategic items"]
  }}
}}

Data to analyze:
{text[:3000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                recommendation_data = json.loads(result)
            except json.JSONDecodeError:
                recommendation_data = {
                    'recommendations': [],
                    'summary': {'total_recommendations': 0, 'top_priority': result}
                }
            
            return {
                'type': 'recommendation',
                'recommendation_data': recommendation_data,
                'visualization': 'recommendation_list',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return {'type': 'recommendation', 'error': f'Recommendation error: {str(e)}'}


class TrendAnalysisProcessor(DataProcessor):
    """
    Trend Analysis Processor
    
    Identifies and analyzes trends in data:
    - Trend direction and strength
    - Seasonal patterns
    - Emerging topics
    
    Use cases:
    - Market trend analysis
    - Topic monitoring
    - Performance tracking
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='TrendAnalysisProcessor',
            description='Identify and analyze trends',
            category='analytics',
            supported_data_types=['text', 'timeseries'],
            output_types=['json', 'trend_chart'],
            requires_llm=True,
            version='1.0.0',
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'trend'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Analyze trends in the data"""
        if not self.validate_data(data):
            return {'type': 'trend', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        
        prompt = f"""Analyze the following data for trends and patterns.

Identify:
1. Overall trend direction (growing, declining, stable)
2. Key emerging topics or themes
3. Seasonal or cyclical patterns
4. Trend strength and confidence

Return result in JSON format:
{{
  "trends": [
    {{
      "name": "Trend name",
      "direction": "up|down|stable",
      "strength": 0-100,
      "description": "Description",
      "start_period": "When trend started",
      "key_drivers": ["driver1", "driver2"]
    }}
  ],
  "emerging_topics": [
    {{
      "topic": "Topic name",
      "relevance": 0-100,
      "growth_rate": "rapid|moderate|slow"
    }}
  ],
  "summary": {{
    "overall_direction": "up|down|stable",
    "key_insight": "Main takeaway",
    "forecast": "Expected future direction"
  }}
}}

Data to analyze:
{text[:3000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                trend_data = json.loads(result)
            except json.JSONDecodeError:
                trend_data = {'summary': {'key_insight': result}}
            
            return {
                'type': 'trend',
                'trend_data': trend_data,
                'visualization': 'trend_chart',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {'type': 'trend', 'error': f'Trend analysis error: {str(e)}'}


class ClusteringProcessor(DataProcessor):
    """
    Clustering Processor
    
    Groups and categorizes data:
    - Automatic topic clustering
    - Entity grouping
    - Category suggestion
    
    Use cases:
    - Content organization
    - Customer segmentation
    - Topic modeling
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='ClusteringProcessor',
            description='Group and categorize data',
            category='ml',
            supported_data_types=['text', 'json'],
            output_types=['json', 'cluster_chart'],
            requires_llm=True,
            version='1.0.0',
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'clustering'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Cluster and categorize data"""
        if not self.validate_data(data):
            return {'type': 'clustering', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        num_clusters = params.get('num_clusters', 'auto')
        
        prompt = f"""Analyze and cluster the following data into meaningful groups.

Number of clusters: {num_clusters}

For each cluster, identify:
1. Main theme or characteristic
2. Key items belonging to this cluster
3. Cluster importance/size

Return result in JSON format:
{{
  "clusters": [
    {{
      "id": "cluster_1",
      "name": "Cluster name",
      "description": "What defines this cluster",
      "size": "Number of items or percentage",
      "key_terms": ["term1", "term2"],
      "representative_items": ["item1", "item2"],
      "importance": 0-100
    }}
  ],
  "summary": {{
    "total_clusters": 0,
    "largest_cluster": "Name of largest cluster",
    "clustering_quality": "high|medium|low",
    "insights": "Key insights from clustering"
  }}
}}

Data to analyze:
{text[:3000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                cluster_data = json.loads(result)
            except json.JSONDecodeError:
                cluster_data = {'clusters': [], 'summary': {'insights': result}}
            
            return {
                'type': 'clustering',
                'cluster_data': cluster_data,
                'visualization': 'cluster_chart',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Clustering error: {e}")
            return {'type': 'clustering', 'error': f'Clustering error: {str(e)}'}


class SummaryProcessor(DataProcessor):
    """
    Summary Processor
    
    Generates concise summaries:
    - Executive summaries
    - Key points extraction
    - Action items identification
    
    Use cases:
    - Document summarization
    - Meeting notes
    - Report generation
    """
    
    @property
    def metadata(self) -> ProcessorMetadata:
        return ProcessorMetadata(
            name='SummaryProcessor',
            description='Generate concise summaries',
            category='nlp',
            supported_data_types=['text'],
            output_types=['text', 'json'],
            requires_llm=True,
            version='1.0.0',
        )
    
    def can_process(self, block_type: str, data_type: str = 'text') -> bool:
        return block_type == 'summary'
    
    def process(self, data: Any, params: Dict) -> Dict:
        """Generate summary of the data"""
        if not self.validate_data(data):
            return {'type': 'summary', 'error': 'No data for analysis'}
        
        text = data.get('data') if isinstance(data, dict) else str(data)
        summary_type = params.get('type', 'executive')  # executive, detailed, bullet_points
        max_length = params.get('max_length', 500)
        
        prompt = f"""Create a {summary_type} summary of the following content.

Maximum length: {max_length} words

Include:
1. Main points and key takeaways
2. Important facts and figures
3. Action items (if applicable)
4. Conclusions

Return result in JSON format:
{{
  "summary": {{
    "title": "Summary title",
    "executive_summary": "Brief overview (2-3 sentences)",
    "key_points": ["point1", "point2", "point3"],
    "details": "Detailed summary",
    "action_items": ["action1", "action2"],
    "conclusions": "Final conclusions"
  }},
  "metadata": {{
    "original_length": "approximate word count of original",
    "summary_length": "word count of summary",
    "compression_ratio": "percentage"
  }}
}}

Content to summarize:
{text[:4000]}"""
        
        try:
            provider = params.get('model', 'yandexgpt')
            result = LLMIntegration.get_llm_response(prompt, provider, params)
            
            try:
                summary_data = json.loads(result)
            except json.JSONDecodeError:
                summary_data = {
                    'summary': {
                        'executive_summary': result,
                        'key_points': [],
                        'details': result
                    }
                }
            
            return {
                'type': 'summary',
                'summary_data': summary_data,
                'visualization': 'text',
                'raw_text': result
            }
        except Exception as e:
            logger.error(f"Summary error: {e}")
            return {'type': 'summary', 'error': f'Summary error: {str(e)}'}


# Automatic initialization on module import
ProcessorRegistry.initialize()
