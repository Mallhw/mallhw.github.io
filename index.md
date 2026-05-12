---
title: Blogs
---

<ul>
{% assign blog_pages = site.pages | sort: "date" | reverse %}
{% for post in blog_pages %}
  {% if post.path contains "blogs/" %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endif %}
{% endfor %}
</ul>
