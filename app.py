import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from services.competitor_finder import find_competitors
from services.content_extractor import extract_content
from services.bedrock_analyzer import analyze_with_bedrock

load_dotenv()

app = Flask(__name__)
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        company_url = data.get('company_url', '').strip()
        
        if not company_url:
            return jsonify({'error': 'Company URL is required'}), 400
        
        logger.info(f"Starting analysis for: {company_url}")
        
        # Step 1: Find competitors
        logger.info("Finding competitors...")
        competitors = find_competitors(company_url)
        if not competitors:
            return jsonify({'error': 'Could not find competitors'}), 404
        
        # Step 2: Extract content from competitor websites
        logger.info(f"Extracting content from {len(competitors)} competitors...")
        competitor_data = []
        for comp in competitors:
            content = extract_content(comp['url'])
            competitor_data.append({
                'name': comp['name'],
                'url': comp['url'],
                'content': content
            })
        
        # Step 3: Analyze with Bedrock Nova Pro
        logger.info("Analyzing with AWS Bedrock Nova Pro...")
        recommendations = analyze_with_bedrock(company_url, competitor_data)
        
        logger.info("Analysis completed successfully")
        return jsonify({
            'company_url': company_url,
            'competitors': competitor_data,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
