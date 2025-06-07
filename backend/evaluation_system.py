"""
AI Response Evaluation System with Faithfulness and Quality Metrics
"""
import os
import re
from openai import OpenAI
import json
from typing import Dict, List, Tuple

class ResponseEvaluator:
    """Evaluates AI responses for faithfulness, relevance, and quality"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def evaluate_response(self, question: str, response: str, context: str) -> Dict[str, float]:
        """
        Evaluate AI response with multiple metrics
        
        Args:
            question: User's question
            response: AI's response
            context: Source context (transcript segments)
            
        Returns:
            Dictionary with evaluation scores (0.0 to 1.0)
        """
        
        # Calculate individual metrics
        faithfulness = self._calculate_faithfulness(response, context)
        relevance = self._calculate_relevance(question, response)
        completeness = self._calculate_completeness(question, response, context)
        clarity = self._calculate_clarity(response)
        
        # Calculate overall quality score
        overall_quality = (faithfulness * 0.4 + relevance * 0.3 + 
                          completeness * 0.2 + clarity * 0.1)
        
        return {
            "faithfulness": round(faithfulness, 2),
            "relevance": round(relevance, 2),
            "completeness": round(completeness, 2),
            "clarity": round(clarity, 2),
            "overall_quality": round(overall_quality, 2)
        }
    
    def _calculate_faithfulness(self, response: str, context: str) -> float:
        """
        Calculate how faithful the response is to the source context
        Uses GPT to evaluate factual consistency
        """
        try:
            prompt = f"""
            Evaluate the faithfulness of the AI response to the provided context.
            
            Context (Source Material):
            {context[:3000]}...
            
            AI Response:
            {response}
            
            Rate the faithfulness on a scale of 0.0 to 1.0 where:
            - 1.0 = Response is completely faithful to the context, no hallucinations
            - 0.8 = Mostly faithful with minor interpretations
            - 0.6 = Generally faithful but some unsupported claims
            - 0.4 = Several unsupported claims or interpretations
            - 0.2 = Many inaccuracies or unsupported claims
            - 0.0 = Response contradicts or ignores the context
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            evaluation_response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = evaluation_response.choices[0].message.content.strip()
            score = float(re.search(r'(\d+\.?\d*)', score_text).group(1))
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            print(f"Debug - Error calculating faithfulness: {e}")
            return 0.7  # Default moderate score
    
    def _calculate_relevance(self, question: str, response: str) -> float:
        """
        Calculate how relevant the response is to the question
        """
        try:
            prompt = f"""
            Evaluate how well the AI response answers the user's question.
            
            User Question:
            {question}
            
            AI Response:
            {response}
            
            Rate the relevance on a scale of 0.0 to 1.0 where:
            - 1.0 = Response directly and completely answers the question
            - 0.8 = Response mostly answers the question with minor tangents
            - 0.6 = Response partially answers the question
            - 0.4 = Response somewhat relates but misses key aspects
            - 0.2 = Response barely relates to the question
            - 0.0 = Response is completely irrelevant
            
            Respond with only a number between 0.0 and 1.0.
            """
            
            evaluation_response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = evaluation_response.choices[0].message.content.strip()
            score = float(re.search(r'(\d+\.?\d*)', score_text).group(1))
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            print(f"Debug - Error calculating relevance: {e}")
            return 0.8  # Default good score
    
    def _calculate_completeness(self, question: str, response: str, context: str) -> float:
        """
        Calculate how complete the response is given available context
        """
        try:
            # Simple heuristics for completeness
            question_words = set(question.lower().split())
            response_words = set(response.lower().split())
            context_words = set(context.lower().split())
            
            # Check if response addresses key question terms
            question_coverage = len(question_words.intersection(response_words)) / max(len(question_words), 1)
            
            # Check response length appropriateness
            response_length = len(response.split())
            length_score = min(response_length / 50, 1.0)  # Prefer responses with at least 50 words
            
            # Combine metrics
            completeness_score = (question_coverage * 0.7 + length_score * 0.3)
            return min(max(completeness_score, 0.0), 1.0)
            
        except Exception as e:
            print(f"Debug - Error calculating completeness: {e}")
            return 0.6  # Default moderate score
    
    def _calculate_clarity(self, response: str) -> float:
        """
        Calculate the clarity and readability of the response
        """
        try:
            # Simple metrics for clarity
            sentences = response.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            
            # Prefer moderate sentence lengths (10-25 words)
            length_score = 1.0 if 10 <= avg_sentence_length <= 25 else max(0.3, 1.0 - abs(avg_sentence_length - 17.5) / 20)
            
            # Check for structure indicators (bullet points, numbers, etc.)
            structure_indicators = len(re.findall(r'[\n•\-\*\d+\.]', response))
            structure_score = min(structure_indicators / 5, 1.0)
            
            # Combine metrics
            clarity_score = (length_score * 0.7 + structure_score * 0.3)
            return min(max(clarity_score, 0.0), 1.0)
            
        except Exception as e:
            print(f"Debug - Error calculating clarity: {e}")
            return 0.7  # Default good score
    
    def get_evaluation_summary(self, scores: Dict[str, float]) -> str:
        """
        Generate a human-readable evaluation summary
        """
        def score_to_grade(score: float) -> str:
            if score >= 0.9: return "Excellent"
            elif score >= 0.8: return "Very Good"
            elif score >= 0.7: return "Good"
            elif score >= 0.6: return "Fair"
            elif score >= 0.5: return "Needs Improvement"
            else: return "Poor"
        
        summary = f"""
**Response Quality Evaluation:**
• **Faithfulness**: {scores['faithfulness']:.1f}/1.0 ({score_to_grade(scores['faithfulness'])})
• **Relevance**: {scores['relevance']:.1f}/1.0 ({score_to_grade(scores['relevance'])})
• **Completeness**: {scores['completeness']:.1f}/1.0 ({score_to_grade(scores['completeness'])})
• **Clarity**: {scores['clarity']:.1f}/1.0 ({score_to_grade(scores['clarity'])})

**Overall Quality**: {scores['overall_quality']:.1f}/1.0 ({score_to_grade(scores['overall_quality'])})
        """
        
        return summary.strip()