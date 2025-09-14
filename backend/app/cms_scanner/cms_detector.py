 
import requests
import re
import json

class CMSDetector:
    def __init__(self):
        self.cms_signatures = {
            'WordPress': {
                'patterns': ['wp-content', 'wp-includes', 'wordpress', '/wp-json/', 'xmlrpc.php'],
                'headers': ['x-powered-by: wordpress', 'x-generator: wordpress']
            },
            'Joomla': {
                'patterns': ['joomla', 'media/joomla', 'com_joomla', '/joomla/', 'index.php?option=com'],
                'headers': ['x-powered-by: joomla']
            },
            'Drupal': {
                'patterns': ['drupal', 'sites/all', 'core/assets', '/sites/default/', 'Drupal.settings'],
                'headers': ['x-generator: drupal']
            },
            'Magento': {
                'patterns': ['magento', 'static/version', 'mage/cookies', 'Mage.Cookies.path'],
                'headers': ['x-powered-by: magento']
            },
            'PrestaShop': {
                'patterns': ['prestashop', 'js/prestashop', 'themes/prestashop', 'Shop.Loader'],
                'headers': ['x-powered-by: prestashop']
            },
            'Shopify': {
                'patterns': ['shopify', 'cdn.shopify.com', 'shopify.settings', 'Shopify.theme'],
                'headers': ['x-shopid:', 'x-shopify-stage:']
            },
            'WooCommerce': {
                'patterns': ['woocommerce', 'wc-ajax=', 'woocommerce_', 'WooCommerce'],
                'headers': []
            },
            'Squarespace': {
                'patterns': ['squarespace', 'static1.squarespace.com', 'squarespace-footers'],
                'headers': ['x-squarespace-version:']
            },
            'Wix': {
                'patterns': ['wix.com', 'static.parastorage.com', 'wix-window', 'Wix.Models'],
                'headers': ['x-wix-request-id:']
            },
            'Blogger': {
                'patterns': ['blogger', 'blogspot.com', 'bp.blogspot.com', 'BloggerTemplate'],
                'headers': []
            },
            'TYPO3': {
                'patterns': ['typo3', 'typo3conf', 'typo3temp', 'TYPO3.Media'],
                'headers': ['x-typo3-sitename:']
            },
            'OpenCart': {
                'patterns': ['opencart', 'catalog/view/theme', 'system/storage', 'OC.'],
                'headers': []
            },
            'Ghost': {
                'patterns': ['ghost', 'ghost.org', 'content/themes/ghost', 'Ghost.init'],
                'headers': ['x-powered-by: ghost']
            },
            'Weebly': {
                'patterns': ['weebly', 'weebly.com', 'ws.weebly.com', 'Weebly.Loader'],
                'headers': ['x-weebly-id:']
            },
            'BigCommerce': {
                'patterns': ['bigcommerce', 'cdn.bigcommerce.com', 'stencil', 'BigCommerce.'],
                'headers': ['x-bc-version:']
            },
            'MediaWiki': {
                'patterns': ['mediawiki', '/w/', '/wiki/', 'mw-config', 'MediaWiki.'],
                'headers': ['x-powered-by: mediawiki']
            },
            'Django': {
                'patterns': ['django', 'csrfmiddlewaretoken', 'admin/js/', 'Django.'],
                'headers': ['x-frame-options: deny']
            },
            'Laravel': {
                'patterns': ['laravel', 'csrf-token', 'mix-manifest.json', 'Laravel.'],
                'headers': ['x-powered-by: laravel']
            },
            'React': {
                'patterns': ['_next/static', '__next__', 'react-dom', 'React.createElement'],
                'headers': ['x-powered-by: next.js']
            },
            'Vue.js': {
                'patterns': ['vue.js', 'vue.min.js', '__vue__', 'Vue.component'],
                'headers': []
            }
        }
    
    def detect_cms(self, url):
        """Détecte le CMS parmi les 20 plus courants"""
        try:
            # 1. Récupère le code source et les entêtes
            response = requests.get(
                url, 
                timeout=10, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                allow_redirects=True
            )
            
            html_content = response.text.lower()
            headers = str(response.headers).lower()
            
            # 2. Score pour chaque CMS
            cms_scores = {}
            
            for cms, signatures in self.cms_signatures.items():
                score = 0
                
                # Vérifie les patterns dans le HTML
                for pattern in signatures['patterns']:
                    if pattern.lower() in html_content:
                        score += 2
                
                # Vérifie les entêtes HTTP
                for header in signatures['headers']:
                    if header.lower() in headers:
                        score += 3
                
                # Vérifie les fichiers spécifiques
                if self.check_specific_files(url, cms):
                    score += 5
                
                if score > 0:
                    cms_scores[cms] = score
            
            # 3. Trouve le CMS avec le score le plus élevé
            if cms_scores:
                detected_cms = max(cms_scores, key=cms_scores.get)
                confidence = cms_scores[detected_cms]
                
                # 4. Détection de version (basique)
                version = self.detect_version(html_content, detected_cms)
                
                return {
                    'cms_name': detected_cms,
                    'confidence_score': confidence,
                    'version': version,
                    'url': url,
                    'status': 'success',
                    'techniques_used': len(cms_scores)
                }
            else:
                return {
                    'cms_name': 'Inconnu',
                    'confidence_score': 0,
                    'url': url,
                    'status': 'no_cms_detected'
                }
            
        except Exception as e:
            return {
                'cms_name': 'Erreur',
                'error': str(e),
                'url': url,
                'status': 'error'
            }
    
    def check_specific_files(self, url, cms):
        """Vérifie les fichiers spécifiques à chaque CMS"""
        file_checks = {
            'WordPress': ['/wp-admin/', '/wp-login.php', '/readme.html'],
            'Joomla': ['/administrator/', '/joomla.xml'],
            'Drupal': ['/sites/default/', '/core/install.php'],
            'Magento': ['/static/frontend/', '/magento_version'],
            'PrestaShop': ['/config/settings.inc.php', '/admin123/']
        }
        
        if cms in file_checks:
            for file_path in file_checks[cms]:
                try:
                    test_url = f"{url.rstrip('/')}{file_path}"
                    response = requests.head(test_url, timeout=5, allow_redirects=False)
                    if response.status_code < 400:
                        return True
                except:
                    continue
        return False
    
    def detect_version(self, html_content, cms_name):
        """Détection basique de version"""
        version_patterns = {
            'WordPress': r'content="WordPress (\d+\.\d+\.\d+)"',
            'Joomla': r'content="Joomla!? (\d+\.\d+)"',
            'Drupal': r'content="Drupal (\d+\.\d+)"',
            'Magento': r'Magento/(\d+\.\d+\.\d+)',
        }
        
        if cms_name in version_patterns:
            match = re.search(version_patterns[cms_name], html_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return 'Inconnu'

# Test
if __name__ == '__main__':
    import sys
    detector = CMSDetector()
    
    test_urls = [
        "https://wordpress.org",
        "https://www.joomla.org",
        "https://www.drupal.org",
        "https://magento.com"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        result = detector.detect_cms(url)
        print(json.dumps(result, indent=2, ensure_ascii=False))