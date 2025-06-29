print(">>> LOADED: lms_core/api.py <<<")

from typing import List
from ninja import NinjaAPI
from ninja.responses import Response
from lms_core.schema import (
    CourseSchemaOut, CourseMemberOut, CourseSchemaIn,
    CourseContentMini, CourseContentFull,
    CourseCommentOut, CourseCommentIn,
    RegisterSchemaIn, RegisterSchemaOut,
    BatchEnrollIn, MessageSchema, UserOut,
    UserDashboardOut, CourseAnalyticsOut,
    CompletionIn, CertificateOut,
    UserProfileOut, EditProfileIn,
)
from lms_core.models import Course, CourseMember, CourseContent, Comment, UserProfile, ContentCompletion
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from ninja.pagination import paginate, PageNumberPagination

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone

apiv1 = NinjaAPI()
apiv1.add_router("/auth/", mobile_auth_router)
apiAuth = HttpJwtAuth()

# === Register ===
@apiv1.post("/register", response={200: RegisterSchemaOut, 400: RegisterSchemaOut})
def register_user(request, payload: RegisterSchemaIn):
    try:
        if User.objects.filter(username=payload.username).exists():
            return 400, {"message": "Username sudah terpakai"}
        if User.objects.filter(email=payload.email).exists():
            return 400, {"message": "Email sudah terdaftar"}

        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password=payload.password
        )

        UserProfile.objects.create(
            user=user,
            phone=payload.handphone,
            description=payload.description
        )

        return 200, {"message": "Pendaftaran berhasil"}
    except IntegrityError:
        return 400, {"message": "Gagal mendaftarkan user karena duplikasi data"}
    except Exception as e:
        return 400, {"message": f"Terjadi kesalahan: {str(e)}"}

# === Batch Enroll Students ===
@apiv1.post("/course/enroll/batch", auth=apiAuth, response={200: MessageSchema, 400: MessageSchema})
def batch_enroll_students(request, payload: BatchEnrollIn):
    try:
        course = Course.objects.get(id=payload.course_id, teacher=request.user)
        current_students = CourseMember.objects.filter(course_id=course).count()
        remaining_slots = course.max_students - current_students

        if remaining_slots <= 0:
            return 400, {"message": "Kuota sudah penuh"}

        enrolled = []
        for student_id in payload.student_ids:
            if remaining_slots == 0:
                break
            try:
                user = User.objects.get(id=student_id)
                if not CourseMember.objects.filter(course_id=course, user_id=user).exists():
                    CourseMember.objects.create(course_id=course, user_id=user, roles='std')
                    enrolled.append(user.username)
                    remaining_slots -= 1
            except User.DoesNotExist:
                continue

        return 200, {"message": f"{len(enrolled)} siswa berhasil didaftarkan: {', '.join(enrolled)}"}
    except Course.DoesNotExist:
        return 400, {"message": "Kursus tidak ditemukan atau Anda bukan pengajarnya"}
    except Exception as e:
        return 400, {"message": f"Gagal: {str(e)}"}

@apiv1.get("/course/my", response=List[CourseSchemaOut], auth=apiAuth)
@paginate(PageNumberPagination)
def get_my_courses(request):
    return Course.objects.filter(teacher=request.user)

@apiv1.get("/users/students", response=List[UserOut], auth=apiAuth)
def list_students(request):
    return User.objects.filter(is_staff=False, is_superuser=False)

@apiv1.get("/course/comments/{content_id}", response=List[CourseCommentOut], auth=apiAuth)
def list_comments(request, content_id: int):
    return Comment.objects.filter(content_id=content_id, is_moderated=True)

@apiv1.post("/course/comments/{comment_id}/moderate", response={200: MessageSchema, 400: MessageSchema}, auth=apiAuth)
def moderate_comment(request, comment_id: int):
    try:
        comment = Comment.objects.get(id=comment_id)
        if comment.content_id.course_id.teacher != request.user:
            return 400, {"message": "Anda bukan pengajar dari course ini"}
        comment.is_moderated = True
        comment.save()
        return 200, {"message": "Komentar berhasil dimoderasi"}
    except Comment.DoesNotExist:
        return 400, {"message": "Komentar tidak ditemukan"}
    except Exception as e:
        return 400, {"message": f"Terjadi kesalahan: {str(e)}"}

@apiv1.get("/user/dashboard", response=UserDashboardOut, auth=apiAuth)
def user_activity_dashboard(request):
    user = request.user
    return {
        "total_course_as_student": CourseMember.objects.filter(user_id=user).count(),
        "total_course_as_teacher": Course.objects.filter(teacher=user).count(),
        "total_comments": Comment.objects.filter(member_id__user_id=user).count(),
        "total_completion": ContentCompletion.objects.filter(member__user_id=user).count()
    }

@apiv1.get("/course/{course_id}/analytics", response={200: CourseAnalyticsOut, 400: MessageSchema}, auth=apiAuth)
def get_course_analytics(request, course_id: int):
    try:
        course = Course.objects.get(id=course_id)
        if course.teacher != request.user:
            return 400, {"message": "Anda bukan pengajar dari course ini"}

        return 200, {
            "total_members": CourseMember.objects.filter(course_id=course).count(),
            "total_contents": CourseContent.objects.filter(course_id=course).count(),
            "total_comments": Comment.objects.filter(content_id__course_id=course).count(),
        }
    except Course.DoesNotExist:
        return 400, {"message": "Kursus tidak ditemukan"}

@apiv1.get("/course/{course_id}/contents/active", response=List[CourseContentMini], auth=apiAuth)
def list_active_course_contents(request, course_id: int):
    now = timezone.now()
    return CourseContent.objects.filter(
        course_id=course_id,
        release_time__lte=now,
        available_from__lte=now,
        available_to__gte=now
    )

@apiv1.post("/course/content/complete", response={200: MessageSchema, 400: MessageSchema}, auth=apiAuth)
def complete_content(request, payload: CompletionIn):
    try:
        content = CourseContent.objects.get(id=payload.content_id)
        member = CourseMember.objects.get(course_id=content.course_id, user_id=request.user)
        ContentCompletion.objects.get_or_create(member=member, content=content)
        return 200, {"message": "Konten berhasil ditandai sebagai selesai"}
    except CourseContent.DoesNotExist:
        return 400, {"message": "Konten tidak ditemukan"}
    except CourseMember.DoesNotExist:
        return 400, {"message": "Anda belum terdaftar di course ini"}
    except Exception as e:
        return 400, {"message": f"Error: {str(e)}"}

@apiv1.get("/user/completed", response=List[CourseContentMini], auth=apiAuth)
def get_completed_contents(request):
    completions = ContentCompletion.objects.filter(member__user_id=request.user)
    return [c.content for c in completions]

@apiv1.get("/course/{course_id}/certificate", response={200: CertificateOut, 400: MessageSchema}, auth=apiAuth)
def get_certificate(request, course_id: int):
    try:
        member = CourseMember.objects.get(course_id=course_id, user_id=request.user)
        total_content = CourseContent.objects.filter(course_id=course_id).count()
        completed = ContentCompletion.objects.filter(member=member).count()

        if total_content == 0:
            return 400, {"message": "Course belum punya konten"}
        if completed < total_content:
            return 400, {"message": "Kamu belum menyelesaikan semua konten"}

        return 200, {
            "username": request.user.username,
            "course_name": member.course_id.name,
            "issued_date": timezone.now()
        }
    except CourseMember.DoesNotExist:
        return 400, {"message": "Kamu belum terdaftar di course ini"}

@apiv1.get("/user/profile/{user_id}", response={200: UserProfileOut, 404: MessageSchema}, auth=apiAuth)
def show_user_profile(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        profile, _ = UserProfile.objects.get_or_create(user=user)

        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "handphone": profile.phone,
            "description": profile.description,
            "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
            "courses_created": list(Course.objects.filter(teacher=user)),
            "courses_joined": list(Course.objects.filter(coursemember__user_id=user).exclude(teacher=user))
        }
    except User.DoesNotExist:
        return 404, {"message": "User tidak ditemukan"}

@apiv1.put("/user/profile", response={200: MessageSchema, 400: MessageSchema}, auth=apiAuth)
def update_profile(request, payload: EditProfileIn):
    try:
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        user.first_name = payload.first_name or user.first_name
        user.last_name = payload.last_name or user.last_name
        user.email = payload.email or user.email
        user.save()

        profile.phone = payload.handphone or profile.phone
        profile.description = payload.description or profile.description
        profile.save()

        return 200, {"message": "Profil berhasil diperbarui"}
    except Exception as e:
        return 400, {"message": f"Terjadi kesalahan: {str(e)}"}
    
@apiv1.get("/course/{course_id}/completion", response=List[CourseContentMini], auth=apiAuth)
def show_course_completion(request, course_id: int):
    try:
        member = CourseMember.objects.get(course_id=course_id, user_id=request.user)
        completions = ContentCompletion.objects.filter(member=member)
        return [c.content for c in completions]
    except CourseMember.DoesNotExist:
        return []

@apiv1.delete("/course/content/complete", response={200: MessageSchema, 400: MessageSchema}, auth=apiAuth)
def delete_completion(request, payload: CompletionIn):
    try:
        content = CourseContent.objects.get(id=payload.content_id)
        member = CourseMember.objects.get(course_id=content.course_id, user_id=request.user)
        completion = ContentCompletion.objects.get(member=member, content=content)
        completion.delete()
        return 200, {"message": "Completion berhasil dihapus"}
    except ContentCompletion.DoesNotExist:
        return 400, {"message": "Data completion tidak ditemukan"}
    except Exception as e:
        return 400, {"message": f"Terjadi kesalahan: {str(e)}"}
