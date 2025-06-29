from ninja import Schema
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr

# ==== USER ====
class UserOut(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    handphone: Optional[str] = None
    description: Optional[str] = None

# ==== REGISTER ====
class RegisterSchemaIn(Schema):
    username: str
    password: str
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    handphone: Optional[str] = None
    description: Optional[str] = None

class RegisterSchemaOut(Schema):
    message: str

# ==== COURSE ====
class CourseSchemaOut(Schema):
    id: int
    name: str
    description: str
    price: int
    image: Optional[str]
    teacher: UserOut
    max_students: int
    created_at: datetime
    updated_at: datetime

class CourseSchemaIn(Schema):
    name: str
    description: str
    price: int
    max_students: Optional[int] = 100

# ==== COURSE MEMBER ====
class CourseMemberOut(Schema):
    id: int 
    course_id: CourseSchemaOut
    user_id: UserOut
    roles: str

# ==== COURSE CONTENT ====
class CourseContentMini(Schema):
    id: int
    name: str
    description: str
    course_id: CourseSchemaOut
    available_from: Optional[datetime] = None  
    available_to: Optional[datetime] = None    
    created_at: datetime
    updated_at: datetime

class CourseContentFull(Schema):
    id: int
    name: str
    description: str
    video_url: Optional[str]
    file_attachment: Optional[str]
    course_id: CourseSchemaOut
    available_from: Optional[datetime] = None  
    available_to: Optional[datetime] = None    
    created_at: datetime
    updated_at: datetime

# ==== COMMENT ====
class CourseCommentOut(Schema):
    id: int
    content_id: CourseContentMini
    member_id: CourseMemberOut
    comment: str
    created_at: datetime
    updated_at: datetime

class CourseCommentIn(Schema):
    comment: str

# ==== BATCH ENROLL ====
class BatchEnrollIn(Schema):
    course_id: int
    student_ids: List[int]

class MessageSchema(Schema):
    message: str

# ==== USER ACTIVITY DASHBOARD ====
class UserDashboardOut(Schema):
    total_course_as_student: int
    total_course_as_teacher: int
    total_comments: int
    total_completion: int = 0  # Jika belum ada fitur content completion, biarkan 0

# ==== COURSE ANALYTICS ====
class CourseAnalyticsOut(Schema):
    total_members: int
    total_contents: int
    total_comments: int
    # total_feedback: int  # tambahkan ini jika kamu sudah buat fitur feedback

# ==== CONTENT COMPLETION ====
class CompletionIn(Schema):
    content_id: int

class CertificateOut(Schema):
    username: str
    course_name: str
    issued_date: datetime

# ==== PROFILE ====
class UserProfileOut(Schema):
    first_name: str
    last_name: str
    email: str
    handphone: Optional[str] = None
    description: Optional[str] = None
    profile_picture: Optional[str] = None
    courses_created: List[CourseSchemaOut] = []
    courses_joined: List[CourseSchemaOut] = []

class EditProfileIn(Schema):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: Optional[EmailStr]
    handphone: Optional[str] = ""
    description: Optional[str] = ""
