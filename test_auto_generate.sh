#!/bin/bash
API="http://localhost:8000"

echo "=== 1. 创建测试项目 ==="
PROJECT=$(curl -s -X POST "$API/projects/" \
  -H "Content-Type: application/json" \
  -d '{"project_name": "自动生成测试", "evaluation_type": "initial"}')
PROJECT_ID=$(echo $PROJECT | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "项目ID: $PROJECT_ID"

echo ""
echo "=== 2. 创建住宅类建筑（应自动生成Q1,Q3,Q4控制项和系统评分项）==="
RES=$(curl -s -X POST "$API/buildings/" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"building_name\": \"住宅楼\", \"building_type\": \"residential\", \"floor_area\": 10000}")
BUILDING_ID=$(echo $RES | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "建筑ID: $BUILDING_ID"

echo ""
echo "=== 3. 自动生成控制项 ==="
curl -s -X POST "$API/templates/generate-control-items/$BUILDING_ID" | python3 -m json.tool

echo ""
echo "=== 4. 自动生成系统评分项 ==="
curl -s -X POST "$API/templates/generate-system-scores/$BUILDING_ID" | python3 -m json.tool

echo ""
echo "=== 5. 查看生成的控制项 ==="
curl -s "$API/scoring/control-items/$BUILDING_ID" | python3 -m json.tool | head -20

echo ""
echo "=== 6. 查看生成的系统评分项 ==="
curl -s "$API/scoring/system-scores/$BUILDING_ID" | python3 -m json.tool | head -30

echo ""
echo "测试完成！"
