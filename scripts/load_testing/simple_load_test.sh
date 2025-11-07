#!/bin/bash

# Simple Load Testing Script for IACT DORA Metrics API
# Uses curl and GNU parallel for concurrent requests
# No external dependencies beyond curl and parallel

set -e

# Configuration
HOST="${HOST:-http://localhost:8000}"
CONCURRENT_USERS="${CONCURRENT_USERS:-10}"
TOTAL_REQUESTS="${TOTAL_REQUESTS:-100}"
OUTPUT_DIR="${OUTPUT_DIR:-./load_test_results}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IACT Load Testing - Simple Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Host: $HOST"
echo "  Concurrent users: $CONCURRENT_USERS"
echo "  Total requests: $TOTAL_REQUESTS"
echo "  Output directory: $OUTPUT_DIR"
echo ""

# Check if parallel is installed
if ! command -v parallel &> /dev/null; then
    echo -e "${RED}Error: GNU parallel is not installed${NC}"
    echo "Install with: sudo apt-get install parallel (Ubuntu/Debian)"
    echo "           or: brew install parallel (macOS)"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="$OUTPUT_DIR/results_${TIMESTAMP}.txt"
SUMMARY_FILE="$OUTPUT_DIR/summary_${TIMESTAMP}.txt"

# Test endpoints
ENDPOINTS=(
    "/api/dora/metrics/?days=30"
    "/api/dora/dashboard/?days=30"
    "/api/dora/charts/deployment-frequency/?days=30"
    "/api/dora/charts/lead-time-trends/?days=30"
    "/api/dora/data-catalog/"
    "/api/dora/ecosystem/health/"
    "/api/dora/analytics/trends/deployment-frequency/?days=90"
    "/api/dora/analytics/comparative/period-over-period/"
)

# Function to make a single request
make_request() {
    local endpoint=$1
    local url="${HOST}${endpoint}"

    # Make request and capture timing
    local start_time=$(date +%s%N)
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$url")
    local end_time=$(date +%s%N)

    # Calculate response time in milliseconds
    local response_time=$(( (end_time - start_time) / 1000000 ))

    # Log result
    echo "$endpoint,$http_code,$response_time" >> "$RESULTS_FILE"

    # Print status
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓${NC} $endpoint - ${response_time}ms"
    else
        echo -e "${RED}✗${NC} $endpoint - HTTP $http_code - ${response_time}ms"
    fi
}

export -f make_request
export HOST RESULTS_FILE GREEN RED NC

echo -e "${YELLOW}Starting load test...${NC}"
echo ""

# Write CSV header
echo "endpoint,http_code,response_time_ms" > "$RESULTS_FILE"

# Generate list of requests to make
requests=()
for i in $(seq 1 $TOTAL_REQUESTS); do
    # Pick random endpoint
    endpoint=${ENDPOINTS[$RANDOM % ${#ENDPOINTS[@]}]}
    requests+=("$endpoint")
done

# Execute requests in parallel
printf '%s\n' "${requests[@]}" | parallel -j $CONCURRENT_USERS make_request

echo ""
echo -e "${GREEN}Load test complete!${NC}"
echo ""

# Generate summary
echo "Analyzing results..."

total_requests=$(tail -n +2 "$RESULTS_FILE" | wc -l)
successful_requests=$(tail -n +2 "$RESULTS_FILE" | awk -F, '$2 == 200' | wc -l)
failed_requests=$((total_requests - successful_requests))

# Calculate response times
response_times=$(tail -n +2 "$RESULTS_FILE" | awk -F, '{print $3}')
avg_response_time=$(echo "$response_times" | awk '{sum+=$1; count++} END {print sum/count}')
min_response_time=$(echo "$response_times" | sort -n | head -1)
max_response_time=$(echo "$response_times" | sort -n | tail -1)

# Calculate percentiles
p50=$(echo "$response_times" | sort -n | awk '{a[NR]=$1} END {print a[int(NR*0.50)]}')
p95=$(echo "$response_times" | sort -n | awk '{a[NR]=$1} END {print a[int(NR*0.95)]}')
p99=$(echo "$response_times" | sort -n | awk '{a[NR]=$1} END {print a[int(NR*0.99)]}')

# Generate summary report
cat > "$SUMMARY_FILE" <<EOF
IACT Load Test Summary
Generated: $(date)
Host: $HOST
Concurrent Users: $CONCURRENT_USERS

========================================
Request Statistics
========================================
Total Requests: $total_requests
Successful (200): $successful_requests
Failed: $failed_requests
Success Rate: $(echo "scale=2; $successful_requests / $total_requests * 100" | bc)%

========================================
Response Time Statistics (ms)
========================================
Average: $(printf "%.2f" $avg_response_time)
Minimum: $min_response_time
Maximum: $max_response_time
Median (p50): $p50
95th Percentile (p95): $p95
99th Percentile (p99): $p99

========================================
Performance Assessment
========================================
EOF

# Performance assessment
if (( $(echo "$p95 < 1000" | bc -l) )); then
    echo "✓ PASS: p95 response time under 1 second" >> "$SUMMARY_FILE"
else
    echo "✗ FAIL: p95 response time exceeds 1 second" >> "$SUMMARY_FILE"
fi

if (( $(echo "$avg_response_time < 500" | bc -l) )); then
    echo "✓ PASS: Average response time under 500ms" >> "$SUMMARY_FILE"
else
    echo "✗ FAIL: Average response time exceeds 500ms" >> "$SUMMARY_FILE"
fi

success_rate=$(echo "scale=2; $successful_requests / $total_requests * 100" | bc)
if (( $(echo "$success_rate >= 99" | bc -l) )); then
    echo "✓ PASS: Success rate >= 99%" >> "$SUMMARY_FILE"
else
    echo "✗ FAIL: Success rate < 99%" >> "$SUMMARY_FILE"
fi

# Display summary
cat "$SUMMARY_FILE"

echo ""
echo "Full results saved to: $RESULTS_FILE"
echo "Summary saved to: $SUMMARY_FILE"
echo ""

# Exit code based on performance
if (( $(echo "$p95 < 1000" | bc -l) )) && \
   (( $(echo "$avg_response_time < 500" | bc -l) )) && \
   (( $(echo "$success_rate >= 99" | bc -l) )); then
    echo -e "${GREEN}All performance targets met!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some performance targets not met${NC}"
    exit 1
fi
