#!/bin/bash

################################################################################
# Autonomous Kids Shorts Generator - Complete Pipeline Orchestration Script
# 
# This script orchestrates the entire pipeline:
# 1. Script Generation
# 2. Video Creation
# 3. YouTube Upload
# 4. EC2 Instance Shutdown
#
# Author: Rajkumarasam
# Created: 2026-01-03
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/pipeline_${TIMESTAMP}.log"
STATE_FILE="${LOG_DIR}/pipeline_state_${TIMESTAMP}.txt"

# Pipeline stages
STAGE_SCRIPT_GENERATION="script_generation"
STAGE_VIDEO_CREATION="video_creation"
STAGE_YOUTUBE_UPLOAD="youtube_upload"
STAGE_SHUTDOWN="ec2_shutdown"

# Flags for conditional execution
SKIP_SCRIPT_GENERATION=${SKIP_SCRIPT_GENERATION:-false}
SKIP_VIDEO_CREATION=${SKIP_VIDEO_CREATION:-false}
SKIP_YOUTUBE_UPLOAD=${SKIP_YOUTUBE_UPLOAD:-false}
SKIP_EC2_SHUTDOWN=${SKIP_EC2_SHUTDOWN:-false}
DRY_RUN=${DRY_RUN:-false}

################################################################################
# Utility Functions
################################################################################

# Initialize logging
initialize_logging() {
    mkdir -p "${LOG_DIR}"
    touch "${LOG_FILE}"
    touch "${STATE_FILE}"
    
    log "INFO" "Pipeline orchestration started"
    log "INFO" "Log file: ${LOG_FILE}"
    log "INFO" "State file: ${STATE_FILE}"
}

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
    
    case ${level} in
        ERROR)
            echo -e "${RED}[${level}] ${message}${NC}" >&2
            ;;
        WARN)
            echo -e "${YELLOW}[${level}] ${message}${NC}" >&2
            ;;
        INFO)
            echo -e "${BLUE}[${level}] ${message}${NC}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[${level}] ${message}${NC}"
            ;;
    esac
}

# Record stage completion
record_stage() {
    local stage=$1
    local status=$2
    local duration=$3
    
    echo "${stage}|${status}|${duration}|$(date '+%Y-%m-%d %H:%M:%S')" >> "${STATE_FILE}"
    log "INFO" "Stage '${stage}' completed with status: ${status} (Duration: ${duration}s)"
}

# Check if required commands exist
check_requirements() {
    log "INFO" "Checking system requirements..."
    
    local required_commands=("python3" "curl" "git" "jq")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "${cmd}" &> /dev/null; then
            log "ERROR" "Required command not found: ${cmd}"
            return 1
        fi
    done
    
    log "SUCCESS" "All required commands found"
    return 0
}

# Check if Python scripts exist
check_scripts_exist() {
    log "INFO" "Checking if required Python scripts exist..."
    
    local required_scripts=(
        "script_generator.py"
        "video_creator.py"
        "youtube_uploader.py"
    )
    
    for script in "${required_scripts[@]}"; do
        if [[ ! -f "${SCRIPT_DIR}/${script}" ]]; then
            log "WARN" "Script not found: ${script}"
        fi
    done
}

# Validate environment
validate_environment() {
    log "INFO" "Validating environment..."
    
    # Check for AWS credentials if EC2 shutdown is not skipped
    if [[ "${SKIP_EC2_SHUTDOWN}" != "true" ]]; then
        if [[ -z "${AWS_ACCESS_KEY_ID:-}" ]] || [[ -z "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
            log "WARN" "AWS credentials not found. EC2 shutdown will be skipped."
            SKIP_EC2_SHUTDOWN=true
        fi
    fi
    
    # Check for YouTube credentials if upload is not skipped
    if [[ "${SKIP_YOUTUBE_UPLOAD}" != "true" ]]; then
        if [[ ! -f "${SCRIPT_DIR}/credentials/youtube_credentials.json" ]]; then
            log "WARN" "YouTube credentials not found at credentials/youtube_credentials.json"
            SKIP_YOUTUBE_UPLOAD=true
        fi
    fi
    
    log "SUCCESS" "Environment validation complete"
}

################################################################################
# Pipeline Stage Functions
################################################################################

# Stage 1: Script Generation
run_script_generation() {
    local start_time=$(date +%s)
    log "INFO" "=========================================="
    log "INFO" "STAGE 1: Script Generation"
    log "INFO" "=========================================="
    
    if [[ "${SKIP_SCRIPT_GENERATION}" == "true" ]]; then
        log "INFO" "Skipping script generation (SKIP_SCRIPT_GENERATION=true)"
        return 0
    fi
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "[DRY RUN] Would execute: python3 script_generator.py"
        return 0
    fi
    
    if [[ ! -f "${SCRIPT_DIR}/script_generator.py" ]]; then
        log "ERROR" "script_generator.py not found"
        return 1
    fi
    
    log "INFO" "Generating video scripts..."
    
    if python3 "${SCRIPT_DIR}/script_generator.py" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "SUCCESS" "Script generation completed successfully"
        record_stage "${STAGE_SCRIPT_GENERATION}" "SUCCESS" "${duration}"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "ERROR" "Script generation failed"
        record_stage "${STAGE_SCRIPT_GENERATION}" "FAILED" "${duration}"
        return 1
    fi
}

# Stage 2: Video Creation
run_video_creation() {
    local start_time=$(date +%s)
    log "INFO" "=========================================="
    log "INFO" "STAGE 2: Video Creation"
    log "INFO" "=========================================="
    
    if [[ "${SKIP_VIDEO_CREATION}" == "true" ]]; then
        log "INFO" "Skipping video creation (SKIP_VIDEO_CREATION=true)"
        return 0
    fi
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "[DRY RUN] Would execute: python3 video_creator.py"
        return 0
    fi
    
    if [[ ! -f "${SCRIPT_DIR}/video_creator.py" ]]; then
        log "ERROR" "video_creator.py not found"
        return 1
    fi
    
    log "INFO" "Creating videos from generated scripts..."
    
    if python3 "${SCRIPT_DIR}/video_creator.py" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "SUCCESS" "Video creation completed successfully"
        record_stage "${STAGE_VIDEO_CREATION}" "SUCCESS" "${duration}"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "ERROR" "Video creation failed"
        record_stage "${STAGE_VIDEO_CREATION}" "FAILED" "${duration}"
        return 1
    fi
}

# Stage 3: YouTube Upload
run_youtube_upload() {
    local start_time=$(date +%s)
    log "INFO" "=========================================="
    log "INFO" "STAGE 3: YouTube Upload"
    log "INFO" "=========================================="
    
    if [[ "${SKIP_YOUTUBE_UPLOAD}" == "true" ]]; then
        log "INFO" "Skipping YouTube upload (SKIP_YOUTUBE_UPLOAD=true)"
        return 0
    fi
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "[DRY RUN] Would execute: python3 youtube_uploader.py"
        return 0
    fi
    
    if [[ ! -f "${SCRIPT_DIR}/youtube_uploader.py" ]]; then
        log "ERROR" "youtube_uploader.py not found"
        return 1
    fi
    
    log "INFO" "Uploading videos to YouTube..."
    
    if python3 "${SCRIPT_DIR}/youtube_uploader.py" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "SUCCESS" "YouTube upload completed successfully"
        record_stage "${STAGE_YOUTUBE_UPLOAD}" "SUCCESS" "${duration}"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "ERROR" "YouTube upload failed"
        record_stage "${STAGE_YOUTUBE_UPLOAD}" "FAILED" "${duration}"
        return 1
    fi
}

# Stage 4: EC2 Instance Shutdown
run_ec2_shutdown() {
    local start_time=$(date +%s)
    log "INFO" "=========================================="
    log "INFO" "STAGE 4: EC2 Instance Shutdown"
    log "INFO" "=========================================="
    
    if [[ "${SKIP_EC2_SHUTDOWN}" == "true" ]]; then
        log "INFO" "Skipping EC2 shutdown (SKIP_EC2_SHUTDOWN=true)"
        return 0
    fi
    
    if [[ "${DRY_RUN}" == "true" ]]; then
        log "INFO" "[DRY RUN] Would shutdown EC2 instance"
        return 0
    fi
    
    # Get the instance ID from AWS metadata
    log "INFO" "Retrieving EC2 instance metadata..."
    
    local instance_id
    instance_id=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "")
    
    if [[ -z "${instance_id}" ]]; then
        log "WARN" "Could not retrieve instance ID from metadata. Skipping EC2 shutdown."
        return 0
    fi
    
    log "INFO" "Shutting down EC2 instance: ${instance_id}"
    
    if aws ec2 stop-instances --instance-ids "${instance_id}" --region "${AWS_REGION:-us-east-1}" >> "${LOG_FILE}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "SUCCESS" "EC2 instance shutdown initiated"
        record_stage "${STAGE_SHUTDOWN}" "SUCCESS" "${duration}"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "ERROR" "EC2 instance shutdown failed"
        record_stage "${STAGE_SHUTDOWN}" "FAILED" "${duration}"
        return 1
    fi
}

# Error handler
error_handler() {
    local exit_code=$?
    local line_number=$1
    
    log "ERROR" "Pipeline execution failed at line ${line_number} with exit code ${exit_code}"
    log "ERROR" "Review the log file for more details: ${LOG_FILE}"
    
    echo ""
    log "INFO" "Pipeline Execution Summary:"
    cat "${STATE_FILE}"
    
    exit ${exit_code}
}

# Pipeline summary
print_summary() {
    echo ""
    log "INFO" "=========================================="
    log "INFO" "PIPELINE EXECUTION SUMMARY"
    log "INFO" "=========================================="
    log "INFO" "Start Time: $(head -1 "${LOG_FILE}" | cut -d' ' -f1,2)"
    log "INFO" "End Time: $(date '+%Y-%m-%d %H:%M:%S')"
    log "INFO" "Log File: ${LOG_FILE}"
    log "INFO" "State File: ${STATE_FILE}"
    echo ""
    log "INFO" "Stage Results:"
    while IFS='|' read -r stage status duration timestamp; do
        if [[ "${status}" == "SUCCESS" ]]; then
            echo -e "${GREEN}  ✓ ${stage}: ${status} (${duration}s)${NC}"
        else
            echo -e "${RED}  ✗ ${stage}: ${status} (${duration}s)${NC}"
        fi
    done < "${STATE_FILE}"
    echo ""
}

# Display usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Orchestrate the complete pipeline for autonomous kids shorts generation.

OPTIONS:
    -h, --help                      Show this help message
    -d, --dry-run                   Run in dry-run mode (no actual operations)
    --skip-script-generation        Skip script generation stage
    --skip-video-creation           Skip video creation stage
    --skip-youtube-upload           Skip YouTube upload stage
    --skip-ec2-shutdown             Skip EC2 shutdown stage
    -v, --verbose                   Enable verbose output

ENVIRONMENT VARIABLES:
    SKIP_SCRIPT_GENERATION          Set to 'true' to skip script generation
    SKIP_VIDEO_CREATION             Set to 'true' to skip video creation
    SKIP_YOUTUBE_UPLOAD             Set to 'true' to skip YouTube upload
    SKIP_EC2_SHUTDOWN               Set to 'true' to skip EC2 shutdown
    DRY_RUN                         Set to 'true' for dry-run mode
    AWS_ACCESS_KEY_ID               AWS access key (required for EC2 shutdown)
    AWS_SECRET_ACCESS_KEY           AWS secret key (required for EC2 shutdown)
    AWS_REGION                      AWS region (default: us-east-1)

EXAMPLES:
    # Run complete pipeline
    ./run_all.sh

    # Run in dry-run mode
    ./run_all.sh --dry-run

    # Skip EC2 shutdown
    ./run_all.sh --skip-ec2-shutdown

    # Run only YouTube upload stage
    ./run_all.sh --skip-script-generation --skip-video-creation

EOF
}

################################################################################
# Main Execution
################################################################################

main() {
    # Set error handler
    trap 'error_handler ${LINENO}' ERR
    
    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-script-generation)
                SKIP_SCRIPT_GENERATION=true
                shift
                ;;
            --skip-video-creation)
                SKIP_VIDEO_CREATION=true
                shift
                ;;
            --skip-youtube-upload)
                SKIP_YOUTUBE_UPLOAD=true
                shift
                ;;
            --skip-ec2-shutdown)
                SKIP_EC2_SHUTDOWN=true
                shift
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Initialize
    initialize_logging
    
    log "INFO" "Configuration:"
    log "INFO" "  Script Directory: ${SCRIPT_DIR}"
    log "INFO" "  DRY_RUN: ${DRY_RUN}"
    log "INFO" "  SKIP_SCRIPT_GENERATION: ${SKIP_SCRIPT_GENERATION}"
    log "INFO" "  SKIP_VIDEO_CREATION: ${SKIP_VIDEO_CREATION}"
    log "INFO" "  SKIP_YOUTUBE_UPLOAD: ${SKIP_YOUTUBE_UPLOAD}"
    log "INFO" "  SKIP_EC2_SHUTDOWN: ${SKIP_EC2_SHUTDOWN}"
    echo ""
    
    # Pre-flight checks
    check_requirements || exit 1
    check_scripts_exist
    validate_environment
    echo ""
    
    # Execute pipeline stages
    run_script_generation
    run_video_creation
    run_youtube_upload
    run_ec2_shutdown
    
    # Print summary and exit successfully
    print_summary
    log "SUCCESS" "Pipeline execution completed successfully!"
    exit 0
}

# Execute main function
main "$@"
