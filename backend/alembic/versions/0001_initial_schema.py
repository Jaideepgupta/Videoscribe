"""Initial database schema with users, videos, transcripts, segments, jobs, and errors.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-22 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('source_url', sa.String(length=2048), nullable=True),
        sa.Column('platform', sa.Enum('youtube', 'upload', 'vimeo', 'direct', 'other', name='platform_type', native_enum=False), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='video_status', native_enum=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_videos_source_url'), 'videos', ['source_url'], unique=False)
    op.create_index(op.f('ix_videos_user_id'), 'videos', ['user_id'], unique=False)

    # Transcripts table
    op.create_table(
        'transcripts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('video_id', sa.String(length=36), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('clean_text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcripts_video_id'), 'transcripts', ['video_id'], unique=True)

    # Transcript Segments table
    op.create_table(
        'transcript_segments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('transcript_id', sa.String(length=36), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('speaker', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['transcript_id'], ['transcripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcript_segments_start_time'), 'transcript_segments', ['start_time'], unique=False)
    op.create_index(op.f('ix_transcript_segments_transcript_id'), 'transcript_segments', ['transcript_id'], unique=False)

    # Transcription Jobs table
    op.create_table(
        'transcription_jobs',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('video_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.Enum('queued', 'detecting', 'extracting', 'transcribing', 'cleaning', 'completed', 'failed', name='job_status', native_enum=False), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcription_jobs_status'), 'transcription_jobs', ['status'], unique=False)
    op.create_index(op.f('ix_transcription_jobs_video_id'), 'transcription_jobs', ['video_id'], unique=False)

    # Processing Errors table
    op.create_table(
        'processing_errors',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('job_id', sa.String(length=64), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['transcription_jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processing_errors_error_code'), 'processing_errors', ['error_code'], unique=False)
    op.create_index(op.f('ix_processing_errors_job_id'), 'processing_errors', ['job_id'], unique=False)


def downgrade() -> None:
    op.drop_table('processing_errors')
    op.drop_table('transcription_jobs')
    op.drop_table('transcript_segments')
    op.drop_table('transcripts')
    op.drop_table('videos')
    op.drop_table('users')
