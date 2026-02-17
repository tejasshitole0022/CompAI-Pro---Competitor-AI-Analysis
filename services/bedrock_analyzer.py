import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def analyze_with_bedrock(company_url, competitor_data):
    """Analyze competitor content using AWS Bedrock Nova Pro"""
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        profile = os.getenv('AWS_PROFILE')
        
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        bedrock = session.client('bedrock-runtime', region_name=region)
        
        # Prepare prompt
        prompt = build_analysis_prompt(company_url, competitor_data)
        
        # Call Bedrock Nova Pro
        model_id = "amazon.nova-pro-v1:0"
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 2000,
                "temperature": 0.7
            }
        }
        
        logger.info(f"Calling Bedrock model: {model_id}")
        
        response = bedrock.converse(
            modelId=model_id,
            messages=request_body["messages"],
            inferenceConfig=request_body["inferenceConfig"]
        )
        
        # Extract response
        output = response['output']['message']['content'][0]['text']
        
        logger.info("Successfully received analysis from Bedrock")
        return parse_recommendations(output)
        
    except ClientError as e:
        logger.error(f"AWS Bedrock error: {e}")
        raise Exception(f"Bedrock API error: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Error analyzing with Bedrock: {e}")
        raise

def build_analysis_prompt(company_url, competitor_data):
    """Build the analysis prompt for Bedrock"""
    if not competitor_data:
        raise ValueError("No competitor data available for analysis")
    
    competitor_names = [comp['name'] for comp in competitor_data]
    
    competitors_text = "\n\n".join([
        f"Competitor: {comp['name']}\nWebsite: {comp['url']}\nContent: {comp['content'][:2000]}"
        for comp in competitor_data
    ])
    
    # Build competitor template dynamically
    competitor_template = "\n\n".join([
        f"""**{name}:**
- Use Case 1: [Brief description]
- Use Case 2: [Brief description]
- Use Case 3: [Brief description]"""
        for name in competitor_names
    ])
    
    prompt = f"""You are an AI business analyst specializing in identifying Generative AI use cases.

Company: {company_url}
Competitors to analyze: {', '.join(competitor_names)}

Analyze the following competitor websites and identify Generative AI use cases they have implemented:

{competitors_text}

IMPORTANT: Use EXACTLY these competitor names in your response: {', '.join(competitor_names)}

Provide your analysis in this exact format:

1. List of Generative AI Use Cases Implemented by Competitors

For each competitor, list EXACTLY 3 use cases:

{competitor_template}

2. Recommendations for {company_url}

Provide 5-7 detailed recommendations in this format:

**[Feature Name]:**
Priority: [High/Medium/Low]
Description: [2-3 sentences explaining the feature and its benefits]
Implementation: [Specific steps or technologies to use]
Expected Impact: [Business value and ROI]

Make each recommendation actionable and specific to the company's industry."""
    
    return prompt

def parse_recommendations(output):
    """Parse and structure the LLM output"""
    return {
        'analysis': output,
        'timestamp': None  # Will be added by frontend
    }
