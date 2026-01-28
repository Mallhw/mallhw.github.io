---
layout: default
title: Home
---

# Blog Posts

<ul>
{% for post in site.blogs %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
    <small>({{ post.date | date: "%Y-%m-%d" }})</small>
  </li>
{% endfor %}
</ul>
