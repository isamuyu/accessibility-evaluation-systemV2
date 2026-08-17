#!/bin/bash
API="http://localhost:8000"

echo "=== 创建测试项目 ==="
PROJECT=$(curl -s -X POST "$API/projects/" \
  -H "Content-Type: application/json" \
  -d '{"project_name": "建筑类型测试", "evaluation_type": "initial"}')
PROJECT_ID=$(echo $PROJECT | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "项目ID: $PROJECT_ID"

echo ""
echo "=== 1. 创建住宅类建筑（应不含Q2）==="
RES=$(curl -s -X POST "$API/buildings/" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"building_name\": \"住宅楼\", \"building_type\": \"residential\", \"floor_area\": 10000}")
echo $RES | python3 -m json.tool | grep -E "building_name|building_type"

echo ""
echo "=== 2. 创建不含住宿公共建筑（应不含Q3）==="
PUB=$(curl -s -X POST "$API/buildings/" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"building_name\": \"办公楼\", \"building_type\": \"public_no_accom\", \"floor_area\": 20000}")
echo $PUB | python3 -m json.tool | grep -E "building_name|building_type"

echo ""
echo "=== 3. 创建含住宿公共建筑（应含全部）==="
HOTEL=$(curl -s -X POST "$API/buildings/" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"building_name\": \"酒店\", \"building_type\": \"public_with_accom\", \"floor_area\": 15000}")
echo $HOTEL | python3 -m json.tool | grep -E "building_name|building_type"

echo ""
echo "测试完成。请在前端查看各建筑的评分界面，验证："
echo "1. 住宅楼：控制项不应有Q2选项"
echo "2. 办公楼：设施不应有居室和无障碍卫生间"
echo "3. 酒店：应包含所有维度和设施"
