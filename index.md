---
title: Blogs
---

<ul>
{% assign blog_pages = site.pages | where_exp: "post", "post.path contains 'blogs/'" | sort: "date" | reverse %}
{% for post in blog_pages %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    {% if post.date %}<span> — {{ post.date | date: "%B %d, %Y" }}</span>{% endif %}
  </li>
{% endfor %}
</ul>

