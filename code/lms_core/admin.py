from django.contrib import admin
from lms_core.models import Course, UserProfile, CourseContent, Comment

# Admin untuk Course
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "max_students", "description", "teacher", "created_at"]
    list_filter = ["teacher"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "description", "price", "max_students", "image", "teacher", "created_at", "updated_at"]

# Admin untuk UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "description"]
    search_fields = ["user__username", "user__email", "description"]

# Admin untuk CourseContent
@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "course_id", "created_at"]
    list_filter = ["course_id"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

# Admin untuk Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "member_id", "content_id", "comment", "is_moderated", "created_at"]
    list_filter = ["is_moderated", "content_id"]
    search_fields = ["comment"]
    readonly_fields = ["created_at", "updated_at"]
