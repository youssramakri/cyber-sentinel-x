from flask import Flask, request, jsonify
from flask_cors import CORS
from app.cms_scanner.cms_detector import CMSDetector
from app.cms_scanner.vulnerability_scanner import VulnerabilityScanner

app = Flask(__name__)
CORS(app)

@app.route('/api/scan/cms', methods=['POST'])
def scan_cms():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        # Détection CMS
        detector = CMSDetector()
        cms_info = detector.detect_cms(url)
        
        # Scan vulnérabilités
        scanner = VulnerabilityScanner()
        vulnerabilities = scanner.scan_vulnerabilities(cms_info['cms_name'], cms_info.get('version'))
        
        return jsonify({
            'success': True,
            'cms_info': cms_info,
            'vulnerabilities': vulnerabilities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'service': 'CMS Scanner'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)