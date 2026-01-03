import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    TIMESTAMP,
    TEXT,
    TIME,
    DATE,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, DOUBLE_PRECISION
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import ARRAY

Base = declarative_base()


# ============== 1. USERS & ROLES (Admin Side) ==============

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    description = Column(TEXT)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    admin_roles = relationship("AdminRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False)
    access_type = Column(String(20))
    description = Column(TEXT)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class Admin(Base):
    __tablename__ = "admin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    department = Column(String(100))
    role = Column(String(50), default="instructor", nullable=False)  # "instructor" or "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    roles = relationship("AdminRole", back_populates="admin", cascade="all, delete-orphan")
    created_courses = relationship("Course", back_populates="created_by_admin")
    course_instructors = relationship("CourseInstructor", back_populates="instructor")


class AdminRole(Base):
    __tablename__ = "admin_roles"
    __table_args__ = (
        UniqueConstraint("admin_id", "role_id", name="uq_admin_role"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admin.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    admin = relationship("Admin", back_populates="roles")
    role = relationship("Role", back_populates="admin_roles")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


# ============== 2. STUDENTS ==============

class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    university_id = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    major = Column(String(100))
    enrollment_year = Column(Integer)
    # FLOAT8[] -> DOUBLE_PRECISION ARRAY
    face_encoding = Column(ARRAY(DOUBLE_PRECISION))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")


# ============== 3. ACADEMIC STRUCTURE ==============

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True)
    name = Column(String(100))
    status = Column(String(20))
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("admin.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    created_by_admin = relationship("Admin", back_populates="created_courses")
    course_instructors = relationship("CourseInstructor", back_populates="course", cascade="all, delete-orphan")


class CourseInstructor(Base):
    __tablename__ = "course_instructors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"))
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("admin.id", ondelete="CASCADE"))
    room_num = Column(String(20))
    lecture_time = Column(TIME)
    days = Column(String(50))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    course = relationship("Course", back_populates="course_instructors")
    instructor = relationship("Admin", back_populates="course_instructors")
    enrollments = relationship("Enrollment", back_populates="course_instructor", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="course_instructor", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_instructors_id", name="uq_student_course_instructor"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"))
    course_instructors_id = Column(UUID(as_uuid=True), ForeignKey("course_instructors.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    student = relationship("Student", back_populates="enrollments")
    course_instructor = relationship("CourseInstructor", back_populates="enrollments")


# ============== 4. ATTENDANCE ==============

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"))
    course_instructors_id = Column(UUID(as_uuid=True), ForeignKey("course_instructors.id", ondelete="CASCADE"))
    date = Column(DATE)
    status = Column(String(20))  # Present / Late / Absent
    total_duration_minutes = Column(Integer)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    student = relationship("Student", back_populates="attendance_records")
    course_instructor = relationship("CourseInstructor", back_populates="attendance_records")
# ============== End of Schema Definitions ==============