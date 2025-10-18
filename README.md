This is the content behind the a16z infra reading list at https://a16z-infra.github.io/reading-list/

The list is built using Jekyll, a static site generator that's integrated into GitHub Pages. The book & author entries are stored as individual markdown files in the `_entries/` directory. Jekyll automatically compiles the new list whenever an update is pushed to the `main` branch.

If you'd like to contribute, just add or edit a file in the `_entries/` directory and submit a PR. Here's an example of what an entry looks like:

```markdown
---
category: must_read
order: 10
book_title:
book_url:
series_title: Dune
series_url: https://en.wikipedia.org/wiki/Dune_(novel)
series_postfix: series
author: Frank Herbert
author_url: https://en.wikipedia.org/wiki/Frank_Herbert
cover_url: https://upload.wikimedia.org/wikipedia/en/d/de/Dune-Frank_Herbert_%281965%29_First_edition.jpg
---
Arrakis. Sand worms. The spice. Paul Muad'Dib. This is the series that brought epic sci-fi to the mainstream. It's also one of the first series that demonstrated sci-fi should be taken seriously, in this case as an allegory for geopolitical tensions in the Middle East. In case you've only seen the (very well done) movies, do yourself a favor and read the books, which are infinitely deeper and more intricately plotted. The last three fast-forward several thousand years and get a little weird (in a good way!).
  - [*Dune*](https://en.wikipedia.org/wiki/Dune_(novel)) (1965)
  - [*Dune Messiah*](https://en.wikipedia.org/wiki/Dune_Messiah) (1969)
  - [*Children of Dune*](https://en.wikipedia.org/wiki/Children_of_Dune) (1976)
  - [*God Emperor of Dune*](https://en.wikipedia.org/wiki/God_Emperor_of_Dune) (1981)
  - [*Heretics of Dune*](https://en.wikipedia.org/wiki/Heretics_of_Dune) (1982)
  - [*Chapterhouse: Dune*](https://en.wikipedia.org/wiki/Chapterhouse:_Dune) (1985)
```

You should specify at most one of `book_title` or `series_title`. And you can leave both blank if you're just highlighting an author.

If you'd like to test the site locally...

1. Install Ruby and Jekyll (mac instructions: https://jekyllrb.com/docs/installation/macos/)
2. Install bundler: run `gem install bundler`
3. Install site dependencies: in your local copy of the repo, run `bundle install`
4. Start the local server: in your local copy, run `bundle exec jekyll serve`
5. Access the site: http://127.0.0.1:4000/ by default

When a PR is merged, the site will be automatically updated
