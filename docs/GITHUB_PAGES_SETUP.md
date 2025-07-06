# GitHub Pages Documentation Setup

This directory contains the Jekyll-based documentation website for Insight Ingenious, configured to automatically deploy to GitHub Pages.

## 📖 What's Been Set Up

The documentation has been configured for GitHub Pages with the following components:

### Core Jekyll Files
- `_config.yml` - Main Jekyll configuration with Minimal Mistakes theme
- `Gemfile` - Ruby dependencies for GitHub Pages
- `index.md` - Homepage with feature showcase
- `_data/navigation.yml` - Site navigation structure

### GitHub Pages Integration
- `.github/workflows/docs.yml` - Automated build and deployment workflow
- Minimal Mistakes theme for professional appearance
- Responsive design optimized for documentation

### Enhanced Features
- 🔍 **Built-in search** powered by Lunr.js
- 📱 **Mobile responsive** design
- 🎨 **Clean navigation** with sidebar and breadcrumbs
- 📊 **Table of contents** for long pages
- 🏷️ **Syntax highlighting** for code blocks
- 🔗 **Cross-references** between documentation sections

## 🚀 How to Enable GitHub Pages

To enable GitHub Pages for this repository:

1. **Go to Repository Settings**
   - Navigate to your repository on GitHub
   - Click on the "Settings" tab

2. **Enable GitHub Pages**
   - Scroll down to the "Pages" section
   - Under "Source", select "GitHub Actions"
   - The workflow will automatically build and deploy when you push to main/master

3. **Access Your Documentation**
   - Your site will be available at: `https://[username].github.io/[repository-name]/`
   - For this repo: `https://insight-services-apac.github.io/ingenious/`

## 🛠️ Local Development

To run the documentation locally:

```bash
# Navigate to the docs directory
cd docs

# Install Ruby dependencies (first time only)
bundle install

# Serve the site locally
bundle exec jekyll serve

# Access at http://localhost:4000
```

## 📝 Adding New Documentation

### Adding a New Page
1. Create a new `.md` file in the appropriate directory
2. Add front matter at the top:
   ```yaml
   ---
   title: "Your Page Title"
   layout: single
   permalink: /your-page-url/
   sidebar:
     nav: "docs"
   toc: true
   ---
   ```
3. Write your content in Markdown

### Updating Navigation
Edit `_data/navigation.yml` to add your new page to the sidebar navigation.

### Images and Assets
Place images in `assets/images/` and reference them with:
```markdown
<!-- Example image reference (ensure image exists in assets/images/):
![Alt text](/assets/images/your-image.png)
-->
```

## 🎨 Theme Customization

The site uses the Minimal Mistakes theme. You can customize:

- **Colors and styling**: Override in `_sass/minimal-mistakes.scss`
- **Layout**: Modify layouts in `_layouts/`
- **Includes**: Add reusable components in `_includes/`

## 📋 Best Practices

### Writing Documentation
- Use clear, descriptive headings
- Include code examples where relevant
- Add table of contents for long pages (`toc: true`)
- Use emoji sparingly but effectively for visual appeal
- Cross-link related documentation

### Markdown Tips
- Use `{% raw %}{% highlight language %}{% endraw %}` for syntax highlighting
- Create call-out boxes with blockquotes
- Use tables for structured data
- Include navigation breadcrumbs with proper permalinks

### SEO and Discoverability
- Set descriptive page titles and meta descriptions
- Use semantic heading structure (H1 → H2 → H3)
- Include relevant keywords naturally
- Add alt text to images

## 🔧 Troubleshooting

### Build Failures
- Check the Actions tab for build logs
- Validate YAML front matter syntax
- Ensure all links are properly formatted
- Verify Gemfile dependencies

### Local Development Issues
- Run `bundle update` to update dependencies
- Clear Jekyll cache: `bundle exec jekyll clean`
- Check Ruby version compatibility

### Theme Issues
- Verify `_config.yml` theme settings
- Check for conflicting CSS/JavaScript
- Review theme documentation: [Minimal Mistakes Guide](https://mmistakes.github.io/minimal-mistakes/)

## 📚 Additional Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Minimal Mistakes Theme Guide](https://mmistakes.github.io/minimal-mistakes/)
- [Markdown Guide](https://www.markdownguide.org/)

---

The documentation is now ready to be published as a professional GitHub Pages site! 🎉
