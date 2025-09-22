# Jekyll Setup Instructions

## Prerequisites

You'll need Ruby installed on your system. macOS comes with Ruby pre-installed.

## Installation

1. Install Jekyll and dependencies:
   ```bash
   gem install bundler jekyll
   bundle install
   ```

2. Run Jekyll locally:
   ```bash
   bundle exec jekyll serve
   ```

3. Open your browser to: http://localhost:4000

## GitHub Pages Deployment

To deploy to GitHub Pages:

1. Go to your repository Settings > Pages
2. Under "Source", select "Deploy from a branch"
3. Choose your branch (usually `main` or `master`)
4. Select `/` (root) as the folder
5. Click Save

Your site will be available at: https://[username].github.io/reading-list/

## Structure

- `_config.yml` - Jekyll configuration
- `_layouts/default.html` - Page layout and styles
- `_entries/` - Individual book/author entries
- `index.md` - Main page that pulls from entries
- `header.png` - Header image

## Customization

- Edit CSS in `_layouts/default.html`
- Modify entry display in `index.md`
- Add new entries to `_entries/` folder
