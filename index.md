---
layout: default
title: a16z Infra Reading List
---

# a16z Infra Reading List

<!-- ![Header](header.png){: .header-image} -->

This is a list of books and authors that at least one member of the a16z infra team read and loved. It's heavy on science fiction because sci-fi is the most infra-y literary genre: it's about new technology, new systems, and the people who devote their lives to building and understanding them.

We hope other infra people will like these books too! Please open a PR for any changes or additions.



<div class="toc">
<ul>
  <li><a href="#sci-fi">Sci-fi</a>
    <ul>
      <li><a href="#must-reads-s-tier">Must reads (S tier)</a></li>
      <li><a href="#classics-a-tier">Classics (A tier)</a></li>
      <li><a href="#very-good-books-a-tier">Very good books (A tier)</a></li>
      <li><a href="#also-worth-reading-b-tier">Also worth reading (B tier)</a></li>
    </ul>
  </li>
  <li><a href="#fantasy">Fantasy</a></li>
  <li><a href="#comic-books">Comic books</a></li>
  <li><a href="#non-fiction">Non-fiction</a></li>
</ul>
</div>

<h2 id="sci-fi">Sci-fi</h2>

<h3 id="must-reads-s-tier">Must reads (S tier)</h3>

<blockquote class="section-intro">
If you haven't read a lot of science fiction before (or want to argue about what merits S tier), start here.
</blockquote>

{% assign must_reads = site.entries | where: "category", "must_read" | sort: "order" %}
{% for entry in must_reads %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}

<h3 id="classics-a-tier">Classics (A tier)</h3>

<blockquote class="section-intro">
These books all had massive impact when they were published and are still great reads today. Some feel a little dated now, so you can skip this section if you don't want to dive into sci-fi history.
</blockquote>

{% assign classics = site.entries | where: "category", "classic" | sort: "order" %}
{% for entry in classics %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}

<h3 id="very-good-books-a-tier">Very good books (A tier)</h3>

<blockquote class="section-intro">
These are all contemporary books and very very good. Highly recommended.
</blockquote>

{% assign very_good = site.entries | where: "category", "very_good" | sort: "order" %}
{% for entry in very_good %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}

<h3 id="also-worth-reading-b-tier">Also worth reading (B tier)</h3>

<blockquote class="section-intro">
These books are all fun and/or, interesting and well worth the time, if you are looking for something new.
</blockquote>

{% assign also_worth = site.entries | where: "category", "also_worth_reading" | sort: "order" %}
{% for entry in also_worth %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}

<h2 id="fantasy">Fantasy</h2>

{% assign fantasy = site.entries | where: "category", "fantasy" | sort: "order" %}
{% for entry in fantasy %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}

<h2 id="comic-books">Comic books</h2>

{% assign comics = site.entries | where: "category", "comic" | sort: "order" %}
{% for entry in comics %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}

<h2 id="non-fiction">Non-fiction</h2>

{% assign non_fiction = site.entries | where: "category", "non_fiction" | sort: "order" %}
{% for entry in non_fiction %}
<div class="entry">
  <div class="entry-image">
    <img src="{{ entry.cover_url }}" alt="{{ entry.series_title | default: entry.book_title | default: entry.author }}">
  </div>
  <div class="entry-content">
    {% if entry.series_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.series_title }}</a></em> {{ entry.series_postfix }}</strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% elsif entry.book_title %}
      <strong><em><a href="{{ entry.title_url }}">{{ entry.book_title }}</a></em></strong> by <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% else %}
      <strong><a href="{{ entry.author_url }}">{{ entry.author }}</a></strong>: 
    {% endif %}
    {{ entry.content | markdownify }}
  </div>
</div>
{% endfor %}
