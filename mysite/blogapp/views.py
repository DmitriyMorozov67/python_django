from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from .models import Article

class ClassBasedView(ListView):
    template_name = "blogapp/article_list.html"
    context_object_name = "articles"
    queryset = (
        Article.objects
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-pub_date")[:5]
        .defer("content")
    )

class ArticleDetailView(DetailView):
    model = Article

class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (
        Article.objects
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-pub_date")[:5]
        .defer("content")
    )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
