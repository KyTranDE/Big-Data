CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE "Emails" (
  "email_id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "date" VARCHAR(50),
  "subject" VARCHAR(255),
  "content" TEXT
);

CREATE TABLE "Addresses" (
  "address_id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  "email_address" VARCHAR(255) UNIQUE
);

CREATE TABLE "EmailAddresses" (
  "email_id" UUID NOT NULL,
  "address_id" UUID NOT NULL,
  "role" VARCHAR(10) NOT NULL,
  CONSTRAINT fk_email
    FOREIGN KEY ("email_id") 
    REFERENCES "Emails" ("email_id"),
  CONSTRAINT fk_address
    FOREIGN KEY ("address_id") 
    REFERENCES "Addresses" ("address_id")
);

CREATE UNIQUE INDEX ON "EmailAddresses" ("email_id", "address_id", "role");
