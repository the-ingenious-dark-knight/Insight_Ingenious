// Mermaid.js initialization for GitHub Pages
// Modern approach for Mermaid v11+

document.addEventListener('DOMContentLoaded', function() {
  // Initialize Mermaid with modern configuration
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    themeVariables: {
      primaryColor: '#0366d6',
      primaryTextColor: '#24292e',
      primaryBorderColor: '#e1e4e8',
      lineColor: '#959da5',
      secondaryColor: '#f6f8fa',
      tertiaryColor: '#ffffff'
    },
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis'
    },
    sequence: {
      useMaxWidth: true,
      wrap: true
    },
    journey: {
      useMaxWidth: true
    },
    securityLevel: 'loose'
  });

  // Target Jekyll's generated code blocks with language-mermaid class
  mermaid.run({
    querySelector: '.language-mermaid'
  });
});
