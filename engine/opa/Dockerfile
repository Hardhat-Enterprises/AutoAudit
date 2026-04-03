# Custom OPA image with compliance policies baked in for Kubernetes deployment.
#
# In local development (docker-compose), OPA uses the upstream image with
# engine/policies/ mounted as a read-only volume. Kubernetes does not support
# host volume mounts, so this Dockerfile packages the policies into the image
# at build time instead.
#
# Build context must be the repository root:
#   docker build -f engine/opa/Dockerfile -t autoaudit/opa .
#
# The build also generates /policies/manifest.json listing every included
# policy file with its SHA-256 checksum for traceability.

FROM alpine:3.21 AS build

COPY engine/policies /policies

# Generate manifest listing all included policy files with SHA-256 checksums
RUN find /policies -type f \( -name "*.rego" -o -name "*.json" \) -exec sh -c \
    'echo "{\"path\": \"$1\", \"sha256\": \"$(sha256sum "$1" | cut -d" " -f1)\"}"' _ {} \; \
    | sort > /policies/manifest.json

# Production OPA image. Runs as non-root (UID 1000:1000) by default.
FROM openpolicyagent/opa:1.4.2
COPY --from=build /policies /policies
