#!/usr/bin/env node
/**
 * Reliable SVG export using Puppeteer
 * This is the most viable approach for extracting real D3.js rendered SVG
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function exportSVGFromHTML(htmlFilePath, outputSVGPath) {
    let browser = null;
    let page = null;
    
    try {
        console.log(`[Puppeteer] Starting SVG export: ${htmlFilePath} -> ${outputSVGPath}`);
        
        // Launch browser with optimized settings
        browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ],
            timeout: 30000
        });
        
        page = await browser.newPage();
        
        // Set viewport for consistent rendering
        await page.setViewport({ width: 1400, height: 900 });
        
        // Convert file path to file:// URL
        const htmlFileURL = `file://${path.resolve(htmlFilePath)}`;
        console.log(`[Puppeteer] Loading: ${htmlFileURL}`);
        
        // Navigate to HTML file with extended timeout
        await page.goto(htmlFileURL, { 
            waitUntil: 'networkidle0',
            timeout: 30000 
        });
        
        // Wait for D3.js to load
        console.log('[Puppeteer] Waiting for D3.js to load...');
        await page.waitForFunction(() => typeof d3 !== 'undefined', { timeout: 15000 });
        
        // Wait for SVG element to be created
        console.log('[Puppeteer] Waiting for SVG element...');
        await page.waitForSelector('svg', { timeout: 15000 });
        
        // Wait for SVG to have content (not just empty)
        console.log('[Puppeteer] Waiting for SVG content...');
        await page.waitForFunction(() => {
            const svg = document.querySelector('svg');
            return svg && svg.children.length > 0;
        }, { timeout: 15000 });
        
        // Additional wait for animations and rendering
        console.log('[Puppeteer] Waiting for rendering to complete...');
        await page.waitForTimeout(3000);
        
        // Extract SVG content with embedded styles
        console.log('[Puppeteer] Extracting SVG content...');
        const svgData = await page.evaluate(() => {
            const svg = document.querySelector('svg');
            if (!svg) {
                throw new Error('No SVG element found');
            }
            
            // Get SVG content
            let svgContent = svg.outerHTML;
            
            // Extract CSS styles from style tags
            const styleElements = document.querySelectorAll('style');
            let cssStyles = '';
            styleElements.forEach(style => {
                cssStyles += style.textContent + '\n';
            });
            
            // Get computed styles for SVG elements
            const svgElements = svg.querySelectorAll('*');
            const computedStyles = new Set();
            
            for (let i = 0; i < Math.min(svgElements.length, 50); i++) {
                const elem = svgElements[i];
                const computed = window.getComputedStyle(elem);
                
                // Extract important styles
                const styles = [];
                if (computed.fill && computed.fill !== 'rgb(0, 0, 0)' && computed.fill !== 'none') {
                    styles.push(`fill: ${computed.fill}`);
                }
                if (computed.stroke && computed.stroke !== 'none') {
                    styles.push(`stroke: ${computed.stroke}`);
                }
                if (computed.strokeWidth && computed.strokeWidth !== '0px') {
                    styles.push(`stroke-width: ${computed.strokeWidth}`);
                }
                if (computed.fontSize) {
                    styles.push(`font-size: ${computed.fontSize}`);
                }
                if (computed.fontWeight && computed.fontWeight !== 'normal') {
                    styles.push(`font-weight: ${computed.fontWeight}`);
                }
                
                if (styles.length > 0 && elem.tagName) {
                    const selector = elem.tagName.toLowerCase();
                    if (elem.className && elem.className.baseVal) {
                        computedStyles.add(`.${elem.className.baseVal} { ${styles.join('; ')}; }`);
                    } else {
                        computedStyles.add(`${selector} { ${styles.join('; ')}; }`);
                    }
                }
            }
            
            // Combine all styles
            const allStyles = cssStyles + '\n' + Array.from(computedStyles).join('\n');
            
            return {
                svgContent: svgContent,
                styles: allStyles,
                elementCount: svg.children.length
            };
        });
        
        console.log(`[Puppeteer] Extracted SVG with ${svgData.elementCount} elements`);
        
        // Process and create final SVG
        let finalSVG = svgData.svgContent;
        
        // Add XML declaration if not present
        if (!finalSVG.startsWith('<?xml')) {
            finalSVG = '<?xml version="1.0" encoding="UTF-8"?>\n' + finalSVG;
        }
        
        // Embed styles in SVG
        if (svgData.styles.trim()) {
            const styleTag = `<style type="text/css"><![CDATA[\n${svgData.styles.trim()}\n]]></style>`;
            
            // Insert style tag after the opening <svg> tag
            const svgTagEnd = finalSVG.indexOf('>');
            if (svgTagEnd !== -1) {
                finalSVG = finalSVG.slice(0, svgTagEnd + 1) + '\n' + styleTag + finalSVG.slice(svgTagEnd + 1);
            }
        }
        
        // Ensure proper namespace
        if (!finalSVG.includes('xmlns="http://www.w3.org/2000/svg"')) {
            finalSVG = finalSVG.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
        }
        
        // Save SVG file
        fs.writeFileSync(outputSVGPath, finalSVG, 'utf8');
        
        console.log(`[Puppeteer] Success: ${outputSVGPath} (${finalSVG.length} chars)`);
        return true;
        
    } catch (error) {
        console.error(`[Puppeteer] Error: ${error.message}`);
        return false;
    } finally {
        // Clean up
        if (page) {
            try {
                await page.close();
            } catch (e) {
                console.warn('[Puppeteer] Warning: Could not close page');
            }
        }
        if (browser) {
            try {
                await browser.close();
            } catch (e) {
                console.warn('[Puppeteer] Warning: Could not close browser');
            }
        }
    }
}

// Command line interface
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length !== 2) {
        console.log('Usage: node puppeteer_svg_export.js <html_file> <output_svg>');
        process.exit(1);
    }
    
    const [htmlFile, outputSVG] = args;
    
    exportSVGFromHTML(htmlFile, outputSVG)
        .then(success => {
            console.log(`[Puppeteer] Final result: ${success ? 'SUCCESS' : 'FAILED'}`);
            process.exit(success ? 0 : 1);
        })
        .catch(error => {
            console.error('[Puppeteer] Fatal error:', error);
            process.exit(1);
        });
}

module.exports = { exportSVGFromHTML };
