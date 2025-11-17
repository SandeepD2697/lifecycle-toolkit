#!/usr/bin/env python3
import sys
import yaml
import json
import html

if len(sys.argv) < 3:
    print("Usage: generate-keptn-html-report.py <analysis.yaml> <output.html>")
    sys.exit(1)

yaml_file = sys.argv[1]
output_file = sys.argv[2]

with open(yaml_file) as f:
    data = yaml.safe_load(f)

status = data.get("status", {})
timeframe = status.get("timeframe", {})
raw_json = status.get("raw", "{}")
state = status.get("state", "")
pass_status = status.get("pass", False)
warning_status = status.get("warning", False)

# Parse the raw field
raw_data = {}
try:
    raw_data = json.loads(raw_json)
except Exception as e:
    print("⚠️ Failed to parse raw field:", e)

objective_results = raw_data.get("objectiveResults", [])
analysis_name = data["metadata"]["name"]
namespace = data["metadata"]["namespace"]

html_content = f"""
<html>
<head>
  <title>Keptn Analysis Report - {analysis_name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background-color: #f2f2f2; }}
    .pass {{ color: green; font-weight: bold; }}
    .fail {{ color: red; font-weight: bold; }}
    .warn {{ color: orange; font-weight: bold; }}
    pre {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
<h1>Keptn Analysis Report</h1>
<p><strong>Analysis:</strong> {analysis_name}</p>
<p><strong>Namespace:</strong> {namespace}</p>
<p><strong>From:</strong> {timeframe.get("from", "")}</p>
<p><strong>To:</strong> {timeframe.get("to", "")}</p>
<p><strong>State:</strong> {state}</p>
<p><strong>Total Score:</strong> {raw_data.get("totalScore", "N/A")} / {raw_data.get("maximumScore", "N/A")}</p>
<p><strong>Passed:</strong> <span class='pass'>{pass_status}</span> | <strong>Warning:</strong> <span class='warn'>{warning_status}</span></p>

<table>
  <tr>
    <th>Objective</th>
    <th>Value</th>
    <th>Fixed Target</th>
    <th>Pass</th>
    <th>Warning</th>
    <th>Failure</th>
    <th>Query</th>
  </tr>
"""

for obj in objective_results:
    objective = obj.get("objective", {}).get("analysisValueTemplateRef", {}).get("name", "-")
    value = obj.get("value", "-")
    result = obj.get("result", {})
    query = html.escape(obj.get("query", ""))
    pass_result = result.get("pass", False)
    warn_result = result.get("warning", False)
    fail_result = result.get("failResult", {}).get("fulfilled", False)

    # Fixed threshold (if defined)
    target = obj.get("objective", {}).get("target", {})
    fixed_value = "-"
    if "failure" in target:
        failure = target.get("failure", {})
        if "greaterThan" in failure:
            fixed_value = failure["greaterThan"].get("fixedValue")
        elif "lessThan" in failure:
            fixed_value = failure["lessThan"].get("fixedValue")

    html_content += f"""
    <tr>
      <td>{objective}</td>
      <td>{value}</td>
      <td>{fixed_value}</td>
      <td class='pass'>{pass_result}</td>
      <td class='warn'>{warn_result}</td>
      <td class='fail'>{fail_result}</td>
      <td><pre>{query}</pre></td>
    </tr>
    """

html_content += "</table></body></html>"

with open(output_file, "w") as f:
    f.write(html_content)

print(f"✅ HTML report generated: {output_file}")
