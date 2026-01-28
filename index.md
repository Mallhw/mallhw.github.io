---
layout: null
---

# Blogs
{% for post in site.blogs %}
[{{ post.title }}]({{ post.url }})  
{% endfor %}

# Test Collection
{% for item in site.test %}
[{{ item.title }}]({{ item.url }})  
{% endfor %}


# Config Test

Collections available:  
{% for name in site.collections %}
- {{ name }}
{% endfor %}
