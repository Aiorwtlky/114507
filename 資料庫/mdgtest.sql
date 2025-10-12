-- #############################################################################
-- -- 1. 人員與權限管理 (User & Permission Management)
-- #############################################################################

-- Model: PersonnelProfile
-- Note: This table extends Django's built-in User model.
-- The user_id is both the Primary Key and a Foreign Key to auth_user.id.
CREATE TABLE "personnel_profile" (
    "user_id" INT NOT NULL PRIMARY KEY,
    "personnel_number" VARCHAR(50) NOT NULL UNIQUE,
    "gender" VARCHAR(20) NOT NULL DEFAULT 'UNSPECIFIED',
    "license_number" VARCHAR(20) NOT NULL,
    "avatar" VARCHAR(100), -- Corresponds to ImageField (stores file path)
    "phone" VARCHAR(20) NOT NULL,
    "license_type" VARCHAR(50) NOT NULL,
    "driving_experience" INT NOT NULL DEFAULT 0,
    "nfc_card_id" VARCHAR(50) UNIQUE
);

-- Model: Group
CREATE TABLE "group" (
    "id" BIGSERIAL PRIMARY KEY,
    "group_number" VARCHAR(50) NOT NULL UNIQUE,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "created_by_id" INT
);

-- Model: GroupMember
-- This is the through table for the many-to-many relationship between Group and User.
CREATE TABLE "group_member" (
    "id" BIGSERIAL PRIMARY KEY,
    "joined_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "role" VARCHAR(10) NOT NULL DEFAULT 'MEMBER',
    "group_id" BIGINT NOT NULL,
    "user_id" INT NOT NULL,
    UNIQUE ("group_id", "user_id")
);

-- Model: ActivationCode
CREATE TABLE "activationcode" (
    "id" BIGSERIAL PRIMARY KEY,
    "code" VARCHAR(16) NOT NULL UNIQUE,
    "max_uses" INT NOT NULL DEFAULT 50,
    "current_uses" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "expires_at" TIMESTAMP WITH TIME ZONE,
    "notes" TEXT NOT NULL
);


-- #############################################################################
-- -- 2. 系統與公告 (System & Announcement)
-- #############################################################################

-- Model: SystemAnnouncement
CREATE TABLE "system_announcement" (
    "id" BIGSERIAL PRIMARY KEY,
    "announcement_number" VARCHAR(50) NOT NULL UNIQUE,
    "content" TEXT NOT NULL,
    "date" TIMESTAMP WITH TIME ZONE NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE
);

-- Model: GroupAnnouncement
CREATE TABLE "group_announcement" (
    "id" BIGSERIAL PRIMARY KEY,
    "announcement_number" VARCHAR(50) NOT NULL UNIQUE,
    "content" TEXT NOT NULL,
    "publish_date" TIMESTAMP WITH TIME ZONE NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "group_id" BIGINT NOT NULL,
    "publisher_id" INT NOT NULL
);

-- Model: InvitationCode
CREATE TABLE "invitationcode" (
    "id" BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL DEFAULT 'Default Invite',
    "code" VARCHAR(8) NOT NULL UNIQUE,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "expires_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "is_used" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_by_id" INT NOT NULL,
    "group_id" BIGINT NOT NULL
);


-- #############################################################################
-- -- 3. 車輛與行程管理 (Vehicle & Trip Management)
-- #############################################################################

-- Model: VehicleDevice
CREATE TABLE "vehicle_device" (
    "id" BIGSERIAL PRIMARY KEY,
    "device_number" VARCHAR(50) NOT NULL UNIQUE,
    "vehicle_type" VARCHAR(20) NOT NULL,
    "activation_date" DATE NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Model: Trip
CREATE TABLE "trip" (
    "id" BIGSERIAL PRIMARY KEY,
    "trip_number" VARCHAR(50) NOT NULL UNIQUE,
    "name" VARCHAR(200) NOT NULL,
    "score" DECIMAL(5, 2),
    "in_car_score" DECIMAL(5, 2),
    "out_car_score" DECIMAL(5, 2),
    "ai_suggestion" TEXT,
    "start_time" TIMESTAMP WITH TIME ZONE,
    "end_time" TIMESTAMP WITH TIME ZONE,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "total_mileage" DOUBLE PRECISION,
    "device_id" BIGINT NOT NULL,
    "group_id" BIGINT NOT NULL,
    "personnel_id" INT NOT NULL
);

-- Model: ScoringStandard
CREATE TABLE "scoring_standard" (
    "id" SERIAL PRIMARY KEY,
    "event_number" VARCHAR(50) NOT NULL UNIQUE,
    "description" VARCHAR(255) NOT NULL,
    "deduction_points" INT NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE
);

-- Model: AiVisionLog
CREATE TABLE "ai_vision_log" (
    "id" BIGSERIAL PRIMARY KEY,
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    "event_details" VARCHAR(255) NOT NULL,
    "confidence_score" DOUBLE PRECISION,
    "event_id" INT NOT NULL,
    "trip_id" BIGINT NOT NULL
);

-- Model: VideoRecord
CREATE TABLE "video_record" (
    "id" BIGSERIAL PRIMARY KEY,
    "video_number" VARCHAR(50) NOT NULL UNIQUE,
    "start_time" TIMESTAMP WITH TIME ZONE NOT NULL,
    "end_time" TIMESTAMP WITH TIME ZONE NOT NULL,
    "location" VARCHAR(500) NOT NULL,
    "file_size" BIGINT,
    "video_url" VARCHAR(500),
    "trip_id" BIGINT NOT NULL
);


-- #############################################################################
-- -- 4. 回饋 (Feedback)
-- #############################################################################

-- Model: TripSuggestionFeedback
CREATE TABLE "tripsuggestionfeedback" (
    "id" BIGSERIAL PRIMARY KEY,
    "feedback_type" INT NOT NULL,
    "comment" TEXT,
    "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
    "trip_id" BIGINT NOT NULL,
    "user_id" INT NOT NULL,
    UNIQUE ("trip_id", "user_id")
);


-- #############################################################################
-- -- FOREIGN KEY CONSTRAINTS
-- -- Applying constraints at the end to avoid dependency errors during creation.
-- #############################################################################

-- Assumes a table named "auth_user" exists for Django's User model.

-- Constraints for PersonnelProfile
ALTER TABLE "personnel_profile" ADD CONSTRAINT "personnel_profile_user_id_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for Group
ALTER TABLE "group" ADD CONSTRAINT "group_created_by_id_fk_auth_user_id" FOREIGN KEY ("created_by_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for GroupMember
ALTER TABLE "group_member" ADD CONSTRAINT "group_member_group_id_fk_group_id" FOREIGN KEY ("group_id") REFERENCES "group" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "group_member" ADD CONSTRAINT "group_member_user_id_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for GroupAnnouncement
ALTER TABLE "group_announcement" ADD CONSTRAINT "group_announcement_group_id_fk_group_id" FOREIGN KEY ("group_id") REFERENCES "group" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "group_announcement" ADD CONSTRAINT "group_announcement_publisher_id_fk_auth_user_id" FOREIGN KEY ("publisher_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for InvitationCode
ALTER TABLE "invitationcode" ADD CONSTRAINT "invitationcode_created_by_id_fk_auth_user_id" FOREIGN KEY ("created_by_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "invitationcode" ADD CONSTRAINT "invitationcode_group_id_fk_group_id" FOREIGN KEY ("group_id") REFERENCES "group" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for Trip
ALTER TABLE "trip" ADD CONSTRAINT "trip_device_id_fk_vehicle_device_id" FOREIGN KEY ("device_id") REFERENCES "vehicle_device" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "trip" ADD CONSTRAINT "trip_group_id_fk_group_id" FOREIGN KEY ("group_id") REFERENCES "group" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "trip" ADD CONSTRAINT "trip_personnel_id_fk_auth_user_id" FOREIGN KEY ("personnel_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for AiVisionLog
ALTER TABLE "ai_vision_log" ADD CONSTRAINT "ai_vision_log_event_id_fk_scoring_standard_id" FOREIGN KEY ("event_id") REFERENCES "scoring_standard" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "ai_vision_log" ADD CONSTRAINT "ai_vision_log_trip_id_fk_trip_id" FOREIGN KEY ("trip_id") REFERENCES "trip" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for VideoRecord
ALTER TABLE "video_record" ADD CONSTRAINT "video_record_trip_id_fk_trip_id" FOREIGN KEY ("trip_id") REFERENCES "trip" ("id") DEFERRABLE INITIALLY DEFERRED;

-- Constraints for TripSuggestionFeedback
ALTER TABLE "tripsuggestionfeedback" ADD CONSTRAINT "tripsuggestionfeedback_trip_id_fk_trip_id" FOREIGN KEY ("trip_id") REFERENCES "trip" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "tripsuggestionfeedback" ADD CONSTRAINT "tripsuggestionfeedback_user_id_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
