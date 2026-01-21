echo "  EchoCare - Long-Term Stability Test"
echo "This script will run EchoCare for extended periods to test stability"
echo "Test Duration: 4 hours (adjustable)"

# Generate timestamp for this test
timestamp=$(date +%Y%m%d_%H%M%S)
log_file="/home/danellepi/echocare/logs/stability_tests/test_${timestamp}.log"

echo "Log file: $log_file"
echo "Starting stability test..."
echo "Press Ctrl+C to stop early"

# Record start time
echo "Test started: $(date)" | tee -a $log_file
echo "=======================================================================" | tee -a $log_file

# Run the system with timeout (4 hours = 14400 seconds)
timeout 14400 python3 /home/danellepi/echocare/EchoCare-Pi/main_monitor/echocare_system.py 2>&1 | tee -a $log_file

# Record end time
echo "" | tee -a $log_file
echo "=======================================================================" | tee -a $log_file
echo "Test ended: $(date)" | tee -a $log_file

# Analyze the log
echo "" | tee -a $log_file
echo "Test Summary:" | tee -a $log_file
echo "-------------" | tee -a $log_file

# Count cries detected
cry_count=$(grep "CRY DETECTED" $log_file | wc -l)
echo "Total cries detected: $cry_count" | tee -a $log_file

# Count errors
error_count=$(grep "ERROR" $log_file | wc -l)
echo "Errors encountered: $error_count" | tee -a $log_file

# Count warnings
warning_count=$(grep "WARNING" $log_file | wc -l)
echo "Warnings: $warning_count" | tee -a $log_file

echo "" | tee -a $log_file
echo "Full log saved to: $log_file"
echo ""