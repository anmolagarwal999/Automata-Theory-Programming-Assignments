while IFS= read -r line; do
    echo "Text read from file: $line"
    python3 q1_check.py $line "$line.json"
    echo "-----------------------------------------"
done < regex_tests_for_q1.txt