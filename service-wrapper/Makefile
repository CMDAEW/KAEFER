# Variables to store package ID and version from manifest.yaml
PKG_ID := $(shell yq e ".id" manifest.yaml)
PKG_VERSION := $(shell yq e ".version" manifest.yaml)
TS_FILES := $(shell find ./ -name \*.ts)

# delete the target of a rule if it has changed and its recipe exits with a nonzero exit status
.DELETE_ON_ERROR:

# Default target
all: verify

# Verification target
verify: $(PKG_ID).s9pk
	start-sdk verify s9pk $(PKG_ID).s9pk

# Installation target
install:
	embassy-cli package install $(PKG_ID).s9pk

# Clean up target
clean:
	rm -f image.tar
	rm -f $(PKG_ID).s9pk
	rm -f scripts/*.js

# Bundle TypeScript files
scripts/embassy.js: $(TS_FILES)
	deno bundle scripts/embassy.ts scripts/embassy.js

# Build Docker image and save it as image.tar
image.tar: Dockerfile entrypoint.sh
	docker buildx build --tag start9/$(PKG_ID)/main:$(PKG_VERSION) --platform=linux/arm64 -o type=docker,dest=image.tar .

# Package target
$(PKG_ID).s9pk: manifest.yaml instructions.md icon.png LICENSE scripts/embassy.js image.tar scripts/migrate-from.js scripts/migrate-to.js
	start-sdk pack
