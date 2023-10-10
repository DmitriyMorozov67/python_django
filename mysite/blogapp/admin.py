from django.contrib import admin

from .models import Article, Author, Category, Tag


class ArticleInline(admin.TabularInline):
    model = Article.tags.through

# class AuthorInline(admin.StackedInline):
#     model = Author
#
# class CategoryInline(admin.StackedInline):
#     model = Category
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    inlines = [
        ArticleInline,
    ]

    list_display = [
        "title",
        "pub_date",
        "category",
        'author',
    ]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "bio"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name",]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name",]