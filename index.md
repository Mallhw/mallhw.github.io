---
title: Blogs
---

<ul>
{% for post in site.pages %}
  {% if post.path contains "blogs/" %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endif %}
{% endfor %}
</ul>
