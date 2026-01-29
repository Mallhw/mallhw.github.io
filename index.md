---
title: Blogs
---

# Blogs

<ul>
{% for post in site.blogs %}
  <li>
    <a href="{{ post.url }}">{{ post.title }}</a>
  </li>
{% endfor %}
</ul>
