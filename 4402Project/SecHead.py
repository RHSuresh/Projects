import asyncio
import aiohttp
import csv
import time
from collections import defaultdict

'''
This script scans websites for HTTP security headers,
analyzes adoption rates, and generates visualizations.
'''

# List of HTTP security headers 
SECURITY_HEADERS = [
    'Content-Security-Policy',        
    'Access-Control-Allow-Origin',    
    'Access-Control-Allow-Methods',   
    'Referrer-Policy',               
    'Strict-Transport-Security',
    'X-Frame-Options',               
    'X-Content-Type-Options'         
]

# CSP directives to analyze - focusing on the 5 most critical
CSP_DIRECTIVES = [
    'default-src',      # Fallback for all other directives 
    'script-src',       # Prevents XSS attacks by controlling script sources
    'style-src',        # Controls stylesheets - prevents CSS injection
    'frame-ancestors',  # Prevents clickjacking - replaces X-Frame-Options
    'base-uri',         # Restricts <base> tag URLs from hijacking
]

async def find_headers(session, url):
    """Fetch HTTP headers from a single URL using HEAD request"""
    try:
        url = url if url.startswith(('http://', 'https://')) else 'https://' + url  
        async with session.head(url, timeout=3, allow_redirects=True, ssl=False) as response:
            return {'url': url, 'status': response.status, 'headers': dict(response.headers)}
    except asyncio.TimeoutError:
        return {'url': url, 'status': 'TIMEOUT', 'headers': {}}
    except Exception as e:
        return {'url': url, 'status': f'ERROR: {str(e)[:50]}', 'headers': {}}

async def scan_websites(urls, batch_size=500):
    """Scan multiple websites concurrently for efficiency"""
    results = []
    connector = aiohttp.TCPConnector(limit=500, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=5, connect=3)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i+batch_size]
            batch_results = await asyncio.gather(*[find_headers(session, url) for url in batch], return_exceptions=True)
            results.extend(batch_results)
            print(f"Processed {min(i+batch_size, len(urls))}/{len(urls)} sites!")
    return results

def parse_csp(csp_header):
    """Parse CSP header and extract individual directives"""
    if not csp_header:
        return {}
    
    directives = {}
    parts = csp_header.split(';')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        tokens = part.split(None, 1)
        if tokens:
            directive_name = tokens[0].lower()
            directive_value = tokens[1] if len(tokens) > 1 else ''
            directives[directive_name] = directive_value
    
    return directives

def get_domain_type(url):
    """Categorize domain by TLD"""
    url = url.lower()
    
    if '.gov' in url:
        return 'gov'
    elif '.edu' in url:
        return 'edu'
    elif '.com' in url:
        return 'com'
    elif '.org' in url:
        return 'org'
    else:
        return 'other'

def analyze_headers(results):
    """Analyze collected headers and calculate adoption statistics"""
    stats = defaultdict(int)
    csp_directive_stats = defaultdict(int)
    domain_type_stats = defaultdict(lambda: {'total': 0, 'successful': 0, 'headers': defaultdict(int)})
    
    #Track unsafe CSP options and CORS wildcards
    csp_unsafe_inline = 0
    csp_unsafe_eval = 0
    cors_wildcard = 0
    cors_specific = 0
    
    successful = sum(1 for r in results if not isinstance(r, Exception) and r['status'] == 200)
    failed = len(results) - successful
    
    for result in results:
        if isinstance(result, Exception) or result['status'] != 200:
            continue
        
        headers_lower = {k.lower(): v for k, v in result['headers'].items()}
        domain_type = get_domain_type(result['url'])
        
        domain_type_stats[domain_type]['successful'] += 1
        
        for header in SECURITY_HEADERS:
            if header.lower() in headers_lower:
                stats[header] += 1
                domain_type_stats[domain_type]['headers'][header] += 1
        
        # Analyze CSP directives and unsafe options
        if 'content-security-policy' in headers_lower:
            csp_value = headers_lower['content-security-policy']
            directives = parse_csp(csp_value)
            
            # Count unsafe options
            if 'unsafe-inline' in csp_value.lower():
                csp_unsafe_inline += 1
            if 'unsafe-eval' in csp_value.lower():
                csp_unsafe_eval += 1
            
            for directive in CSP_DIRECTIVES:
                if directive in directives:
                    csp_directive_stats[directive] += 1
        
        # Analyze CORS configuration
        if 'access-control-allow-origin' in headers_lower:
            cors_value = headers_lower['access-control-allow-origin']
            if cors_value.strip() == '*':
                cors_wildcard += 1
            else:
                cors_specific += 1
    
    return {
        'stats': dict(stats),
        'csp_directives': dict(csp_directive_stats),
        'csp_unsafe_inline': csp_unsafe_inline,
        'csp_unsafe_eval': csp_unsafe_eval,
        'cors_wildcard': cors_wildcard,
        'cors_specific': cors_specific,
        'domain_types': dict(domain_type_stats),
        'successful': successful,
        'failed': failed,
        'total': len(results)
    }

def save_results_csv(results, output_file='security_headers_results.csv'):
    """Save scan results to CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'URL', 'Domain Type', 'Status', 'CSP', 
            'CSP-default-src', 'CSP-script-src', 'CSP-style-src', 'CSP-frame-ancestors', 'CSP-base-uri',
            'CORS', 'Referrer-Policy', 'HSTS', 'X-Frame-Options', 'X-Content-Type-Options'
        ])
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            status = result.get('status', 'UNKNOWN')
            domain_type = get_domain_type(result['url'])
            row = [result['url'], domain_type, status]
            
            if status != 200:
                row.extend(['N/A'] * 11)
            else:
                headers_lower = {k.lower(): v for k, v in result.get('headers', {}).items()}
                
                has_csp = 'content-security-policy' in headers_lower
                row.append('Yes' if has_csp else 'No')
                
                if has_csp:
                    csp_value = headers_lower['content-security-policy']
                    directives = parse_csp(csp_value)
                    for directive in ['default-src', 'script-src', 'style-src', 'frame-ancestors', 'base-uri']:
                        row.append('Yes' if directive in directives else 'No')
                else:
                    row.extend(['No'] * 5)
                
                for header in ['access-control-allow-origin', 'referrer-policy',
                              'strict-transport-security', 'x-frame-options', 'x-content-type-options']:
                    row.append('Yes' if header in headers_lower else 'No')
            
            writer.writerow(row)
    
    print(f"\nResults saved to {output_file}")

def print_analysis(analysis):
    """Show results in terminal"""
    print("\n" + "="*70)
    print("------SECURITY HEADERS ADOPTION ANALYTICS------")
    print("="*70)
    print(f"\nScanned: {analysis['total']} sites")
    print(f"Successfully scanned: {analysis['successful']} sites ({100*analysis['successful']/analysis['total']:.1f}%)")
    print(f"Failed to scan: {analysis['failed']} sites\n")
    
    print("-"*70)
    print("OVERALL HEADER ADOPTION RATES:")
    print("-"*70)
    for header, count in sorted(analysis['stats'].items(), key=lambda x: x[1], reverse=True):
        percentage = 100 * count / analysis['successful'] if analysis['successful'] > 0 else 0
        print(f"{header}: {count} sites ({percentage:.1f}%)")
    
    # CSP Directive breakdown
    if analysis['csp_directives']:
        print("\n" + "="*70)
        print("CSP DIRECTIVE BREAKDOWN (among sites with CSP):")
        print("="*70)
        sites_with_csp = analysis['stats'].get('Content-Security-Policy', 0)
        print(f"Total sites with CSP: {sites_with_csp}\n")
        
        for directive, count in sorted(analysis['csp_directives'].items(), key=lambda x: x[1], reverse=True):
            percentage = 100 * count / sites_with_csp if sites_with_csp > 0 else 0
            print(f"  {directive}: {count} sites ({percentage:.1f}%)")
        
        # Unsafe CSP options
        print(f"\n  CSP MISCONFIGURATIONS:")
        unsafe_inline_pct = 100 * analysis['csp_unsafe_inline'] / sites_with_csp if sites_with_csp > 0 else 0
        unsafe_eval_pct = 100 * analysis['csp_unsafe_eval'] / sites_with_csp if sites_with_csp > 0 else 0
        print(f"unsafe-inline: {analysis['csp_unsafe_inline']} sites ({unsafe_inline_pct:.1f}%)")
        print(f"unsafe-eval: {analysis['csp_unsafe_eval']} sites ({unsafe_eval_pct:.1f}%)")
    
    # CORS analysis
    total_cors = analysis['stats'].get('Access-Control-Allow-Origin', 0)
    if total_cors > 0:
        print("\n" + "="*70)
        print("CORS CONFIG ANALYSIS:")
        print("="*70)
        print(f"Total sites with CORS: {total_cors}\n")
        wildcard_pct = 100 * analysis['cors_wildcard'] / total_cors
        specific_pct = 100 * analysis['cors_specific'] / total_cors
        print(f"Wildcard (*) - INSECURE: {analysis['cors_wildcard']} sites ({wildcard_pct:.1f}%)")
        print(f"Specific origins - SECURE: {analysis['cors_specific']} sites ({specific_pct:.1f}%)")
    
    # Domain type analysis
    print("\n" + "="*70)
    print("SECURITY HEADERS BY DOMAIN TYPE:")
    print("="*70)
    
    for domain_type, data in sorted(analysis['domain_types'].items(), key=lambda x: x[1]['successful'], reverse=True):
        if data['successful'] == 0:
            continue
            
        print(f"\n{domain_type.upper()} domains ({data['successful']} sites):")
        print("-" * 50)
        
        for header in SECURITY_HEADERS:
            count = data['headers'].get(header, 0)
            percentage = 100 * count / data['successful'] if data['successful'] > 0 else 0
            print(f"  {header}: {count}/{data['successful']} ({percentage:.1f}%)")

def analyze_specific_domains(results, domain_extension):
    """Analyze specific domain types"""
    print("\n" + "="*70)
    print(f"{domain_extension.upper().replace('.', '')} DOMAINS")
    print("="*70)
    
    matching_results = [r for r in results 
                       if not isinstance(r, Exception) 
                       and r['status'] == 200 
                       and domain_extension in r['url'].lower()]
    
    if not matching_results:
        print(f"No successful scans found for {domain_extension} domains")
        return
    
    print(f"\nAnalyzing {len(matching_results)} {domain_extension} domains\n")
    
    for i, result in enumerate(matching_results[:3], 1):
        print(f"Example {i}: {result['url']}")
        print("-" * 50)
        
        headers_lower = {k.lower(): v for k, v in result['headers'].items()}
        
        if 'content-security-policy' in headers_lower:
            csp = headers_lower['content-security-policy']
            print(f"CSP: Present")
            directives = parse_csp(csp)
            if directives:
                print(f"     Directives found: {', '.join(list(directives.keys())[:5])}")
            if 'unsafe-inline' in csp or 'unsafe-eval' in csp:
                print(f"Warning: Contains unsafe directives")
        else:
            print(f"CSP: Not present")
        
        if 'strict-transport-security' in headers_lower:
            print(f"HSTS: Present ({headers_lower['strict-transport-security'][:50]})")
        else:
            print(f"HSTS: Not present")
        
        if 'x-frame-options' in headers_lower:
            print(f"X-Frame-Options: {headers_lower['x-frame-options']}")
        else:
            print(f"X-Frame-Options: Not present")
        
        if 'x-content-type-options' in headers_lower:
            print(f"X-Content-Type-Options: {headers_lower['x-content-type-options']}")
        else:
            print(f"X-Content-Type-Options: Not present")
        
        print()

def generate_graphs(analysis):
    """Generate necessary graphs and save as PNG files"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed. No graphs will be generated.")
        return
    
    # GRAPH 1: Domain Type Comparison
    domain_data = analysis['domain_types']
    
    domain_types = []
    csp_rates = []
    hsts_rates = []
    xframe_rates = []
    
    # Graph creation
    for domain_type in ['gov', 'org', 'com', 'edu', 'other']:
        if domain_type in domain_data and domain_data[domain_type]['successful'] > 0:
            domain_types.append(domain_type.upper())
            total = domain_data[domain_type]['successful']
            
            csp = domain_data[domain_type]['headers'].get('Content-Security-Policy', 0)
            hsts = domain_data[domain_type]['headers'].get('Strict-Transport-Security', 0)
            xframe = domain_data[domain_type]['headers'].get('X-Frame-Options', 0)
            
            csp_rates.append((csp / total) * 100)
            hsts_rates.append((hsts / total) * 100)
            xframe_rates.append((xframe / total) * 100)
    
    if domain_types:
        x = np.arange(len(domain_types))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bars1 = ax.bar(x - width, hsts_rates, width, label='HSTS', color='#2E86AB')
        bars2 = ax.bar(x, csp_rates, width, label='CSP', color='#F18F01')
        bars3 = ax.bar(x + width, xframe_rates, width, label='X-Frame-Options', color='#6A994E')
        
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Domain Type', fontsize=14, fontweight='bold')
        ax.set_ylabel('Adoption Rate (%)', fontsize=14, fontweight='bold')
        ax.set_title('Security Header Adoption by Domain Type\n(20,000 websites scanned)', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(domain_types, fontsize=12)
        ax.legend(fontsize=12, loc='upper right')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('graph1_domain_comparison.png', dpi=300, bbox_inches='tight')
        print("Graph 1 saved as graph1_domain_comparison.png")
        plt.close()
    
    # GRAPH 2: CORS Configuration Analysis
    cors_wildcard = analysis.get('cors_wildcard', 0)
    cors_specific = analysis.get('cors_specific', 0)
    total_cors = cors_wildcard + cors_specific
    
    if total_cors > 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sizes = [cors_wildcard, cors_specific]
        labels = [f'Wildcard (*)\nINSECURE\n{cors_wildcard} sites', 
                  f'Specific Origins\nSECURE\n{cors_specific} sites']
        colors = ['#E63946', '#06A77D']
        explode = (0.1, 0)
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                           startangle=90, explode=explode, textprops={'fontsize': 12, 'weight': 'bold'})
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
            autotext.set_weight('bold')
        
        ax.set_title(f'CORS Configuration Analysis\n({total_cors} sites with CORS enabled)', 
                     fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('graph2_cors_analysis.png', dpi=300, bbox_inches='tight')
        print("Graph 2 saved as graph2_cors_analysis.png")
        plt.close()
    else:
        print("No CORS data to generate graph")
    
    print("\nAll graphs generated successfully")

async def main():
    """Main execution function"""
    print("Loading URLs from Tranco list")
    
    try:
        with open('top-1m.csv', 'r') as f:
            all_urls = [row[1] for row in csv.reader(f)]
    except FileNotFoundError:
        print("Error: Tranco CSV file not found.")
        return
    
    urls = all_urls[:10000] + all_urls[-10000:]
    
    # Testing uconn.edu 
    urls.append('uconn.edu')
    
    print(f"Loaded {len(all_urls[:10000])} top URLs and {len(all_urls[-10000:])} bottom URLs")
    print(f"Added UConn.edu for testing purposes")
    print(f"Total URLs to scan: {len(urls)}\n")
    
    print("Scanning websites for security headers now! Should take ~ 2-3 minutes")
    start_time = time.time()
    results = await scan_websites(urls)
    
    print("\nAnalyzing results")
    analysis = analyze_headers(results)
    
    print_analysis(analysis)
    save_results_csv(results)
    
    analyze_specific_domains(results, '.gov')
    analyze_specific_domains(results, '.edu')
    analyze_specific_domains(results, 'uconn.edu')
    
    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"{'='*70}\n")
    
    print("\n" + "="*70)
    print("GENERATING GRAPHS")
    print("="*70 + "\n")
    generate_graphs(analysis)

if __name__ == "__main__":
    asyncio.run(main())